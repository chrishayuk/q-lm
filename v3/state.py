"""QLM-STATE-001 (docs/qlm-state-001-plan.md): contextual computational states.

The working state is (entity, steps taken), with a weight. A relation on
the start whose value constrains the walk's length is learned:
- for each attribute relation, its values on the training starts are
  counted against the lengths of their computation-labelled walks;
- the relation whose values predict the length best is the constraint;
- each value means the length it was counted with most often.
A state may stop only at that length: mass that stops elsewhere, or walks
past it, is REJECTED, and the accepted answers are renormalised.

Arms A and E are SOFT-ROUTING-001's (hard; weighted over entities, merged
by entity). S: (entity, steps) states, merged by (entity, steps). S-beam:
S keeping the 8 heaviest states per pass. S-shuffled: S with each test
start given another test start's value (the structure without the
evidence).

    python3 -I v3/state.py WORLD_DIR [WORLD_DIR ...]
"""
import contextlib, io, math, sys, time
from collections import Counter, defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import latent
from runtime import STOP, Runtime
from softroute import CAP, FLOOR_W, execute

BEAM = 8


def execute_s(start, post, kq, length, beam=None, acct=None, dist=None, merge_steps=True):
    """length: a hard constraint (or None); dist: {length: probability}, a soft one
    (stopping mass at n steps is weighted by dist[n]). merge_steps False keys the
    state by entity alone and reads the step count from the global pass index
    (synchronous passes: every state at pass i has taken i steps)."""
    acct = acct if acct is not None else defaultdict(float)
    if dist is not None:
        length = None
    maxlen = max(dist) if dist else length
    states = {(start, 0): 1.0}
    answer = defaultdict(float)
    max_active, expansions = 1, 0
    for _ in range(CAP):
        new = defaultdict(float)
        for (e, n), w in states.items():
            expansions += 1
            for a, pa in post(e).items():
                wa = w * pa
                if a is STOP:
                    keep = dist.get(n, 0.0) if dist else (1.0 if length is None or n == length else 0.0)
                    answer[e] += wa * keep
                    acct["completed"] += wa * keep
                    acct["rejected"] += wa * (1 - keep)  # stopped at a wrong (or unlikely) length
                    continue
                if maxlen is not None and n + 1 > maxlen:
                    acct["rejected"] += wa  # walks past the length
                    continue
                nxt = kq.get((e, a))
                if not nxt:
                    acct["dead end"] += wa
                    continue
                for o, x in nxt.items():
                    new[(o, n + 1)] += wa * x  # merge_steps False: every key at this pass has the same n
        before = sum(new.values())
        new = {s: w for s, w in new.items() if w >= FLOOR_W}
        if beam and len(new) > beam:
            new = dict(sorted(new.items(), key=lambda x: -x[1])[:beam])
        acct["pruned"] += before - sum(new.values())
        states = new
        max_active = max(max_active, len(states))
        if not states:
            break
    acct["unfinished"] += sum(states.values())
    z = sum(answer.values())
    return ({e: w / z for e, w in answer.items()} if z else {}), max_active, expansions


