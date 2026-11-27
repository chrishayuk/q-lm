# Results: LARQL-QLM-SEM-001, version-2 worlds

Reported against [larql-qlm-sem-001-plan.md](larql-qlm-sem-001-plan.md) and
its three amendments. The same-type relation test and the recombined query
need the version-3 worlds, and follow separately. Full tables:
[tables/sem-001-v2.md](tables/sem-001-v2.md).

The models are 18: Llama and the custom transformer, seeds 1 to 3, on the
three version-2 worlds. Interventions are at block outputs, at the last
prompt position unless stated. Block 4 is the last, read directly by the
output head: it is the positive control. Ranges are over the 9 runs of each
architecture.

**Instrument check.** The custom transformer cannot be loaded by VINDEX3
(its output layer is separate and has a bias). For Llama, LARQL's per-layer
states agree with PyTorch's to 1e-6 (GROUP-001, same architecture and
code). It is not repeated on these models.

**Gate.** Every model knows every fact used: 24 of 24 capitals, both
wordings, every continent and every home city. Nothing is excluded.

## What the last position holds: mostly the answer

**Convergence.** Cosine similarity of centred last-position states, means
over the 9 runs.

| block | Llama: same fact, two wordings | Llama: same answer, other relation | Llama: different facts, same wording | custom: same fact | custom: same answer | custom: different facts |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.37 | −0.01 | 0.53 | −0.36 | −0.41 | 0.98 |
| 2 | **0.77** | 0.51 | 0.14 | 0.05 | −0.24 | 0.79 |
| 3 | 0.93 | 0.82 | 0.00 | **0.55** | 0.42 | 0.31 |
| 4 | 0.97 | 0.93 | −0.03 | 0.80 | 0.80 | 0.03 |

The "same answer, other relation" pairs are `C has capital` against
`P lives in`, for a resident P of C's capital. Same answer, different
relation and different subject.

**Full-state transplant** into `the capital of C' is`: the share of pairs
in which the donor's city wins.

| block | Llama, same wording | other wording | **same answer** (`P lives in`) | other relation (`C is in`) | random | custom, same wording | other wording | same answer | other relation | random |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.67 | 0.83 | **0.98** | 0.25 | 0.01 | 0.00 | 0.05 | 0.05 | 0.05 | 0.03 |
| 2 | 0.99 | 1.00 | **1.00** | 0.29 | 0.00 | 0.43 | 0.52 | 0.69 | 0.32 | 0.01 |
| 3 | 1.00 | 1.00 | 1.00 | 0.31 | 0.00 | 0.95 | 1.00 | 1.00 | 0.59 | 0.00 |
| 4 (control) | 1.00 | 1.00 | 1.00 | 0.33 | 0.00 | 0.99 | 1.00 | 1.00 | 0.62 | 0.00 |

- **The cross-wording transplant works**, as well as the same-wording one.
  But **a donor with the same answer through a different relation and a
  different subject works just as well**, and in Llama it already works
  after block 1.
- By the time the last position is read, the answer has been resolved:
  - in Llama after block 1 or 2;
  - in the custom transformer by block 3.

  What moves is the answer, as the amendment warned it might.
- **The criterion for a fact state, as opposed to an answer state, fails.**
  At the block where convergence peaks (block 4), same-fact similarity
  exceeds same-answer similarity by 0.04 in Llama and 0.00 in the custom
  transformer, against a required 0.1.
  - There is a fact-specific excess earlier: 0.26 at block 2 and 0.11 at
    block 3 in Llama, and 0.13 at block 3 in the custom transformer.
  - But by then the transplants already move the answer as well from a
    same-answer donor as from a same-fact one.
