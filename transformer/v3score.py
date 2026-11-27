"""Score a trained transformer on a v3 world's held-out tests (v3/worlds.py).

The answer is the most probable next token after <S> and the prompt's words,
over the whole vocabulary. Accuracy by test kind and depth.

    .venv-gpt2/bin/python transformer/v3score.py WORLD_DIR MODEL_DIR [...]
"""
import sys
from collections import defaultdict

import torch
from transformers import AutoModelForCausalLM

torch.set_grad_enabled(False)
for d, mdir in zip(sys.argv[1::2], sys.argv[2::2]):
    vocab = ["<PAD>", "<S>", "END"] + [w for w in open(f"{d}/vocab.txt").read().split() if w != "END"]
    ix = {w: i for i, w in enumerate(vocab)}
    m = AutoModelForCausalLM.from_pretrained(mdir).eval()
    by = defaultdict(lambda: [0, 0])
    for line in open(f"{d}/tests.tsv"):
        task, kind, prompt, answer, depth = line.rstrip("\n").split("\t")
        ids = [1] + [ix[w] for w in prompt.split()]
        lg = m(torch.tensor([ids])).logits[0, -1].double()
        lg[0] = lg[1] = -float("inf")
        by[f"{kind} d{depth}"][0] += vocab[int(lg.argmax())] == answer
        by[f"{kind} d{depth}"][1] += 1
    print(f"{mdir}: " + " | ".join(f"{k} {v[0] / v[1]:.3f} (n={v[1]})" for k, v in sorted(by.items())))
