"""QLM-ATTENTION-001 (prototype): graph-native attention, learned without
backpropagation. See docs/qlm-attention-001-plan.md.

    python3 -I v2/attn.py data-ts 100000 --arm F

The retrieval component at position t: P_attn(w) = sum_i a_i A(w | x_i)
over the earlier positions of the sentence. A is a counted association (w
anywhere later in the same sentence as u). The keys and the query are
pass-1 distributional vectors. The weights depend on the arm. The component
joins the v2 mixture (5-gram plus 4 class models); its parameter is fitted
on development 1-1,000; arms are compared on 1,001-3,000 (--split select)
or confirmed on 3,001-7,000 (--split confirm).
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
ap.add_argument("--arm", default="A")
ap.add_argument("--split", default="select", choices=["select", "confirm"])
a = ap.parse_args()
t0 = time.time()
core.setup(a.dir, a.n)
V, END, wid, dev = core.V, core.END, core.wid, core.dev
classes = []
E = None
for seed in range(1, 5):
    hard, C, Es = core.learn(np.arange(V), 256, seed)
    classes.append(core.ClassModel(hard, C))
    if seed == 1:
        E = Es
hard1, C1 = classes[0].hard, classes[0].C

# Association values A(w | u): w (or END) anywhere later in the sentence.
assoc = collections.defaultdict(collections.Counter)
cassoc = collections.defaultdict(collections.Counter)  # class level, for arm G
for s in core.enc:
    seq = s + [END]
    for i, u in enumerate(s):
        for w in seq[i + 1:]:
            assoc[u][w] += 1
            cassoc[hard1[u]][C1 + 1 if w == END else hard1[w]] += 1
atot = {u: sum(c.values()) for u, c in assoc.items()}
ctot = {u: sum(c.values()) for u, c in cassoc.items()}
uni = np.zeros(V + 1)
for s in core.enc:
    for w in s:
        uni[w] += 1
    uni[END] += 1
uni = (uni + 0.01) / (uni + 0.01).sum()
Pw1 = classes[0].Pw  # P(w | class), with END's class at C1 + 1


def A(w, u):
    if u not in atot:
        return uni[w]
    return assoc[u][w] / atot[u]


def Ac(w, u):
    cu = hard1[u]
    if cu not in ctot:
        return uni[w]
    cw = C1 + 1 if w == END else hard1[w]
    return cassoc[cu][cw] / ctot[cu] * Pw1[cw, w]


def weights(s_ids, t, arm, p):
    """Attention weights over positions 0..t-1 (t >= 1)."""
    d = np.arange(t, 0, -1, dtype=float)  # distance t - i
    if arm == "C":
        z = np.zeros(t)
    elif arm == "D":
        z = d * math.log(p)  # rho ** d
    else:
        q = E[s_ids[t - 1]]
        k = E[s_ids[:t]]
        z = (k @ q) / p["tau"]
        if arm in ("F", "G"):
            z = z - p["slope"] * d
    z = z - z.max()
    w = np.exp(z)
    return w / w.sum()


def attn_probs(s, arm, p, level="word"):
    ids = [wid[x] for x in s]
    out = []
    for t in range(len(ids) + 1):
        w = END if t == len(ids) else ids[t]
        if t == 0:
            out.append(uni[w])
            continue
        a_ = weights(ids, t, arm, p)
        f = A if level == "word" else Ac
        out.append(max(sum(a_[i] * f(w, ids[i]) for i in range(t)), 1e-12))
    return out


kn_file = f"{a.dir}/v2/kn{8 if a.arm == 'B' else 5}-{a.n}.txt"
kn = [[float(x) for x in l.split()] for l in open(kn_file)]
cls_probs = [[m.probs(dev[i]) for m in classes] for i in range(7000)]


def components(i, extra):
    return [kn[i]] + cls_probs[i] + extra(i)


def em_bits(extra, fit_rows, eval_rows, long_only=False):
    J = len(components(0, extra))
    comps = {i: components(i, extra) for i in list(fit_rows) + list(eval_rows)}
    w = np.full(J, 1.0 / J)
    for _ in range(40):
        acc = np.zeros(J)
        for i in fit_rows:
            for t in range(len(comps[i][0])):
                pv = np.array([c[t] for c in comps[i]]) * w
                acc += pv / pv.sum()
        w = acc / acc.sum()

    def bits(rows, long_only):
        tot = n = 0
        for i in rows:
            for t in range(len(comps[i][0])):
                if long_only and t < 6:
                    continue
                tot -= math.log2(sum(w[j] * comps[i][j][t] for j in range(J)))
                n += 1
        return tot / max(n, 1)

    return bits(eval_rows, False), bits(eval_rows, True), w


fit = range(0, 1000)
evalr = range(1000, 3000) if a.split == "select" else range(3000, 7000)
none = lambda i: []
if a.arm in ("A", "B"):
    best = (em_bits(none, fit, evalr), None)
else:
    grid = {
        "C": [None],
        "D": [0.5, 0.7, 0.85, 0.95],
        "E": [{"tau": t} for t in (0.05, 0.1, 0.2, 0.5)],
        "F": [{"tau": t, "slope": s} for t in (0.05, 0.1, 0.2) for s in (0.0, 0.1, 0.3, 0.6)],
        "G": [{"tau": t, "slope": s} for t in (0.05, 0.1, 0.2) for s in (0.0, 0.1, 0.3, 0.6)],
    }[a.arm]
    # Choose the parameter on the fitting split only.
    scored = []
    for p in grid:
        cache = {}

        def extra(i, p=p, cache=cache):
            if i not in cache:
                r = [attn_probs(dev[i], a.arm, p)]
                if a.arm == "G":
                    r.append(attn_probs(dev[i], a.arm, p, level="class"))
                cache[i] = r
            return cache[i]

        fb, _, _ = em_bits(extra, fit, fit)
        scored.append((fb, p, extra))
    _, p, extra = min(scored, key=lambda x: x[0])
    best = (em_bits(extra, fit, evalr), p)
(b_all, b_long, w), p = best
print(f"n={a.n} arm={a.arm} split={a.split} | all positions {b_all:.4f} | positions 6+ {b_long:.4f} | parameter {p} | weights {np.round(w, 3).tolist()} | {time.time() - t0:.0f}s")
