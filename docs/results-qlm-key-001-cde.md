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

## Addendum: the storage control, and weights that depend on position

Table: [tables/key-001-controls-100k.txt](tables/key-001-controls-100k.txt).
The comparison split, 100,000 sentences.

**The controls:**
- **Arm R:** E's 18 templates, but each key's earlier item is at a
  pseudo-random distance (2 to t), fixed by the sentence and the position.
  So it has the same templates and more storage (9.7 M bindings against
  7.2 M), but no consistent addressing.
- **Buckets:** the mixture weights fitted separately for each position
  0 to 5, and 6+. That is a simple form of choosing, per context, which
  component to trust. Applied to every arm alike.

| model | stored bindings | all | 2–4 | 5+ |
|---|---:|---:|---:|---:|
| v2 alone | 0 | 4.0516 | 3.9060 | 3.8305 |
| v2 alone, weights by position | 0 | 4.0497 | 3.9074 | 3.8312 |
| E's keys | 7.2 M | 4.0335 | 3.9117 | 3.7959 |
| E's keys, weights by position | 7.2 M | **4.0236** | **3.8936** | **3.7936** |
| random-distance keys (R) | 9.7 M | 4.0445 | 3.8987 | 3.8207 |
| R, weights by position | 9.7 M | 4.0431 | 3.9057 | 3.8208 |

**Addressing, not storage.**
- At positions 5+, E's keys beat random-distance keys by 0.025 bits
  (3.7959 against 3.8207), with a quarter less storage.
- Against this storage control, the plan's 0.02 margin is met.
- Against C and D (all-word and all-node keys), it is not (0.011 and
  0.015, above). So consistent addressing matters a great deal; E's
  selection among consistent addresses adds a little more.

**Weights by position help only once there is something to choose
between:**
- 0.002 for v2 alone;
- 0.010 with the keys, mostly at positions 0 to 4: 2–4 improve by 0.018.

**Where it stands:** 4.024 overall.
- The 5-gram's window, in a transformer: 3.935, 0.089 better.
- The full-context transformer: 3.760, 0.264 better.

## Addendum: arm G, successive factorised lookups

Specified in the plan before running. Step 1: the local class trigram
gives P(c | h). Step 2: P(w | c, x_{t−d}), one component per d = 2 to 8.
No table indexed by (x_{t−1}, x_{t−d}) is stored. 100,000 sentences, with
weights by position.

| model | stored bindings | all | 2–4 | 5+ |
|---|---:|---:|---:|---:|
| v2 alone | 0 | 4.0497 | 3.9074 | 3.8312 |
| **G: successive** | **1.40 M** | 4.0386 | 3.8948 | 3.8177 |
| R: random-distance keys | 9.69 M | 4.0431 | 3.9057 | 3.8208 |
| E's keys (flat, materialised) | 7.24 M | **4.0236** | **3.8936** | **3.7936** |

**The criterion fails both ways.**
- G does not beat E at positions 5+ (3.8177 against 3.7936).
- With 19% of E's bindings, it is 0.015 bits behind overall, against the
  0.005 allowed.

**But it is the more efficient use of storage:**
- G gains 0.011 bits overall from 1.40 M bindings, about 0.008 bits per
  million;
- E gains 0.026 from 7.24 M, about 0.004 per million;
- G beats the random-distance keys while storing a seventh as much.

**What the factorisation gives up.** In G, the distant word chooses
*within* the class the local context predicts. It cannot change which
class comes next, and it cannot interact with the recent word itself. E's
joint (recent word, distant word) keys can do both, at the price of
materialising them. The extra 0.015 bits E gets is the value of that
interaction.

The successive form tested here is the simplest one:
- a hard class as the intermediate result;
- one distant word.

The plan's richer intermediates are not built yet:
- weighted distributions over classes;
- kept bindings: actor, object;
- a second lookup chosen by the first's result.
