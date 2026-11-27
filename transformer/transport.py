"""LARQL-QLM-TRANSPORT-001: which operation, and which heads, carry the entity
from its position to the answer position? See
docs/larql-qlm-transport-001-plan.md.

    python3 transformer/transport.py data-sem1 transformer-20004-s1
    python3 transformer/transport.py data-sem1 llama-20004-s1

Recipient `the capital of C' is`, donor `the capital of C is`; the country
is position 4 (after <S>), the last position 5.
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
CITIES, COUNTRIES = types["city"], types["country"]
capital = {}
for l in open(f"{DIR}/world.txt"):
    w = l.split()
    if len(w) == 5 and w[1] == "capital":
        capital[w[0]] = w[2]
CPOS, LPOS = 4, 5
prompt = lambda c: torch.tensor([[1] + [ix[w] for w in f"the capital of {c} is".split()]])


class Custom:
    """The custom transformer, run explicitly so that every head's output can
    be read and replaced. Checked against the module's own forward."""

    def __init__(self, trained):
        keep = sys.argv[:]
        sys.argv = [sys.argv[0], DIR, "100", "0", "1"]
        src = open(os.path.join(os.path.dirname(__file__), "train.py")).read()
        g = {}
        exec(compile(src[: src.index("model = Model()")], "train.py", "exec"), g)
        sys.argv = keep
        torch.manual_seed(1)
        self.m = g["Model"]()
        if trained:
            self.m.load_state_dict(torch.load(f"{DIR}/{NAME}.pt"))
        self.m.eval()
        self.H = g["HEADS"]
        self.D = g["D"]
        self.blocks = len(self.m.blocks)
        self.unembed = self.m.out.weight

    def run(self, ids, edits=()):
        m, H, D = self.m, self.H, self.D
        hd = D // H
        T = ids.shape[1]
        x = m.tok(ids)[0] + m.pos(torch.arange(T))
        rec = {"in": [], "mid": [], "out": [], "z": [], "A": [], "Wo": []}
        mask = torch.triu(torch.full((T, T), float("-inf")), 1)
        for b, blk in enumerate(m.blocks):
            for k, bb, p, v in [e for e in edits if e[0] == "in" and e[1] == b]:
                x = x.clone(); x[p] = v
            rec["in"].append(x.clone())
            a = blk.attn
            h = blk.ln1(x)
            q, k_, v_ = F.linear(h, a.in_proj_weight, a.in_proj_bias).chunk(3, -1)
            q, k_, v_ = (t.view(T, H, hd).transpose(0, 1) for t in (q, k_, v_))
            A = torch.softmax(q @ k_.transpose(1, 2) / math.sqrt(hd) + mask, -1)
            z = A @ v_  # (H, T, hd)
            for e in [e for e in edits if e[0] == "z" and e[1] == b]:
                z = z.clone(); z[e[2], e[3]] = e[4]
            rec["z"].append(z.clone()); rec["A"].append(A)
            attn_out = a.out_proj(z.transpose(0, 1).reshape(T, D))
            x = x + attn_out
            for k, bb, p, v in [e for e in edits if e[0] == "mid" and e[1] == b]:
                x = x.clone(); x[p] = v
            rec["mid"].append(x.clone())
            f = blk.mlp(blk.ln2(x))
            for e in [e for e in edits if e[0] == "ffn" and e[1] == b]:
                f = f.clone(); f[e[2]] = e[3]
            rec.setdefault("ffn", []).append(f.clone())
            x = x + f
            for k, bb, p, v in [e for e in edits if e[0] == "out" and e[1] == b]:
                x = x.clone(); x[p] = v
            rec["out"].append(x.clone())
        logits = m.out(m.ln(x))[-1].double()
        return logits, rec

    def head_out(self, b, h, zvec):
        """A head's contribution to the residual stream, from its z."""
        a = self.m.blocks[b].attn
        hd = self.D // self.H
        return a.out_proj.weight[:, h * hd:(h + 1) * hd] @ zvec


