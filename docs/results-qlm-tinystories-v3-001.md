# Results: QLM-TINYSTORIES-V3-001, learned computation on TinyStories

Against [qlm-tinystories-v3-001-plan.md](qlm-tinystories-v3-001-plan.md),
revisions 1 and 2. No backpropagation anywhere. Tables in `docs/tables/`:
- ts-v3-001-AB.txt (retrieval arms);
- ts-v3-001-CD.txt (C, D, D0);
- ts-v3-001-bindshuf.txt (capacity controls);
- ts-v3-001-confirm3.txt;
- ts-v3-001-full.txt.

Stories: [stories/](stories/).

## Data

- **The preprocessing is reproduced exactly** (`tools/ts_prep.py`): all
  346,098 training and 13,959 development sentences, line for line.
- **Story boundaries are exact.**
- **confirm3:** TinyStories validation stories 1,000 to 1,999, untouched
  until its single use here.
- **Leakage checks** (`tools/check_story_leak.py`, run on composite.py's own
  code): 200 component-sentence checks, no probability changes when later
  words or sentences change.

## Bits per token (select split, development 1,000 to 2,999)

| arm | 1,000 | 10,000 | 100,000 | 346,098 (all) |
|---|---:|---:|---:|---:|
| A: frozen v2 (5-gram, classes, E's keys, position buckets) | 6.1432 | 4.9595 | 4.0236 | 3.6860 |
| B: + story word cache | 5.7690 | 4.7861 | 3.9458 | |
| B2: + previous-word cache | 5.5475 | 4.6224 | 3.8293 | |
| B3: + trigram and recency caches (strong retrieval) | 5.5301 | 4.6092 | 3.8196 | 3.5143 |
| C: B3 + learned spans | 5.5313 | 4.6099 | 3.8198 | |
| **D: B3 + learned binding (two reads)** | **5.5008** | **4.5897** | **3.8090** | **3.5065** |
| D0: B3 + the same reads, unlearned | 5.5301 | 4.6092 | 3.8196 | |
| D-shuffled: D's pairs, lift values reassigned | 5.5114 | 4.5960 | 3.8155 | |
| D-random: as many pairs, at random (seeds 7, 8, 9) | 5.5288 | 4.6092, 4.6092, 4.6093 | 3.8196 | |

**confirm3 (fresh stories, read once), 100,000 sentences:**

| arm | bits per token |
|---|---:|
| A | 4.4893 |
| B3 | 4.2520 |
| D | **4.2363** |

The fresh stories are harder for every arm; the differences are what
compare.

## Against the criteria

- **Story context helps: passes.** B is below A at every size. Strong
  retrieval is worth 0.61, 0.35, 0.20 and 0.17 bits, shrinking as the
  statistics improve.
- **Computation helps** (C or D below B3 by 0.005 at 10,000 and 100,000,
  confirmed): **passes, for D.**
  - −0.020 at 10,000 and −0.011 at 100,000 (select);
  - −0.016 on confirm3;
  - also −0.029 at 1,000 and −0.008 on the full corpus.
  - C (learned spans) adds nothing beyond B3's phrase caches.
- **Successive computation helps** (D below B3 + D0 by 0.003): **passes.**
  D0, the same two reads with no learned binding, adds nothing at any
  size.

**The capacity controls.**
- **Random pairs** (same number, D's lift values) give nothing, on three
  seeds.
- **D's own pairs with shuffled values** keep part of the gain: 0.019 of
  0.029, 0.013 of 0.020 and 0.004 of 0.011 bits.
- So the gain comes from which word pairs were learned to bind, and, more
  so as data grows, from the learned strengths.

## What the binding learned (10,000 sentences)

It is learned from which earlier words' continuations predict what follows
the current word.
- "she" and "he" bind to names (john, becky, sara; paul, sarah, ted).
- "his" binds to "your" and "my".
- Gender is not separated, and the strongest lifts are dominated by rare
  words: the smoothing (α = 5) is weak.

It is predictive substitutability, not shown to be reference.

## Comparison with transformers: not yet fair

The transformers were trained and scored one sentence at a time.
- At 100,000 sentences: windowed 3.935, full 3.760.
- D's 3.809 is below the windowed transformer and above the full one.
- With story context, which the transformers never had, the comparison
  is not like for like. A story-context transformer is still to be
  trained.

## Generation

`v2/generate.py` samples from exactly the scored mixture.
- **How it is built:**
  - it runs composite.py itself;
  - the 5-gram comes from the new `qlm knserve`, identical to `knprobs`;
  - every component's probability of the observed word matches the
    scorer's, on 30 development sentences (worst relative difference
    3e-16);
  - every step's distribution sums to 1.
- **Story ends** are sampled from the training stories' length hazard,
  excluding a story cut off at the corpus boundary.

Seed 1, "once upon a time", B3 + D:
- **10,000 sentences:** grammatical fragments; a name reused across
  sentences; "once upon a time" restarting about five times; "the end ."
  mid-story.
- **100,000 sentences:** whole clauses grammatical; the opening still
  restarts; a different character in most sentences; no plot.
- Mis-decoded quotes ("â € œ") from the source corpus appear. They are left
  as the model produces them; the corpus fix is a separate, versioned
  experiment.

## Costs

- **Full corpus, D:** learning (classes, keys and binding) 284 s; 0.40 ms
  per token for the added components; peak memory 6.8 GB.
- **Storage:** 18.2 million stored bindings. The 12-bytes-each estimate
  is 219 MB; serialised size is not measured yet.

## What it says

- **One learned computation adds predictive value on natural language
  beyond strong retrieval, and the gain generalises to unseen stories:**
  a read whose address comes from a learned binding, followed by a read of
  what followed the addressed words.
- **The gain is small, 0.008 to 0.029 bits, and shrinks with data.**
- **The generated stories show the limit:** local language without a state
  of the story. That is the motivation for QLM-WORKING-GRAPH-001.
