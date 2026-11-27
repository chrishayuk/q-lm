"""Q-LM v2, stages E1 to E3, prototype (docs/qlm-v2-plan.md).

    python3 -I v2/classes.py data-ts 10000 --width 2 --classes 256 --members 1 --ppmi

E1: every word's contexts, the w words before and after it, counted.
E2: similarities from those context vectors (PPMI weighted or binary),
    reduced by truncated SVD.
E3: abstraction nodes, k-means clusters of the words. Every word keeps its
    identity and gets weighted memberships in its top m clusters.

Judged by held-out prediction: a class trigram over the abstraction nodes,
P(w | h) = sum_c P(c | the classes of the previous two words) P(w | c),
interpolated with the Kneser-Ney word 5-gram (`qlm knprobs`). The weight is
fitted on development sentences 1-1,000 and scored on 1,001-3,000.
"""
import argparse
import collections
import math
import time

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import svds

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("n", type=int)
ap.add_argument("--width", default="2")  # e.g. "2" or "1+2+4"
ap.add_argument("--classes", type=int, default=256)
ap.add_argument("--members", type=int, default=1)
ap.add_argument("--ppmi", action="store_true")
ap.add_argument("--dims", type=int, default=128)
a = ap.parse_args()
t0 = time.time()
train = [l.split() for l in open(f"{a.dir}/train.txt")][: a.n]
dev = [l.split() for l in open(f"{a.dir}/dev.txt")][:3000]
vocab = [w for w in open(f"{a.dir}/vocab.txt").read().split()]
wid = {w: i for i, w in enumerate(vocab)}
V = len(vocab)
counts = np.zeros(V)
for s in train:
    for w in s:
        counts[wid[w]] += 1

# E1: context features of widths w, left and right.
widths = [int(x) for x in a.width.split("+")]
feat = {}
rows, cols = [], []
for s in train:
    p = ["<s>"] * 8 + s + ["</s>"] * 8
    for i, w in enumerate(s):
        j = i + 8
        for k in widths:
            for side, ctx in (("L", tuple(p[j - k:j])), ("R", tuple(p[j + 1:j + 1 + k]))):
                f = feat.setdefault((k, side, ctx), len(feat))
                rows.append(wid[w])
                cols.append(f)
X = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(V, len(feat)))
X.sum_duplicates()
t1 = time.time()

# E2: PPMI (or binary), then truncated SVD; rows normalised.
if a.ppmi:
    total = X.sum()
    pw = np.asarray(X.sum(1)).ravel() / total
    pf = np.asarray(X.sum(0)).ravel() / total
    X = X.tocoo()
    pmi = np.log((X.data / total) / (pw[X.row] * pf[X.col]))
    keep = pmi > 0
    X = sp.csr_matrix((pmi[keep], (X.row[keep], X.col[keep])), shape=(V, len(feat)))
else:
    X.data[:] = 1.0
seen = counts > 0
k = min(a.dims, min(X.shape) - 1)
U, S, _ = svds(X.astype(np.float64), k=k)
E = U * S
E[~seen] = 0
norm = np.linalg.norm(E, axis=1, keepdims=True)
E = np.divide(E, norm, out=np.zeros_like(E), where=norm > 0)

# E3: k-means abstraction nodes over seen words, weighted by frequency.
rng = np.random.default_rng(1)
idx = np.flatnonzero(seen)
C = min(a.classes, len(idx))
cent = E[rng.choice(idx, C, replace=False)]
for _ in range(30):
    sim = E[idx] @ cent.T
    assign = sim.argmax(1)
    for c in range(C):
        m = idx[assign == c]
        if len(m):
            v = (E[m] * counts[m, None]).sum(0)
            cent[c] = v / (np.linalg.norm(v) + 1e-12)
sim = E @ cent.T  # every word against every node
# Memberships: top m nodes, weights proportional to exp(cos / 0.1).
M = np.zeros((V, C))
top = np.argsort(-sim, axis=1)[:, : a.members]
for w in range(V):
    if not seen[w]:
        continue
    s = sim[w, top[w]]
    e = np.exp((s - s.max()) / 0.1)
    M[w, top[w]] = e / e.sum()
hard = np.where(seen, sim.argmax(1), -1)
t2 = time.time()

# P(w | c): frequency times membership, per node.
END = V  # END's word id
END_C, START_C, UNK_C = C, C + 1, C + 2  # END's class, the start padding, words unseen in the slice
Pwc = np.zeros((C + 3, V + 1))
Pwc[:C, :V] = (M * counts[:, None]).T
Pwc[END_C, END] = 1.0
Pwc[UNK_C, :V] = (~seen).astype(float)
Pwc /= Pwc.sum(1, keepdims=True) + 1e-300
cls = lambda w: hard[wid[w]] if hard[wid[w]] >= 0 else UNK_C

# Class trigram with interpolated absolute discounting.
D = 0.75
tri, bi, uni = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter), collections.Counter()
for s in train:
    seq = [START_C, START_C] + [cls(w) for w in s] + [END_C]
    for i in range(2, len(seq)):
        tri[(seq[i - 2], seq[i - 1])][seq[i]] += 1
        bi[seq[i - 1]][seq[i]] += 1
        uni[seq[i]] += 1
N1 = sum(uni.values())
K = C + 3


def p_uni(c):
    return (uni[c] + 0.1) / (N1 + 0.1 * K)


def p_bi(c, h1):
    d = bi.get(h1)
    if not d:
        return p_uni(c)
    tot = sum(d.values())
    return max(d[c] - D, 0) / tot + D * len(d) / tot * p_uni(c)


def p_tri(c, h2, h1):
    d = tri.get((h2, h1))
    if not d:
        return p_bi(c, h1)
    tot = sum(d.values())
    return max(d[c] - D, 0) / tot + D * len(d) / tot * p_bi(c, h1)




def class_probs(s):
    """P(token | history) under the class model, for each token of s and END."""
    out = []
    hist = [START_C, START_C]
    for i in range(len(s) + 1):
        w = END if i == len(s) else wid[s[i]]
        # sum over the classes the token belongs to
        cs = [END_C] if w == END else np.flatnonzero(M[w]) if seen[w] else [UNK_C]
        p = sum(p_tri(c, hist[-2], hist[-1]) * Pwc[c, w] for c in cs)
        out.append(max(p, 1e-12))
        if i < len(s):
            hist.append(cls(s[i]))
    return out


kn = [[float(x) for x in l.split()] for l in open(f"{a.dir}/v2/kn5-{a.n}.txt")]
pc = [class_probs(s) for s in dev]
fit, score = range(0, 1000), range(1000, 3000)


def bits(lam, rng_):
    tot = toks = 0
    for i in rng_:
        for x, y in zip(pc[i], kn[i]):
            tot -= math.log2(lam * x + (1 - lam) * y)
            toks += 1
    return tot / toks


lam = min((l / 20 for l in range(0, 21)), key=lambda l: bits(l, fit))
t3 = time.time()
print(
    f"n={a.n} width={a.width} classes={C} members={a.members} ppmi={a.ppmi} | "
    f"5-gram {bits(0, score):.4f} | class model {bits(1, score):.4f} | mixed {bits(lam, score):.4f} (lambda {lam:.2f}) | "
    f"features {len(feat)} | E1 {t1 - t0:.0f}s E2-E3 {t2 - t1:.0f}s scoring {t3 - t2:.0f}s"
)
