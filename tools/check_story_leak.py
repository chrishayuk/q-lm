"""Leakage checks for the story-local components in v2/composite.py, run on
its own code: a component's probability at a position must not change when
(1) later words of the same sentence or (2) later sentences of the story,
or of any story, are changed. And (3) data-ts-c3 must equal data-ts on the
first 11,000 development sentences, so confirm3 (11,000 onward) cannot
reach the fit or select splits.

    python3 -I tools/check_story_leak.py
"""
import random, sys
sys.argv = ["composite.py", "data-ts", "1000", "--arm", "A", "--story", "cache,bicache,tricache,rcache95,rcache99,bind,wg=w:ss+p1:ss"]
import os; os.environ.setdefault("WG_STORIES", "40")
sys.path.insert(0, "v2")
src = open("v2/composite.py").read()
src = src[: src.index("# Admission gate")]
g = {"__name__": "check", "__file__": "v2/composite.py"}
exec(compile(src, "composite.py", "exec"), g)
dev, models, vocab = g["dev"], [m for m in g["models"] if getattr(m, "story", False)], g["core"].vocab
rng = random.Random(3)
checked = 0
for i in rng.sample([i for i in range(1, 3000) if g["STORY"][i] == g["STORY"][i - 1]], 15):
    for m in models:
        base = m.probs_ctx(dev[i], i)
        # (1) later words of this sentence
        t = rng.randrange(len(dev[i]))
        changed = dev[i][: t + 1] + [rng.choice(vocab) for _ in dev[i][t + 1:]]
        assert m.probs_ctx(changed, i)[: t + 1] == base[: t + 1], ("within-sentence future", i, t)  # position k scores word k given words before it
        # (2) every later sentence
        saved = dev[i + 1:]
        dev[i + 1:] = [[rng.choice(vocab) for _ in s] for s in saved]
        assert m.probs_ctx(dev[i], i) == base, ("later sentences", i)
        dev[i + 1:] = saved
        checked += 1
print(f"(1) and (2): {checked} component-sentence checks, no change from future text")
a = open("data-ts/dev.txt").read().splitlines()[:11000]
b = open("data-ts-c3/dev.txt").read().splitlines()[:11000]
sa = open("data-ts/dev.txt.story").read().splitlines()[:11000]
sb = open("data-ts-c3/dev.txt.story").read().splitlines()[:11000]
assert a == b and sa == sb
c3 = set(open("data-ts-c3/dev.txt.story").read().split()[11000:])
assert not c3 & set(open("data-ts/dev.txt.story").read().split()), "confirm3 shares a story with data-ts dev"
print("(3) data-ts-c3 equals data-ts on development 0 to 10,999; confirm3's stories are disjoint from data-ts's development stories")
