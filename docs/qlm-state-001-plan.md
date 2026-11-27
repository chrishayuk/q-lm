# QLM-STATE-001 plan: contextual computational states

Written before any code. It follows QLM-SOFT-ROUTING-001. There, keeping
a distribution over entities made the model much less confidently wrong
(12.4 bits for the true answer down to 2.6) but rarely changed which
answer it chose. Weighted routing has no evidence for choosing between
the alternatives it keeps.

## The question

If the working state carries more than (entity, weight), and the text
offers evidence that bears on the whole computation and not on one node,
can the runtime use that evidence to choose between alternatives, and so
answer more held-out paths?

## The task: B-latent with a length fact

B-latent (noisy and clean), plus, for **every** start node, held-out ones
included, a one-hop fact in the training text: "the walk from X takes L
steps ." (L in two, three, five, seven).
- It says nothing about the end: held-out starts' answers are still never
  seen.
- It constrains the computation: a walk is right only if it stops after
  exactly L steps.
- Errors at a node usually change the length (a wrong action leads into a
  distractor's random walk), so the fact can reject wrong alternatives
  after they are made.

## What is learned, and what is supplied

- **Learned (v3.1):** the fact is a relation, "the walk from _ takes _
  steps .", binding a start to a token.
- **Learned, not supplied:** what the token means. For training starts, the
  learner has the length of their labelled walk (from the computation
  labels), so it counts which token goes with which length. At test, a
  token maps to the length it was counted with most often.
- **Supplied:** that a state may carry a step count, and that a relation
  on the start may constrain it. The runtime is given a slot for it, not
  its meaning.

## The states

| arm | state | merging | use of the length fact |
|---|---|---|---|
| A | entity | by entity | none (hard routing; the SOFT-ROUTING-001 baseline) |
| E | entity, weight | by entity | none (soft; SOFT-ROUTING-001's arm E) |
| S-shuffled | as S | by (entity, steps) | as S, but each start is given another start's length fact (a control: the state's structure without the evidence) |
| S | (entity, steps taken), weight | by (entity, steps) | a state stops only at the learned length; completed mass at another length is rejected, and the rest renormalised |
| S-beam | as S, beam of 8 | by (entity, steps) | as S |

The equivalence point from review: once the state holds the step count,
two paths at the same entity with different counts are different states,
and merging is by (entity, steps), not by entity.

## Accounting

As in SOFT-ROUTING-001 after review: completed, dead end, pruned,
unfinished, and now **rejected** (completed at the wrong length) are
reported apart. Only completed-and-accepted mass is the answer.

## Worlds and splits

- Comparison: B-latent noisy and clean, seeds 1 to 3; explicit B, seeds 1
  to 3 (no cost when certain).
- Confirmation, once: B-latent noisy, seeds 201 to 203, arms A, E and the
  better S arm.

## Criteria

- **The evidence matters:** S beats S-shuffled at 7 steps on the noisy
  worlds by at least 0.15.
- **Context helps:** S or S-beam beats E at 7 steps on the noisy worlds by
  at least 0.15 averaged over the three seeds, and confirms on the fresh
  seeds by at least 0.10.
- **The meaning is learned:** the token → length mapping is right for all
  four tokens, on every world.
- **Bounded:** at most 100 active states per query (S-beam: 8).
- **No cost when certain:** at most 0.02 lost on the explicit worlds.

## Not a test of

- Learned state design. The step slot is supplied.
- Reasoning in general. One kind of global evidence (length) is tested.
- Scalable learning. The labels still come from walk enumeration.
