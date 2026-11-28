"""QLM-KEY-001, arms C, D and E (prototype): composite keys, and keys learned
by utility. See docs/qlm-key-001-plan.md.

    python3 -I v2/composite.py data-ts 100000 --arm E

A key template pairs the recent word v = x_{t-1} with one other piece of
the history:
- ("w", d): the word d positions back (d = 2..8);
- ("c", d): that word's abstraction node (pass 1);
- ("cw", d): v's node (not v itself) paired with the word d back.

Each template gives a component P(w | v, key), with interpolated absolute
discounting back to the bigram P(w | v). Where the history is too short,
the component is the bigram.

Arms:
- C: every ("w", d) template;
- D: every ("c", d) template;
- E: the templates of any kind whose utility is positive. Utility is the
  held-out gain over the bigram, in bits per token, on the last 10% of the
  training sentences, counted on the first 90%; minus lam times (1/2)
  log2(N) per stored binding, over the N training tokens. lam = 0 keeps any
  template that generalises at all; the full description-length charge
  (lam = 1) charges the whole table against one pass over the data, which
  no table passes at these sizes.

The components join the v2 mixture (5-gram + 4 class models). Weights by EM
on development 1-1,000; reported on 1,001-3,000 by position, or on
3,001-7,000 with --split confirm.
"""
import argparse
import collections
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("n", type=int)
ap.add_argument("--arm", default="E")
ap.add_argument("--split", default="select", choices=["select", "confirm", "confirm2", "confirm3"])
ap.add_argument("--lam", type=float, default=1.0)
ap.add_argument("--buckets", action="store_true", help="mixture weights per position bucket")
ap.add_argument("--keys", default="", help="for arm R or V: comma-separated templates, e.g. w2,w3,c2")
ap.add_argument("--story", default="", help="QLM-TINYSTORIES-V3-001: comma-separated story-local components: cache, bicache, tricache, rcache95, rcache99")
a = ap.parse_args()
t0 = time.time()
core.setup(a.dir, a.n)
V, END, wid, dev = core.V, core.END, core.wid, core.dev
classes = []
for seed in range(1, 5):
    hard, C, _ = core.learn(np.arange(V), 256, seed)
    classes.append(core.ClassModel(hard, C))
node = classes[0].hard
START = -1
D_ = 0.75
templates = [(k, d) for k in ("w", "c", "cw") for d in range(2, 9)]


RANDOM = False  # arm R: the earlier item is at a random distance, not d


def key_of(tmpl, ids, t):
    """The key for predicting ids[t] (ids starts with the sentence's words);
    None if the history is too short."""
    k, d = tmpl
    if k == "j":  # joint: (v, x_{t-d1}, x_{t-d2})
        d1, d2 = d
        if t - max(d1, d2) < 0:
            return None
        return ("j", ids[t - 1], ids[t - d1], ids[t - d2])
    if RANDOM and t >= 2:
        # A pseudo-random distance in 2..t, fixed by the sentence and the
        # position: the same storage, no consistent addressing.
        h = (hash(tuple(ids[:t])) ^ (d * 0x9E3779B1)) & 0xFFFFFFFF
        d = 2 + h % (t - 1)
    if t - d < 0 or t - 1 < 0:
        return None
    v, x = ids[t - 1], ids[t - d]
    if k == "w":
        return (v, x)
    if k == "c":
        return (v, node[x])
    return ("cw", node[v], x)


