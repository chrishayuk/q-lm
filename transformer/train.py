"""A small decoder-only transformer trained on sentences of the language of
Colmerauer's grammar, given nothing but the sentences and the vocabulary.

    python3 transformer/train.py data 1000 6000 1   # data/train-1000.txt, 6,000 steps, seed 1

Writes, for training size N and seed S:
- data/transformer-N-sS.bits: bits per token (END included) on the development,
  deeper and deeper-with-corpus-words sentences, the most a next-token
  distribution strays from summing to 1, then key=value notes;
- data/transformer-N-sS.samples: 300 sampled sentences, one per line;
- data/transformer-N-sS.curve: "step bits" on 2,000 development sentences,
  every 250 steps.
`qlm report data` reads and judges them. PAD and the start token are never
predicted: their logits are removed before every probability.
"""
import math
import random
import sys
import time

import torch
import torch.nn as nn
import torch.nn.functional as F

DIR, N = sys.argv[1], int(sys.argv[2])
STEPS = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 1
BATCH = 64
D, LAYERS, HEADS = 128, 4, 4
MAX_LEN = 256
SAMPLES = 300

random.seed(SEED)
torch.manual_seed(SEED)
device = "mps" if torch.backends.mps.is_available() else "cpu"


def read(path):
    with open(path) as f:
        return [line.rstrip("\n").split("\t")[-1].split() for line in f if line.strip()]


vocab = ["<PAD>", "<S>", "END"] + [w for w in open(f"{DIR}/vocab.txt").read().split() if w != "END"]
index = {w: i for i, w in enumerate(vocab)}
PAD, BOS, EOS = 0, 1, 2

train_all = read(f"{DIR}/train-{N}.txt")
held = read(f"{DIR}/dev.txt")  # development sentences
deep = read(f"{DIR}/deep.txt")
deep_seen = read(f"{DIR}/deep-seen.txt")
curve_set = held[:2000]

# A tenth of the training sentences (at least ten) choose when to stop.
random.shuffle(train_all)
k = max(10, len(train_all) // 10) if len(train_all) > 20 else 0
valid, train = (train_all[:k], train_all[k:]) if k else (train_all, train_all)


def encode(s):
    return [BOS] + [index[w] for w in s] + [EOS]


class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(D), nn.LayerNorm(D)
        self.attn = nn.MultiheadAttention(D, HEADS, batch_first=True)
        self.mlp = nn.Sequential(nn.Linear(D, 4 * D), nn.GELU(), nn.Linear(4 * D, D))

    def forward(self, x, mask):
        h = self.ln1(x)
        x = x + self.attn(h, h, h, attn_mask=mask, need_weights=False)[0]
        return x + self.mlp(self.ln2(x))


class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok = nn.Embedding(len(vocab), D)
        self.pos = nn.Embedding(MAX_LEN, D)
        self.blocks = nn.ModuleList(Block() for _ in range(LAYERS))
        self.ln = nn.LayerNorm(D)
        self.out = nn.Linear(D, len(vocab))

    def forward(self, ids):
        t = ids.shape[1]
        mask = torch.triu(torch.full((t, t), float("-inf"), device=ids.device), 1)
        x = self.tok(ids) + self.pos(torch.arange(t, device=ids.device))
        for b in self.blocks:
            x = b(x, mask)
        return self.out(self.ln(x))


def batches(sentences, size, shuffle):
    order = list(range(len(sentences)))
    if shuffle:
        random.shuffle(order)
    for i in range(0, len(order), size):
        seqs = [encode(sentences[j]) for j in order[i : i + size]]
        L = max(len(s) for s in seqs)
        ids = torch.tensor([s + [PAD] * (L - len(s)) for s in seqs], device=device)
        yield ids[:, :-1], ids[:, 1:]


def predict(model, x):
    """Logits over the tokens that can follow: never PAD or the start."""
    logits = model(x)
    logits[..., PAD] = float("-inf")
    logits[..., BOS] = float("-inf")
    return logits


def bits_per_token(model, sentences):
    model.eval()
    total, tokens = 0.0, 0
    with torch.no_grad():
        for x, y in batches(sentences, 256, False):
            logits = predict(model, x)
            nll = F.cross_entropy(logits.reshape(-1, len(vocab)), y.reshape(-1), ignore_index=PAD, reduction="sum")
            total += nll.item()
            tokens += (y != PAD).sum().item()
    model.train()
    return total / tokens / math.log(2)


model = Model().to(device)
params = sum(p.numel() for p in model.parameters())
opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1)
start = time.time()
best, best_state, step = float("inf"), None, 0
curve = []
while step < STEPS:
    for x, y in batches(train, BATCH, True):
        loss = F.cross_entropy(model(x).reshape(-1, len(vocab)), y.reshape(-1), ignore_index=PAD)
        opt.zero_grad()
        loss.backward()
        opt.step()
        step += 1
        if step % 250 == 0:
            curve.append((step, bits_per_token(model, curve_set)))
        if step % 200 == 0 or step == STEPS:
            v = bits_per_token(model, valid)
            if v < best:
                best, best_state = v, {k: t.detach().clone() for k, t in model.state_dict().items()}
        if step >= STEPS:
            break
secs = time.time() - start
model.load_state_dict(best_state)

h, d, ds = bits_per_token(model, held), bits_per_token(model, deep), bits_per_token(model, deep_seen)

# How far each next-token distribution strays from summing to 1, over the
# prefixes of 50 held-out and 50 deeper sentences.
model.eval()
worst = 0.0
with torch.no_grad():
    for x, _ in batches(held[:50] + deep[:50], 100, False):
        z = F.softmax(predict(model, x).float().cpu().double(), -1).sum(-1)
        worst = max(worst, (z - 1).abs().max().item())

gen = torch.Generator(device="cpu").manual_seed(SEED)
model.eval()
samples = []
with torch.no_grad():
    for _ in range(SAMPLES):
        ids = [BOS]
        while len(ids) < 200:
            logits = predict(model, torch.tensor([ids], device=device))[0, -1].float().cpu()
            nxt = torch.multinomial(F.softmax(logits, -1), 1, generator=gen).item()
            if nxt == EOS:
                break
            ids.append(nxt)
        samples.append(" ".join(vocab[i] for i in ids[1:]))

name = f"{DIR}/transformer-{N}-s{SEED}"
with open(f"{name}.bits", "w") as f:
    f.write(f"{h} {d} {ds} {worst} params={params} steps={STEPS} seed={SEED} train_secs={secs:.0f} device={device}\n")
with open(f"{name}.samples", "w") as f:
    f.write("\n".join(samples) + "\n")
with open(f"{name}.curve", "w") as f:
    f.write("".join(f"{s} {b}\n" for s, b in curve))
print(f"{name}: held {h:.4f} deeper {d:.4f} deeper-seen {ds:.4f} bits/token; {params} parameters; {secs:.0f} s on {device}")
