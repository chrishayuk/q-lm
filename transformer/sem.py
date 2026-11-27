"""LARQL-QLM-SEM-001: does a fact have a state of its own, apart from its
wording? See docs/larql-qlm-sem-001-plan.md, with its three amendments.

    python3 transformer/sem.py data-sem1 llama-20004-s1
    python3 transformer/sem.py data-sem1-v3 transformer-20004-s1   # v3 adds born

Interventions are made at block outputs (the residual stream after a
block). The last block's output, read straight by the output head, is the
positive control: transfer there is automatic.
"""
import math
import os
import random
import sys

import torch
import torch.nn.functional as F

DIR, NAME = sys.argv[1], sys.argv[2]
torch.set_grad_enabled(False)
vocab = ["<PAD>", "<S>", "END"] + [w for w in open(f"{DIR}/vocab.txt").read().split() if w != "END"]
ix = {w: i for i, w in enumerate(vocab)}
types = {l.split("\t")[0]: l.rstrip("\n").split("\t")[1].split() for l in open(f"{DIR}/types.tsv")}
CITIES, COUNTRIES, CONTS = types["city"], types["country"], types["continent"]
capital, continent, lives, born = {}, {}, {}, {}
for l in open(f"{DIR}/world.txt"):
    w = l.split()
    if len(w) == 5 and w[1] == "capital":
        capital[w[0]], continent[w[0]] = w[2], w[4]
    elif len(w) == 5 and w[1] == "lives":
        lives[w[0]] = w[2]
    elif len(w) == 3 and w[1] == "born":
        born[w[0]] = w[2]
tests = [l.rstrip("\n").split("\t") for l in open(f"{DIR}/tests.tsv")]
held_phr = sorted({t[1].split()[3] for t in tests if t[0] == "phrasing"})
fit_c = [c for c in COUNTRIES if c not in held_phr]  # the 18 fitting countries
residents = {}
for p, k in lives.items():
    residents.setdefault(k, []).append(p)


def load(trained):
    if NAME.startswith("llama"):
        from transformers import AutoConfig, AutoModelForCausalLM

        torch.manual_seed(1)
        hf = (AutoModelForCausalLM.from_pretrained(f"{DIR}/{NAME}") if trained else AutoModelForCausalLM.from_config(AutoConfig.from_pretrained(f"{DIR}/{NAME}"))).eval()
        return (lambda ids: hf(input_ids=ids).logits), list(hf.model.layers), hf.lm_head.weight
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
    return m.eval(), list(m.blocks), m.out.weight


fwd, layers, head = load(True)
L = len(layers)
first = lambda o: o[0] if isinstance(o, tuple) else o


def ids_of(prompt):
    return torch.tensor([[1] + [ix[w] for w in prompt.split()]])


def run(prompt, patch=None):
    """Logits at the last position, and the state at every block output for
    every position. patch = (block, position, fn(state) -> new state)."""
    got = []

    def hook(k):
        def f(mod, i, o):
            t = first(o)
            if patch is not None and patch[0] == k:
                t = t.clone()
                t[0, patch[1]] = patch[2](t[0, patch[1]])
                got.append(t[0].clone())
                return (t,) + tuple(o[1:]) if isinstance(o, tuple) else t
            got.append(t[0].clone())

        return f

    hs = [l.register_forward_hook(hook(k)) for k, l in enumerate(layers)]
    logits = fwd(ids_of(prompt))[0, -1].double()
    for h in hs:
        h.remove()
    logits[0] = logits[1] = -math.inf
    return F.log_softmax(logits, -1), got


def top(lp, names):
    return max(names, key=lambda w: lp[ix[w]].item())


# Prompts.
W1 = {c: f"{c} has capital" for c in COUNTRIES}
W2 = {c: f"the capital of {c} is" for c in COUNTRIES}
R1 = {c: f"{c} is in" for c in COUNTRIES}  # continent, wording 1
R2 = {c: f"{c} lies on" for c in COUNTRIES}  # continent, wording 2
LIV = {p: f"{p} lives in" for p in lives}
BRN = {p: f"{p} was born in" for p in born}
BRN2 = {p: f"{p} is a native of" for p in born}
LIV2 = {p: f"{p} is from" for p in lives}

cache = {}


def state(prompt):
    if prompt not in cache:
        cache[prompt] = run(prompt)
    return cache[prompt]


# The learned-facts gate (third amendment).
ok = lambda prompt, ans, names: top(state(prompt)[0], names) == ans
gate_c = [c for c in COUNTRIES if ok(W1[c], capital[c], CITIES) and (c in held_phr or ok(W2[c], capital[c], CITIES))]
gate_r = [c for c in gate_c if ok(R1[c], continent[c], CONTS)]
gate_p = [p for p in lives if ok(LIV[p], lives[p], CITIES)]
print(f"## {DIR} {NAME}\n")
print(f"Admitted by the learned-facts gate: {len(gate_c)} of 24 countries (capital), {len(gate_r)} with continent too, {len(gate_p)} of {len(lives)} people (lives in)." + (f" Born in: {sum(ok(BRN[p], born[p], CITIES) for p in born)} of {len(born)}." if born else "") + "\n")