class Successive:
    """Arm G: P(w | h) = P(c(w) | the last two classes) * P(w | c(w), x_{t-d}),
    backed off to P(w | c(w)). Nothing indexed by (x_{t-1}, x_{t-d}) is
    stored."""

    def __init__(self, d, cm):
        self.d, self.cm = d, cm
        self.c = collections.defaultdict(collections.Counter)  # (class, earlier word) -> w
        for s in core.enc:
            seq = s + [END]
            for t in range(len(seq)):
                if t - d < 0:
                    continue
                w = seq[t]
                cw = cm.END_C if w == END else cm.hard[w]
                self.c[(cw, seq[t - d])][w] += 1
        self.ct = {k: (sum(c.values()), len(c)) for k, c in self.c.items()}
        self.bindings = sum(len(c) for c in self.c.values())

    def probs(self, s):
        ids = [wid[x] for x in s]
        base = self.cm.probs(s)  # P(c(w) | h) * P(w | c(w))
        out = []
        for t in range(len(ids) + 1):
            w = END if t == len(ids) else ids[t]
            cw = self.cm.END_C if w == END else self.cm.hard[w]
            pwc = self.cm.Pw[cw, w]
            if t - self.d < 0 or (cw, ids[t - self.d]) not in self.ct or pwc == 0:
                out.append(base[t])
                continue
            tot, nd = self.ct[(cw, ids[t - self.d])]
            p_in = max(self.c[(cw, ids[t - self.d])][w] - D_, 0) / tot + D_ * nd / tot * pwc
            out.append(max(base[t] / pwc * p_in, 1e-12))  # P(c | h) * P(w | c, x)
        return out


class SuccessiveSoft:
    """Arm G-soft: P(w | h) = sum over w's classes c of P(c | h) P(w | c, x_{t-d}),
    with soft memberships (top 4) and fractional counts."""

    def __init__(self, d, cm, mem):
        self.d, self.cm, self.mem = d, cm, mem
        C = cm.C
        self.c = collections.defaultdict(collections.Counter)
        pw = np.zeros((C, V))
        for w, lst in mem.items():
            for c, x in lst:
                pw[c, w] = core.counts[w] * x
        self.pw = pw / (pw.sum(1, keepdims=True) + 1e-300)
        for s in core.enc:
            for t in range(len(s)):
                if t - d < 0:
                    continue
                for c, x in mem.get(s[t], []):
                    self.c[(c, s[t - d])][s[t]] += x
        # Fractional counts: the mass the discount removes from a key is
        # sum of min(count, D), not D per word, so the backoff gets exactly that.
        self.ct = {k: (sum(c.values()), sum(min(x, D_) for x in c.values())) for k, c in self.c.items()}
        self.bindings = sum(len(c) for c in self.c.values())

    def probs(self, s):
        ids = [wid[x] for x in s]
        cm = self.cm
        hist = [cm.START_C, cm.START_C]
        out = []
        for t in range(len(ids) + 1):
            if t == len(ids):
                out.append(max(cm.p_tri(cm.END_C, hist[-2], hist[-1]), 1e-12))
                break
            w = ids[t]
            if w not in self.mem:
                out.append(max(cm.p_tri(cm.UNK_C, hist[-2], hist[-1]) * cm.Pw[cm.UNK_C, w], 1e-12))
            else:
                p = 0.0
                for c, _ in self.mem[w]:
                    pc = cm.p_tri(c, hist[-2], hist[-1])
                    base = self.pw[c, w]
                    key = (c, ids[t - self.d]) if t - self.d >= 0 else None
                    if key in self.ct:
                        tot, removed = self.ct[key]
                        base = max(self.c[key][w] - D_, 0) / tot + removed / tot * base
                    p += pc * base
                out.append(max(p, 1e-12))
            hist.append(cm.hard[w])
        return out


class SuccessiveBind:
    """Arm G-bind: P(w | h) = P(c(w) | h) P(w | c(w), x*), x* the most recent
    earlier word (distance >= 2) whose class is entity-like."""

    def __init__(self, cm, entity):
        self.cm, self.entity = cm, entity
        self.c = collections.defaultdict(collections.Counter)
        for s in core.enc:
            seq = s + [END]
            for t in range(len(seq)):
                x = self.slot(seq, t)
                if x is None:
                    continue
                w = seq[t]
                cw = cm.END_C if w == END else cm.hard[w]
                self.c[(cw, x)][w] += 1
        self.ct = {k: (sum(c.values()), len(c)) for k, c in self.c.items()}
        self.bindings = sum(len(c) for c in self.c.values())

    def slot(self, seq, t):
        for i in range(t - 2, -1, -1):
            if self.cm.hard[seq[i]] in self.entity:
                return seq[i]
        return None

    def probs(self, s):
        ids = [wid[x] for x in s]
        seq = ids + [END]
        base = self.cm.probs(s)
        out = []
        for t in range(len(seq)):
            w = seq[t]
            cw = self.cm.END_C if w == END else self.cm.hard[w]
            pwc = self.cm.Pw[cw, w]
            x = self.slot(seq, t)
            if x is None or (cw, x) not in self.ct or pwc == 0:
                out.append(base[t])
                continue
            tot, nd = self.ct[(cw, x)]
            p_in = max(self.c[(cw, x)][w] - D_, 0) / tot + D_ * nd / tot * pwc
            out.append(max(base[t] / pwc * p_in, 1e-12))
        return out


