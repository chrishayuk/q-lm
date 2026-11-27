"""Flat controls for v3 (docs/qlm-v3-plan.md): predictors that store
statistics and do no computation, on the same training text and tests.

- NGRAM: interpolated absolute-discount n-gram, orders 1 to 5 (D = 0.75).
- MATCHED: NGRAM mixed with composite keys (distance d = 1..5, the word at
  t - d) -> next word, the keys kept by count up to a budget equal to the
  number of entries in v3's learned knowledge (v3.1 on the same text).
  Mixture weights by EM on dev.txt.

The answer is the most probable next token after the prompt. Every
distribution passes the normalisation gate.

    python3 -I v3/flat.py WORLD_DIR [WORLD_DIR ...]
"""
import sys
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from learn import learn

D, ORDER, DMAX = 0.75, 5, 5


class NGram:
    def __init__(self, sents, vocab):
        self.V = vocab + ["END"]
        self.c = [defaultdict(lambda: defaultdict(int)) for _ in range(ORDER)]
        for s in sents:
            t = ["<S>"] * (ORDER - 1) + s + ["END"]
            for i in range(ORDER - 1, len(t)):
                for n in range(ORDER):
                    self.c[n][tuple(t[i - n:i])][t[i]] += 1
        self.tot = [{h: (sum(v.values()), len(v)) for h, v in c.items()} for c in self.c]

    def dist(self, hist):
        h = (["<S>"] * (ORDER - 1) + hist)[-(ORDER - 1):]
        p = {w: 1 / len(self.V) for w in self.V}
        for n in range(ORDER):
            key = tuple(h[len(h) - n:]) if n else ()
            if key in self.tot[n]:
                tot, nd = self.tot[n][key]
                cn = self.c[n][key]
                p = {w: max(cn.get(w, 0) - D, 0) / tot + D * nd / tot * p[w] for w in self.V}
        return p


class Keys:
    def __init__(self, sents, vocab, budget):
        self.V = vocab + ["END"]
        c = defaultdict(lambda: defaultdict(int))
        for s in sents:
            t = s + ["END"]
            for i in range(len(t)):
                for d in range(2, DMAX + 1):  # distance 1 is in the n-gram already
                    if i - d >= 0:
                        c[(d, t[i - d])][t[i]] += 1
        keep = sorted(c, key=lambda k: -sum(c[k].values()))
        kept, used = {}, 0
        for k in keep:
            if used + len(c[k]) > budget:
                break
            kept[k] = c[k]
            used += len(c[k])
        self.c, self.entries = kept, used

    def dist(self, hist, d):
        key = (d, hist[-d]) if len(hist) >= d else None
        if key not in self.c:
            return {w: 1 / len(self.V) for w in self.V}
        cn = self.c[key]
        tot = sum(cn.values())
        return {w: (cn.get(w, 0) + 0.01) / (tot + 0.01 * len(self.V)) for w in self.V}


def main(d):
    sents = [l.split() for l in open(f"{d}/train.txt").read().splitlines()]
    dev = [l.split() for l in open(f"{d}/dev.txt").read().splitlines()][:500]
    vocab = [w for w in open(f"{d}/vocab.txt").read().split() if w != "END"]
    tests = [l.rstrip("\n").split("\t") for l in open(f"{d}/tests.tsv")]
    budget = len(learn([" ".join(s) for s in sents])["knowledge"])
    ng, keys = NGram(sents, vocab), Keys(sents, vocab, budget)
    comps = lambda hist: [ng.dist(hist)] + [keys.dist(hist, k) for k in range(2, DMAX + 1)]
    # EM for the mixture weights on dev.
    rows = [(comps(s[:i]), (s + ["END"])[i]) for s in dev for i in range(len(s) + 1)]
    w = [1 / len(rows[0][0])] * len(rows[0][0])
    for _ in range(20):
        acc = [0.0] * len(w)
        for cs, y in rows:
            ps = [wi * c[y] for wi, c in zip(w, cs)]
            z = sum(ps)
            for j, x in enumerate(ps):
                acc[j] += x / z
        w = [a / len(rows) for a in acc]
    out = {}
    for name, f in (("NGRAM", lambda h: ng.dist(h)), ("MATCHED", lambda h: {v: sum(wi * c[v] for wi, c in zip(w, comps(h))) for v in ng.V})):
        by, worst = defaultdict(lambda: [0, 0]), 0.0
        for task, kind, prompt, ans, depth in tests:
            p = f(prompt.split())
            worst = max(worst, abs(sum(p.values()) - 1))
            by[f"{kind} d{depth}"][0] += max(p, key=p.get) == ans
            by[f"{kind} d{depth}"][1] += 1
        out[name] = (" | ".join(f"{k} {v[0] / v[1]:.3f}" for k, v in sorted(by.items())), worst)
    print(f"{d}: budget {budget} entries (v3's knowledge), composite keys hold {keys.entries}; weights "
          + " ".join(f"{x:.2f}" for x in w))
    for name, (line, worst) in out.items():
        print(f"  {name}: {line} (gate worst |sum - 1| {worst:.1e})")


if __name__ == "__main__":
    for d in sys.argv[1:]:
        main(d)
