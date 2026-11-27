"""Q-LM v3.1: entities, relations and bindings learned from the training
text; the program is still supplied (docs/qlm-v3-plan.md, revision 1).

The learner reads only train.txt. world.json is read only to score what
was learned, and to supply the program, written as surface frames.

Learning, three steps:
1. FRAMES. For every distinct sentence, every way of replacing 1 or 2 of
   its positions with a slot gives a candidate frame. A frame's support is
   the number of distinct sentences it matches. Each sentence is parsed by
   its highest-support frame, if that support is at least MIN_SUPPORT.
   Supplied prior: facts have at most 2 arguments.
2. ENTITIES. The slot fillers, kept as individual tokens. Nothing merges
   two entities.
3. RELATIONS. Two-slot frames are grouped when the sets of (first, second)
   pairs they bind overlap with Jaccard at least JACCARD: one relation,
   several wordings. Bindings: (subject, relation) -> {object: count}.

Execution: the v3.0 runtime over the learned bindings. The program names
its relations by one wording each ("{} lives in {} ."); a wording resolves
to the learned relation that contains it, or to nothing.

    python3 -I v3/learn.py WORLD_DIR [WORLD_DIR ...]
"""
import itertools, json, pickle, sys, time
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from runtime import STOP, Runtime

MIN_SUPPORT = 3
JACCARD = 0.5


def frames_of(toks):
    for k in (1, 2):
        for slots in itertools.combinations(range(len(toks)), k):
            yield tuple("_" if i in slots else t for i, t in enumerate(toks)), slots


def learn(sentences):
    t0 = time.time()
    distinct = sorted(set(tuple(s.split()) for s in sentences))
    support = defaultdict(int)
    for toks in distinct:
        for f, _ in frames_of(toks):
            support[f] += 1
    parse = {}
    for toks in distinct:
        f, slots = max(frames_of(toks), key=lambda x: (support[x[0]], len(x[1])))
        if support[f] >= MIN_SUPPORT:
            parse[toks] = (f, tuple(toks[i] for i in slots))
    entities = {e for _, args in parse.values() for e in args}
    pairs = defaultdict(set)
    for f, args in parse.values():
        if len(args) == 2:
            pairs[f].add(args)
    # Group wordings: union-find over frames whose pair sets overlap.
    group = {f: f for f in pairs}
    find = lambda f: f if group[f] == f else find(group[f])
    fs = sorted(pairs)
    jac = {}
    for a, b in itertools.combinations(fs, 2):
        j = len(pairs[a] & pairs[b]) / len(pairs[a] | pairs[b])
        jac[(a, b)] = j
        if j >= JACCARD:
            group[find(a)] = find(b)
    rel = {f: find(f) for f in fs}
    counts = defaultdict(lambda: defaultdict(float))
    for toks, (f, args) in parse.items():
        if len(args) == 2:
            counts[(args[0], rel[f])][args[1]] += sentences_count(sentences, toks)
    knowledge = {k: {o: c / sum(v.values()) for o, c in v.items()} for k, v in counts.items()}
    return {"frames": rel, "entities": entities, "knowledge": knowledge, "jaccard": jac,
            "unparsed": len(distinct) - len(parse), "distinct": len(distinct), "seconds": time.time() - t0}


_counts = {}


def sentences_count(sentences, toks):
    key = id(sentences)
    if key not in _counts:
        c = defaultdict(int)
        for s in sentences:
            c[tuple(s.split())] += 1
        _counts.clear()
        _counts[key] = c
    return _counts[key][toks]


def frame(template):
    return tuple("_" if t == "{}" else t for t in template.split())


