"""LARQL-QLM-GROUP-001: does a trained transformer group words by category,
keep their identity, and represent their role, layer by layer? See
docs/larql-qlm-group-001-plan.md.

    python3 transformer/group.py data-right llama-36000-s1
    python3 transformer/group.py data-right transformer-36000-s1

Reads DIR/roles.txt (`qlm roles DIR`). Prints one table per model: the
trained model and the same architecture untrained (seed 1).
"""
import math
import os
import random
import sys

import torch
import torch.nn.functional as F

DIR, NAME = sys.argv[1], sys.argv[2]
torch.set_grad_enabled(False)
torch.manual_seed(1)
random.seed(1)
vocab = ["<PAD>", "<S>", "END"] + [w for w in open(f"{DIR}/vocab.txt").read().split() if w != "END"]
ix = {w: i for i, w in enumerate(vocab)}
sents = []
for line in open(f"{DIR}/roles.txt"):
    toks = [t.split(" ") for t in line.rstrip("\n").split("\t")]
    sents.append([(w, c, int(sl), int(d)) for w, c, sl, d in toks])
cls_of = {w: c for s in sents for w, c, _, _ in s}


def load(trained):
    """(forward(ids) -> logits, layers: list of modules whose output is the
    residual stream after each block, embed(ids) -> layer-0 states)."""
    if NAME.startswith("llama"):
        from transformers import AutoConfig, AutoModelForCausalLM

        if trained:
            hf = AutoModelForCausalLM.from_pretrained(f"{DIR}/{NAME}").eval()
        else:
            torch.manual_seed(1)
            hf = AutoModelForCausalLM.from_config(AutoConfig.from_pretrained(f"{DIR}/{NAME}")).eval()
        return (lambda ids: hf(input_ids=ids).logits), list(hf.model.layers), (lambda ids: hf.model.embed_tokens(ids))
    keep = sys.argv[:]
    sys.argv = [sys.argv[0], DIR, "100", "0", "1"]
    src = open(os.path.join(os.path.dirname(__file__), "train.py")).read()
    g = {}
    exec(compile(src[: src.index("model = Model()")], "train.py", "exec"), g)
    sys.argv = keep
    torch.manual_seed(1)
    m = g["Model"]()
    if trained:
        m.load_state_dict(torch.load(f"{DIR}/{NAME}.pt"))
    m.eval()
    return m, list(m.blocks), (lambda ids: m.tok(ids) + m.pos(torch.arange(ids.shape[1])))


def states(fwd, layers, embed):
    """Per layer (0 = embedding), per sentence: tensor (tokens, width) at
    the word positions (after <S>)."""
    out = [[] for _ in range(len(layers) + 1)]
    caught = []
    hooks = [l.register_forward_hook(lambda mod, i, o: caught.append(o[0] if isinstance(o, tuple) else o)) for l in layers]
    for s in sents:
        ids = torch.tensor([[1] + [ix[w] for w, *_ in s]])
        caught.clear()
        fwd(ids)
        out[0].append(embed(ids)[0, 1:].float())
        for k, h in enumerate(caught):
            out[k + 1].append(h[0, 1:].float())
    for h in hooks:
        h.remove()
    return out


def probe(X, y, Xt, yt, steps=300):
    """Accuracy of a softmax probe trained on (X, y), tested on (Xt, yt)."""
    labels = sorted(set(y) | set(yt))
    m = {l: i for i, l in enumerate(labels)}
    yi, yti = torch.tensor([m[v] for v in y]), torch.tensor([m[v] for v in yt])
    mu, sd = X.mean(0), X.std(0) + 1e-6
    X, Xt = (X - mu) / sd, (Xt - mu) / sd
    W = torch.zeros(X.shape[1], len(labels), requires_grad=True)
    b = torch.zeros(len(labels), requires_grad=True)
    opt = torch.optim.Adam([W, b], lr=0.05)
    with torch.enable_grad():
        for _ in range(steps):
            opt.zero_grad()
            loss = F.cross_entropy(X @ W + b, yi) + 1e-3 * (W**2).sum()
            loss.backward()
            opt.step()
    return ((Xt @ W + b).argmax(1) == yti).float().mean().item()


