# Results: QLM-KEY-001, arms C, D and E (composite keys, learned by held-out utility)

Reported against [qlm-key-001-plan.md](qlm-key-001-plan.md). Prototype
`v2/composite.py`. Tables:
[tables/key-001-cde-10k.txt](tables/key-001-cde-10k.txt) and
[tables/key-001-cde-100k.txt](tables/key-001-cde-100k.txt).

**The keys.** A key pairs the recent word v with:
- the word d back ("w", d = 2 to 8);
- that word's node ("c");
- or, for "cw", v's node paired with the word d back.

Each key's component is P(next | key), backed off to the bigram. All of
them join the v2 mixture (5-gram + 4 class models).

**Arm E keeps a key by utility:** its held-out gain over the bigram on the
last 10% of the training sentences (counted on the first 90%), minus λ ×
(1/2) log2 N per stored binding, over the N training tokens.

## A correction to the plan's complexity charge

At λ = 1 the charge puts the whole stored table against one pass over the
data: about 4 bits per token at 10,000 sentences, against held-out gains
of at most 0.08. Nothing passes it, not even the 5-gram's own table. So
λ is swept:
- **λ = 0:** held-out gain alone, which already penalises keys that do not
  generalise;
- **λ = 0.01 and 0.001.**

Also, the first version's "cw" key still held v itself, which made it the
same as "w". That was fixed before these runs.

## Results (comparison split, development 1,001 to 3,000)

| training sentences | arm | all | 2–4 | 5+ | keys kept | stored bindings |
|---:|---|---:|---:|---:|---|---:|
| 10,000 | v2 | 4.9740 | 4.9629 | 4.8201 | | |
| 10,000 | C (all w) | 4.9646 | 4.9597 | 4.8052 | w2–w8 | 0.45 M |
| 10,000 | D (all c) | 4.9662 | 4.9591 | 4.8080 | c2–c8 | 0.42 M |
| 10,000 | E, λ = 0 | 4.9650 | 4.9526 | 4.8078 | w2, w3, c2, cw2, cw3 | 0.33 M |
| 100,000 | v2 | 4.0516 | 3.9060 | 3.8305 | | |
| 100,000 | C | 4.0405 | 3.9151 | 3.8065 | w2–w8 | 3.0 M |
| 100,000 | D | 4.0420 | 3.9128 | 3.8109 | c2–c8 | 2.6 M |
| 100,000 | E, λ = 0 or 0.001 | **4.0335** | 3.9117 | **3.7959** | w2–w8, c2–c7, cw2–cw6 | 7.2 M |

**What the held-out gain selects depends on data size.**
- At 10,000 sentences, every key 4 or more words back has negative
  held-out gain, so E keeps only short ones. Long context is not yet worth
  anything, as the windowed transformer showed.
- At 100,000 sentences, keys up to 8 words back (words), 7 (nodes) and 6
  (node and word) have positive held-out gain, and are kept. The gain
  falls with distance:
  - w2 +0.49, w4 +0.20, w6 +0.06, w8 +0.01;
  - c8, cw7 and cw8 are negative, and are dropped.
- The selection is readable. It is the learned "index" the plan asked
  for, and it widens as data grows.

## Against the plan

**Learned addressing helps** if E beats C and D, and a storage-matched
control, by at least 0.02 bits on positions 5+ at 100,000 sentences.

| comparison at positions 5+, 100,000 sentences | difference |
|---|---:|
| E against v2 | −0.035 |
| E against C | −0.011 |
| E against D | −0.015 |

**The criterion fails.**
- E is better than C and D, but by less than 0.02.
- It also stores 2.4 times C's bindings, and the storage-matched control
  was not run.

**What it recovers of the measured long-context value:** 0.035 of the
0.258 bits at positions 5+ that long context is worth to the transformer.
That is about 14%. Overall, E reaches 4.034, against the windowed
transformer's 3.935 and the full one's 3.760.

## What it says

- **Selecting keys by held-out gain works as a learning rule:**
  - it chooses distances and levels;
  - it widens with data;
  - it rejects what does not generalise.
- **But single pairs (recent word, one earlier item) recover little of what
  long context is worth.**
  - Mixed with the 5-gram, most of their individual gain (w2's +0.49 over
    the bigram) is already in the 5-gram.
  - The far keys carry little each.
- **What the transformer's long context does is probably not pairwise.**
  It conditions on several earlier items jointly, and on what they say
  together. The next step in this direction is keys built from a
  retrieved result (arm G): a first lookup's answer becomes part of the
  second key. That is the plan's successive computation.
