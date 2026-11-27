# Results: LARQL-QLM-RESOLVE-001, where the answer forms, and editing a fact from outside

Reported against [larql-qlm-resolve-001-plan.md](larql-qlm-resolve-001-plan.md).
Full tables: [tables/resolve-001.md](tables/resolve-001.md). The models are
the 18 version-3 models: Llama and the custom transformer, seeds 1 to 3,
three worlds. Prompts: `the capital of C is`, 24 per model. Means over 9
models, with ranges.

**Corrections made to the measures before reporting, after one model of
each showed them to be wrong:**
- **The answer-free test.** It replaced only the feed-forward's input,
  while the answer was already in the residual stream. So the model gave
  the true capital whatever the feed-forward did. It is now read on the
  feed-forward's output alone, through the output head.
- **The random control for the external table.** That control measured
  whether the true city survives. For an edited table, the question is
  whether a random vector gives the edited city. Both are now reported.
- **The plan's leave-one-out ceiling cannot be built.** Each city is the
  capital of exactly one country. The prompt's own output is reported
  instead, a trivial upper bound.

## A. Where the answer forms at the answer position

The logit lens at the answer position: the share of the 24 prompts in which
the true capital is the top city.

| block | Llama: before attention | after attention | after feed-forward | custom: before attention | after attention | after feed-forward |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.04 | 0.15 | 0.21 | 0.04 | 0.04 | 0.05 |
| 2 | 0.21 | 0.44 | **0.80** | 0.05 | 0.12 | 0.16 |
| 3 | 0.80 | 0.84 | 0.92 | 0.16 | 0.57 | **0.86** |
| 4 | 0.92 | 0.96 | 0.98 | 0.86 | 0.94 | 0.97 |

**The answer forms in the middle.**
- In Llama, in block 2: attention takes it from 0.21 to 0.44, and the
  feed-forward from 0.44 to 0.80.
- In the custom transformer, in block 3: attention takes it from 0.16 to
  0.57, and the feed-forward from 0.57 to 0.86.

**By the late feed-forward, the answer is already there.** Before block 4's
feed-forward, the lens finds it in 0.96 of prompts in Llama and 0.94 in the
custom transformer.

The late feed-forward:

| | Llama, block 3 | Llama, block 4 | custom, block 4 |
|---|---:|---:|---:|
| removed: own-capital accuracy (from 0.98 / 0.97) | 0.87 | 0.92 | 0.91 |
| removed at position 2 (control) | 0.98 | 0.98 | 0.97 |
| its output alone names the true capital | 0.92 | 0.98 | 0.92 |
| the same, with every city direction removed from its input | 0.81 | 0.90 | 0.58 |
| the same, with a random subspace removed | 0.86 | 0.97 | 0.91 |

**Against the plan's reading:**
- **Not retrieval:** the answer is present before the late feed-forward in
  more than half the prompts, and removing that feed-forward costs only 6
  to 11 points.
- **Not amplification as defined** either. Even with every city direction
  taken out of its input, its output still names the capital (0.81 to 0.90
  in Llama, 0.58 in the custom transformer).
- **What is established, and what is not:**

  | finding | evidence |
  |---|---|
  | the answer is present before the late feed-forward | strong |
  | the late feed-forward's output favours the answer on its own | strong |
  | the late feed-forward is not needed for most correct answers | strong: removing it costs 6 to 11 points |
  | its output still favours the answer when the cities' output directions are removed from its input | strong |
  | it performs a fresh lookup of the fact | **not established** |

  Removing the output directions does not remove every trace of the city:
  the answer could still be in another subspace, or non-linearly. A first
  draft said the late feed-forward "computes the answer again"; that
  overstated it.

Where the fact is actually produced is the middle block's attention and
feed-forward at the answer position. That is the next place to look.

## B. Editing a fact from outside, without changing a weight

The answer vector of each city is the mean feed-forward output, at block b,
at the answer position of `P lives in` for that city's two residents.
These come from another relation and other subjects, never the capital
prompt. At block b, the feed-forward output of `the capital of C is` is
replaced by a table's city's answer vector.

| block | Llama: edited table (a different city for every country) | random, matched: gives the edited city | custom: edited table | random: edited city |
|---:|---:|---:|---:|---:|
| 1 | 0.06 | 0.04 | 0.04 | 0.01 |
| 2 | 0.44 (0.17 to 0.67) | 0.02 | 0.03 | 0.00 |
| 3 | **0.90** (0.67 to 1.00) | 0.01 | 0.16 | 0.01 |
| 4 (last) | 0.91 (0.75 to 1.00) | 0.00 | 0.74 (0.62 to 0.96) | 0.00 |

- **In Llama, a table edit entering at block 3 changes the stated capital
  in 90% of prompts.** Block 4 then runs on it unchanged. A random vector of
  the same size never gives the edited city (0.01).
  - That passes the plan's edited-fact criterion (75%).
  - It is before the last block, so it is the plan's stronger result.
- **In the custom transformer, an edit works only at the last block**
  (0.74, just under the criterion), where adding an answer vector just
  before the output head favours its city partly by construction.
- **The true-table criterion cannot be judged.** A random vector in place
  of the feed-forward output leaves the true capital standing in 72% to 89%
  of prompts, because the answer is already in the residual stream. So the
  table giving the true capital (1.00) shows nothing.

## What it shows

- **The model accepts a city vector made elsewhere.** It is built from
  another relation and other people, and it enters at the answer position
  of a capital prompt, in Llama at block 3. The model then states that
  city.
- **Which city it states is set by an external table, and a table edit
  changes it.** This is a narrow hybrid: the table supplies the answer, not
  a query. The entity and the relation are resolved from the table, outside
  the model, and the model is handed a city vector. The vector works across
  relations: one made from `lives in` serves `capital of`.
- **Not yet shown:** an external operation given the model's own entity and
  relation state, answering from it. That would mean reading the entity
  and the relation component (SEM-001 version 3) at the answer position
  after block 1 or 2, and replacing block 2's computation. Block 2 is where
  the fact forms.

## Confirmation: worlds 4 to 6

The 18 models were trained on three fresh version-3 worlds, made after this
experiment's plan. The run is unchanged. Tables:
[tables/resolve-001-confirm.md](tables/resolve-001-confirm.md).

| | worlds 1 to 3 | worlds 4 to 6 |
|---|---:|---:|
| Llama, edited table at block 3: edited city stated | 0.90 (0.67 to 1.00) | **0.92** (0.88 to 1.00) |
| Llama, at block 4 | 0.91 | 0.92 |
| Llama, at block 2 | 0.44 | 0.44 |
| custom, at block 4 | 0.74 | 0.75 |
| random, matched: gives the edited city | 0.00 to 0.01 | 0.00 to 0.02 |

The result replicates.
