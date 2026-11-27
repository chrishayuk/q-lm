"""QLM-KEY-001, arm B (prototype): similar recent histories. See
docs/qlm-key-001-plan.md.

    python3 -I v2/keys.py data-ts 100000

P_B(w | x_{t-2}, x_{t-1}) = sum_u K(x_{t-2}, u) c(u, x_{t-1}, w)
                          / sum_u K(x_{t-2}, u) c(u, x_{t-1}),
over the words u that preceded x_{t-1} in training, the k nearest to
x_{t-2} by distributional cosine. K = exp(cos / tau). The exact history u =
x_{t-2} is one of them. Positions with fewer than two words of history use
the bigram counts. P_B joins the v2 mixture (5-gram + 4 class models).
tau and k are chosen on development 1-1,000; reported on 1,001-3,000 by
position (0-1, 2-4, 5+), or on 3,001-7,000 with --split confirm.
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
ap.add_argument("--split", default="select", choices=["select", "confirm"])
a = ap.parse_args()
t0 = time.time()
core.setup(a.dir, a.n)
V, END, wid, dev = core.V, core.END, core.wid, core.dev
classes, E = [], None
for seed in range(1, 5):
    hard, C, Es = core.learn(np.arange(V), 256, seed)
    classes.append(core.ClassModel(hard, C))
    E = Es if seed == 1 else E
START = -1
tri = collections.defaultdict(collections.Counter)  # (u, v) -> next counts
prev_of = collections.defaultdict(collections.Counter)  # v -> u -> count of (u, v)
bi = collections.defaultdict(collections.Counter)
for s in core.enc:
    seq = [START, START] + s + [END]
    for i in range(2, len(seq)):
        u, v, w = seq[i - 2], seq[i - 1], seq[i]
        tri[(u, v)][w] += 1
        prev_of[v][u] += 1
        bi[v][w] += 1
uni = np.zeros(V + 1)
for s in core.enc:
    for w in s:
        uni[w] += 1
    uni[END] += 1
uni = (uni + 0.01) / (uni + 0.01).sum()
vec = lambda u: E[u] if u >= 0 else None


def neighbours(u0, v, k, tau):
    """The words u preceding v in training, the k nearest to u0, with kernel weights."""
    us = list(prev_of[v])
    if u0 < 0 or not us:
        return [(u, 1.0 if u == u0 else 0.0) for u in us if u == u0] or [(u, 1.0) for u in us]
    q = E[u0]
    sims = np.array([q @ E[u] if u >= 0 else -1.0 for u in us])
    top = np.argsort(-sims)[:k]
    return [(us[j], math.exp((sims[j] - 1.0) / tau)) for j in top]


def probs(s, k, tau):
    ids = [START, START] + [wid[x] for x in s] + [END]
    out = []
    for i in range(2, len(ids)):
        u0, v, w = ids[i - 2], ids[i - 1], ids[i]
        if v == START:
            out.append(uni[w])
            continue
        num = den = 0.0
        for u, kw in neighbours(u0, v, k, tau):
            c = tri[(u, v)]
            tot = sum(c.values())
            num += kw * c[w]
            den += kw * tot
        if den == 0:
            tot = sum(bi[v].values())
            out.append(max(bi[v][w] / tot, 1e-12) if tot else uni[w])
        else:
            out.append(max(num / den, 1e-12))
    return out


kn = [[float(x) for x in l.split()] for l in open(f"{a.dir}/v2/kn5-{a.n}.txt")]
cls = [[m.probs(dev[i]) for m in classes] for i in range(7000)]
fit = range(0, 1000)
evalr = range(1000, 3000) if a.split == "select" else range(3000, 7000)


def mix(extra_of, rows_fit, rows_eval):
    comps = {i: [kn[i]] + cls[i] + extra_of(i) for i in list(rows_fit) + list(rows_eval)}
    J = len(comps[rows_fit[0]])
    w = np.full(J, 1.0 / J)
    for _ in range(40):
        acc = np.zeros(J)
        for i in rows_fit:
            for t in range(len(comps[i][0])):
                pv = np.array([c[t] for c in comps[i]]) * w
                acc += pv / pv.sum()
        w = acc / acc.sum()
    buckets = {"0-1": [0, 0], "2-4": [0, 0], "5+": [0, 0], "all": [0, 0]}
    for i in rows_eval:
        for t in range(len(comps[i][0])):
            b = -math.log2(sum(w[j] * comps[i][j][t] for j in range(J)))
            key = "0-1" if t < 2 else "2-4" if t <= 4 else "5+"
            for kk in (key, "all"):
                buckets[kk][0] += b
                buckets[kk][1] += 1
    return {k: v[0] / v[1] for k, v in buckets.items()}, w


base, wb = mix(lambda i: [], fit, evalr)
grid = [(k, tau) for k in (10, 50) for tau in (0.05, 0.1, 0.2)]
scored = []
for k, tau in grid:
    cache = {}
    f = lambda i, k=k, tau=tau, cache=cache: cache.setdefault(i, [probs(dev[i], k, tau)])
    fb, _ = mix(f, fit, fit)
    scored.append((fb["all"], k, tau, f))
_, k, tau, f = min(scored, key=lambda x: x[0])
res, w = mix(f, fit, evalr)
fmt = lambda r: " ".join(f"{b} {r[b]:.4f}" for b in ("all", "0-1", "2-4", "5+"))
print(f"n={a.n} split={a.split} | v2: {fmt(base)} | v2 + B (k={k}, tau={tau}): {fmt(res)} | B's weight {w[-1]:.3f} | {time.time() - t0:.0f}s")