def entity_classes(cm, k=16):
    """The k classes whose words, as the distant item of (class of v, word
    d back) keys, d = 2..8, give the most held-out gain per occurrence (last
    10% of the training sentences, counted on the first 90%)."""
    cut = int(0.9 * len(core.enc))
    fitS, holdS = core.enc[:cut], core.enc[cut:]
    base = Model(None, fitS)
    gain, cnt = collections.Counter(), collections.Counter()
    for d in range(2, 9):
        m = Model(("cw", d), fitS)
        for s in holdS:
            seq = s + [END]
            for t in range(d, len(seq)):
                x = seq[t - d]
                gain[cm.hard[x]] += math.log2(max(m.p(seq, t), 1e-12)) - math.log2(max(base.p(seq, t), 1e-12))
                cnt[cm.hard[x]] += 1
    score = {c: gain[c] / cnt[c] for c in cnt if cnt[c] >= 200}
    return set(sorted(score, key=lambda c: -score[c])[:k])


class Model:
    """P(w | v, key), backing off to the bigram P(w | v), both counted on `sents`."""

    def __init__(self, tmpl, sents):
        self.tmpl = tmpl
        self.c = collections.defaultdict(collections.Counter)
        self.bi = collections.defaultdict(collections.Counter)
        self.uni = collections.Counter()
        for s in sents:
            seq = s + [END]
            for t in range(len(seq)):
                v = seq[t - 1] if t > 0 else START
                self.bi[v][seq[t]] += 1
                self.uni[seq[t]] += 1
                key = key_of(tmpl, seq, t) if tmpl else None
                if key is not None:
                    self.c[key][seq[t]] += 1
        self.N = sum(self.uni.values())
        if tmpl and tmpl[0] == "j":
            self.c = collections.defaultdict(collections.Counter, {k: c for k, c in self.c.items() if sum(c.values()) >= 3})
        self.ct = {k: (sum(c.values()), len(c)) for k, c in self.c.items()}
        self.bt = {k: (sum(c.values()), len(c)) for k, c in self.bi.items()}
        self.bindings = sum(len(c) for c in self.c.values())

    def p_uni(self, w):
        return (self.uni[w] + 0.01) / (self.N + 0.01 * (V + 1))

    def p_bi(self, w, v):
        if v not in self.bt:
            return self.p_uni(w)
        tot, nd = self.bt[v]
        return max(self.bi[v][w] - D_, 0) / tot + D_ * nd / tot * self.p_uni(w)

    def p(self, ids, t):
        seq = ids
        w = seq[t]
        v = seq[t - 1] if t > 0 else START
        key = key_of(self.tmpl, seq, t) if self.tmpl else None
        if key is None or key not in self.ct:
            return self.p_bi(w, v)
        tot, nd = self.ct[key]
        return max(self.c[key][w] - D_, 0) / tot + D_ * nd / tot * self.p_bi(w, v)

    def probs(self, s):
        seq = [wid[x] for x in s] + [END]
        return [max(self.p(seq, t), 1e-12) for t in range(len(seq))]


