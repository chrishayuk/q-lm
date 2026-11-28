"""QLM-WORKING-GRAPH-001, stage 1 prototype (docs/qlm-working-graph-001-plan.md).

A working graph for one story: a node per token occurrence, each with sparse
weighted features by type. Original types: "w" (the word), "c" (its class
under v2's first class model), "ps" (position in sentence, capped at 6),
"ss" (sentence in story, capped at 3). A pass p applies an operation
(q, k): the current node's q-features address earlier nodes through their
k-features, by a learned lift table; the addressed nodes' words are written
onto the current node as type "p{p}" (a result that later passes can use as
q), and the current word is written onto the addressed nodes as type
"p{p}b" (a causal revision of earlier nodes, disabled in the frozen arm).
The final pass predicts from the addressed nodes' successors.

Learning, with no gradient:
- every candidate's lift table is counted on one fixed sample of training
  stories (the same for all candidates), with earlier passes frozen;
- the candidate kept at each pass is the one that most lowers bits on
  held-out training stories, mixed with a story bigram-cache baseline by EM
  on those held-out stories; selection stops when nothing gains 0.001 bits.

Stage 2 (signed writes, transforms, consolidation) and the beam are not here.
"""
import collections, math, time

BETA = 1.0
MAX_ADDR = 64      # addressed nodes per operation (budget)
MAX_FEAT = 16      # written features per node per type (budget)
PRUNE = 0.01
ALPHA = 5.0        # lift smoothing
ORIGINAL = ("w", "c", "ps", "ss")
MAX_NODES = 4096   # a benchmarking constraint only, not architecture (limit computation, not context):
                   # older nodes are kept and indexed but not addressed. It never binds on TinyStories.


class Graph:
    """The working graph of one story prefix, built token by token."""

    def __init__(self, ops, lifts, cls, frozen=False, predict="final"):
        self.ops, self.lifts, self.cls, self.frozen, self.predict = ops, lifts, cls, frozen, predict
        self.all_addr = {}
        self.nodes = []          # each: {"f": {type: {value: weight}}, "succ": token or None, "disc": {type: mass}}
        self.index = collections.defaultdict(lambda: collections.defaultdict(set))  # type -> value -> {node}
        self.sent, self.pos = 0, 0
        self.lookups = 0

    def add(self, tok, END):
        if self.nodes:
            self.nodes[-1]["succ"] = tok
        f = {"w": {tok: 1.0}, "c": {self.cls(tok): 1.0}, "ps": {min(self.pos, 6): 1.0}, "ss": {min(self.sent, 3): 1.0}}
        n = len(self.nodes)
        self.nodes.append({"f": f, "succ": None, "disc": {}})
        for t, vals in f.items():
            for v in vals:
                self.index[t][v].add(n)
        if tok == END:
            self.sent, self.pos = self.sent + 1, 0
        else:
            self.pos += 1

    def write(self, n, typ, vals):
        """Add evidence (vals carry absolute strength, not unit mass). Weights are scaled down only
        if their total with the discarded mass exceeds 1, never up, so weak evidence stays weak.
        Pruned features leave the index and their mass is recorded as discarded."""
        node = self.nodes[n]
        cur = node["f"].setdefault(typ, {})
        for v, w in vals.items():
            if v not in cur:
                self.index[typ][v].add(n)
            cur[v] = cur.get(v, 0.0) + w
        disc = node["disc"].get(typ, 0.0)
        z = max(1.0, sum(cur.values()) + disc)
        scaled = sorted(((v, w / z) for v, w in cur.items()), key=lambda x: -x[1])
        kept = {v: w for v, w in scaled[:MAX_FEAT] if w >= PRUNE}
        dropped = [v for v, _ in scaled if v not in kept]
        for v in dropped:
            self.index[typ][v].discard(n)
        node["disc"][typ] = disc / z + sum(w for v, w in scaled if v not in kept)
        node["f"][typ] = kept

    def address(self, p, q, k, lift):
        """Weights over earlier nodes with a known successor (the last node is the query)."""
        qn = len(self.nodes) - 1
        score = collections.defaultdict(float)
        for qv, qw in self.nodes[qn]["f"].get(q, {}).items():
            for kv, nodes in self.index[k].items():
                l = lift.get((qv, kv))
                if l is None or l <= 1.0:
                    continue
                for n in nodes:
                    if qn - MAX_NODES <= n < qn:
                        self.lookups += 1
                        kw = self.nodes[n]["f"].get(k, {}).get(kv, 0.0)
                        if kw:
                            score[n] += qw * kw * (l - 1.0)
        return dict(sorted(score.items(), key=lambda x: -x[1])[:MAX_ADDR])

    def run(self):
        """Apply every pass at the current position; return the last pass's addressed nodes."""
        if not self.nodes:
            return {}
        self.all_addr = {}
        qn = len(self.nodes) - 1
        addr = {}
        for p, (q, k) in enumerate(self.ops, 1):
            addr = self.address(p, q, k, self.lifts[p - 1])
            tot = sum(addr.values())
            if tot <= 0:
                continue
            strength = tot / (tot + 1.0)  # evidence strength of this pass's result, in (0, 1)
            wvals = collections.defaultdict(float)
            for n, s in addr.items():
                for v, w in self.nodes[n]["f"]["w"].items():
                    wvals[v] += strength * s / tot * w
            self.write(qn, f"p{p}", wvals)
            if not self.frozen:
                qw = self.nodes[qn]["f"]["w"]
                for n, s in addr.items():
                    self.write(n, f"p{p}b", {v: strength * s / tot * w for v, w in qw.items()})
            for n, s_ in addr.items():
                self.all_addr[n] = self.all_addr.get(n, 0.0) + s_
        return addr

    def dist(self, p_uni):
        """Next-token distribution (sparse explicit part + weight on the unigram) from the final pass."""
        addr = self.run()
        if self.predict == "all":  # the accumulated state: every pass's addressed nodes
            addr = self.all_addr
        e, tot = collections.defaultdict(float), 0.0
        for n, s in addr.items():
            y = self.nodes[n]["succ"]
            if y is not None:
                e[y] += s
                tot += s
        d = {y: x / (tot + BETA) + BETA / (tot + BETA) * p_uni(y) for y, x in e.items()}
        d["__rest__"] = BETA / (tot + BETA)
        return d