- **The other-relation donor carries some of the country.** `C is in`
  (whose answer is C's continent) gives C's capital in 25% to 33% of pairs
  in Llama and 59% to 62% in the custom transformer, against 0% for
  random. So these last states hold more than their own answer: something
  of C, or of C's other facts.
- **The probe does not generalise.** A ridge map from state to the answer's
  output-embedding row, fitted on 18 countries, finds the held-out 6's
  capitals:
  - in wording 1, at 26% to 33% at the last block, and near 0 before it;
  - in wording 2, at about 4%;
  - untrained, at 0.

  So no linear map from the last state to the answer generalises from 18
  examples before the last block.
- **Entity transplant at the country's own position.** In `the capital of
  C' is`, the state at C''s position is replaced by the state at C's
  position in `the capital of C is`. The share in which C's capital wins,
  means with ranges:

  | block | Llama | custom transformer | random (both) |
  |---:|---:|---:|---:|
  | 1 | 0.18 (0 to 0.55) | **0.96** (0.91 to 1.00) | ≤ 0.01 |
  | 2 | 0.00 | 0.38 (0.05 to 0.80) | 0.00 |
  | 3 | 0.00 | 0.00 | 0.00 |
  | 4 | 0.00 | 0.00 | 0.00 |

  **In the custom transformer, this is an entity state with the query
  still to be computed.**
  - After block 1, the country's position holds the country, and the
    capital has not been looked up yet.
  - Moving it moves which capital the later blocks compute, in 96% of
    pairs.
  - After block 2 the last position has read it, and overwriting the
    country's position no longer matters.

  In Llama, that hand-off happens within block 1. These are the plan's
  "earlier position" stages, seen as a sequence: entity at its own
  position, then read by the last position, then resolved there. (The
  first draft of this note said the transplant did nothing; that was read
  from one model, and is corrected.)
- **The held-out phrasings** are not a test here: every model answers all
  6 correctly unintervened. That matches QLM-SEMANTIC-001 (98%).

## Partial transplants (capital against continent)

Subspaces fitted on wording 2 over the 18 fitting countries, and applied on
wording 1 to the 6 held-out countries.

| block | Llama, relation only: C's continent wins | random, matched | Llama, entity only: C2's capital wins | custom, relation only | random | custom, entity only |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.83 (0.50 to 1.00) | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 |
| 2 | **1.00** | 0.00 | 0.50 | 0.70 | 0.00 | 0.06 |
| 3 | 0.98 | 0.00 | 0.04 | **0.96** | 0.00 | 0.11 |
| 4 (control) | 1.00 | 0.00 | 0.02 | 1.00 | 0.00 | 0.13 |

- **By the plan's criterion, the relation-only swap succeeds:**
  - fitted on another wording and other countries, it switches `C has
    capital` to C's continent in at least half of the held-out countries
    before the last block. That is Llama at blocks 1 to 3, and the custom
    transformer at blocks 2 and 3;
  - the magnitude-matched random subspace never does.
- **This is the confound the second amendment named.** There are only 4
  continents, and the relation subspace has 4 dimensions. It can carry the
  answer type and which continent, which is what switching to C's
  continent requires. This result does not show a relation component
  separate from the answer. The version-3 test, where both relations
  answer with a city among 24, is the one that can.
- **The entity-only swap fails** (criterion: at least half), except
  Llama's 0.50 at block 2, which just reaches it. A 10-dimensional
  subspace of country means does not carry which capital follows.

## Against the plan

| criterion | Llama | custom transformer |
|---|---|---|
| a shared fact state (similarity, probe, cross-wording transplant against other-relation control) | **fails**: the probe fails, and the other-relation control is not under a tenth | **fails**, the same |
| wording-independent transfer (cross-wording ≥ half of same-wording) | holds | holds |
| a fact state, not an answer state | **fails** at the peak; a fact-specific excess at blocks 2 and 3 | **fails** at the peak; an excess at block 3 |
| a relation state separable from the entity (capital/continent) | holds, but confounded by answer type | holds, but confounded |
| an entity state separable from the relation (partial subspace, last position) | fails (0.50 at one block) | fails |
| an entity state at the entity's position, query computed afterwards (full state) | weak: 0.18 after block 1 | **holds**: 0.96 after block 1 |

## What this means

- The transformers' cross-wording success is explained by **answer
  states**. Both wordings, and a different relation with the same answer,
  converge on the same last-position state. That state is formed within
  one or two blocks.
- **Before the answer is formed, there is an entity state at the entity's
  own position.** In the custom transformer, moving it after block 1 moves
  the computed capital in 96% of pairs. The query is then computed from it
  by the later blocks. This is the stage-wise picture of entity, then
  query, then answer, in one architecture, measured causally.
- There is weaker evidence of something fact-specific in the middle blocks:
  - the convergence excess;
  - the other-relation donor carrying part of the country.

  It is not what the last-position transplant moves.
- So far this is closer to Hypothesis A (computations converging on an
  answer) than to B (a preserved binding). The version-3 same-type
  relation swap and the recombined query test B more directly.
