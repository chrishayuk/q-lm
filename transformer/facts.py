"""QLM-SEMANTIC-001: the fact tests (DIR/tests.tsv) for a trained model, scored
as `qlm facts` scores the grammar: the answer's rank among its type, bits on
it, and contrast (log2 of its probability over the mean of its type's false
answers), every probability floored at 0.999 model + 0.001 uniform.

    python3 transformer/facts.py data-sem1 transformer-20004-s1   # custom model (.pt)
    python3 transformer/facts.py data-sem1 llama-20004-s1         # Hugging Face dir
"""
import math
import os
import sys
from collections import defaultdict

import torch
import torch.nn.functional as F

DIR, NAME = sys.argv[1], sys.argv[2]
torch.set_grad_enabled(False)
vocab = ["<PAD>", "<S>", "END"] + [w for w in open(f"{DIR}/vocab.txt").read().split() if w != "END"]
ix = {w: i for i, w in enumerate(vocab)}
types = {l.split("\t")[0]: l.rstrip("\n").split("\t")[1].split() for l in open(f"{DIR}/types.tsv")}
tests = [l.rstrip("\n").split("\t") for l in open(f"{DIR}/tests.tsv")]

if os.path.isdir(f"{DIR}/{NAME}"):
    from transformers import AutoModelForCausalLM

    hf = AutoModelForCausalLM.from_pretrained(f"{DIR}/{NAME}").eval()
    model = lambda ids: hf(input_ids=ids).logits
else:
    keep = sys.argv[:]
    sys.argv = [sys.argv[0], DIR, "100", "0", "1"]
    src = open(os.path.join(os.path.dirname(__file__), "train.py")).read()
    g = {}
    exec(compile(src[: src.index("model = Model()")], "train.py", "exec"), g)
    sys.argv = keep
    m = g["Model"]()
    m.load_state_dict(torch.load(f"{DIR}/{NAME}.pt"))
    m.eval()
    model = m

u = 0.001 / (len(vocab) - 2 + 1)  # as `qlm facts`: vocabulary plus END
agg = defaultdict(lambda: [0, 0, 0.0, 0.0])
for test, prefix, answer, kind in tests:
    ids = torch.tensor([[1] + [ix[w] for w in prefix.split()]])
    lg = model(ids)[0, -1].double()
    lg[0] = lg[1] = -math.inf
    q = F.softmax(lg, -1)
    p = lambda w: u + 0.999 * q[ix[w]].item()
    cands = types[kind]
    best = max(cands, key=p)
    false_mean = sum(p(w) for w in cands if w != answer) / (len(cands) - 1)
    a = agg[test]
    a[0] += 1
    a[1] += best == answer
    a[2] -= math.log2(p(answer))
    a[3] += math.log2(p(answer)) - math.log2(false_mean)
for test in sorted(agg):
    n, right, bits, contrast = agg[test]
    print(f"| {NAME} | {test} | {n} | {right} | {100 * right / n:.1f}% | {bits / n:.2f} | {contrast / n:.2f} |")