half = len(sents) // 2


def gather(layer_states, pick):
    """Features and labels from the tokens `pick(token) -> label or None`,
    split into the first half of the sentences (train) and the rest (test)."""
    X, y, Xt, yt = [], [], [], []
    for si, s in enumerate(sents):
        for ti, tok in enumerate(s):
            lab = pick(tok, ti, s)
            if lab is None:
                continue
            (X if si < half else Xt).append(layer_states[si][ti])
            (y if si < half else yt).append(lab)
    return torch.stack(X), y, torch.stack(Xt), yt


def ari(a, b):
    """Adjusted Rand index of two labellings."""
    from collections import Counter

    n = len(a)
    c2 = lambda x: x * (x - 1) / 2
    pairs = Counter(zip(a, b))
    sa, sb = Counter(a), Counter(b)
    idx = sum(c2(v) for v in pairs.values())
    ea, eb = sum(c2(v) for v in sa.values()), sum(c2(v) for v in sb.values())
    exp = ea * eb / c2(n)
    mx = (ea + eb) / 2
    return (idx - exp) / (mx - exp) if mx != exp else 1.0


def kmeans(X, k, iters=50):
    torch.manual_seed(0)
    C = X[torch.randperm(len(X))[:k]].clone()
    for _ in range(iters):
        a = torch.cdist(X, C).argmin(1)
        C = torch.stack([X[a == j].mean(0) if (a == j).any() else C[j] for j in range(k)])
    return a.tolist()


def substitution(fwd, layers, layer, same_class, pairs=150):
    """Replace the state at one noun position with that of another token
    from another sentence at the same position (a noun at the same slot and
    depth, or, as the control, a token of another class). Returns the mean
    total variation of the following next-token distributions, over word
    classes and over words."""
    classes = sorted(set(cls_of.values()) | {"END"})
    cmat = torch.zeros(len(vocab), len(classes))
    for w, i in ix.items():
        c = "END" if w == "END" else cls_of.get(w)
        if c is not None:
            cmat[i, classes.index(c)] = 1
    rng = random.Random(layer * 7 + same_class)
    tv_c = tv_w = 0.0
    done = 0
    tries = 0
    while done < pairs and tries < 20000:
        tries += 1
        a = rng.randrange(len(sents))
        nouns = [i for i, t in enumerate(sents[a]) if t[1] == "N"]
        if not nouns:
            continue
        i = rng.choice(nouns)
        w, c, sl, d = sents[a][i]
        cand = [
            b for b in range(len(sents))
            if b != a and len(sents[b]) > i and (
                (sents[b][i][1] == "N" and sents[b][i][2] == sl and sents[b][i][3] == d and sents[b][i][0] != w)
                if same_class else sents[b][i][1] not in ("N",))
        ]
        if not cand:
            continue
        b = rng.choice(cand)
        ida = torch.tensor([[1] + [ix[t[0]] for t in sents[a]]])
        idb = torch.tensor([[1] + [ix[t[0]] for t in sents[b]]])
        got = []
        h = layers[layer].register_forward_hook(lambda m, inp, o: got.append((o[0] if isinstance(o, tuple) else o)[0, i + 1].clone()))
        fwd(idb)
        h.remove()
        donor = got[0]

        def swap(m, inp, o):
            t = o[0] if isinstance(o, tuple) else o
            t = t.clone()
            t[0, i + 1] = donor
            return (t,) + tuple(o[1:]) if isinstance(o, tuple) else t

        base = F.softmax(fwd(ida)[0, i + 1 :].double(), -1)
        h = layers[layer].register_forward_hook(swap)
        new = F.softmax(fwd(ida)[0, i + 1 :].double(), -1)
        h.remove()
        tv_w += 0.5 * (base - new).abs().sum(-1).mean().item()
        tv_c += 0.5 * (base @ cmat.double() - new @ cmat.double()).abs().sum(-1).mean().item()
        done += 1
    return tv_c / max(done, 1), tv_w / max(done, 1), done