def centred(vs):
    m = torch.stack(vs).mean(0)
    return [v - m for v in vs]


# 1. Convergence, at each block output, last position, centred over all prompts used.
print("**1. Convergence** (cosine, centred, last position)\n")
print("| block | same fact, two wordings (seen) | same fact, two wordings (held-out phrasing) | different facts, same wording | different facts, different wordings | same answer, different relation (capital / lives in) |")
print("|---:|---:|---:|---:|---:|---:|")
for b in range(L):
    S = {}
    for d in (W1, W2):
        for c in COUNTRIES:
            S[d[c]] = state(d[c])[1][b][-1]
    for p in lives:
        S[LIV[p]] = state(LIV[p])[1][b][-1]
    keys = list(S)
    vals = centred([S[k] for k in keys])
    C = dict(zip(keys, vals))
    cos = lambda a, b2: F.cosine_similarity(C[a], C[b2], 0).item()
    mean = lambda xs: sum(xs) / len(xs) if xs else float("nan")
    seen = [c for c in COUNTRIES if c not in held_phr]
    same_seen = mean([cos(W1[c], W2[c]) for c in seen])
    same_held = mean([cos(W1[c], W2[c]) for c in held_phr])
    diff_same = mean([cos(W1[a], W1[c]) for a in COUNTRIES for c in COUNTRIES if a < c])
    diff_diff = mean([cos(W1[a], W2[c]) for a in COUNTRIES for c in COUNTRIES if a != c])
    same_ans = mean([cos(W1[c], LIV[p]) for c in COUNTRIES for p in residents.get(capital[c], [])])
    print(f"| {b + 1} | {same_seen:.3f} | {same_held:.3f} | {diff_same:.3f} | {diff_diff:.3f} | {same_ans:.3f} |")

# 2. Probe from state to the answer's output-embedding row: fitted on the 18
# fitting countries in wording 1, tested on the 6 held-out-phrasing countries.
print("\n**2. Probe to the answer's output embedding** (fitted on 18 countries, wording 1; tested on the other 6 by the nearest city)\n")
print("| block | held-out 6, wording 1 | held-out 6, wording 2 | untrained model, wording 2 |")
print("|---:|---:|---:|---:|")
def probe_acc(states_fit, states_test, answers_test):
    Hc = F.normalize(head[[ix[k] for k in CITIES]].float(), dim=1)
    X = torch.stack(states_fit)
    Y = torch.stack([head[ix[capital[c]]].float() for c in fit_c])
    mu = X.mean(0)
    A = torch.linalg.solve((X - mu).T @ (X - mu) + 1.0 * torch.eye(X.shape[1]), (X - mu).T @ Y)
    hit = 0
    for s, ans in zip(states_test, answers_test):
        y = F.normalize(((s - mu) @ A)[None], dim=1)
        hit += CITIES[(y @ Hc.T).argmax().item()] == ans
    return hit / len(answers_test)


untrained = load(False)
for b in range(L):
    fit = [state(W1[c])[1][b][-1] for c in fit_c]
    a1 = probe_acc(fit, [state(W1[c])[1][b][-1] for c in held_phr], [capital[c] for c in held_phr])
    a2 = probe_acc(fit, [state(W2[c])[1][b][-1] for c in held_phr], [capital[c] for c in held_phr])
    fwd_t, layers_t, head_t = fwd, layers, head
    fwd, layers, head = untrained
    cache_t = dict(cache)
    cache.clear()
    fitu = [state(W1[c])[1][b][-1] for c in fit_c]
    au = probe_acc(fitu, [state(W2[c])[1][b][-1] for c in held_phr], [capital[c] for c in held_phr])
    fwd, layers, head = fwd_t, layers_t, head_t
    cache.clear()
    cache.update(cache_t)
    print(f"| {b + 1} | {a1:.2f} | {a2:.2f} | {au:.2f} |")


def matched_random(delta, seed):
    g = torch.Generator().manual_seed(seed)
    r = torch.randn(delta.shape, generator=g)
    return r / r.norm() * delta.norm()