class Llama:
    def __init__(self, trained):
        from transformers import AutoConfig, AutoModelForCausalLM

        torch.manual_seed(1)
        if trained:
            self.hf = AutoModelForCausalLM.from_pretrained(f"{DIR}/{NAME}", attn_implementation="eager").eval()
        else:
            self.hf = AutoModelForCausalLM.from_config(AutoConfig.from_pretrained(f"{DIR}/{NAME}"), attn_implementation="eager").eval()
        c = self.hf.config
        self.H, self.D, self.blocks = c.num_attention_heads, c.hidden_size, c.num_hidden_layers
        self.unembed = self.hf.lm_head.weight

    def run(self, ids, edits=()):
        rec = {"in": [], "mid": [], "out": [], "z": [], "A": [], "Wo": []}
        hooks = []
        H, D = self.H, self.D
        hd = D // H
        for b, layer in enumerate(self.hf.model.layers):
            def pre(mod, args, kwargs, b=b):
                x = (args[0] if args else kwargs["hidden_states"]).clone()
                for e in edits:
                    if e[0] == "in" and e[1] == b:
                        x[0, e[2]] = e[3]
                rec["in"].append(x[0].clone())
                if args:
                    return (x,) + tuple(args[1:]), kwargs
                kwargs["hidden_states"] = x
                return args, kwargs

            def zpre(mod, args, b=b):
                z = args[0].clone()  # (1, T, H*hd)
                for e in edits:
                    if e[0] == "z" and e[1] == b:
                        z[0, e[3], e[2] * hd:(e[2] + 1) * hd] = e[4]
                rec["z"].append(z[0].view(z.shape[1], H, hd).transpose(0, 1).clone())
                return (z,)

            def attn_hook(mod, i, o, b=b):
                out = o[0].clone()
                rec["A"].append(o[1][0] if o[1] is not None else None)
                for e in edits:
                    if e[0] == "mid" and e[1] == b:
                        out[0, e[2]] = e[3] - rec["in"][b][e[2]]
                rec["mid"].append(rec["in"][b] + out[0])
                return (out,) + tuple(o[1:])

            def post(mod, i, o, b=b):
                t = (o[0] if isinstance(o, tuple) else o).clone()
                for e in edits:
                    if e[0] == "out" and e[1] == b:
                        t[0, e[2]] = e[3]
                rec["out"].append(t[0].clone())
                return (t,) + tuple(o[1:]) if isinstance(o, tuple) else t

            def mlp_hook(mod, i, o, b=b):
                t = o.clone()
                for e in edits:
                    if e[0] == "ffn" and e[1] == b:
                        t[0, e[2]] = e[3]
                rec.setdefault("ffn", []).append(t[0].clone())
                return t

            hooks += [
                layer.mlp.register_forward_hook(mlp_hook),
                layer.register_forward_pre_hook(pre, with_kwargs=True),
                layer.self_attn.o_proj.register_forward_pre_hook(zpre),
                layer.self_attn.register_forward_hook(attn_hook),
                layer.register_forward_hook(post),
            ]
        logits = self.hf(input_ids=ids, output_attentions=True).logits[0, -1].double()
        for h in hooks:
            h.remove()
        return logits, rec

    def head_out(self, b, h, zvec):
        hd = self.D // self.H
        return self.hf.model.layers[b].self_attn.o_proj.weight[:, h * hd:(h + 1) * hd] @ zvec


if os.environ.get("TRANSPORT_CLASSES_ONLY") == "1":
    raise SystemExit
M = Llama(True) if NAME.startswith("llama") else Custom(True)
if isinstance(M, Custom):
    ref = M.m(prompt(COUNTRIES[0]))[0, -1].double()
    got = M.run(prompt(COUNTRIES[0]))[0]
    assert (ref - got).abs().max().item() < 1e-4, "the explicit forward does not match the module"


def top_city(logits):
    return max(CITIES, key=lambda w: logits[ix[w]].item())


cache = {c: M.run(prompt(c)) for c in COUNTRIES}
rng = random.Random(1)
pairs = rng.sample([(c, c2) for c in COUNTRIES for c2 in COUNTRIES if c != c2], 120)


# Heads are chosen on the first half of the pairs and judged on the second.
select, judge = pairs[:60], pairs[60:]


def share(make_edits, on=None):
    on = pairs if on is None else on
    return sum(top_city(M.run(prompt(c2), make_edits(c, c2))[0]) == capital[c] for c, c2 in on) / len(on)


def rand_like(delta, seed):
    g = torch.Generator().manual_seed(seed)
    r = torch.randn(delta.shape, generator=g)
    return r / r.norm() * delta.norm()


print(f"## {DIR} {NAME}\n")
same = sum(top_city(M.run(prompt(c), [("in", 0, CPOS, cache[c][1]["in"][0][CPOS])])[0]) == capital[c] for c in COUNTRIES)
print(f"Machinery check: patching a prompt with its own state leaves the answer: {same} of 24.\n")

print("**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)\n")
print("| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |")
print("|---:|---:|---:|---:|---:|")
for b in range(M.blocks):
    row = []
    for point in ("in", "mid", "out"):
        row.append(share(lambda c, c2, point=point: [(point, b, CPOS, cache[c][1][point][b][CPOS])]))
    rr = share(lambda c, c2: [("in", b, CPOS, cache[c2][1]["in"][b][CPOS] + rand_like(cache[c][1]["in"][b][CPOS] - cache[c2][1]["in"][b][CPOS], hash((c, c2, b)) % 10**6))])
    print(f"| {b + 1} | {row[0]:.2f} | {row[1]:.2f} | {row[2]:.2f} | {rr:.2f} |")

