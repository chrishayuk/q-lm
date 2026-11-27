"""QLM-PERF-001: the transformer's cost per next-token distribution, measured
the way `qlm prefix` measures the learned grammar's.

    python3 transformer/bench.py data 10000 1     # data/transformer-10000-s1.pt

The sentences are those `qlm prefix` reads: the first 200 development
sentences and the first 100 deeper sentences with corpus words, every prefix
of each, END included. One CPU thread, one sentence at a time, as the grammar.

Two ways of computing each distribution:
- full: the whole prefix through the model again, as train.py samples;
- cached: one new position, attending to the keys and values kept from the
  positions before it (a KV cache). Checked against full.
"""
import math
import sys
import time

import torch
import torch.nn.functional as F

DIR, N = sys.argv[1], int(sys.argv[2])
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 1
torch.set_num_threads(1)
torch.set_grad_enabled(False)

# The model, as train.py defines it, without its training.
sys.argv = [sys.argv[0], DIR, "100", "0", str(SEED)]
src = open(__file__.replace("bench.py", "train.py")).read()
src = src[: src.index("model = Model()")]
_keep = DIR, N, SEED
exec(compile(src, "train.py", "exec"))
DIR, N, SEED = _keep

model = Model()
model.load_state_dict(torch.load(f"{DIR}/transformer-{N}-s{SEED}.pt"))
model.eval()
params = sum(p.numel() for p in model.parameters())


def full(ids):
    """Log-probabilities of the next token after ids, recomputing everything."""
    logits = model(torch.tensor([ids]))[0, -1]
    logits[PAD] = logits[BOS] = float("-inf")
    return F.log_softmax(logits.double(), -1)


def cached(tok, pos, cache):
    """Log-probabilities of the next token, given one new token at pos."""
    x = model.tok.weight[tok] + model.pos.weight[pos]
    for i, b in enumerate(model.blocks):
        a = b.attn
        h = b.ln1(x)
        q, k, v = F.linear(h, a.in_proj_weight, a.in_proj_bias).chunk(3)
        ks, vs = cache[i]
        ks.append(k)
        vs.append(v)
        K, V = torch.stack(ks), torch.stack(vs)
        hd = D // HEADS
        qh, Kh, Vh = q.view(HEADS, 1, hd), K.view(-1, HEADS, hd).transpose(0, 1), V.view(-1, HEADS, hd).transpose(0, 1)
        w = torch.softmax(qh @ Kh.transpose(1, 2) / math.sqrt(hd), -1)
        o = (w @ Vh).reshape(D)
        x = x + a.out_proj(o)
        x = x + b.mlp(b.ln2(x))
    logits = model.out(model.ln(x))
    logits[PAD] = logits[BOS] = float("-inf")
    return F.log_softmax(logits.double(), -1)


sets = [(held[:200], "development"), (deep_seen[:100], "deeper, corpus words")]
t_full = t_cached = 0.0
count = 0
stray = 0.0
for sentences, label in sets:
    nll, tokens = 0.0, 0
    for s in sentences:
        ids = encode(s)  # <S> w1 ... wn END
        cache = [([], []) for _ in model.blocks]
        for i in range(len(ids) - 1):
            t = time.perf_counter()
            lp_full = full(ids[: i + 1])
            t_full += time.perf_counter() - t
            t = time.perf_counter()
            lp = cached(ids[i], i, cache)
            t_cached += time.perf_counter() - t
            stray = max(stray, (lp.exp() - lp_full.exp()).abs().max().item())
            nll -= lp[ids[i + 1]].item()
            tokens += 1
            count += 1
    print(f"  {label}: {len(sentences)} sentences, {nll / tokens / math.log(2):.4f} bits/token")
print(f"transformer-{N}-s{SEED}: {params} parameters; {count} distributions on one CPU thread")
print(f"  full prefix each time: {1000 * t_full / count:.3f} ms per next-token distribution")
print(f"  with a key-value cache: {1000 * t_cached / count:.3f} ms per next-token distribution")
print(f"  most cached and full probabilities differ: {stray:.1e}")
