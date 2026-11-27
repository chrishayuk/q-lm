"""Q-LM v3.3 and v3.4: a state-dependent routing policy and its stopping
condition, learned from composed examples (docs/qlm-v3-plan.md, revision 1).

From train.txt only (v3.1 learns the knowledge):
- A CONDITION is a learned relation with at most MAX_VALUES distinct
  objects: the value it gives for the current entity is what the policy
  looks at. (Supplied prior: conditions have few values.)
- A POLICY maps each value of the condition to an action: follow one of the
  learned relations, or STOP.
- It is run on the working state until every entity in it has stopped, or
  CAP passes.

For each learned relation Q with composed pairs (s, o) and no fixed program
(v3.2), every condition and every table is tried. The best is the one right
on most of Q's fitting pairs, then with the fewest STOP values. A tenth of
the subjects are kept back; the policy is accepted if right on at least
ACCEPT of them.

Controls:
- the best fixed program (v3.2), which cannot depend on the state;
- the learned routing run for a fixed number of passes (the best k on the
  training pairs), with no stop decision: terminal values follow the
  relation most used by the policy.

world.json is read only to score, and to compare the learned table with
the world's rule.

    python3 -I v3/policy.py WORLD_DIR [WORLD_DIR ...]
"""
import itertools, json, sys, time
from collections import Counter, defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from runtime import STOP, Runtime
from learn import learn
from program import ACCEPT, wording

MAX_VALUES = 8
CAP = 32


def walk(k, start, cond, table, passes):
    """Run the policy from start; returns the final state (one entity here, as knowledge is one-hot)."""
    def choose(e, i):
        v = k.get((e, cond))
        return table.get(max(v, key=v.get)) if v else STOP
    return Runtime(k).run(start, choose, passes)[0]


def fast_walk(k, start, cond, table, cap):
    """The same walk on the most likely entity only, for the search."""
    e = start
    for _ in range(cap):
        v = k.get((e, cond))
        a = table.get(max(v, key=v.get)) if v else STOP
        if a is STOP:
            return e
        nxt = k.get((e, a))
        if not nxt:
            return e
        e = max(nxt, key=nxt.get)
    return e


def main(d):
    world = json.load(open(f"{d}/world.json"))
    sentences = open(f"{d}/train.txt").read().splitlines()
    vocab = [w for w in open(f"{d}/vocab.txt").read().split() if w != "END"]
    tests = [l.rstrip("\n").split("\t") for l in open(f"{d}/tests.tsv")]
    t0 = time.time()
    m = learn(sentences)
    k = m["knowledge"]
    rels = sorted(set(m["frames"].values()))
    pairs = defaultdict(list)
    for (s, g), objs in k.items():
        pairs[g].append((s, max(objs, key=objs.get)))
    values = {g: {o for (s, h), objs in k.items() if h == g for o in objs} for g in rels}
    conds = [g for g in rels if len(values[g]) <= MAX_VALUES]
    out = [f"{d} ({world['task']}, {world['regime']}): conditions (relations with at most {MAX_VALUES} values): "
           + ", ".join(wording(m, g) for g in conds)]
    # Candidate targets: relations whose subjects are not their objects' subjects... all relations are tried,
    # and the composed one is the one a policy explains.
    policies = {}
    for q in rels:
        if q in conds or not pairs[q]:
            continue
        subjects = sorted({s for s, _ in pairs[q]})
        sel = set(subjects[::10])
        fit = [(s, o) for s, o in pairs[q] if s not in sel]
        chk = [(s, o) for s, o in pairs[q] if s in sel]
        # Knowledge without Q itself: the policy may not read the answers it is explaining.
        kq = {key: v for key, v in k.items() if key[1] != q}
        actions = [r for r in rels if r != q and r not in conds] + [STOP]
        best, tried = (None, None, -1, 99), 0
        for cond in conds:
            vals = sorted(values[cond])
            for acts in itertools.product(actions, repeat=len(vals)):
                tried += 1
                table = dict(zip(vals, acts))
                hit = sum(fast_walk(kq, s, cond, table, CAP) == o for s, o in fit)
                stops = acts.count(STOP)
                if hit > best[2] or (hit == best[2] and stops < best[3]):
                    best = (cond, table, hit, stops)
        cond, table, hit, _ = best
        sel_acc = sum(fast_walk(kq, s, cond, table, CAP) == o for s, o in chk) / max(len(chk), 1)
        ok = sel_acc >= ACCEPT
        shown = ", ".join(f"{v}→{'STOP' if a is STOP else wording(m, a).split(' / ')[0]}" for v, a in sorted(table.items()))
        out.append(f"  {wording(m, q)}: {'POLICY' if ok else 'no policy'}; condition {wording(m, cond)}; table {shown}; "
                   f"fit {hit / len(fit):.3f}, held-back tenth {sel_acc:.3f}; {tried} tables")
        if ok:
            policies[q] = (cond, table, kq)
            if world["task"] == "B":
                truth = {kd: STOP for kd in world["terminal"]} | world["rule"]
                learned = {v: (STOP if a is STOP else wording(m, a).split(" / ")[0].split(" ", 1)[1].rsplit(" ", 2)[0]) for v, a in table.items()}
                agree = sum(learned.get(v) == truth[v] for v in truth)
                out.append(f"    against the world's rule: {agree} of {len(truth)} values agree")
    out.insert(1, f"  learned in {time.time() - t0:.1f}s")

    # Tests: prompts read through the learned frames, as in v3.2.
    two = [(f, g) for f, g in m["frames"].items() if f[-2:] == ("_", ".") and f.count("_") == 2]

    def read_prompt(words):
        for f, g in two:
            body = f[:-2]
            if len(body) == len(words) and all(a == b or a == "_" for a, b in zip(body, words)):
                return words[body.index("_")], g
        return None, None

    def answer(prompt, passes, stop=True):
        start, g = read_prompt(prompt.split())
        if g not in policies:
            return {}
        cond, table, kq = policies[g]
        if not stop:  # control: no stop decision; stopping values follow the policy's most used relation
            common = Counter(a for a in table.values() if a is not STOP).most_common(1)[0][0]
            table = {v: (common if a is STOP else a) for v, a in table.items()}
        return walk(kq, start, cond, table, passes)

    for stop in (True, False):
        worst, rows = 0.0, []
        for passes in (1, 2, 3, 4, 8, CAP):
            by = defaultdict(lambda: [0, 0])
            for task, kind, prompt, ans, depth in tests:
                p = Runtime.project(answer(prompt, passes, stop), vocab)
                worst = max(worst, abs(sum(p.values()) - 1))
                by[f"{kind} d{depth}"][0] += max(p, key=p.get) == ans
                by[f"{kind} d{depth}"][1] += 1
            rows.append((passes, {kk: v[0] / v[1] for kk, v in sorted(by.items())}))
        out.append(f"  held-out tests, {'learned stop' if stop else 'CONTROL: no stop, fixed passes'} (gate worst |sum - 1| {worst:.1e})")
        out.append("    passes | " + " | ".join(rows[0][1]))
        for passes, acc in rows:
            out.append(f"    {passes:>6} | " + " | ".join(f"{acc[kk]:.3f}" for kk in acc))
    print("\n".join(out))


if __name__ == "__main__":
    for d in sys.argv[1:]:
        main(d)
