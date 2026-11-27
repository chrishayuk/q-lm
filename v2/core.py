"""Shared parts of the v2 prototypes: pass-1 learning (E1 to E3) and the
class trigram. `setup(dir, n)` must be called first."""
import collections

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import svds

train = dev = vocab = wid = None
V = END = 0
counts = seen = enc = None
widths = [1, 2]


def setup(dir, n, width="1+2"):
    global train, dev, vocab, wid, V, END, counts, seen, enc, widths
    train = [l.split() for l in open(f"{dir}/train.txt")][:n]
    dev = [l.split() for l in open(f"{dir}/dev.txt")][:11000]
    vocab = open(f"{dir}/vocab.txt").read().split()
    wid = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)
    END = V
    counts = np.zeros(V)
    for s in train:
        for w in s:
            counts[wid[w]] += 1
    seen = counts > 0
    widths = [int(x) for x in width.split("+")]
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
    return hard, C, E


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




def memberships(E, hard, C, m):
    """Soft memberships of every seen word in its top m classes: weights
    proportional to exp(cos / 0.1) to the classes' frequency-weighted
    centroids. Returns a dict word -> [(class, weight)]."""
    cent = np.zeros((C, E.shape[1]))
    for w in range(V):
        if seen[w]:
            cent[hard[w]] += E[w] * counts[w]
    cent /= np.linalg.norm(cent, axis=1, keepdims=True) + 1e-12
    sim = E @ cent.T
    out = {}
    for w in range(V):
        if not seen[w]:
            continue
        top = np.argsort(-sim[w])[:m]
        e = np.exp((sim[w, top] - sim[w, top].max()) / 0.1)
        e = e / e.sum()
        out[w] = [(int(c), float(x)) for c, x in zip(top, e) if x > 1e-3]
    return out
