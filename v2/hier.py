"""Q-LM v2, stage E4 (prototype): abstractions as contexts for further
abstraction. See docs/qlm-v2-plan.md.

    python3 -I v2/hier.py data-ts 100000 --passes 3

Pass 1 is E1 to E3 (classes.py, with its fixes): word contexts, PPMI, SVD,
k-means nodes. Pass k > 1 rewrites every context in terms of pass k-1's
nodes (a context word becomes its node) and learns new nodes from those
contexts. Each pass gives a class trigram over its nodes. The predictor is
a mixture of the word 5-gram and the per-pass class models. Its weights are
fitted by EM on development sentences 1-1,000; settings are compared on
1,001-3,000; one final run is reported on 3,001-7,000 (confirmation).

Fixes from classes.py: START is not a predicted class, so every model's
next-token probabilities sum to one (checked); the SVD has a fixed start
vector; everything is seeded.

Controls (--control):
- flat: one pass with as many nodes as all passes together;
- seeds: as many independent pass-1 models (different seeds) as passes.
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
ap.add_argument("--passes", type=int, default=1)
ap.add_argument("--width", default="1+2")
ap.add_argument("--classes", type=int, default=256)
ap.add_argument("--control", default="")
ap.add_argument("--split", default="select", choices=["select", "confirm"])
ap.add_argument("--check", action="store_true")
a = ap.parse_args()
t0 = time.time()
train = [l.split() for l in open(f"{a.dir}/train.txt")][: a.n]
dev_all = [l.split() for l in open(f"{a.dir}/dev.txt")]
dev = dev_all[:7000]
vocab = open(f"{a.dir}/vocab.txt").read().split()
wid = {w: i for i, w in enumerate(vocab)}
V = len(vocab)
END = V
counts = np.zeros(V)
for s in train:
    for w in s:
        counts[wid[w]] += 1
seen = counts > 0
widths = [int(x) for x in a.width.split("+")]
enc = [[wid[w] for w in s] for s in train]


def learn(labels, n_classes, seed):
    """Nodes from contexts written in `labels` (a label per word id)."""
    feat, rows, cols = {}, [], []
    for s in enc:
        p = [-1] * 8 + [labels[w] for w in s] + [-2] * 8
        for i, w in enumerate(s):
            j = i + 8
            for k in widths:
                for side, ctx in (("L", tuple(p[j - k:j])), ("R", tuple(p[j + 1:j + 1 + k]))):
                    rows.append(w)
                    cols.append(feat.setdefault((k, side, ctx), len(feat)))
    X = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(V, len(feat)))
    X.sum_duplicates()
    total = X.sum()
    pw = np.asarray(X.sum(1)).ravel() / total
    pf = np.asarray(X.sum(0)).ravel() / total
    X = X.tocoo()
    with np.errstate(divide="ignore"):
        pmi = np.log((X.data / total) / (pw[X.row] * pf[X.col]))
    keep = pmi > 0
    X = sp.csr_matrix((pmi[keep], (X.row[keep], X.col[keep])), shape=(V, len(feat)))
    rng = np.random.default_rng(seed)
    k = min(128, min(X.shape) - 1)
    U, S, _ = svds(X, k=k, v0=rng.standard_normal(min(X.shape)))
    E = U * S
    E[~seen] = 0
    nrm = np.linalg.norm(E, axis=1, keepdims=True)
    E = np.divide(E, nrm, out=np.zeros_like(E), where=nrm > 0)
    idx = np.flatnonzero(seen)
    C = min(n_classes, len(idx))
    cent = E[rng.choice(idx, C, replace=False)]
    for _ in range(30):
        assign = (E[idx] @ cent.T).argmax(1)
        for c in range(C):
            m = idx[assign == c]
            if len(m):
                v = (E[m] * counts[m, None]).sum(0)
                cent[c] = v / (np.linalg.norm(v) + 1e-12)
    hard = np.where(seen, (E @ cent.T).argmax(1), C)  # C: unseen words
    return hard, C


class ClassModel:
    """Class trigram, interpolated absolute discounting, over C nodes plus
    END and UNSEEN. START is history only, never predicted."""

    def __init__(self, hard, C):
        self.hard, self.C = hard, C
        self.END_C, self.UNK_C, self.START_C = C + 1, C, C + 2
        self.K = C + 2  # predicted classes: 0..C-1, UNK_C, END_C
        Pw = np.zeros((C + 2, V + 1))
        for w in range(V):
            if seen[w]:
                Pw[hard[w], w] = counts[w]
        Pw[self.UNK_C, :V] = (~seen).astype(float)
        if not (~seen).any():
            Pw[self.UNK_C, :V] = 1.0
        Pw[self.END_C, END] = 1.0
        self.Pw = Pw / Pw.sum(1, keepdims=True)
        self.tri = collections.defaultdict(collections.Counter)
        self.bi = collections.defaultdict(collections.Counter)
        self.uni = collections.Counter()
        for s in enc:
            seq = [self.START_C, self.START_C] + [hard[w] for w in s] + [self.END_C]
            for i in range(2, len(seq)):
                self.tri[(seq[i - 2], seq[i - 1])][seq[i]] += 1
                self.bi[seq[i - 1]][seq[i]] += 1
                self.uni[seq[i]] += 1
        self.N1 = sum(self.uni.values())
        self.tt = {h: (sum(d.values()), len(d)) for h, d in self.tri.items()}
        self.bt = {h: (sum(d.values()), len(d)) for h, d in self.bi.items()}

    def p_uni(self, c):
        return (self.uni[c] + 0.1) / (self.N1 + 0.1 * self.K)

    def p_bi(self, c, h1):
        if h1 not in self.bt:
            return self.p_uni(c)
        tot, nd = self.bt[h1]
        return max(self.bi[h1][c] - 0.75, 0) / tot + 0.75 * nd / tot * self.p_uni(c)

    def p_tri(self, c, h2, h1):
        if (h2, h1) not in self.tt:
            return self.p_bi(c, h1)
        tot, nd = self.tt[(h2, h1)]
        return max(self.tri[(h2, h1)][c] - 0.75, 0) / tot + 0.75 * nd / tot * self.p_bi(c, h1)

    def probs(self, s):
        ws = [wid[w] for w in s] + [END]
        hist = [self.START_C, self.START_C]
        out = []
        for i, w in enumerate(ws):
            c = self.END_C if w == END else self.hard[w]
            out.append(self.p_tri(c, hist[-2], hist[-1]) * self.Pw[c, w])
            if i < len(s):
                hist.append(self.hard[w])
        return out

    def total(self, h2, h1):
        """Sum over every next token of P(token | history): should be 1."""
        pc = np.array([self.p_tri(c, h2, h1) for c in range(self.C)] + [self.p_tri(self.UNK_C, h2, h1), self.p_tri(self.END_C, h2, h1)])
        return pc.sum()


models = []
if a.control == "flat":
    hard, C = learn(np.arange(V), a.classes * a.passes, 1)
    models.append(ClassModel(hard, C))
elif a.control == "seeds":
    for p in range(a.passes):
        hard, C = learn(np.arange(V), a.classes, 1 + p)
        models.append(ClassModel(hard, C))
else:
    labels = np.arange(V)  # pass 1: contexts in words
    for p in range(a.passes):
        hard, C = learn(labels, a.classes, 1)
        models.append(ClassModel(hard, C))
        labels = hard  # the next pass reads contexts in these nodes
t1 = time.time()
if a.check:
    m = models[0]
    for h in [(m.START_C, m.START_C), (0, 1), (m.hard[wid["the"]], m.hard[wid["girl"]])]:
        print(f"check: next-class probabilities sum to {m.total(*h):.6f}")

kn = [[float(x) for x in l.split()] for l in open(f"{a.dir}/v2/kn5-{a.n}.txt")]
if len(kn) < 7000:
    raise SystemExit("kn5 file has fewer than 7,000 sentences; rerun qlm knprobs")
comps = [[kn[i]] + [m.probs(dev[i]) for m in models] for i in range(7000)]


def mixture_bits(w, rows):
    tot = toks = 0
    for i in rows:
        for t in range(len(comps[i][0])):
            tot -= math.log2(sum(w[j] * comps[i][j][t] for j in range(len(w))))
            toks += 1
    return tot / toks


# EM for the mixture weights on the fitting sentences.
J = len(comps[0])
w = np.full(J, 1.0 / J)
for _ in range(50):
    acc = np.zeros(J)
    for i in range(1000):
        for t in range(len(comps[i][0])):
            p = np.array([comps[i][j][t] for j in range(J)]) * w
            acc += p / p.sum()
    w = acc / acc.sum()
rows = range(1000, 3000) if a.split == "select" else range(3000, 7000)
t2 = time.time()
print(
    f"n={a.n} passes={a.passes} width={a.width} classes={a.classes} control={a.control or 'none'} split={a.split} | "
    f"5-gram {mixture_bits(np.eye(J)[0], rows):.4f} | mixture {mixture_bits(w, rows):.4f} | weights {np.round(w, 3).tolist()} | "
    f"learn {t1 - t0:.0f}s score {t2 - t1:.0f}s"
)
