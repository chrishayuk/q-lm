# Results: Q-LM v3.2 to v3.4, programs, routing and stopping learned from examples

Against [qlm-v3-plan.md](qlm-v3-plan.md), revision 1. Code:
`v3/program.py` (v3.2, static programs) and `v3/policy.py` (v3.3 routing
and v3.4 stopping). Tables:
- [tables/v3.2-programs.txt](tables/v3.2-programs.txt);
- [tables/v3.3-policy.txt](tables/v3.3-policy.txt);
- [tables/v3-llama-baseline.txt](tables/v3-llama-baseline.txt).

**What the learners read.** Only `train.txt`: v3.1 learns the knowledge,
and these learn the computation over it. `world.json` is read only to score
and to compare a learned table with the world's rule.

**Supplied priors:**
- facts have at most 2 arguments (v3.1);
- programs are at most 5 steps (v3.2);
- a condition is a relation with at most 8 distinct values (v3.3).

**No backpropagation anywhere.** Learning is counting and exhaustive search
over candidates, ranked by how many training examples they reproduce.

## v3.2: static programs

For each learned relation, every sequence of 1 to 5 other learned relations
is tried. The shortest, most accurate one is kept if it is right on at
least 90% of a held-back tenth of the subjects.

**Safeguards, added after review, before these results:**
1. **Cycles** in program definitions are rejected explicitly. None arose,
   so the check is not exercised by these worlds.
2. **Programs are verified after expansion:** each derived relation's
   program, expanded into stored relations, is run over a knowledge base
   with **every derived relation's stored answers deleted**. It must still
   reproduce its training pairs. This is also the compression test.
3. **Prompts are read only through learned frames,** with no
   task-specific parsing.
4. **Abstention and lost mass are counted apart.** An abstention is an
   unseen query wording, or no answer and no program; only those are
   spread uniformly. A read that finds nothing during execution is counted
   as an execution miss. There were none.

**Results** (all 12 task-A worlds behave the same within their kind):

| world | learned program | held-out 3 hops | held-out 4 hops |
|---|---|---:|---:|
| A, T2 | lives on = is from → is a city of → is in | 1.000 (3+ passes), 0 below | |
| A-deepL, T2 (composed 4-hop answers) | hemisphere = **lives on** → lies in | 1.000 | 1.000 (4+ passes), 0 below |
| A-deep, T2 (no composed 4-hop answers) | lives on, as above | 1.000 | 0: abstains, the query wording never seen |
| A and A-deep, T1 (no composed answers) | none | 0: abstains | 0 |
| B, T2 | no fixed program fits (best: 3 to 5% of training pairs) | 0 at every length | |

- **Program reuse:** the four-hop program is written with the learned
  three-hop program as its first step. Expanded, it is 4 primitive steps,
  and reproduces 100% of its training pairs with every stored composed
  answer deleted.
- **Compression:** deleting the derived relations' stored answers changes
  no answer. The model shrinks from 11.5 kB to 9.1 kB (A), and from
  14.4 kB to 9.6 kB (A-deepL).
- **Distractor:** "P was born in ?" is answered by its own stored relation,
  100% everywhere, never by the home chain.

## v3.3 and v3.4: routing and stopping (task B)

A policy is a condition (a learned relation with few values) and a table
mapping each of its values to an action: follow a learned relation, or
STOP. It runs until every entity has stopped (cap 32 passes). All 15,625
tables are tried; the best reproduces most training pairs, then has the
fewest STOP values.

**The learned tables, against each world's randomised rule:**

| world | learned | agrees with the rule |
|---|---|---:|
| B-s1 | black, blue → STOP; green → points to; red → calls; white → faces; yellow → holds | 6 of 6 |
| B-s2 | red, white → STOP; black → holds; blue → faces; green → calls; yellow → points to | 6 of 6 |
| B-s3 | black, blue → STOP; green → calls; red → faces; white → points to; yellow → holds | 6 of 6 |

Each fits 100% of its training pairs and 100% of the held-back tenth.
Under T1 (no composed answers) no policy is found, as it should not be.

**Held-out accuracy, the same on all three worlds:**

| passes | 2 steps | 3 steps | 5 steps | 7 steps (never composed) |
|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 0 |
| 2 | 1 | 0 | 0 | 0 |
| 3 | 1 | 1 | 0 | 0 |
| 4 | 1 | 1 | 0 | 0 |
| 8 | 1 | 1 | 1 | 1 |
| 32 | 1 | 1 | 1 | 1 |

**The control: the learned routing, but no stop decision** (stopping
values follow the policy's most used relation; a fixed number of passes):

| passes | 2 steps | 3 steps | 5 steps | 7 steps |
|---:|---:|---:|---:|---:|
| 2 | 1 | 0 | 0 | 0 |
| 3 | 0 | 1 | 0 | 0 |
| 4, 8, 32 | 0 | 0 | 0 | 0 |

- **The stop is learned from the state:** two colours stop, and with it
  extra passes never hurt.
- **Without it,** a fixed number of passes is right only at exactly the
  path length.
- **Cost:** learning takes 2 minutes per world, because the search is
  exhaustive (5^6 tables). That does not scale; it is a proof that the
  policy is identifiable from the examples, not an efficient learner.

## The transformer baseline, on the exact same data

Llama-shaped, about 1.1M parameters, 6,000 steps, seed 1. Most probable
next token after the prompt.

| world | 3 hops (chance 0.25) | 4 hops (chance 0.5) | distractor | task B, any length (chance about 0.001) |
|---|---:|---:|---:|---:|
| A, T2, seeds 1 to 3 | 0.500, 0.750, 0.750 | | 1.000 | |
| A-deep, T2 | 0.792, 0.500, 0.458 | 0.000 (wording never seen) | 1.000 | |
| A-deepL, T2 | 0.500, 0.500, 0.625 | 0.792, 0.583, 0.792 | 1.000 | |
| B, T2, seeds 1 to 3 | | | | 0.000 at 2, 3, 5 and 7 steps |

## Against the plan's criteria

- **v3 learns computation** (≥ 90% held-out composition with the learned
  chain, on all three worlds, with 1 pass ≤ 35%):
  - **passes** on A, at 1.000;
  - **passes** on B, with the learned policy and stop, at 1.000.
  - The flat-predictor (v2) and matched-budget controls were **not run**.
    The transformer baseline was: 0.46 to 0.79 on A, 0 on B.
- **Depth:**
  - **D-extend passes on B** (7 steps, never composed, solved by the
    learned loop) and **fails on A**. A static program cannot answer a
    query wording it has never seen; it abstains, and so does the
    transformer.
  - **D-learn passes on A** (a four-hop program learned from four-hop
    examples, by reusing the three-hop one).
- **Paraphrased queries:** **not run.** No test-only query wording exists
  yet.
- **Distractors:** pass, at 1.000.

## What it says, and its limits

- **On these worlds, without backpropagation, the system learns:**
  - a knowledge graph from text;
  - functions over it (v3.2), composing one learned function inside
    another;
  - a loop with conditional dispatch and a learned stopping condition
    (v3.3, v3.4), which runs to depths never seen composed.
- **The worlds are clean and the priors are strong:**
  - every sentence is a fact in a template;
  - the condition is stated directly ("X is red .");
  - paths use their own nodes;
  - the search is exhaustive over small spaces.
- **Next tests that would matter:**
  - paraphrased query wordings;
  - conditions not stated directly (learned from distributional
    evidence);
  - noisy text and sentences that are not facts;
  - search that scales (greedy or constraint-based, not exhaustive);
  - the v2 and matched-budget controls.