class StoryCache:
    """QLM-TINYSTORIES-V3-001 arm B (order 1) and B2 (order 2): direct retrieval
    from the story prefix. The prefix is the earlier development sentences of
    the same story (recovered boundaries, tools/story_ids.py) and the earlier
    words of this sentence. Order 1: P(w) = (n(w) + BETA p_uni(w)) / (N + BETA).
    Order 2: P(w | v) from the prefix's own bigrams after v, backing off to
    order 1 in the same way."""
    story = True
    BETA = 1.0

    def __init__(self, order, base, decay=1.0):
        self.order, self.base, self.bindings, self.decay = order, base, 0, decay

    def context(self, i):
        sid = STORY[i]
        j, out = i - 1, []
        while j >= 0 and STORY[j] == sid:
            out = dev[j] + ["<eos>"] + out
            j -= 1
        return [wid.get(x, END) if x != "<eos>" else END for x in out]

    def probs_ctx(self, s, i):
        ctx = self.context(i)
        seq = [wid[x] for x in s] + [END]
        out = []
        for t in range(len(seq)):
            prev = ctx + seq[:t]
            if self.decay < 1.0:  # recency-weighted: an occurrence k tokens back counts decay^k
                L = len(prev)
                wt = collections.defaultdict(float)
                for k, x in enumerate(prev):
                    wt[x] += self.decay ** (L - 1 - k)
                n = sum(wt.values())
                p1 = (wt[seq[t]] + self.BETA * self.base.p_uni(seq[t])) / (n + self.BETA)
            else:
                uni = collections.Counter(prev)
                p1 = (uni[seq[t]] + self.BETA * self.base.p_uni(seq[t])) / (len(prev) + self.BETA)
            for o in range(2, self.order + 1):  # the prefix's own n-grams after the last o-1 words, backing off
                hist = tuple(prev[-(o - 1):]) if len(prev) >= o - 1 else None
                if hist is None:
                    break
                nxt = collections.Counter(prev[k + o - 1] for k in range(len(prev) - o + 1) if tuple(prev[k:k + o - 1]) == hist)
                m = sum(nxt.values())
                p1 = (nxt[seq[t]] + self.BETA * p1) / (m + self.BETA)
            out.append(max(p1, 1e-12))
        self.bindings = max(self.bindings, len(ctx) + len(seq))
        return out


class StoryDist:
    """Story components defined by a full next-word distribution at a position
    (dist), used both for scoring and for the admission gate."""
    story = True
    BETA = 1.0
    bindings = 0

    def context(self, i):
        return StoryCache.context(self, i)

    def probs_ctx(self, s, i):
        ctx = self.context(i)
        seq = [wid[x] for x in s] + [END]
        out = []
        for t in range(len(seq)):
            d = self.dist(ctx + seq[:t])
            out.append(max(d.get(seq[t], self.floor(seq[t], d)), 1e-12))
        return out

    def floor(self, w, d):
        return d["__rest__"] * self.base.p_uni(w)

    def gate_sum(self, pre, i):
        ctx = self.context(i)
        seq = [wid[x] for x in pre]
        d = self.dist(ctx + seq)
        return sum(d.get(w, self.floor(w, d)) for w in list(range(V)) + [END])

    def finish(self, e, rest):
        """e: explicit mass per word; rest: the weight on the training unigram.
        Returns full probabilities for the explicit words, and __rest__ for the others."""
        d = {w: x + rest * self.base.p_uni(w) for w, x in e.items()}
        d["__rest__"] = rest
        return d

    def backoff_parts(self, prev):
        """B3's order-2 cache over the word cache: p(w) = e[w] + rest * p_uni(w)."""
        uni = collections.Counter(prev)
        n = len(prev)
        e1 = {w: c / (n + self.BETA) for w, c in uni.items()}
        rest1 = self.BETA / (n + self.BETA)
        v = prev[-1] if prev else START
        nxt = collections.Counter(prev[k + 1] for k in range(len(prev) - 1) if prev[k] == v)
        m = sum(nxt.values())
        e2 = {w: (nxt.get(w, 0) + self.BETA * e1.get(w, 0.0)) / (m + self.BETA) for w in set(e1) | set(nxt)}
        return e2, self.BETA * rest1 / (m + self.BETA)

    def backoff(self, prev):
        return self.finish(*self.backoff_parts(prev))


