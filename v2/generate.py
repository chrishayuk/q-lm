"""Generate stories from the scored Q-LM mixture (v2 + composite keys + story
components), with no gradient anywhere.

The model is built and its mixture weights fitted by running v2/composite.py
itself, with the same arguments, so what is sampled is what is scored. The
5-gram's distribution comes from `qlm knserve`, the model `knprobs` scores.
Every component gives a full distribution over the vocabulary and END,
checked to sum to 1 at every step.

    python3 -I v2/generate.py DIR N [composite.py options] --stories K --sentences S --seed R [--top-p P]
"""
import math, os, subprocess, sys

import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]


def take(flag, default, cast):
    if flag in args:
        i = args.index(flag)
        v = cast(args[i + 1])
        del args[i:i + 2]
        return v
    return default


K = take("--stories", 3, int)
S = take("--sentences", "learned", str)  # a number, or "learned": stop by the training stories' length hazard
SEED = take("--seed", 1, int)
TOP_P = take("--top-p", 1.0, float)
OPENING = take("--opening", "once upon a time", str)
CHECK = "--check" in args
if CHECK:
    args.remove("--check")
sys.argv = ["composite.py"] + args
sys.path.insert(0, here)
g = {"__name__": "generate", "__file__": os.path.join(here, "composite.py")}
exec(compile(open(os.path.join(here, "composite.py")).read(), "composite.py", "exec"), g)
core, V, END, wid = g["core"], g["V"], g["END"], g["wid"]
vocab = core.vocab
inv = {i: w for w, i in wid.items()}
inv[END] = "END"
classes, models, W, bucket, START = g["classes"], g["models"], g["W"], g["bucket"], g["START"]
D_ = g["D_"]
kn = subprocess.Popen([os.path.join(here, "..", "target", "release", "qlm"), "knserve", g["a"].dir, str(g["a"].n), "5"],
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
order_ix = np.array([wid[w] for w in [x for x in open(f"{g['a'].dir}/vocab.txt").read().split() if x != "END"]] + [END])


def kn_dist(sent):
    kn.stdin.write(" ".join(inv[x] for x in sent) + "\n")
    kn.stdin.flush()
    row = np.array(list(map(float, kn.stdout.readline().split())))
    out = np.zeros(V + 1)
    out[order_ix] = row
    return out


def class_dist(cm, sent):
    hist = [cm.START_C, cm.START_C] + [cm.hard[w] for w in sent]
    pc = np.array([cm.p_tri(c, hist[-2], hist[-1]) for c in range(cm.C)] + [cm.p_tri(cm.UNK_C, hist[-2], hist[-1]), cm.p_tri(cm.END_C, hist[-2], hist[-1])])
    return pc @ cm.Pw


def key_dist(m, sent):
    U = (np.array([m.uni.get(w, 0) for w in range(V + 1)]) + 0.01) / (m.N + 0.01 * (V + 1))
    t = len(sent)
    v = sent[-1] if t else START
    if v in m.bt:
        tot, nd = m.bt[v]
        p = D_ * nd / tot * U
        for w, c in m.bi[v].items():
            p[w] += max(c - D_, 0) / tot
    else:
        p = U
    key = g["key_of"](m.tmpl, sent + [0], t) if m.tmpl else None
    if key is None or key not in m.ct:
        return p
    tot, nd = m.ct[key]
    q = D_ * nd / tot * p
    for w, c in m.c[key].items():
        q[w] += max(c - D_, 0) / tot
    return q


def story_dist(m, prev):
    U = np.array([m.base.p_uni(w) for w in range(V + 1)])
    if isinstance(m, g["StoryDist"]):
        d = m.dist(prev)
        out = d["__rest__"] * U
        for w, x in d.items():
            if w != "__rest__":
                out[w] = x
        return out
    # StoryCache (B3's components), the same formula as its probs_ctx
    if m.decay < 1.0:
        wt = np.zeros(V + 1)
        L = len(prev)
        for k, x in enumerate(prev):
            wt[x] += m.decay ** (L - 1 - k)
    else:
        wt = np.bincount(np.array(prev, dtype=int), minlength=V + 1).astype(float) if prev else np.zeros(V + 1)
    p = (wt + m.BETA * U) / (wt.sum() + m.BETA)
    for o in range(2, m.order + 1):
        if len(prev) < o - 1:
            break
        hist = tuple(prev[-(o - 1):])
        nxt = np.zeros(V + 1)
        for k in range(len(prev) - o + 1):
            if tuple(prev[k:k + o - 1]) == hist:
                nxt[prev[k + o - 1]] += 1
        p = (nxt + m.BETA * p) / (nxt.sum() + m.BETA)
    return p


if CHECK:
    # Parity: for real development sentences, each component's scorer probability of the
    # observed word must equal the generator's full distribution at that word.
    worst = {}
    names = ["5-gram"] + [f"class{j}" for j in range(len(classes))] + [type(m).__name__ + (str(getattr(m, "tmpl", "")) if not getattr(m, "story", False) else f"({getattr(m, 'order', '')},{getattr(m, 'decay', '')})") for m in models]
    dev = g["dev"]
    for i in __import__("random").Random(11).sample(range(1000, 3000), 30):
        s_ = dev[i]
        sc = [g["kn"][i]] + [cm.probs(s_) for cm in classes] + [m.probs_ctx(s_, i) if getattr(m, "story", False) else m.probs(s_) for m in models]
        ids = [wid[w] for w in s_] + [END]
        ctx = models[0].context(i) if False else None
        story_ctx = next((m.context(i) for m in models if getattr(m, "story", False)), [])
        for t in range(len(ids)):
            sent = ids[:t]
            comps = [kn_dist(sent)] + [class_dist(cm, sent) for cm in classes]
            for m in models:
                comps.append(story_dist(m, story_ctx + sent) if getattr(m, "story", False) else key_dist(m, sent))
            for j, c in enumerate(comps):
                ref = sc[j][t]
                if ref > 1e-11:
                    worst[names[j]] = max(worst.get(names[j], 0.0), abs(c[ids[t]] - ref) / ref)
    for n_, v in worst.items():
        print(f"parity {n_}: worst relative difference {v:.1e}")
    bad = {n_: v for n_, v in worst.items() if v > 1e-6}
    print("PARITY OK" if not bad else f"PARITY FAILED: {bad}")
    sys.exit(0 if not bad else 1)
# Learned story termination: after sentence k, stop with the probability a training story
# of at least k sentences has exactly k (story ids of the n training sentences).
import collections as _c
_all = [int(x) for x in open(f"{g['a'].dir}/train.txt.story")]
_ids = _all[: g["a"].n]
_per = _c.Counter(_ids)
if g["a"].n < len(_all) and _all[g["a"].n] == _ids[-1]:
    del _per[_ids[-1]]  # the last story is cut off by the corpus cutoff: its length is not observed
_len = _c.Counter(_per.values())
_ge = lambda k: sum(c for L, c in _len.items() if L >= k)
HAZARD = {k: _len.get(k, 0) / _ge(k) for k in range(1, max(_len) + 1) if _ge(k)}
rng = np.random.default_rng(SEED)
print(f"# Q-LM stories: {' '.join(sys.argv[1:])}; seed {SEED}; top-p {TOP_P}; opening '{OPENING}'")
for k in range(K):
    story, ctx = [], []
    for si in range(40 if S == "learned" else int(S)):
        sent = [wid[w] for w in OPENING.split()] if si == 0 else []
        while len(sent) < 40:
            comps = [kn_dist(sent)] + [class_dist(cm, sent) for cm in classes]
            for m in models:
                comps.append(story_dist(m, ctx + sent) if getattr(m, "story", False) else key_dist(m, sent))
            for c in comps:
                assert abs(c.sum() - 1) < 1e-6, f"a component does not sum to 1 ({c.sum()})"
            p = sum(w * c for w, c in zip(W[bucket(len(sent))], comps))
            p = p / p.sum()
            if TOP_P < 1.0:
                order = np.argsort(-p)
                keep = order[: np.searchsorted(np.cumsum(p[order]), TOP_P) + 1]
                q = np.zeros_like(p)
                q[keep] = p[keep]
                p = q / q.sum()
            w = int(rng.choice(len(p), p=p))
            if w == END:
                break
            sent.append(w)
        story.append(" ".join(inv[x] for x in sent))
        ctx = ctx + sent + [END]
        if S == "learned" and rng.random() < HAZARD.get(si + 1, 1.0):
            break
    print(f"\n## story {k + 1}\n")
    print(" ".join(story))
kn.stdin.close()