def score(d):
    world = json.load(open(f"{d}/world.json"))
    sentences = open(f"{d}/train.txt").read().splitlines()
    vocab = [w for w in open(f"{d}/vocab.txt").read().split() if w != "END"]
    tests = [l.rstrip("\n").split("\t") for l in open(f"{d}/tests.tsv")]
    m = learn(sentences)
    out = [f"{d} ({world['task']}, {world['regime']}): {m['distinct']} distinct sentences, {m['unparsed']} unparsed; learned in {m['seconds']:.2f}s"]

    # Entities against the truth.
    truth_e = {e for v in world["types"].values() for e in v}
    if world["task"] == "B":
        truth_e = set(world["types"]["node"]) | set(world["kind"].values())
    tp = len(m["entities"] & truth_e)
    out.append(f"  entities: {len(m['entities'])} learned, precision {tp / len(m['entities']):.3f}, recall {tp / len(truth_e):.3f}; "
               f"entity merges 0 (identities are kept by construction)")

    # Relations: each learned group against the true relations of its wordings.
    true_rel = {frame(t): r for r, ts in world["phrasings"].items() for t in ts}
    groups = defaultdict(set)
    for f, g in m["frames"].items():
        groups[g].add(f)
    found, mixed, other = 0, 0, 0
    for g, fs in groups.items():
        rs = {true_rel.get(f) for f in fs}
        if None in rs:
            other += 1  # a frame that is not a one-hop relation (composed statements, under T2)
        elif len(rs) > 1:
            mixed += 1
        elif fs == {frame(t) for t in world["phrasings"][rs.pop()]}:
            found += 1
    multi = [r for r, ts in world["phrasings"].items() if len(ts) > 1]
    para = sum(len({m["frames"].get(frame(t)) for t in world["phrasings"][r]}) == 1 and frame(world["phrasings"][r][0]) in m["frames"] for r in multi)
    out.append(f"  relations: {len(groups)} learned; {found} of {len(world['phrasings'])} true relations recovered exactly; "
               f"{mixed} groups merge different relations; {other} other (e.g. composed); paraphrases grouped {para} of {len(multi)}")
    js = sorted(((j, a, b) for (a, b), j in m["jaccard"].items() if j > 0.05), reverse=True)
    if js:
        out.append("  overlaps above 0.05: " + "; ".join(f"{' '.join(a)} ~ {' '.join(b)} {j:.2f}" for j, a, b in js[:6]))

    # Bindings against the true facts.
    if world["task"] == "A":
        truth_b = {(s, r, o) for r, mm in world["relations"].items() for s, o in mm.items()}
    else:
        truth_b = {(v, "is", k) for v, k in world["kind"].items()} | {(v, r, o) for v, es in world["edges"].items() for r, o in es.items()}
    rep = {}  # learned relation -> the true relation of its wordings, when all agree
    for g, fs in groups.items():
        rs = {true_rel.get(f) for f in fs}
        rep[g] = rs.pop() if len(rs) == 1 else None
    learned_b = {(s, rep[g], o) for (s, g), objs in m["knowledge"].items() for o in objs if rep.get(g)}
    unmapped = sum(len(objs) for (s, g), objs in m["knowledge"].items() if not rep.get(g))
    # Composed facts are true facts too, but not one-hop ones: counted apart.
    comp_truth = set()
    if world["task"] == "A":
        r = world["relations"]
        comp_truth = {(p, r["continent"][r["located"][r["lives"][p]]]) for p in r["lives"]}
    else:
        def end(v):
            while world["kind"][v] not in world["terminal"]:
                v = world["edges"][v][world["rule"][world["kind"][v]]]
            return v
        comp_truth = {(v, end(v)) for v in world["kind"]}
    unmapped_true = sum(1 for (s, g), objs in m["knowledge"].items() if not rep.get(g) for o in objs if (s, o) in comp_truth)
    tp = len(learned_b & truth_b)
    allb = len(learned_b) + unmapped
    out.append(f"  bindings: {allb} learned in all; {len(learned_b)} in relations matching a one-hop relation, precision {tp / max(len(learned_b), 1):.3f}, "
               f"recall {tp / len(truth_b):.3f}; {unmapped} in relations matching none ({unmapped_true} of them true composed facts); "
               f"precision over all bindings, counting composed facts as correct, {(tp + unmapped_true) / max(allb, 1):.3f}")

    # Execution over the learned knowledge, program supplied as wordings.
    rt = Runtime(m["knowledge"])
    resolve = lambda t: m["frames"].get(frame(t))
    if world["task"] == "A":
        P = world["phrasings"]
        progs = {"lives on": ["lives", "located", "continent"], "was born in": ["born"],
                 "lives in hemisphere": ["lives", "located", "continent", "hemisphere"]}
        progs = {q: [resolve(P[r][0]) for r in rs] for q, rs in progs.items() if all(r in P for r in rs)}
        choose_for = lambda q: (lambda e, i, p=progs.get(q, []): p[i] if i < len(p) else STOP)
    else:
        is_rel = resolve("{} is {} .")
        rule = {k: resolve("{} " + r + " {} .") for k, r in world["rule"].items()}
        terminal = set(world["terminal"])

        def choose_b(e, i):
            kd = rt.k.get((e, is_rel))
            kind = max(kd, key=kd.get) if kd else None
            return STOP if kind is None or kind in terminal else rule.get(kind)
        choose_for = lambda q: choose_b
    worst, rows = 0.0, []
    for passes in (1, 2, 3, 4, 8):
        by = defaultdict(lambda: [0, 0])
        for task, kind, prompt, answer, depth in tests:
            w = prompt.split()
            start, q = (w[1], None) if task == "B" else (w[0], " ".join(w[1:]))
            state, _ = rt.run(start, choose_for(q), passes)
            p = Runtime.project(state, vocab)
            worst = max(worst, abs(sum(p.values()) - 1))
            by[f"{kind} d{depth}"][0] += max(p, key=p.get) == answer
            by[f"{kind} d{depth}"][1] += 1
        rows.append((passes, {k: v[0] / v[1] for k, v in sorted(by.items())}))
    out.append(f"  execution over learned knowledge ({len(rt.k)} entries, {len(pickle.dumps(m))} bytes serialised, whole learned model); gate worst |sum - 1| {worst:.1e}")
    out.append("    passes | " + " | ".join(rows[0][1]))
    for passes, acc in rows:
        out.append(f"    {passes:>6} | " + " | ".join(f"{acc[k]:.3f}" for k in acc))
    print("\n".join(out))


if __name__ == "__main__":
    for d in sys.argv[1:]:
        score(d)