# 3. Transplants into "the capital of C' is", last position.
print("\n**3. Full-state transplant** into `the capital of C' is` (last position): share of pairs where the donor country's capital becomes the top city; mean change in log2 P(K) − log2 P(K')\n")
print("| block | same wording | other wording (`C has capital`) | other relation (`C is in`) | same answer (`P lives in`, P in C's capital) | random, magnitude-matched |")
print("|---:|---:|---:|---:|---:|---:|")
rng = random.Random(1)
pairs = [(c, c2) for c in gate_c for c2 in gate_c if c != c2 and c2 not in held_phr]
pairs = rng.sample(pairs, min(len(pairs), 120))
for b in range(L):
    cells = []
    for kind in ("same", "other", "relation", "answer", "random"):
        hit, delta_sum, n = 0, 0.0, 0
        for c, c2 in pairs:
            k, k2 = capital[c], capital[c2]
            rec = W2[c2]
            h = state(rec)[1][b][-1]
            if kind == "same":
                d = state(W2[c])[1][b][-1]
            elif kind == "other":
                d = state(W1[c])[1][b][-1]
            elif kind == "relation":
                d = state(R1[c])[1][b][-1]
            elif kind == "answer":
                if not residents.get(k):
                    continue
                d = state(LIV[residents[k][0]])[1][b][-1]
            else:
                d = h + matched_random(state(W1[c])[1][b][-1] - h, hash((c, c2, b)) % 10**6)
            pos = len(rec.split())  # last position (after <S>)
            lp, _ = run(rec, (b, pos, lambda s, d=d: d))
            base = state(rec)[0]
            hit += top(lp, CITIES) == k
            delta_sum += ((lp[ix[k]] - lp[ix[k2]]) - (base[ix[k]] - base[ix[k2]])).item() / math.log(2)
            n += 1
        cells.append(f"{hit / n:.2f} ({delta_sum / n:+.1f})")
    print(f"| {b + 1}{' (positive control)' if b == L - 1 else ''} | " + " | ".join(cells) + " |")

# 3b. At the country's own position in "the capital of C' is" (index 4: <S> the capital of C').
print("\n**3b. Entity transplant at the country's position** in `the capital of C' is`, from `the capital of C is`: share where C's capital becomes the top city\n")
print("| block | share | random, magnitude-matched |")
print("|---:|---:|---:|")
for b in range(L):
    hit = hr = 0
    for c, c2 in pairs:
        rec = W2[c2]
        d = state(W2[c])[1][b][4]
        h = state(rec)[1][b][4]
        hit += top(run(rec, (b, 4, lambda s, d=d: d))[0], CITIES) == capital[c]
        r = h + matched_random(d - h, hash((c, c2, b, 4)) % 10**6)
        hr += top(run(rec, (b, 4, lambda s, r=r: r))[0], CITIES) == capital[c]
    print(f"| {b + 1} | {hit / len(pairs):.2f} | {hr / len(pairs):.2f} |")

# 4. The held-out phrasings: own fact from wording 1 into wording 2.
print("\n**4. Held-out phrasings**: `the capital of C is` for the 6, unintervened and with its last state from `C has capital`\n")
base_acc = sum(ok(W2[c], capital[c], CITIES) for c in held_phr) / len(held_phr)
print(f"Unintervened accuracy on the 6: {base_acc:.2f}\n")
print("| block | with wording 1's state |")
print("|---:|---:|")
for b in range(L):
    hit = 0
    for c in held_phr:
        d = state(W1[c])[1][b][-1]
        hit += top(run(W2[c], (b, len(W2[c].split()), lambda s, d=d: d))[0], CITIES) == capital[c]
    print(f"| {b + 1} | {hit / len(held_phr):.2f} |")


# Partial transplants (amendments): subspaces fitted on wording 2, measured
# on wording 1, for the held-out 6.
def basis(vectors, k):
    X = torch.stack(vectors)
    X = X - X.mean(0)
    U, S, V = torch.linalg.svd(X, full_matrices=False)
    return V[:k]


def span(rows):
    Q, _ = torch.linalg.qr(torch.stack(rows).T)
    return Q  # columns orthonormal