# Controls independent of the model: position and length alone.
def pos_feats(pick):
    X, y, Xt, yt = [], [], [], []
    for si, s in enumerate(sents):
        for ti, tok in enumerate(s):
            lab = pick(tok, ti, s)
            if lab is None:
                continue
            f = torch.zeros(80)
            f[min(ti, 39)] = 1
            f[40 + min(len(s), 39)] = 1
            (X if si < half else Xt).append(f)
            (y if si < half else yt).append(lab)
    return probe(torch.stack(X), y, torch.stack(Xt), yt)


picks = {
    "class": lambda t, i, s: t[1],
    "noun slot": lambda t, i, s: t[2] if t[1] == "N" else None,
    "noun depth": lambda t, i, s: t[3] if t[1] == "N" else None,
}
print(f"## {DIR} {NAME}\n")
print("Position and length alone: " + ", ".join(f"{k} {pos_feats(p):.3f}" for k, p in picks.items()) + "\n")
for trained in (True, False):
    fwd, layers, embed = load(trained)
    S = states(fwd, layers, embed)
    words_by_class = {}
    for w, c in cls_of.items():
        words_by_class.setdefault(c, []).append(w)
    print(f"**{'trained' if trained else 'untrained (seed 1)'}**\n")
    print("| layer | class | identity within class (N; V) | noun slot | noun depth | words clustered vs true classes (ARI) | within / between class distance | substitution, same class: TV classes / words | other class: TV classes / words |")
    print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for L in range(len(S)):
        acc = {k: probe(*gather(S[L], p)) for k, p in picks.items()}
        ident = []
        for c in ("N", "V"):
            if len(words_by_class.get(c, [])) >= 3:
                ident.append(f"{probe(*gather(S[L], lambda t, i, s, c=c: t[0] if t[1] == c else None)):.3f}")
        # Mean state per word, clustered into as many groups as classes.
        ws = sorted(cls_of)
        means = torch.stack([torch.cat([S[L][si][ti:ti + 1] for si, s in enumerate(sents) for ti, t in enumerate(s) if t[0] == w]).mean(0) for w in ws])
        clusters = kmeans((means - means.mean(0)) / (means.std(0) + 1e-6), len(set(cls_of.values())))
        a = ari(clusters, [cls_of[w] for w in ws])
        # Geometry: mean distance between the mean states of words of one
        # class, over the mean distance between words of different classes.
        Z = (means - means.mean(0)) / (means.std(0) + 1e-6)
        D = torch.cdist(Z, Z)
        same = [D[x, y].item() for x in range(len(ws)) for y in range(x) if cls_of[ws[x]] == cls_of[ws[y]]]
        diff = [D[x, y].item() for x in range(len(ws)) for y in range(x) if cls_of[ws[x]] != cls_of[ws[y]]]
        ratio = (sum(same) / len(same)) / (sum(diff) / len(diff))
        if L > 0:
            sc, sw, n1 = substitution(fwd, layers, L - 1, True)
            oc, ow, n2 = substitution(fwd, layers, L - 1, False)
            sub = f"{sc:.3f} / {sw:.3f} ({n1})", f"{oc:.3f} / {ow:.3f} ({n2})"
        else:
            sub = ("–", "–")
        print(f"| {L} | {acc['class']:.3f} | {'; '.join(ident)} | {acc['noun slot']:.3f} | {acc['noun depth']:.3f} | {a:.2f} | {ratio:.2f} | {sub[0]} | {sub[1]} |")
    print()
