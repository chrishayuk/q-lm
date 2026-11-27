"""LARQL-QLM-RESOLVE-001: does the late feed-forward at the answer position
retrieve the fact, and can an external table stand in for it? See
docs/larql-qlm-resolve-001-plan.md.

    python3 transformer/resolve.py data-sem1-v3 llama-20004-s1
"""
import math
import os
import random
import sys

import torch
import torch.nn.functional as F

os.environ["TRANSPORT_CLASSES_ONLY"] = "1"
here = os.path.dirname(os.path.abspath(__file__))
g = {"__name__": "transport", "__file__": os.path.join(here, "transport.py")}
try:
    exec(compile(open(os.path.join(here, "transport.py")).read(), "transport.py", "exec"), g)
except SystemExit:
    pass
DIR, NAME, ix, CITIES, COUNTRIES, capital, prompt = (g[k] for k in ("DIR", "NAME", "ix", "CITIES", "COUNTRIES", "capital", "prompt"))
LLAMA = NAME.startswith("llama")
M = g["Llama"](True) if LLAMA else g["Custom"](True)
LPOS = 5
if LLAMA:
    hf = M.hf
    lens = lambda x: hf.lm_head(hf.model.norm(x))
    ffn_of = lambda b, x: hf.model.layers[b].mlp(hf.model.layers[b].post_attention_layernorm(x))
else:
    lens = lambda x: M.m.out(M.m.ln(x))
    ffn_of = lambda b, x: M.m.blocks[b].mlp(M.m.blocks[b].ln2(x))
top_city = lambda lg: max(CITIES, key=lambda w: lg[ix[w]].item())
lives = {}
for l in open(f"{DIR}/world.txt"):
    w = l.split()
    if len(w) == 5 and w[1] == "lives":
        lives[w[0]] = w[2]
residents = {}
for p, k in lives.items():
    residents.setdefault(k, []).append(p)
cache = {c: M.run(prompt(c)) for c in COUNTRIES}
live_ids = lambda p: torch.tensor([[1] + [ix[w] for w in f"{p} lives in".split()]])
pcache = {p: M.run(live_ids(p)) for p in lives}
base_acc = sum(top_city(cache[c][0]) == capital[c] for c in COUNTRIES) / 24


def rand_like(v, seed):
    gen = torch.Generator().manual_seed(seed)
    r = torch.randn(v.shape, generator=gen)
    return r / r.norm() * v.norm()


U = M.unembed[[ix[k] for k in CITIES]].float()
Qc, _ = torch.linalg.qr(U.T)  # orthonormal basis of the 24 city directions
Qr, _ = torch.linalg.qr(torch.randn(U.shape[1], U.shape[0], generator=torch.Generator().manual_seed(5)))
proj_out = lambda Q, x: x - Q @ (Q.T @ x)

print(f"## {DIR} {NAME}\n")
print(f"Unintervened accuracy on `the capital of C is`: {base_acc:.2f}\n")
blocks = [M.blocks - 2, M.blocks - 1] if LLAMA else [M.blocks - 1]
head_alone = lambda v: M.unembed.float() @ v  # an output read alone, without the norm
print("**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)\n")
print("| block | before attention | after attention | after the feed-forward |")
print("|---:|---:|---:|---:|")
for b in range(M.blocks):
    row = [sum(top_city(lens(cache[c][1][k][b][LPOS])) == capital[c] for c in COUNTRIES) / 24 for k in ("in", "mid", "out")]
    print(f"| {b + 1} | {row[0]:.2f} | {row[1]:.2f} | {row[2]:.2f} |")
print("\n**A. Retrieval or amplification** (answer position)\n")
print("| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |")
print("|---:|---:|---:|---:|---:|---:|")
for b in blocks:
    mean5 = torch.stack([cache[c][1]["ffn"][b][LPOS] for c in COUNTRIES]).mean(0)
    mean2 = torch.stack([cache[c][1]["ffn"][b][2] for c in COUNTRIES]).mean(0)
    rem = sum(top_city(M.run(prompt(c), [("ffn", b, LPOS, mean5)])[0]) == capital[c] for c in COUNTRIES) / 24
    rem2 = sum(top_city(M.run(prompt(c), [("ffn", b, 2, mean2)])[0]) == capital[c] for c in COUNTRIES) / 24
    alone = free = rnd = 0
    for c in COUNTRIES:
        x = cache[c][1]["mid"][b][LPOS]
        alone += top_city(head_alone(cache[c][1]["ffn"][b][LPOS])) == capital[c]
        free += top_city(head_alone(ffn_of(b, proj_out(Qc, x)))) == capital[c]
        rnd += top_city(head_alone(ffn_of(b, proj_out(Qr, x)))) == capital[c]
    print(f"| {b + 1} | {rem:.2f} | {rem2:.2f} | {alone / 24:.2f} | {free / 24:.2f} | {rnd / 24:.2f} |")

# B. The answer vector of a city: the mean block-b feed-forward output at the
# answer position of `P lives in`, over the residents of that city. Other
# relation, other subject: never the capital prompt.
rng = random.Random(4)
perm = COUNTRIES[:]
while True:
    rng.shuffle(perm)
    edited = {c: capital[p] for c, p in zip(COUNTRIES, perm)}
    if all(edited[c] != capital[c] for c in COUNTRIES):
        break
print("\n**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)\n")
print("| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |")
print("|---:|---:|---:|---:|---:|---:|---:|")
for b in range(M.blocks):
    avec = {k: torch.stack([pcache[p][1]["ffn"][b][-1] for p in residents[k]]).mean(0) for k in CITIES if k in residents}
    true = ed = rc = rv = ceil = rved = 0
    for i, c in enumerate(COUNTRIES):
        k, kstar = capital[c], edited[c]
        true += top_city(M.run(prompt(c), [("ffn", b, LPOS, avec[k])])[0]) == k
        ed += top_city(M.run(prompt(c), [("ffn", b, LPOS, avec[kstar])])[0]) == kstar
        kr = CITIES[(i * 7 + 3) % 24]
        rc += top_city(M.run(prompt(c), [("ffn", b, LPOS, avec[kr])])[0]) == kr
        own = cache[c][1]["ffn"][b][LPOS]
        rl = M.run(prompt(c), [("ffn", b, LPOS, rand_like(avec[kstar], i))])[0]
        rv += top_city(rl) == k
        rved += top_city(rl) == kstar
        # The plan's leave-one-out ceiling cannot be built: every city is the
        # capital of exactly one country. The prompt's own output is reported
        # instead, a trivial upper bound.
        ceil += top_city(M.run(prompt(c), [("ffn", b, LPOS, own)])[0]) == k
    print(f"| {b + 1}{' (last)' if b == M.blocks - 1 else ''} | {true / 24:.2f} | {ed / 24:.2f} | {rved / 24:.2f} | {rv / 24:.2f} | {rc / 24:.2f} | {ceil / 24:.2f} |")
print()
