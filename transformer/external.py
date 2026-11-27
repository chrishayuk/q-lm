"""LARQL-QLM-EXTERNAL-001: an external graph provider driven only by the
model's own activations. See docs/larql-qlm-external-001-plan.md.

    python3 transformer/external.py data-sem1-v3 llama-20004-s1

The provider sees the residual stream at the answer position after block R
(Llama: 1, custom: 2), decodes the relation (nearest centroid) and the
entity (nearest key, keys from prompts of a different relation), looks the
pair up in a graph, and injects the answer's vector at block J's
feed-forward output (Llama: 3, custom: 4).
"""
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
DIR, NAME, ix, CITIES, COUNTRIES = (g[k] for k in ("DIR", "NAME", "ix", "CITIES", "COUNTRIES"))
CONTS = g["types"]["continent"]
LLAMA = NAME.startswith("llama")
M = g["Llama"](True) if LLAMA else g["Custom"](True)
R, J = (0, 2) if LLAMA else (1, 3)  # block indices: read after R, inject at J
if os.environ.get("READ"):  # exploratory: read after another block (not the plan)
    R = int(os.environ["READ"]) - 1
capital, continent, lives, lives_on, born = {}, {}, {}, {}, {}
for l in open(f"{DIR}/world.txt"):
    w = l.split()
    if len(w) == 5 and w[1] == "capital":
        capital[w[0]], continent[w[0]] = w[2], w[4]
    elif len(w) == 5 and w[1] == "lives":
        lives[w[0]], lives_on[w[0]] = w[2], w[4]
    elif len(w) == 3 and w[1] == "born":
        born[w[0]] = w[2]
tests = [l.rstrip("\n").split("\t") for l in open(f"{DIR}/tests.tsv")]
new_people = sorted({t[1].split()[0] for t in tests if t[0] == "new entity"})
PEOPLE = sorted(lives)

PHR = {  # relation: (wording 1 = test, wording 2 = fitting, entity type, answer type)
    "capital": ("{} has capital", "the capital of {} is", "country", "city"),
    "continent": ("{} is in", "{} lies on", "country", "continent"),
    "home": ("{} lives in", "{} is from", "person", "city"),
    "birth": ("{} was born in", "{} is a native of", "person", "city"),
}
KEYREL = {"capital": "continent", "continent": "capital", "home": "birth", "birth": "home"}
cache = {}


def run(text, edits=()):
    if not edits and text in cache:
        return cache[text]
    out = M.run(torch.tensor([[1] + [ix[w] for w in text.split()]]), list(edits))
    if not edits:
        cache[text] = out
    return out


state = lambda text: run(text)[1]["out"][R][-1]
ffn_out = lambda text: run(text)[1]["ffn"][J][-1]
top_of = lambda logits, names: max(names, key=lambda w: logits[ix[w]].item())
LAST = lambda text: len(text.split())  # position of the last token (after <S>)

