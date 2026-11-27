"""QLM-KEY-001, arms C, D and E (prototype): composite keys, and keys learned
by utility. See docs/qlm-key-001-plan.md.

    python3 -I v2/composite.py data-ts 100000 --arm E

A key template pairs the recent word v = x_{t-1} with one other piece of
the history:
- ("w", d): the word d positions back (d = 2..8);
- ("c", d): that word's abstraction node (pass 1);
- ("cw", d): v's node (not v itself) paired with the word d back.

Each template gives a component P(w | v, key), with interpolated absolute
discounting back to the bigram P(w | v). Where the history is too short,
the component is the bigram.

Arms:
- C: every ("w", d) template;
- D: every ("c", d) template;
- E: the templates of any kind whose utility is positive. Utility is the
  held-out gain over the bigram, in bits per token, on the last 10% of the
  training sentences, counted on the first 90%; minus lam times (1/2)
  log2(N) per stored binding, over the N training tokens. lam = 0 keeps any
  template that generalises at all; the full description-length charge
  (lam = 1) charges the whole table against one pass over the data, which
  no table passes at these sizes.

The components join the v2 mixture (5-gram + 4 class models). Weights by EM
on development 1-1,000; reported on 1,001-3,000 by position, or on
3,001-7,000 with --split confirm.
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
ap.add_argument("--arm", default="E")
ap.add_argument("--split", default="select", choices=["select", "confirm"])
ap.add_argument("--lam", type=float, default=1.0)
ap.add_argument("--buckets", action="store_true", help="mixture weights per position bucket")
ap.add_argument("--keys", default="", help="for arm R or V: comma-separated templates, e.g. w2,w3,c2")
a = ap.parse_args()
t0 = time.time()
core.setup(a.dir, a.n)
V, END, wid, dev = core.V, core.END, core.wid, core.dev
classes = []
for seed in range(1, 5):
    hard, C, _ = core.learn(np.arange(V), 256, seed)
    classes.append(core.ClassModel(hard, C))
node = classes[0].hard
START = -1
D_ = 0.75
templates = [(k, d) for k in ("w", "c", "cw") for d in range(2, 9)]


RANDOM = False  # arm R: the earlier item is at a random distance, not d


def key_of(tmpl, ids, t):
    """The key for predicting ids[t] (ids starts with the sentence's words);
    None if the history is too short."""
    k, d = tmpl
    if RANDOM and t >= 2:
        # A pseudo-random distance in 2..t, fixed by the sentence and the
        # position: the same storage, no consistent addressing.
        h = (hash(tuple(ids[:t])) ^ (d * 0x9E3779B1)) & 0xFFFFFFFF
        d = 2 + h % (t - 1)
    if t - d < 0 or t - 1 < 0:
        return None
    v, x = ids[t - 1], ids[t - d]
    if k == "w":
        return (v, x)
    if k == "c":
        return (v, node[x])
    return ("cw", node[v], x)


class Successive:
    """Arm G: P(w | h) = P(c(w) | the last two classes) * P(w | c(w), x_{t-d}),
    backed off to P(w | c(w)). Nothing indexed by (x_{t-1}, x_{t-d}) is
    stored."""

    def __init__(self, d, cm):
        self.d, self.cm = d, cm
        self.c = collections.defaultdict(collections.Counter)  # (class, earlier word) -> w
        for s in core.enc:
            seq = s + [END]
            for t in range(len(seq)):
                if t - d < 0:
                    continue
                w = seq[t]
                cw = cm.END_C if w == END else cm.hard[w]
                self.c[(cw, seq[t - d])][w] += 1
        self.ct = {k: (sum(c.values()), len(c)) for k, c in self.c.items()}
        self.bindings = sum(len(c) for c in self.c.values())

    def probs(self, s):
        ids = [wid[x] for x in s]
        base = self.cm.probs(s)  # P(c(w) | h) * P(w | c(w))
        out = []
        for t in range(len(ids) + 1):
            w = END if t == len(ids) else ids[t]
            cw = self.cm.END_C if w == END else self.cm.hard[w]
            pwc = self.cm.Pw[cw, w]
            if t - self.d < 0 or (cw, ids[t - self.d]) not in self.ct or pwc == 0:
                out.append(base[t])
                continue
            tot, nd = self.ct[(cw, ids[t - self.d])]
            p_in = max(self.c[(cw, ids[t - self.d])][w] - D_, 0) / tot + D_ * nd / tot * pwc
            out.append(max(base[t] / pwc * p_in, 1e-12))  # P(c | h) * P(w | c, x)
        return out


class Model:
    """P(w | v, key), backing off to the bigram P(w | v), both counted on `sents`."""

    def __init__(self, tmpl, sents):
        self.tmpl = tmpl
        self.c = collections.defaultdict(collections.Counter)
        self.bi = collections.defaultdict(collections.Counter)
        self.uni = collections.Counter()
        for s in sents:
            seq = s + [END]
            for t in range(len(seq)):
                v = seq[t - 1] if t > 0 else START
                self.bi[v][seq[t]] += 1
                self.uni[seq[t]] += 1
                key = key_of(tmpl, seq, t) if tmpl else None
                if key is not None:
                    self.c[key][seq[t]] += 1
        self.N = sum(self.uni.values())
        self.ct = {k: (sum(c.values()), len(c)) for k, c in self.c.items()}
        self.bt = {k: (sum(c.values()), len(c)) for k, c in self.bi.items()}
        self.bindings = sum(len(c) for c in self.c.values())

    def p_uni(self, w):
        return (self.uni[w] + 0.01) / (self.N + 0.01 * (V + 1))

    def p_bi(self, w, v):
        if v not in self.bt:
            return self.p_uni(w)
        tot, nd = self.bt[v]
        return max(self.bi[v][w] - D_, 0) / tot + D_ * nd / tot * self.p_uni(w)

    def p(self, ids, t):
        seq = ids
        w = seq[t]
        v = seq[t - 1] if t > 0 else START
        key = key_of(self.tmpl, seq, t) if self.tmpl else None
        if key is None or key not in self.ct:
            return self.p_bi(w, v)
        tot, nd = self.ct[key]
        return max(self.c[key][w] - D_, 0) / tot + D_ * nd / tot * self.p_bi(w, v)

    def probs(self, s):
        seq = [wid[x] for x in s] + [END]
        return [max(self.p(seq, t), 1e-12) for t in range(len(seq))]


enc = core.enc
if a.arm == "A":  # v2 alone (5-gram + 4 class models)
    chosen, util = [], {}
elif a.arm == "G":
    chosen, util = [], {}
elif a.arm in ("R", "V"):
    chosen = [("cw" if x.startswith("cw") else x[0], int("".join(ch for ch in x if ch.isdigit()))) for x in a.keys.split(",")]
    RANDOM = a.arm == "R"
    util = {}
elif a.arm == "C":
    chosen = [t for t in templates if t[0] == "w"]
    util = {}
elif a.arm == "D":
    chosen = [t for t in templates if t[0] == "c"]
    util = {}
else:
    cut = int(0.9 * len(enc))
    fitS, holdS = enc[:cut], enc[cut:]
    base = Model(None, fitS)
    hold_tokens = sum(len(s) + 1 for s in holdS)
    base_ll = sum(math.log2(max(base.p(s + [END], t), 1e-12)) for s in holdS for t in range(len(s) + 1))
    Ntok = sum(len(s) + 1 for s in enc)
    util = {}
    for tm in templates:
        m = Model(tm, fitS)
        ll = sum(math.log2(max(m.p(s + [END], t), 1e-12)) for s in holdS for t in range(len(s) + 1))
        gain = (ll - base_ll) / hold_tokens
        cost = a.lam * m.bindings * 0.5 * math.log2(Ntok) / Ntok
        util[tm] = (gain, cost, gain - cost)
    chosen = [tm for tm in templates if util[tm][2] > 0]
models = [Model(tm, enc) for tm in chosen]
if a.arm == "G":
    models = [Successive(d, classes[0]) for d in range(2, 9)]
t1 = time.time()
kn = [[float(x) for x in l.split()] for l in open(f"{a.dir}/v2/kn5-{a.n}.txt")]
cls = [[m.probs(dev[i]) for m in classes] for i in range(7000)]
fit = range(0, 1000)
evalr = range(1000, 3000) if a.split == "select" else range(3000, 7000)
comps = {i: [kn[i]] + cls[i] + [m.probs(dev[i]) for m in models] for i in list(fit) + list(evalr)}
J = len(comps[0])
bucket = (lambda t: min(t, 6)) if a.buckets else (lambda t: 0)
NB = 7
W = np.full((NB, J), 1.0 / J)
for _ in range(40):
    acc = np.zeros((NB, J)) + 1e-9
    for i in fit:
        for t in range(len(comps[i][0])):
            b = bucket(t)
            pv = np.array([c[t] for c in comps[i]]) * W[b]
            acc[b] += pv / pv.sum()
    W = acc / acc.sum(1, keepdims=True)
w = W[0]
B = {}
for i in evalr:
    for t in range(len(comps[i][0])):
        b = -math.log2(sum(W[bucket(t)][j] * comps[i][j][t] for j in range(J)))
        for kk in ("0-1" if t < 2 else "2-4" if t <= 4 else "5+", "all"):
            e = B.setdefault(kk, [0, 0])
            e[0] += b
            e[1] += 1
res = " ".join(f"{k} {B[k][0] / B[k][1]:.4f}" for k in ("all", "0-1", "2-4", "5+"))
kept = ", ".join(f"{k}{d}" for k, d in chosen) or ("successive g2-g8" if a.arm == "G" else "none")
print(f"n={a.n} arm={a.arm}{' buckets' if a.buckets else ''} split={a.split} | {res} | keys: {kept} | stored bindings {sum(m.bindings for m in models)} | {time.time() - t0:.0f}s")
if util:
    for tm in templates:
        g, c, u = util[tm]
        print(f"    {tm[0]}{tm[1]}: held-out gain {g:+.4f}, cost {c:.4f}, utility {u:+.4f}")
