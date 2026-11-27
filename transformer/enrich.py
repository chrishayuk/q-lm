"""LARQL-QLM-ENRICH-001: is the fact looked up at the entity's position, by
the feed-forward? See docs/larql-qlm-enrich-001-plan.md.

    python3 transformer/enrich.py data-sem1 transformer-20004-s1      # capitals (v2)
    python3 transformer/enrich.py data-sem1-v3 llama-20004-s1         # adds the reuse test (v3)

Uses the model classes of transport.py. The block is chosen on the first 60
pairs and judged on the other 60.
"""
import math
import os
import random
import sys

import torch
import torch.nn.functional as F

os.environ["TRANSPORT_CLASSES_ONLY"] = "1"
src = open(os.path.join(os.path.dirname(__file__), "transport.py")).read()
g = {"__name__": "transport", "__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "transport.py")}
try:
    exec(compile(src, "transport.py", "exec"), g)
except SystemExit:
    pass
DIR, NAME, ix, CITIES, COUNTRIES, capital, prompt = (g[k] for k in ("DIR", "NAME", "ix", "CITIES", "COUNTRIES", "capital", "prompt"))
M = g["Llama"](True) if NAME.startswith("llama") else g["Custom"](True)
CPOS = 4
top_city = lambda lg: max(CITIES, key=lambda w: lg[ix[w]].item())
cache = {c: M.run(prompt(c)) for c in COUNTRIES}
rng = random.Random(1)
pairs = rng.sample([(c, c2) for c in COUNTRIES for c2 in COUNTRIES if c != c2], 120)
select, judge = pairs[:60], pairs[60:]


def rand_like(delta, seed):
    gen = torch.Generator().manual_seed(seed)
    r = torch.randn(delta.shape, generator=gen)
    return r / r.norm() * delta.norm()


def donor_share(b, on, random_ctrl=False):
    hit = 0
    for c, c2 in on:
        v = cache[c][1]["ffn"][b][CPOS]
        if random_ctrl:
            own = cache[c2][1]["ffn"][b][CPOS]
            v = own + rand_like(v - own, hash((c, c2, b)) % 10**6)
        hit += top_city(M.run(prompt(c2), [("ffn", b, CPOS, v)])[0]) == capital[c]
    return hit / len(on)


print(f"## {DIR} {NAME}\n")
print("**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)\n")
print("| block | chosen-on pairs | judged pairs | random, matched (judged) |")
print("|---:|---:|---:|---:|")
sel = {}
for b in range(M.blocks):
    sel[b] = donor_share(b, select)
    print(f"| {b + 1} | {sel[b]:.2f} | {donor_share(b, judge):.2f} | {donor_share(b, judge, True):.2f} |")
B = max(sel, key=sel.get)
print(f"\nChosen block: {B + 1}.\n")

print("**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital\n")
print("| block | unablated | country position ablated | control: position 2 (`capital`) ablated |")
print("|---:|---:|---:|---:|")
base = sum(top_city(cache[c][0]) == capital[c] for c in COUNTRIES) / 24
for b in range(M.blocks):
    mean_c = torch.stack([cache[c][1]["ffn"][b][CPOS] for c in COUNTRIES]).mean(0)
    mean_2 = torch.stack([cache[c][1]["ffn"][b][2] for c in COUNTRIES]).mean(0)
    a = sum(top_city(M.run(prompt(c), [("ffn", b, CPOS, mean_c)])[0]) == capital[c] for c in COUNTRIES) / 24
    a2 = sum(top_city(M.run(prompt(c), [("ffn", b, 2, mean_2)])[0]) == capital[c] for c in COUNTRIES) / 24
    print(f"| {b + 1} | {base:.2f} | {a:.2f} | {a2:.2f} |")

print("\n**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns\n")
print("| block | restored | random, matched |")
print("|---:|---:|---:|")
for b in range(M.blocks):
    hit = hr = 0
    for c, c2 in judge:  # corrupted prompt: c; clean: c2
        v = cache[c2][1]["ffn"][b][CPOS]
        hit += top_city(M.run(prompt(c), [("ffn", b, CPOS, v)])[0]) == capital[c2]
        own = cache[c][1]["ffn"][b][CPOS]
        hr += top_city(M.run(prompt(c), [("ffn", b, CPOS, own + rand_like(v - own, hash((c2, c, b)) % 10**6))])[0]) == capital[c2]
    print(f"| {b + 1} | {hit / len(judge):.2f} | {hr / len(judge):.2f} |")

# 5. Follow-up, not in the plan: the feed-forward at the last position.
print("\n**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins\n")
print("| block | patched | random, matched |")
print("|---:|---:|---:|")
LPOS = 5
for b in range(M.blocks):
    hit = hr = 0
    for c, c2 in judge:
        v = cache[c][1]["ffn"][b][LPOS]
        own = cache[c2][1]["ffn"][b][LPOS]
        hit += top_city(M.run(prompt(c2), [("ffn", b, LPOS, v)])[0]) == capital[c]
        hr += top_city(M.run(prompt(c2), [("ffn", b, LPOS, own + rand_like(v - own, hash((c, c2, b, 5)) % 10**6))])[0]) == capital[c]
    print(f"| {b + 1} | {hit / len(judge):.2f} | {hr / len(judge):.2f} |")

# 4. Reuse across queries (version 3): one patch at the person's position,
# read under `P lives in` and `P was born in`. Causal attention makes the
# state at P's position the same under both queries.
born, lives = {}, {}
for l in open(f"{DIR}/world.txt"):
    w = l.split()
    if len(w) == 3 and w[1] == "born":
        born[w[0]] = w[2]
    elif len(w) == 5 and w[1] == "lives":
        lives[w[0]] = w[2]
if born:
    q = lambda p, rel: torch.tensor([[1] + [ix[w] for w in f"{p} {rel}".split()]])
    people = [p for p in born if top_city(M.run(q(p, "lives in"))[0]) == lives[p] and top_city(M.run(q(p, "was born in"))[0]) == born[p]]
    rng.shuffle(people)
    ppairs = [(a, b2) for a in people for b2 in people if a != b2 and lives[a] != lives[b2] and born[a] != born[b2]]
    ppairs = random.Random(3).sample(ppairs, min(120, len(ppairs)))
    psel, pjudge = ppairs[:60], ppairs[60:]
    pc = {p: M.run(q(p, "lives in")) for p in people}
    print(f"\n**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. {len(people)} people admitted.\n")
    print("| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |")
    print("|---:|---:|---:|---:|---:|")
    for b in range(M.blocks):
        h1 = h2 = both = rb = 0
        for a, d in pjudge:
            v = pc[d][1]["ffn"][b][1]
            r1 = top_city(M.run(q(a, "lives in"), [("ffn", b, 1, v)])[0]) == lives[d]
            r2 = top_city(M.run(q(a, "was born in"), [("ffn", b, 1, v)])[0]) == born[d]
            h1 += r1; h2 += r2; both += r1 and r2
            own = pc[a][1]["ffn"][b][1]
            rv = own + rand_like(v - own, hash((a, d, b)) % 10**6)
            rb += (top_city(M.run(q(a, "lives in"), [("ffn", b, 1, rv)])[0]) == lives[d]) and (top_city(M.run(q(a, "was born in"), [("ffn", b, 1, rv)])[0]) == born[d])
        n = len(pjudge)
        print(f"| {b + 1} | {h1 / n:.2f} | {h2 / n:.2f} | {both / n:.2f} | {rb / n:.2f} |")
print()