def stories_of(sents, ids):
    out = []
    for s, sid in zip(sents, ids):
        if out and out[-1][0] == sid:
            out[-1][1].append(s)
        else:
            out.append([sid, [s]])
    return [x[1] for x in out]


def count_lift(stories, ops, lifts, q, k, cls, END):
    """The lift table for a new pass (q, k), earlier passes frozen, on the sample stories."""
    hits, trials = collections.Counter(), collections.Counter()
    for story in stories:
        g = Graph(ops, lifts, cls)
        toks = [t for s in story for t in s + [END]]
        for t, tok in enumerate(toks):
            if t >= 2:
                g.run()  # earlier passes write their results before the new pass is counted
                qn = len(g.nodes) - 1
                qf = g.nodes[qn]["f"].get(q, {})
                for n in range(qn):
                    succ = g.nodes[n]["succ"]
                    for kv, kw in g.nodes[n]["f"].get(k, {}).items():
                        for qv, qw in qf.items():
                            trials[(qv, kv)] += qw * kw
                            if succ == tok:
                                hits[(qv, kv)] += qw * kw
            g.add(tok, END)
    h0 = sum(hits.values()) / max(sum(trials.values()), 1e-12)
    return {key: ((hits[key] + ALPHA * h0) / (n + ALPHA)) / h0 for key, n in trials.items()
            if (hits[key] + ALPHA * h0) / (n + ALPHA) > h0}


def heldout_bits(stories, ops, lifts, cls, END, p_uni, frozen=False):
    """Bits on held-out stories of a 2-component mixture: a story bigram cache and the graph's
    prediction, the weight fitted by EM on these stories. Returns (bits with, bits cache alone)."""
    rows, story_of_row = [], []
    for si, story in enumerate(stories):
        g = Graph(ops, lifts, cls, frozen)
        toks = [t for s in story for t in s + [END]]
        prev = []
        for t, tok in enumerate(toks):
            if t >= 1:
                # baseline: the story's own bigram cache over its word cache
                uni = collections.Counter(prev)
                p1 = (uni[tok] + BETA * p_uni(tok)) / (len(prev) + BETA)
                nxt = collections.Counter(prev[i + 1] for i in range(len(prev) - 1) if prev[i] == prev[-1])
                pb = (nxt[tok] + BETA * p1) / (sum(nxt.values()) + BETA)
                d = g.dist(p_uni) if ops else {"__rest__": 1.0}
                pg = d.get(tok, d["__rest__"] * p_uni(tok))
                rows.append((pb, pg))
                story_of_row.append(si)
            g.add(tok, END)
            prev.append(tok)
    half = len(stories) // 2  # whole stories: the weight is fitted on the first half of the stories, scored on the rest
    fitr = [r for r, si in zip(rows, story_of_row) if si < half]
    evr = [r for r, si in zip(rows, story_of_row) if si >= half]
    lam = 0.5
    for _ in range(30):
        r = [lam * pg / (lam * pg + (1 - lam) * pb) for pb, pg in fitr]
        lam = sum(r) / len(r)
    with_ = -sum(math.log2(lam * pg + (1 - lam) * pb) for pb, pg in evr) / len(evr)
    alone = -sum(math.log2(pb) for pb, _ in evr) / len(evr)
    return with_, alone, lam


def select(train_stories, held_stories, cls, END, p_uni, max_passes, log=print, frozen=False):
    """Greedy pass-by-pass selection of (q, k) by held-out gain."""
    ops, lifts, best_bits = [], [], None
    for p in range(1, max_passes + 1):
        qtypes = list(ORIGINAL) + [f"p{j}" for j in range(1, p)]
        ktypes = list(ORIGINAL) + ([] if frozen else [f"p{j}b" for j in range(1, p)])
        cands = []
        for q in qtypes:
            for k in ktypes:
                if q in ("ps", "ss") and k in ("ps", "ss"):
                    continue  # position against position alone addresses no content
                t0 = time.time()
                lift = count_lift(train_stories, ops, lifts, q, k, cls, END)
                b, base, lam = heldout_bits(held_stories, ops + [(q, k)], lifts + [lift], cls, END, p_uni, frozen)
                cands.append((b, q, k, lift, base, lam, time.time() - t0, len(lift)))
                log(f"    pass {p} candidate ({q}, {k}): held-out {b:.4f} (cache alone {base:.4f}, weight {lam:.2f}), {len(lift)} lifts, {time.time() - t0:.0f}s")
        b, q, k, lift, base, lam, _, _ = min(cands, key=lambda c: c[0])
        ref = best_bits if best_bits is not None else base
        if ref - b < 0.001:
            log(f"  pass {p}: no candidate gains 0.001 bits (best ({q}, {k}) {b:.4f} against {ref:.4f}); stop")
            break
        ops.append((q, k))
        lifts.append(lift)
        best_bits = b
        log(f"  pass {p}: kept ({q}, {k}), held-out {b:.4f} (gain {ref - b:.4f})")
    return ops, lifts
