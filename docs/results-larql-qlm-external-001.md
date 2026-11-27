# Results: LARQL-QLM-EXTERNAL-001, an external graph driven by the model's own state

Reported against [larql-qlm-external-001-plan.md](larql-qlm-external-001-plan.md).
Full tables: [tables/external-001.md](tables/external-001.md). The models
are the 18 version-3 models: Llama and the custom transformer, seeds 1 to
3, worlds 1 to 3. The confirmation worlds 4 to 6 are still training.

**What the provider sees.** Only the residual stream at the answer position:
after block 1 (Llama) or block 2 (custom transformer).

**What it does:**
1. Decodes the relation, by nearest centroid fitted on the other wording.
2. Decodes the entity, by nearest key. Keys come from prompts of a
   *different* relation for each entity, so a key prompt is never the
   query prompt: the provider decodes the relation first, then matches the
   entity against the other relation's keys. (That is the plan's intent;
   its literal key choice for countries would have used the query prompt
   for continent queries.)
3. Looks up the pair in a graph.
4. Injects the answer's vector, made from prompts of another relation, at
   the block-3 (Llama) or block-4 (custom) feed-forward output.

The test set is the held-out quarter: 6 countries and 11 people, 34 prompts
per model.

## Results: means over 9 models (ranges)

| arm | Llama: entity decoded | relation decoded | gives the graph's answer | random gives it | custom: entity | relation | answer | random |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| oracle | 1 | 1 | 0.99 | 0.86 | 1 | 1 | 0.99 | 0.96 |
| A: entity from the state | 0.82 | 1 | 0.86 | 0.86 | 0.43 | 1 | 0.76 | 0.97 |
| B: relation from the state | 1 | 0.93 | 0.92 | 0.81 | 1 | 0.91 | 0.90 | 0.88 |
| C: both | 0.76 (0.56 to 0.91) | 0.93 (0.82 to 1) | 0.81 | 0.85 | 0.40 | 0.91 | 0.74 | 0.97 |
| **D: both, edited graph** | 0.76 | 0.93 | **0.62** (0.44 to 0.76) | **0.00** | 0.40 | 0.91 | 0.12 | 0.00 |
| **E: both, new birth facts** | 0.42 | 1 | **0.42** (0.25 to 0.75) | 0.03 | 0.39 | 1 | 0.33 | 0.00 |
| paraphrase (wording 2, not counted) | 0.78 | 1 | 0.82 | 0.80 | 0.31 | 1 | 0.74 | 0.94 |

**With the provider disabled,** the model gives its own answer: the graph's
answer in arms A to C, and 0 of the edited and new answers.

## Against the plan

| criterion | Llama | custom transformer |
|---|---|---|
| **C works:** entity and relation decoded ≥ 90%, answer ≥ 85%, random < 5% | **fails**: entity 0.76; and the random criterion cannot be met, because the answer is already in the residual stream (as in RESOLVE-001) | fails |
| **D, editing:** edited answer ≥ 75% | **fails**: 0.62, with 0.00 random | fails: 0.12 |
| **E, adding:** new fact in ≥ 3 of 4 | **fails**: 0.42 | fails: 0.33 |

**The random criterion for arms A to C was ill-posed,** the same mistake as
RESOLVE-001's true-table control. Injecting a random vector leaves the
model's own correct answer, so "gives the true graph's answer" cannot
separate the provider from doing nothing. Only arms D and E, whose answers
the model does not hold, can show the provider at work. That is noted
here, and the plan's criteria are kept as written.

## What it shows

- **The relation can be read from the activations.**
  - In Llama after block 1, in 93% of held-out prompts (100% in 5 of the 9
    models).
  - The centroids were fitted on another wording and other entities.
  - The custom transformer after block 2: 91%.
- **The entity is the bottleneck.**
  - Matching the state against keys from another relation finds the right
    entity in 76% of prompts in Llama, and 40% in the custom transformer.
  - Where the entity is right, the rest mostly works:
    - with the true graph, the answer is right whenever it was already
      there;
    - with the edited graph, Llama gives the edited answer in 0.62,
      against 0.76 entity accuracy.
- **Facts can be changed, and added, from outside, with only activations
  as input.**
  - **Changed:** in Llama, with an edited graph, the model states the
    edited answer for 62% of held-out prompts. Its own answer is never the
    edited one, and a random injection gives it 0% of the time.
  - **Added:** for people the model never learned a birth city for, 42% of
    held-out prompts give the graph's birth city. Random gives 3%. These
    are 4 people per world, so this is a small test.

  Both fall short of the plan's thresholds, by about the shortfall in
  entity decoding.
- **Reading later does not help** (exploratory, not in the plan). In Llama
  after block 2, entity decoding falls to 0.53 and edited answers to 0.42.
  In the custom transformer after block 3, edited answers are 0.15. The
  entity is most matchable early in Llama, at block 1.

## What would close the gap

The entity key. Two possibilities, to be planned:
- **Keys from more prompt types,** averaged, or a fitted linear map from
  the answer-position state to the entity. The map would be trained on the
  fitting entities, and so would need a held-out-entity test, which a
  per-entity key avoids.
- **Reading the entity where it is cleanest:** its own position after
  block 1. SEM-001 showed a causal entity state there.

That position is not the answer position. The provider would then read two
positions: still only activations, but more than one place.

## Not shown

- The confirmation worlds 4 to 6. They are training; this experiment is
  rerun on them unchanged.
- Larger models, more relations, real text.