print("\n**5. Partial transplants** (subspaces fitted on wording 2 over the 18; measured on wording 1 for the held-out 6 that pass the gate)\n")
test6 = [c for c in held_phr if c in gate_r]
print(f"Held-out countries passing the gate (capital and continent): {len(test6)}\n")
print("| block | relation only, `C is in` into `C has capital`: continent wins | random, same dimension and magnitude | entity only, `C2 has capital` into `C has capital`: C2's capital wins | random |")
print("|---:|---:|---:|---:|---:|")
for b in range(L):
    diffs = [state(R2[c])[1][b][-1] - state(W2[c])[1][b][-1] for c in fit_c]
    mean_d = torch.stack(diffs).mean(0)
    Rb = span([mean_d] + list(basis(diffs, 3)))
    means = [(state(W2[c])[1][b][-1] + state(R2[c])[1][b][-1]) / 2 for c in fit_c]
    Eb = span(list(basis(means, 10)))
    proj = lambda Q, v: Q @ (Q.T @ v)
    rel = relr = ent = entr = 0
    for c in test6:
        h = state(W1[c])[1][b][-1]
        dvec = proj(Rb, state(R1[c])[1][b][-1] - h)
        lp = run(W1[c], (b, len(W1[c].split()), lambda s, v=dvec: s + v))[0]
        rel += top(lp, CONTS + CITIES) == continent[c]
        g = torch.Generator().manual_seed(b * 100 + len(c))
        Qr = torch.linalg.qr(torch.randn(h.shape[0], Rb.shape[1], generator=g))[0]
        rv = proj(Qr, torch.randn(h.shape[0], generator=g))
        rv = rv / rv.norm() * dvec.norm()
        relr += top(run(W1[c], (b, len(W1[c].split()), lambda s, v=rv: s + v))[0], CONTS + CITIES) == continent[c]
        c2 = rng.choice([x for x in gate_c if x != c])
        evec = proj(Eb, state(W1[c2])[1][b][-1] - h)
        ent += top(run(W1[c], (b, len(W1[c].split()), lambda s, v=evec: s + v))[0], CITIES) == capital[c2]
        Qe = torch.linalg.qr(torch.randn(h.shape[0], Eb.shape[1], generator=g))[0]
        ev = proj(Qe, torch.randn(h.shape[0], generator=g))
        ev = ev / ev.norm() * evec.norm()
        entr += top(run(W1[c], (b, len(W1[c].split()), lambda s, v=ev: s + v))[0], CITIES) == capital[c2]
    n = max(len(test6), 1)
    print(f"| {b + 1}{' (positive control)' if b == L - 1 else ''} | {rel}/{n} | {relr}/{n} | {ent}/{n} | {entr}/{n} |")

if born:
    # Version 3: same-type relation swap (born against lives) and the
    # recombined query, fitted on three quarters of the admitted people
    # (wording 2: `is a native of` against `is from`), tested on the rest
    # (wording 1: `was born in` against `lives in`).
    gp = [p for p in gate_p if ok(BRN[p], born[p], CITIES)]
    rng2 = random.Random(2)
    rng2.shuffle(gp)
    cut = (3 * len(gp)) // 4
    fit_p, test_p = gp[:cut], gp[cut:]
    print(f"\n**6. Version 3: born against lives** (admitted people: {len(gp)}; fitted on {len(fit_p)}, tested on {len(test_p)})\n")
    print("| block | relation only, `P was born in` into `P lives in`: birth city wins | random | recombined: A's entity, B's relation: A's birth city wins | B's birth city wins (injection) | A's home city wins (no effect) | random |")
    print("|---:|---:|---:|---:|---:|---:|---:|")
    for b in range(L):
        diffs = [state(BRN2[p])[1][b][-1] - state(LIV2[p])[1][b][-1] for p in fit_p]
        Rb = span([torch.stack(diffs).mean(0)] + list(basis(diffs, 3)))
        proj = lambda Q, v: Q @ (Q.T @ v)
        rel = relr = comp = inj = none = rnd = 0
        npairs = 0
        for a in test_p:
            h = state(LIV[a])[1][b][-1]
            dv = proj(Rb, state(BRN[a])[1][b][-1] - h)
            rel += top(run(LIV[a], (b, len(LIV[a].split()), lambda s, v=dv: s + v))[0], CITIES) == born[a]
            g = torch.Generator().manual_seed(b * 1000 + len(a))
            Qr = torch.linalg.qr(torch.randn(h.shape[0], Rb.shape[1], generator=g))[0]
            rv = proj(Qr, torch.randn(h.shape[0], generator=g))
            rv = rv / rv.norm() * dv.norm()
            relr += top(run(LIV[a], (b, len(LIV[a].split()), lambda s, v=rv: s + v))[0], CITIES) == born[a]
            for bb in [x for x in gp if x != a and born[x] not in (born[a], lives[a])][:5]:
                dv2 = proj(Rb, state(BRN[bb])[1][b][-1] - state(LIV[bb])[1][b][-1])
                t = top(run(LIV[a], (b, len(LIV[a].split()), lambda s, v=dv2: s + v))[0], CITIES)
                comp += t == born[a]
                inj += t == born[bb]
                none += t == lives[a]
                rv2 = proj(Qr, torch.randn(h.shape[0], generator=g))
                rv2 = rv2 / rv2.norm() * dv2.norm()
                rnd += top(run(LIV[a], (b, len(LIV[a].split()), lambda s, v=rv2: s + v))[0], CITIES) == born[a]
                npairs += 1
        n = max(len(test_p), 1)
        m = max(npairs, 1)
        print(f"| {b + 1}{' (positive control)' if b == L - 1 else ''} | {rel}/{n} | {relr}/{n} | {comp}/{m} | {inj}/{m} | {none}/{m} | {rnd}/{m} |")
print()