class SpanCache(StoryDist):
    """Arm C: the longest learned span (2 to 4 words, seen often in training)
    ending the context is the key; what followed it in the story prefix is
    predicted, backing off to B3's order-2 cache."""

    def __init__(self, base, spans):
        self.base, self.spans = base, spans

    def dist(self, prev):
        e2, rest2 = self.backoff_parts(prev)
        for L in (4, 3, 2):
            if len(prev) >= L and tuple(prev[-L:]) in self.spans:
                key = tuple(prev[-L:])
                nxt = collections.Counter(prev[k + L] for k in range(len(prev) - L) if tuple(prev[k:k + L]) == key)
                m = sum(nxt.values())
                if m:
                    e3 = {w: (nxt.get(w, 0) + self.BETA * e2.get(w, 0.0)) / (m + self.BETA) for w in set(e2) | set(nxt)}
                    return self.finish(e3, self.BETA * rest2 / (m + self.BETA))
                break
        return self.finish(e2, rest2)


class Bind(StoryDist):
    """Arm D (learned) and D0 (uniform): read 1, a distribution over the prefix's
    other words a given the current word r; read 2, what followed each a in the
    prefix. D weights a by max(lift(r, a) - 1, 0) x occurrences of a; D0 by
    occurrences alone (the same reads, no learned binding)."""
    ALPHA = 5.0

    def __init__(self, base, learned, sents, story_ids):
        self.base, self.learned = base, learned
        self.lift = {}
        if learned:
            hits, trials = collections.Counter(), collections.Counter()
            stories = []
            for sent, sid in zip(sents, story_ids):
                if stories and stories[-1][0] == sid:
                    stories[-1][1].extend(sent + [END])
                else:
                    stories.append([sid, sent + [END]])
            for _, toks in stories:
                foll = collections.defaultdict(set)
                for t in range(1, len(toks)):
                    r, y = toks[t - 1], toks[t]
                    for x, nx in foll.items():
                        if x != r:
                            trials[(r, x)] += 1
                            if y in nx:
                                hits[(r, x)] += 1
                    if t >= 2:
                        foll[toks[t - 2]].add(toks[t - 1])
            h0 = sum(hits.values()) / max(sum(trials.values()), 1)
            self.lift = {k: ((hits[k] + self.ALPHA * h0) / (n + self.ALPHA)) / h0 for k, n in trials.items()
                         if (hits[k] + self.ALPHA * h0) / (n + self.ALPHA) > h0}
            self.all_pairs = list(trials)  # every pair that co-occurred, for the random-pairs control
            self.bindings = len(self.lift)

    def dist(self, prev):
        if len(prev) < 2:
            return {"__rest__": 1.0}
        r = prev[-1]
        foll = collections.defaultdict(collections.Counter)
        occ = collections.Counter(prev[:-1])
        for k in range(len(prev) - 1):
            foll[prev[k]][prev[k + 1]] += 1
        wts = {}
        for x in foll:
            if x == r:
                continue
            wts[x] = (self.lift.get((r, x), 1.0) - 1.0) * occ[x] if self.learned else occ[x]
        wts = {x: v for x, v in wts.items() if v > 0}
        W = sum(wts.values())
        if not W:
            return {"__rest__": 1.0}
        d = collections.defaultdict(float)
        rest = 0.0
        for x, v in wts.items():
            m = sum(foll[x].values())
            for y, c in foll[x].items():
                d[y] += v / W * c / (m + self.BETA)
            rest += v / W * self.BETA / (m + self.BETA)
        d = dict(d)
        for y in d:
            d[y] += rest * self.base.p_uni(y)
        d["__rest__"] = rest
        return d


STORY = [int(x) for x in open(f"{a.dir}/dev.txt.story")] if a.story else []
STORY_TRAIN = [int(x) for x in open(f"{a.dir}/train.txt.story")][: a.n] if a.story else []
enc = core.enc
if a.arm == "A":  # v2 alone (5-gram + 4 class models)
    chosen, util = [], {}
elif a.arm in ("G", "GS", "GB"):
    chosen, util = [], {}
elif a.arm == "J":
    chosen, util = [("j", p) for p in [(2, 3), (2, 4), (3, 4), (2, 5), (3, 6)]], {}
elif a.arm in ("R", "V"):
    chosen = [("cw" if x.startswith("cw") else x[0], int("".join(ch for ch in x if ch.isdigit()))) for x in a.keys.split(",")]
    RANDOM = a.arm == "R"
    util = {}
