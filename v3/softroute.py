"""QLM-SOFT-ROUTING-001 (docs/qlm-soft-routing-001-plan.md): execute over the
posterior over actions instead of its most probable action.

The knowledge, the posterior over actions (naive Bayes from computation
labels) and the composed relation come from v3/latent.py, unchanged.

    python3 -I v3/softroute.py WORLD_DIR [WORLD_DIR ...]
"""
import contextlib, io, math, sys, time
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import latent
from runtime import STOP, Runtime

CAP = 32
FLOOR_W = 1e-12  # numerical floor on a state's weight, for every arm
BEAM = 8


def execute(start, post, kq, mode, T=1.0, prune=0.0, acct=None):
    """Returns (answer distribution, max active states, state expansions).
    The answer holds completed (stopped) mass only. acct, if given, receives the
    mass by outcome: completed, dead end (a read found nothing), pruned (floor,
    threshold or beam) and unfinished (still active at the cap)."""
    acct = acct if acct is not None else defaultdict(float)
    merge = mode != "B"
    states = {start: 1.0} if merge else [(start, 1.0)]
    answer = defaultdict(float)
    max_active, expansions = 1, 0
    for _ in range(CAP):
        new = defaultdict(float) if merge else []
        items = states.items() if merge else states
        for e, w in items:
            expansions += 1
            pi = post(e)
            if mode == "A":
                a = max(pi, key=pi.get)
                pi = {a: 1.0}
            else:
                if T != 1.0:
                    pi = {a: p ** (1 / T) for a, p in pi.items()}
                if mode == "C":
                    pi = dict(sorted(pi.items(), key=lambda x: -x[1])[:2])
                z = sum(pi.values())
                pi = {a: p / z for a, p in pi.items()}
            for a, pa in pi.items():
                wa = w * pa
                if a is STOP:
                    answer[e] += wa
                    acct["completed"] += wa
                    continue
                nxt = kq.get((e, a))
                if not nxt:
                    acct["dead end"] += wa  # nothing to read: not an answer
                    continue
                for o, x in nxt.items():
                    if merge:
                        new[o] += wa * x
                    else:
                        new.append((o, wa * x))
        floor = max(FLOOR_W, prune)
        before = sum(new.values()) if merge else sum(w for _, w in new)
        if merge:
            new = {e: w for e, w in new.items() if w >= floor}
            if mode == "D" and len(new) > BEAM:
                new = dict(sorted(new.items(), key=lambda x: -x[1])[:BEAM])
            states = new
        else:
            states = [(e, w) for e, w in new if w >= floor]
        acct["pruned"] += before - (sum(states.values()) if merge else sum(w for _, w in states))
        n = len(states)
        max_active = max(max_active, n)
        if not n:
            break
        if n > 2_000_000:
            raise RuntimeError("state explosion")
    acct["unfinished"] += sum(states.values()) if merge else sum(w for _, w in states)  # not an answer
    return dict(answer), max_active, expansions


def main(d):
    with contextlib.redirect_stdout(io.StringIO()):
        ctx = latent.main(d)
    world, q, kq, vocab = ctx["world"], ctx["q"], ctx["kq"], ctx["vocab"]
    cache = {}

    def post(e):
        if e not in cache:
            cache[e] = ctx["nb_post"](e) if e in ctx["subjects"] else {STOP: 1.0}
        return cache[e]

    def bits(ans, a):
        p = Runtime.project(ans, vocab)
        return -math.log2(p[a])

    # F: temperature and pruning threshold chosen on the training composed pairs.
    best = None
    for T in (1.0, 2.0, 4.0, 8.0):
        for tau in (1e-6, 1e-4, 1e-3, 1e-2):
            b = sum(bits(execute(s, post, kq, "F", T, tau)[0], o) for s, o in ctx["pairs"]) / len(ctx["pairs"])
            if best is None or b < best[0]:
                best = (b, T, tau)
    _, T_F, tau_F = best
    tests = [(kind, depth, *ctx["read_prompt"](prompt.split()), ans) for _, kind, prompt, ans, depth in ctx["tests"]]
    print(f"{d} ({world['task']}, {world['regime']}; policy {'accepted' if ctx['accepted'] else 'NOT accepted'} by latent.py); "
          f"F chose temperature {T_F:g}, prune below {tau_F:g} (training bits {best[0]:.3f})")
    print("    arm | 2 steps | 3 steps | 5 steps | 7 steps | bits for the true answer | max active | expansions/query | ms/query | mean mass by outcome")
    import os
    for arm in ("ABCDEF" if os.environ.get("SOFT_B") == "1" else "ACDEF"):
        by, b, mx, ex, t0 = defaultdict(lambda: [0, 0]), 0.0, 0, 0, time.time()
        acct = defaultdict(float)
        try:
            runs = [(kind, depth, ans, *(execute(start, post, kq, arm, *((T_F, tau_F) if arm == "F" else (1.0, 0.0)), acct=acct) if g == q else ({}, 0, 0)))
                    for kind, depth, start, g, ans in tests]
        except RuntimeError:
            print(f"      {arm} | exploded: more than 2,000,000 active states in one query")
            continue
        for kind, depth, ans, ansd, act, exp in runs:
            p = Runtime.project(ansd, vocab)
            assert abs(sum(p.values()) - 1) < 1e-6, "admission gate"
            by[depth][0] += max(p, key=p.get) == ans
            by[depth][1] += 1
            b += -math.log2(p[ans])
            mx, ex = max(mx, act), ex + exp
        n = len(tests)
        print(f"      {arm} | " + " | ".join(f"{by[x][0] / by[x][1]:.3f}" for x in ("2", "3", "5", "7"))
              + f" | {b / n:.3f} | {mx} | {ex / n:.1f} | {(time.time() - t0) * 1000 / n:.2f} | "
              + ", ".join(f"{o} {acct[o] / n:.4f}" for o in ("completed", "dead end", "pruned", "unfinished")))


if __name__ == "__main__":
    for d in sys.argv[1:]:
        main(d)
