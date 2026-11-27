"""Q-LM v3.0: the execution runtime, qualified with supplied knowledge and
programs (the oracle stage; docs/qlm-v3-plan.md, revision 1).

Persistent knowledge: (entity, relation) -> {object: weight}.
Working state: {entity: weight}, a distribution over individual entities.
One pass: ADDRESS (entity, relation) for each entity in the state, READ its
objects, TRANSFORM (weight times object weight), WRITE the new state.
- A static program supplies the relation for pass i.
- A dynamic policy chooses the relation from each entity in the state, or
  STOP; stopped mass stays where it is.
Projection: the final state, mixed with a uniform floor, as a next-token
distribution over the vocabulary and END.

Nothing here is learned. Learned stages replace the knowledge, the
program and the policy one at a time.

    python3 -I v3/runtime.py WORLD_DIR [WORLD_DIR ...]
"""
import json, pickle, sys, time
from collections import defaultdict

STOP = None
FLOOR = 1e-4  # uniform mass in the projection, so every token has probability


class Runtime:
    def __init__(self, knowledge):
        self.k = knowledge  # (entity, relation) -> {object: weight}, weights summing to 1

    def run(self, start, choose, passes):
        """choose(entity, i) -> relation or STOP. Returns the state and the trace."""
        state, trace = {start: 1.0}, []
        for i in range(passes):
            new = defaultdict(float)
            ops = []
            for e, w in state.items():
                r = choose(e, i)
                objs = self.k.get((e, r)) if r is not STOP else None
                if not objs:  # stopped, or nothing to read: the mass stays
                    new[e] += w
                    continue
                ops.append((e, r))
                for o, x in objs.items():
                    new[o] += w * x
            trace.append(ops)
            state = dict(new)
            if not ops:
                break
        return state, trace

    @staticmethod
    def project(state, vocab):
        """Next-token distribution over vocab + END."""
        n = len(vocab) + 1
        p = {w: FLOOR / n for w in vocab}
        p["END"] = FLOOR / n
        for e, w in state.items():
            p[e] += (1 - FLOOR) * w
        missing = 1 - sum(state.values())  # nothing executed, or mass lost: spread it, so the result still sums to 1
        for w in p:
            p[w] += (1 - FLOOR) * missing / n
        return p


def oracle(world):
    k = {}
    if world["task"] == "A":
        for r, m in world["relations"].items():
            for s, o in m.items():
                k[(s, r)] = {o: 1.0}
    else:
        for v, es in world["edges"].items():
            for r, o in es.items():
                k[(v, r)] = {o: 1.0}
    return k


def chooser(world, query, stop=True):
    if world["task"] == "A":
        prog = {"lives on": ["lives", "located", "continent"], "was born in": ["born"],
                "lives in hemisphere": ["lives", "located", "continent", "hemisphere"]}[query]
        return lambda e, i: prog[i] if i < len(prog) else STOP
    rule, terminal, kind = world["rule"], set(world["terminal"]), world["kind"]
    if not stop:  # control: no stop decision; terminal nodes follow their first relation
        return lambda e, i: rule.get(kind[e], "points to")
    return lambda e, i: STOP if kind[e] in terminal else rule[kind[e]]


def qualify(d, stop=True):
    world = json.load(open(f"{d}/world.json"))
    vocab = [w for w in open(f"{d}/vocab.txt").read().split() if w != "END"]
    tests = [l.rstrip("\n").split("\t") for l in open(f"{d}/tests.tsv")]
    rt = Runtime(oracle(world))
    t0 = time.time()
    worst = 0.0
    rows = []
    for passes in (1, 2, 3, 4, 8):
        by = defaultdict(lambda: [0, 0])
        for task, kind, prompt, answer, depth in tests:
            words = prompt.split()
            start, query = (words[1], None) if task == "B" else (words[0], " ".join(words[1:]))
            state, _ = rt.run(start, chooser(world, query, stop), passes)
            p = Runtime.project(state, vocab)
            worst = max(worst, abs(sum(p.values()) - 1))
            hit = max(p, key=p.get) == answer
            key = f"{kind} d{depth}"
            by[key][0] += hit
            by[key][1] += 1
        rows.append((passes, {k: v[0] / v[1] for k, v in sorted(by.items())}, {k: v[1] for k, v in by.items()}))
    ms = (time.time() - t0) * 1000 / (5 * len(tests))
    size = len(pickle.dumps(rt.k))
    print(f"{d} ({world['task']}, {world['regime']}{'' if stop else ', NO STOP'}): knowledge {len(rt.k)} entries, {size} bytes serialised; "
          f"{ms:.3f} ms per query with projection; gate worst |sum - 1| {worst:.1e}")
    keys = list(rows[0][1])
    print("  passes | " + " | ".join(f"{k} (n={rows[0][2][k]})" for k in keys))
    for passes, acc, _ in rows:
        print(f"  {passes:>6} | " + " | ".join(f"{acc[k]:.3f}" for k in keys))
    return world, rt, vocab


def ambiguity(d):
    """One held-out person's home split 0.5/0.5 between two cities on different continents."""
    world = json.load(open(f"{d}/world.json"))
    rel = world["relations"]
    p = world["held"][0]
    t_of = lambda k: rel["continent"][rel["located"][k]]
    home = rel["lives"][p]
    other = next(k for k in world["types"]["K"] if t_of(k) != t_of(home))
    k = oracle(world)
    k[(p, "lives")] = {home: 0.5, other: 0.5}
    state, _ = Runtime(k).run(p, chooser(world, "lives on"), 3)
    print(f"  ambiguity: {p} lives in {home} or {other} (0.5 each) -> "
          + ", ".join(f"{e} {w:.3f}" for e, w in sorted(state.items(), key=lambda x: -x[1]))
          + f" (expected {t_of(home)} 0.5, {t_of(other)} 0.5)")


if __name__ == "__main__":
    for d in sys.argv[1:]:
        world, _, _ = qualify(d)
        if world["task"] == "A":
            ambiguity(d)
        else:
            qualify(d, stop=False)