# The entities the model knows (learned-facts gate), split into fitting and held out.
known_c = [c for c in COUNTRIES if top_of(run(PHR["capital"][0].format(c))[0], CITIES) == capital[c]]
known_p = [p for p in PEOPLE if p in born and p not in new_people and top_of(run(PHR["home"][0].format(p))[0], CITIES) == lives[p] and top_of(run(PHR["birth"][0].format(p))[0], CITIES) == born[p]]
rng = random.Random(11)
rng.shuffle(known_c)
rng.shuffle(known_p)
fit_c, test_c = known_c[: 3 * len(known_c) // 4], known_c[3 * len(known_c) // 4:]
fit_p, test_p = known_p[: 3 * len(known_p) // 4], known_p[3 * len(known_p) // 4:]

# Relation centroids, from wording 2 over the fitting entities.
centroid = {}
for rel, (w1, w2, et, at) in PHR.items():
    ents = fit_c if et == "country" else fit_p
    centroid[rel] = torch.stack([state(w2.format(e)) for e in ents]).mean(0)


def decode_relation(s):
    return max(centroid, key=lambda r: F.cosine_similarity(s, centroid[r], 0).item())


def decode_entity(s, rel):
    et = PHR[rel][2]
    cands = COUNTRIES if et == "country" else PEOPLE
    keyrel = KEYREL[rel]
    return max(cands, key=lambda e: F.cosine_similarity(s, state(PHR[keyrel][0].format(e)), 0).item())


# Answer vectors at block J, from prompts of another relation than the query's.
def mean_ffn(texts):
    return torch.stack([ffn_out(t) for t in texts]).mean(0)


vec_from_home = {k: mean_ffn([PHR["home"][0].format(p) for p in PEOPLE if lives[p] == k]) for k in CITIES if any(lives[p] == k for p in PEOPLE)}
vec_from_birth = {k: mean_ffn([PHR["birth"][0].format(p) for p in born if born[p] == k and p not in new_people]) for k in CITIES if any(born[p] == k and p not in new_people for p in born)}
vec_cont = {t: mean_ffn([f"{p} lives on" for p in PEOPLE if lives_on[p] == t]) for t in CONTS}


def answer_vector(rel, ans):
    if rel == "continent":
        return vec_cont[ans]
    return (vec_from_birth if rel == "home" else vec_from_home)[ans]


def truth(rel, e):
    return {"capital": capital, "continent": continent, "home": lives, "birth": born}[rel][e]


def derange(keys, values, seed):
    r = random.Random(seed)
    while True:
        v = values[:]
        r.shuffle(v)
        if all(a != b for a, b in zip(values, v)):
            return dict(zip(keys, v))


edited = {
    "capital": derange(COUNTRIES, [capital[c] for c in COUNTRIES], 1),
    "continent": derange(COUNTRIES, [continent[c] for c in COUNTRIES], 2),
    "home": derange(PEOPLE, [lives[p] for p in PEOPLE], 3),
    "birth": derange(sorted(born), [born[p] for p in sorted(born)], 4),
}


def rand_like(v, seed):
    gen = torch.Generator().manual_seed(seed)
    r = torch.randn(v.shape, generator=gen)
    return r / r.norm() * v.norm()


print(f"## {DIR} {NAME}\n")
print(f"Read after block {R + 1}, inject at block {J + 1}. Known entities: {len(known_c)} countries, {len(known_p)} people; held out: {len(test_c)} countries, {len(test_p)} people; {len(new_people)} single-observation people.\n")
items = [(rel, e) for rel in ("capital", "continent") for e in test_c] + [(rel, e) for rel in ("home", "birth") for e in test_p]
print("| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |")
print("|---|---:|---:|---:|---:|---:|")


def evaluate(arm, items, graph, use_entity, use_relation, wording=0):
    ent_ok = rel_ok = hit = rnd = off = 0
    for i, (rel, e) in enumerate(items):
        text = PHR[rel][wording].format(e)
        s = state(text)
        drel = decode_relation(s) if use_relation else rel
        dent = decode_entity(s, drel) if use_entity else e
        rel_ok += drel == rel
        ent_ok += dent == e
        names = CONTS if PHR[rel][3] == "continent" else CITIES
        want = graph(rel, e)
        try:
            got_ans = graph(drel, dent)
            v = answer_vector(drel, got_ans)
        except KeyError:
            v = None
        if v is not None:
            hit += top_of(run(text, [("ffn", J, LAST(text), v)])[0], names) == want
            rnd += top_of(run(text, [("ffn", J, LAST(text), rand_like(v, i))])[0], names) == want
        off += top_of(run(text)[0], names) == want
    n = len(items)
    print(f"| {arm} | {ent_ok / n:.2f} | {rel_ok / n:.2f} | **{hit / n:.2f}** | {rnd / n:.2f} | {off / n:.2f} |")


true_g = truth
edit_g = lambda rel, e: edited[rel][e]
evaluate("oracle (true graph)", items, true_g, False, False)
evaluate("A: entity from the state", items, true_g, True, False)
evaluate("B: relation from the state", items, true_g, False, True)
evaluate("C: both from the state", items, true_g, True, True)
evaluate("D: both from the state, edited graph", items, edit_g, True, True)
evaluate("paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted)", items, true_g, True, True, wording=1)
new_items = [("birth", p) for p in new_people]
evaluate("E: both from the state, new birth facts (single-observation people)", new_items, true_g, True, True)
s0 = state("the")
sims = {r: round(F.cosine_similarity(s0, centroid[r], 0).item(), 2) for r in centroid}
print(f"\nA prompt the provider should not answer (`the`): nearest relation {decode_relation(s0)}; cosine to each centroid {sims}.\n")
