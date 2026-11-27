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

## Revision 1: diagnostics and uncertain meanings (after the first results)

Written after STATE-001's results and after one look, at seed 202, the
confirmation seed that failed. It is exploratory, not a new
pre-registration of the arms above. Seed 202 is now spent; the fresh
confirmation seeds are 301 to 303.

**New arms:**
- **S-global:** an entity-only state that enforces the length by the
  global pass index. In synchronous passes every active state has taken
  the same number of steps, so this is equivalent to S for this
  constraint; the arm tests that.
- **S-soft:** the meaning of a length word is a distribution,
  P(length | word), from the weighted counts. Mass that stops at n steps
  is weighted by P(n | word), not rejected outright.
- **S-oracle (diagnostic only):** the true length, from world.json. It
  separates "the constraint cannot be read" from "the constraint does not
  help".

**New labelling, `LABELS=em`:**
- Every consistent walk of every training example is kept, with equal
  weights at first.
- Ten rounds: the naive Bayes is fitted from fractional labels, and each
  walk is re-weighted by the product of its actions' posteriors, its final
  STOP included.
- Walk lengths become distributions, and so do word meanings.

**Questions, each answered on the comparison worlds and then once on seeds
301 to 303:**
1. Does S-oracle beat E at 7 steps (is the 7-step failure one of
   grounding)?
2. Does S-global equal S (is the per-entity step count needed)?
3. Do S-soft and EM labels avoid the wrong-meaning collapse?
4. Do EM labels improve node accuracy and 5-step accuracy over shortest
   labels?