elif a.arm == "C":
    chosen = [t for t in templates if t[0] == "w"]
    util = {}
elif a.arm == "D":
    chosen = [t for t in templates if t[0] == "c"]
    util = {}
else:
    cut = int(0.9 * len(enc))
    fitS, holdS = enc[:cut], enc[cut:]
    base = Model(None, fitS)
    hold_tokens = sum(len(s) + 1 for s in holdS)
    base_ll = sum(math.log2(max(base.p(s + [END], t), 1e-12)) for s in holdS for t in range(len(s) + 1))
    Ntok = sum(len(s) + 1 for s in enc)
    util = {}
    for tm in templates:
        m = Model(tm, fitS)
        ll = sum(math.log2(max(m.p(s + [END], t), 1e-12)) for s in holdS for t in range(len(s) + 1))
        gain = (ll - base_ll) / hold_tokens
        cost = a.lam * m.bindings * 0.5 * math.log2(Ntok) / Ntok
        util[tm] = (gain, cost, gain - cost)
    chosen = [tm for tm in templates if util[tm][2] > 0]
t_learn = time.time()
models = [Model(tm, enc) for tm in chosen]
if a.arm == "G":
    models = [Successive(d, classes[0]) for d in range(2, 9)]
elif a.arm == "GS":
    _, C0, E0 = core.learn(np.arange(V), 256, 1)
    mem = core.memberships(E0, classes[0].hard, classes[0].C, 4)
    models = [SuccessiveSoft(d, classes[0], mem) for d in range(2, 9)]
elif a.arm == "GB":
    ent = entity_classes(classes[0])
    models = [SuccessiveBind(classes[0], ent)]