print("\n**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)\n")
print("| block | " + " | ".join(f"head {h}" for h in range(M.H)) + " |")
print("|---:|" + "---:|" * M.H)
scores = {}
for b in range(M.blocks):
    cells = []
    for h in range(M.H):
        s = share(lambda c, c2: [("z", b, h, LPOS, cache[c][1]["z"][b][h, LPOS])], select)
        A = cache[COUNTRIES[0]][1]["A"][b]
        w = sum(cache[c][1]["A"][b][h, LPOS, CPOS].item() for c in COUNTRIES) / len(COUNTRIES) if A is not None else float("nan")
        scores[(b, h)] = s
        cells.append(f"{s:.2f} (w {w:.2f})")
    print(f"| {b + 1} | " + " | ".join(cells) + " |")
best = sorted(scores, key=lambda k: -scores[k])[:3]
together = share(lambda c, c2: [("z", b, h, LPOS, cache[c][1]["z"][b][h, LPOS]) for b, h in best], judge)
rheads = random.Random(7).sample([k for k in scores if k not in best], 3)
rtogether = share(lambda c, c2: [("z", b, h, LPOS, cache[c][1]["z"][b][h, LPOS]) for b, h in rheads], judge)
print(f"\nTop three heads {[(b + 1, h) for b, h in best]} patched together: {together:.2f}. Three other heads {[(b + 1, h) for b, h in rheads]}: {rtogether:.2f}.\n")

# Interactions: every nonempty subset of the three heads, on the judged
# pairs: the share where the donor's capital wins, and the mean change in
# log2 P(K) − log2 P(K').
from itertools import combinations


def effect(heads):
    hit, d = 0, 0.0
    for c, c2 in judge:
        lp = M.run(prompt(c2), [("z", b, h, LPOS, cache[c][1]["z"][b][h, LPOS]) for b, h in heads])[0]
        base = cache[c2][0]
        k, k2 = ix[capital[c]], ix[capital[c2]]
        hit += top_city(lp) == capital[c]
        d += ((F.log_softmax(lp, -1)[k] - F.log_softmax(lp, -1)[k2]) - (F.log_softmax(base, -1)[k] - F.log_softmax(base, -1)[k2])).item() / math.log(2)
    return hit / len(judge), d / len(judge)


print("**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)\n")
print("| heads | share | change, bits |")
print("|---|---:|---:|")
eff = {}
for r in (1, 2, 3):
    for sub in combinations(best, r):
        eff[sub] = effect(sub)
        print(f"| {', '.join(f'({b + 1},{h})' for b, h in sub)} | {eff[sub][0]:.2f} | {eff[sub][1]:+.2f} |")
singles = sum(eff[(x,)][1] for x in best)
print(f"\nSum of the single heads' changes: {singles:+.2f} bits; all three together: {eff[tuple(best)][1]:+.2f} bits.\n")

print("**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns\n")
rest = sum(top_city(M.run(prompt(c), [("z", b, h, LPOS, cache[c2][1]["z"][b][h, LPOS]) for b, h in best])[0]) == capital[c2] for c, c2 in judge) / len(judge)
rrest = sum(top_city(M.run(prompt(c), [("z", b, h, LPOS, cache[c2][1]["z"][b][h, LPOS]) for b, h in rheads])[0]) == capital[c2] for c, c2 in judge) / len(judge)
print(f"Top heads restored: {rest:.2f}. Other heads restored: {rrest:.2f}.\n")

print("**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)\n")
print("| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |")
print("|---|---:|---:|---:|---:|")
U = M.unembed


def lens(vec, names, answer):
    return max(names, key=lambda w: (U[ix[w]] @ vec).item()) == answer


for (b, h), (rb, rh) in zip(best, rheads):
    ce = ca = rce = rca = 0
    for c in COUNTRIES:
        v = M.head_out(b, h, cache[c][1]["z"][b][h, LPOS])
        ce += lens(v, COUNTRIES, c)
        ca += lens(v, CITIES, capital[c])
        rv = M.head_out(rb, rh, cache[c][1]["z"][rb][rh, LPOS])
        rce += lens(rv, COUNTRIES, c)
        rca += lens(rv, CITIES, capital[c])
    print(f"| ({b + 1}, {h}) | {ce}/24 | {ca}/24 | {rce}/24 | {rca}/24 |")
print()