def main(d):
    with contextlib.redirect_stdout(io.StringIO()):
        ctx = latent.main(d)
    world, m, q, kq, vocab = ctx["world"], ctx["m"], ctx["q"], ctx["kq"], ctx["vocab"]
    k = m["knowledge"]
    cache = {}

    def post(e):
        if e not in cache:
            cache[e] = ctx["nb_post"](e) if e in ctx["subjects"] else {STOP: 1.0}
        return cache[e]

    # Learn which attribute constrains the length, and what its values mean.
    best = None
    for r in ctx["attrs"]:
        co = defaultdict(Counter)
        for s, Ld in ctx["walk_len"].items():
            v = k.get((s, r))
            if v:
                for L, w in Ld.items():
                    co[max(v, key=v.get)][L] += w
        n = sum(sum(c.values()) for c in co.values())
        if n == 0:
            continue
        purity = sum(max(c.values()) for c in co.values()) / n
        coverage = n / len(ctx["walk_len"])
        if best is None or purity * coverage > best[0]:
            best = (purity * coverage, r, {v: max(c, key=c.get) for v, c in co.items()}, purity, coverage, co)
    _, rel, meaning, purity, coverage, co = best
    soft = {v: {L: w / sum(c.values()) for L, w in c.items()} for v, c in co.items()}  # P(length | word)
    truth = {"two": 2, "three": 3, "five": 5, "seven": 7}
    right = sum(meaning.get(w) == L for w, L in truth.items())
    name = " ".join(next(f for f, g in m["frames"].items() if g == rel))
    token_of = lambda s: max(k[(s, rel)], key=k[(s, rel)].get) if (s, rel) in k else None
    length_of = lambda s: meaning.get(token_of(s))
    dist_of = lambda s: soft.get(token_of(s))

    tests = [(kind, depth, *ctx["read_prompt"](prompt.split()), ans) for _, kind, prompt, ans, depth in ctx["tests"]]
    starts = [t[2] for t in tests]
    shuffled = dict(zip(starts, starts[7:] + starts[:7]))  # each start given another start's value
    print(f"{d} ({world['task']}, {world['regime']}): length constraint learned as '{name}' "
          f"(purity {purity:.3f}, coverage {coverage:.3f}); meanings " + ", ".join(f"{w}→{L}" for w, L in sorted(meaning.items()))
          + f"; {right} of 4 right; labels {latent.LABELS}")
    print("    P(length | word): " + "; ".join(f"{w}: " + ", ".join(f"{L} {p:.2f}" for L, p in sorted(d_.items()) if p >= 0.01) for w, d_ in sorted(soft.items())))
    print("        arm | 2 steps | 3 steps | 5 steps | 7 steps | bits for the true answer | max active | expansions/query | ms/query | mean mass by outcome")
    arms = {
        "A": lambda s, acct: execute(s, post, kq, "A", acct=acct),
        "E": lambda s, acct: execute(s, post, kq, "E", acct=acct),
        "S": lambda s, acct: execute_s(s, post, kq, length_of(s), acct=acct),
        "S-beam": lambda s, acct: execute_s(s, post, kq, length_of(s), BEAM, acct=acct),
        "S-shuffled": lambda s, acct: execute_s(s, post, kq, length_of(shuffled[s]), acct=acct),
        "S-global": lambda s, acct: execute_s(s, post, kq, length_of(s), acct=acct, merge_steps=False),
        "S-soft": lambda s, acct: execute_s(s, post, kq, None, acct=acct, dist=dist_of(s)),
        "S-oracle": lambda s, acct: execute_s(s, post, kq, world["lengths"][s], acct=acct),  # diagnostic: the true length
    }
    for arm, run in arms.items():
        by, b, mx, ex, acct, t0 = defaultdict(lambda: [0, 0]), 0.0, 0, 0, defaultdict(float), time.time()
        for kind, depth, start, g, ans in tests:
            ansd, act, exp = run(start, acct) if g == q else ({}, 0, 0)
            p = Runtime.project(ansd, vocab)
            assert abs(sum(p.values()) - 1) < 1e-6, "admission gate"
            by[depth][0] += max(p, key=p.get) == ans
            by[depth][1] += 1
            b += -math.log2(p[ans])
            mx, ex = max(mx, act), ex + exp
        n = len(tests)
        print(f"  {arm:>10} | " + " | ".join(f"{by[x][0] / by[x][1]:.3f}" for x in ("2", "3", "5", "7"))
              + f" | {b / n:.3f} | {mx} | {ex / n:.1f} | {(time.time() - t0) * 1000 / n:.2f} | "
              + ", ".join(f"{o} {acct[o] / n:.4f}" for o in ("completed", "rejected", "dead end", "pruned", "unfinished")))


if __name__ == "__main__":
    for d in sys.argv[1:]:
        main(d)