if a.story:
    _base = Model(None, enc)
    kinds = {"cache": (1, 1.0), "bicache": (2, 1.0), "tricache": (3, 1.0), "rcache95": (1, 0.95), "rcache99": (1, 0.99)}
    for x in a.story.split(","):
        if x in kinds:
            models.append(StoryCache(kinds[x][0], _base, kinds[x][1]))
        elif x == "spans":
            grams = collections.Counter(tuple(sn[k:k + L]) for sn in enc for L in (2, 3, 4) for k in range(len(sn) - L + 1))
            th = max(5, a.n // 20000)
            m = SpanCache(_base, {g_ for g_, c in grams.items() if c >= th})
            m.bindings = len(m.spans)
            models.append(m)
        elif x in ("bind", "bind0", "bindshuf", "bindrand"):
            bm = Bind(_base, x != "bind0", enc, STORY_TRAIN)
            if x == "bindshuf":  # matched capacity: D's table, its lift values reassigned at random among its keys
                import random as _r
                keys, vals = list(bm.lift), list(bm.lift.values())
                _r.Random(7).shuffle(vals)
                bm.lift = dict(zip(keys, vals))
            if x == "bindrand":  # matched capacity, unlearned selection: as many pairs, drawn from all co-occurring pairs
                import random as _r
                vals = list(bm.lift.values())
                bm.lift = dict(zip(_r.Random(int(os.environ.get("RAND_SEED", 7))).sample(bm.all_pairs, len(vals)), vals))
            models.append(bm)
learn_secs = time.time() - t_learn
t1 = time.time()

# Admission gate: every added component's next-token distribution must sum
# to 1 over the whole vocabulary and END, on prefixes that include unknown
# words and every length from empty to long. A run that fails is refused.
def gate(models, n_prefixes=12):
    rng = __import__("random").Random(5)
    unseen = [w for w in core.vocab if not core.seen[wid[w]]]
    prefixes = [[]] + [dev[i][: rng.randrange(1, len(dev[i]) + 1)] for i in rng.sample(range(3000, 7000), n_prefixes)]
    if unseen:
        prefixes.append(dev[0][:3] + [unseen[0]])
    worst = 0.0
    story_is = rng.sample([i for i in range(3000, 7000) if i > 0 and STORY[i] == STORY[i - 1]], n_prefixes) if a.story else []
    for m in models:
        if getattr(m, "story", False):  # with a real story prefix
            for i in story_is:
                pre = dev[i][: rng.randrange(0, len(dev[i]) + 1)]
                if isinstance(m, StoryDist):
                    tot = m.gate_sum(pre, i)
                else:
                    tot = sum(m.probs_ctx(pre + [w], i)[len(pre)] for w in core.vocab) + m.probs_ctx(pre, i)[len(pre)]
                worst = max(worst, abs(tot - 1))
            continue
        for pre in prefixes:
            tot = sum(m.probs(pre + [w])[len(pre)] for w in core.vocab) + m.probs(pre)[len(pre)]
            worst = max(worst, abs(tot - 1))
    if worst > 1e-6:
        raise SystemExit(f"admission gate: a component's next-token probabilities are off by {worst:.2e}; refused")
    return worst, len(prefixes)


# Every added component and every baseline class model. The 5-gram's
# probabilities come precomputed for the observed tokens only (qlm knprobs),
# so its normalisation is not yet gated here.
gate_worst, gate_n = gate(list(models) + list(classes)) if os.environ.get("NO_GATE") != "1" else (float("nan"), 0)
kn = [[float(x) for x in l.split()] for l in open(f"{a.dir}/v2/kn5-{a.n}.txt")]
fit = range(0, 1000)
evalr = {"select": range(1000, 3000), "confirm": range(3000, 7000), "confirm2": range(7000, 11000),
         "confirm3": range(11000, len(dev))}[a.split]  # confirm3: data-ts-c3 only (validation stories 1000-1999)
cls = {i: [m.probs(dev[i]) for m in classes] for i in list(fit) + list(evalr)}
t_inf = time.time()
extra = {i: [m.probs_ctx(dev[i], i) if getattr(m, "story", False) else m.probs(dev[i]) for m in models] for i in list(fit) + list(evalr)}
inf_tokens = sum(len(dev[i]) + 1 for i in list(fit) + list(evalr))
ms_per_token = 1000 * (time.time() - t_inf) / inf_tokens
comps = {i: [kn[i]] + cls[i] + extra[i] for i in list(fit) + list(evalr)}
J = len(comps[0])
bucket = (lambda t: min(t, 6)) if a.buckets else (lambda t: 0)
NB = 7
W = np.full((NB, J), 1.0 / J)
for _ in range(40):
    acc = np.zeros((NB, J)) + 1e-9
    for i in fit:
        for t in range(len(comps[i][0])):
            b = bucket(t)
            pv = np.array([c[t] for c in comps[i]]) * W[b]
            acc[b] += pv / pv.sum()
    W = acc / acc.sum(1, keepdims=True)
w = W[0]
B = {}
for i in evalr:
    for t in range(len(comps[i][0])):
        b = -math.log2(sum(W[bucket(t)][j] * comps[i][j][t] for j in range(J)))
        for kk in ("0-1" if t < 2 else "2-4" if t <= 4 else "5+", "all"):
            e = B.setdefault(kk, [0, 0])
            e[0] += b
            e[1] += 1
res = " ".join(f"{k} {B[k][0] / B[k][1]:.4f}" for k in ("all", "0-1", "2-4", "5+"))
kept = ", ".join(f"{k}{d}" for k, d in chosen) or {"G": "successive g2-g8 (hard)", "GS": "successive g2-g8 (soft, top 4)", "GB": "successive, entity slot"}.get(a.arm, "none")
print(f"n={a.n} arm={a.arm}{' buckets' if a.buckets else ''}{' story=' + a.story if a.story else ''} split={a.split} | {res} | keys: {kept} | stored bindings {sum(m.bindings for m in models)} ({sum(m.bindings for m in models) * 12 / 1e6:.0f} MB at 12 bytes each) | learn {learn_secs:.0f}s | {ms_per_token:.3f} ms/token for the added components | gate: worst |sum - 1| {gate_worst:.1e} over {gate_n} prefixes | {time.time() - t0:.0f}s")
if util:
    for tm in templates:
        g, c, u = util[tm]
        print(f"    {tm[0]}{tm[1]}: held-out gain {g:+.4f}, cost {c:.4f}, utility {u:+.4f}")
