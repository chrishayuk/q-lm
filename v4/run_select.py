"""Select working-graph passes on training stories (no development data).

    python3 -I v4/run_select.py DIR N TRAIN_STORIES HELD_STORIES MAX_PASSES [frozen]
The sample: the first TRAIN_STORIES stories of the first 90% of the N training
sentences, for counting; the first HELD_STORIES stories of the last 10%, for
selection. Both fixed, the same for every candidate.
"""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v2"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, wgraph

d, n, nt, nh, P = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
frozen = len(sys.argv) > 6 and sys.argv[6] == "frozen"
core.setup(d, n)
hard, C, _ = core.learn(np.arange(core.V), 256, 1)
cls = lambda w: int(hard[w]) if w < len(hard) else -1
ids = [int(x) for x in open(f"{d}/train.txt.story")][:n]
cut = int(0.9 * n)
fit_st = wgraph.stories_of(core.enc[:cut], ids[:cut])[:nt]
held_st = wgraph.stories_of(core.enc[cut:], ids[cut:])[1:nh + 1]  # the first may be cut by the split
N = sum(len(s) + 1 for s in core.enc)
uni = np.bincount([w for s in core.enc for w in s + [core.END]], minlength=core.V + 1)
p_uni = lambda w: (uni[w] + 0.01) / (N + 0.01 * (core.V + 1))
t0 = time.time()
print(f"{d} n={n}: counting on {len(fit_st)} stories, selecting on {len(held_st)} held-out training stories, up to {P} passes{' (frozen)' if frozen else ''}")
ops, lifts = wgraph.select(fit_st, held_st, cls, core.END, p_uni, P, frozen=frozen)
print(f"selected: {ops}; {time.time() - t0:.0f}s")
