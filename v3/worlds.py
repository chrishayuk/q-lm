"""Q-LM v3 task worlds (docs/qlm-v3-plan.md, revision 1).

Task A, geography: P lives in K . / K is located in C . / C is in T .
(and, in the deep world, T lies in H .). Composed: P lives on T .
Distractor relation: P was born in K' (K' never P's home city).

Task B, state-dependent routing: nodes with a kind and four outgoing
relations; the relation to follow depends on the current node's kind; two
kinds stop the walk. Composed: from X the end is Z .

Writes, for each world, a directory in the format transformer/train.py
reads (train.txt, train-N.txt, dev.txt, vocab.txt), plus tests.tsv and
world.json. world.json is the truth: only the oracle runtime and the scorer
may read it.

    python3 -I v3/worlds.py OUT_DIR {A|A-deep|B} SEED {T1|T2}
"""
import json, os, random, sys

REPEAT = int(os.environ.get("REPEAT", 4))  # each one-hop fact, and each composed training answer, this many times


def names(n, rng, used):
    syl = [c + v for c in "bdfgklmnprstvz" for v in "aeiou"]
    out = []
    while len(out) < n:
        w = "".join(rng.choice(syl) for _ in range(3))
        if w not in used:
            used.add(w)
            out.append(w)
    return out


def task_a(rng, deep):
    used = set()
    H = names(2, rng, used) if deep else []
    T = names(4, rng, used)
    C = names(24, rng, used)
    K = names(24, rng, used)
    P = names(96, rng, used)
    rel = {"lives": {}, "located": {}, "continent": {}, "hemisphere": {}, "born": {}}
    for i, c in enumerate(C):
        rel["continent"][c] = T[i // 6]
    for i, k in enumerate(K):
        rel["located"][k] = C[i]
    for i, p in enumerate(P):
        rel["lives"][p] = K[i // 4]
        rel["born"][p] = K[(i // 4 + 1 + rng.randrange(23)) % 24]
    if deep:
        for i, t in enumerate(T):
            rel["hemisphere"][t] = H[i // 2]
    else:
        del rel["hemisphere"]
    # Held out: one quarter of the people, balanced by continent.
    held = set()
    for t in T:
        on = [p for p in P if rel["continent"][rel["located"][rel["lives"][p]]] == t]
        held.update(rng.sample(on, len(on) // 4))
    facts = [(r, s, o) for r in rel for s, o in rel[r].items()]

    def lives_on(p):
        return rel["continent"][rel["located"][rel["lives"][p]]]

    composed = {p: lives_on(p) for p in P if p not in held}
    comp_text = [f"{p} lives on {t} ." for p, t in composed.items()]
    tests = [("A", "compose", f"{p} lives on", lives_on(p), 3) for p in sorted(held)]
    tests += [("A", "distractor", f"{p} was born in", rel["born"][p], 1) for p in sorted(held)]
    if deep:
        tests += [("A", "depth", f"{p} lives in hemisphere", rel["hemisphere"][lives_on(p)], 4) for p in sorted(held)]
    world = {"task": "A", "deep": deep, "relations": rel, "held": sorted(held), "types": {"P": P, "K": K, "C": C, "T": T, "H": H},
             "phrasings": {r: PHRASE_A[r] for r in rel}}
    return facts, comp_text, tests, world


# Each fact, at each repetition, is written in one of its relation's phrasings.
PHRASE_A = {"lives": ["{} lives in {} .", "{} is from {} ."], "located": ["{} is located in {} .", "{} is a city of {} ."],
            "continent": ["{} is in {} ."], "hemisphere": ["{} lies in {} ."], "born": ["{} was born in {} ."]}
KINDS = ["red", "blue", "green", "yellow", "black", "white"]
RELS = ["points to", "faces", "holds", "calls"]


def task_b(rng):
    used = set()
    kinds, rels = KINDS[:], RELS[:]
    rng.shuffle(kinds); rng.shuffle(rels)  # the mapping differs for every world
    rule = dict(zip(kinds[:4], rels))  # the program: kind -> relation; the other two kinds stop
    terminal = kinds[4:]
    kind, edges, starts = {}, {}, []

    def path(length):
        nodes = names(length + 1, rng, used)
        for i, v in enumerate(nodes):
            kind[v] = rng.choice(terminal) if i == length else rng.choice(kinds[:4])
            edges[v] = {}
        for i in range(length):
            edges[nodes[i]][rule[kind[nodes[i]]]] = nodes[i + 1]
        return nodes

    paths = {L: [path(L) for _ in range(60 if L != 7 else 30)] for L in (2, 3, 5, 7)}
    allnodes = list(kind)
    for v in allnodes:  # distractors: every relation a node does not use points somewhere random
        for r in RELS:
            if r not in edges[v]:
                edges[v][r] = rng.choice(allnodes)
    held = set()
    for L in (2, 3, 5):
        held.update(p[0] for p in rng.sample(paths[L], 15))
    facts = [("is", v, kind[v]) for v in allnodes] + [(r, v, o) for v in allnodes for r, o in edges[v].items()]
    end = {p[0]: (p[-1], L) for L, ps in paths.items() for p in ps}
    comp_text = [f"from {s} the end is {e} ." for s, (e, L) in end.items() if s not in held and L != 7]
    tests = [("B", "compose", f"from {s} the end is", e, L) for s, (e, L) in sorted(end.items()) if s in held]
    tests += [("B", "depth", f"from {s} the end is", e, L) for s, (e, L) in sorted(end.items()) if L == 7]
    world = {"task": "B", "rule": rule, "terminal": terminal, "kind": kind, "edges": edges, "held": sorted(held),
             "types": {"node": allnodes, "kind": KINDS}, "phrasings": {r: ["{} " + r + " {} ."] for r in ["is"] + RELS}}
    return facts, comp_text, tests, world


def main():
    out, task, seed, regime = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    rng = random.Random(seed)
    facts, comp, tests, world = task_b(rng) if task == "B" else task_a(rng, task == "A-deep")
    world["regime"] = regime
    say = lambda f: rng.choice(world["phrasings"][f[0]]).format(f[1], f[2])
    text = [say(f) for f in facts for _ in range(REPEAT)] + (comp * REPEAT if regime == "T2" else [])
    rng.shuffle(text)
    dev = [say(f) for f in facts]
    rng.shuffle(dev)
    os.makedirs(out, exist_ok=True)
    for f in (f"{out}/train.txt", f"{out}/train-{len(text)}.txt"):
        open(f, "w").write("\n".join(text) + "\n")
    open(f"{out}/dev.txt", "w").write("\n".join(dev[:2000]) + "\n")
    vocab = sorted({w for s in text + dev for w in s.split()} | {t[3] for t in tests} | {w for t in tests for w in t[2].split()})
    open(f"{out}/vocab.txt", "w").write("\n".join(vocab + ["END"]) + "\n")
    open(f"{out}/tests.tsv", "w").write("".join("\t".join(map(str, t)) + "\n" for t in tests))
    json.dump(world, open(f"{out}/world.json", "w"))
    print(f"{out}: {len(text)} training sentences, {len(vocab)} words, {len(tests)} tests")


if __name__ == "__main__":
    main()
