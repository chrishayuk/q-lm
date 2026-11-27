# Results: QLM-STATE-001, contextual computational states

Against [qlm-state-001-plan.md](qlm-state-001-plan.md). Code:
`v3/state.py`. Tables: [tables/state-001.txt](tables/state-001.txt) and
[tables/state-001-confirm.txt](tables/state-001-confirm.txt).

## What was learned

On every world the constraint relation is found: "the walk from _ takes
_ steps .", with purity 0.88 to 0.93 and coverage 1.0.

**The word meanings:**
- **Two, three and five** are right on all 9 comparison worlds.
- **"Seven" is never given a meaning:** 3 of 4 right on every world. No
  7-step walk is composed in training, so nothing labels it. The
  evidence is unreadable at exactly the depth that needs it.
- **On fresh seed 202, "five" was learned as 4** (2 of 4 right). The likely
  cause is labels: the learner labels each example with its shortest
  consistent walk, and a spurious 4-step walk is shorter than some true
  5-step paths.

**A confound:** the length relation is an attribute, so it is also a naive
Bayes feature for start nodes. All arms see the same worlds.

## Results (comparison worlds)

**Noisy latent worlds, accuracy by path length:**

| world | arm | 2 | 3 | 5 | 7 | bits for the true answer | max active | ms/query |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| s1 | A | 0.800 | 0.600 | 0.400 | 0.333 | 11.82 | 1 | 0.27 |
| | E | 0.800 | 0.667 | 0.400 | 0.267 | 2.51 | 1,013 | 48 |
| | **S** | **1.000** | **1.000** | **0.733** | 0.267 | **1.68** | 1,013 | 17 |
| | S-beam | 1.000 | 1.000 | 0.733 | 0.267 | 1.86 | 8 | 0.41 |
| | S-shuffled | 0.467 | 0.333 | 0.267 | 0.200 | 11.98 | 1,013 | 17 |
| s2 | E | 0.733 | 0.667 | 0.467 | 0.333 | 2.18 | | |
| | S | 0.933 | 0.933 | 0.800 | 0.333 | 1.46 | | |
| s3 | E | 0.667 | 0.533 | 0.267 | 0.200 | 3.47 | | |
| | S | 1.000 | 0.933 | 0.667 | 0.200 | 2.36 | | |

- **Clean latent worlds:** S reaches 1.000 at 2, 3 and 5 steps on all
  seeds but one cell (0.933), where E has 0.867 to 1.000. At 7 steps S and
  E are equal.
- **Explicit worlds:** every arm but S-shuffled is at 1.000; no cost.

**Accounting:** in S, about 30% of the mass on noisy worlds is rejected for
stopping at the wrong length (s1: completed 0.695, rejected 0.305). No dead
ends and nothing unfinished; S-beam prunes about 0.016.

## Confirmation (fresh noisy seeds 201 to 203, run once)

| seed | arm | 2 | 3 | 5 | 7 |
|---|---|---:|---:|---:|---:|
| 201 | E | 0.800 | 0.467 | 0.333 | 0.100 |
| | S-beam | 0.933 | 0.800 | 0.867 | 0.100 |
| 202 ("five" learned as 4) | E | 0.867 | 0.600 | 0.200 | 0.367 |
| | S-beam | 0.933 | 0.800 | **0.000** | 0.367 |
| 203 | E | 0.733 | 0.867 | 0.467 | 0.367 |
| | S-beam | 0.867 | 0.867 | 0.867 | 0.367 |

## Against the criteria

- **Context helps (S over E at 7 steps by 0.15): FAILS.** The gain at 7
  steps is 0 on every world, because "seven" has no learned meaning.
- **The evidence matters (S over S-shuffled at 7 steps by 0.15): FAILS,**
  for the same reason. Even at 7 steps the shuffled control is no better
  than S.
- **The meaning is learned (all four words): FAILS.** 3 of 4 on every
  comparison world; 2 of 4 on one fresh seed.
- **Bounded:** passes. S-beam keeps 8 states, at 0.41 ms per query.
- **No cost when certain:** passes.

## What it says (beyond the registered criteria)

- **Where the evidence is readable (2, 3 and 5 steps), contextual states
  turn kept alternatives into right answers.**
  - Noisy worlds, 5 steps: E averages 0.378 and S 0.733.
  - Two of three fresh seeds: 0.333 → 0.867 and 0.467 → 0.867.
  - Shuffling the evidence removes the gain, so it comes from the
    evidence, not from the larger state.
- **This answers SOFT-ROUTING-001's failure.** Keeping alternatives helps
  when something later can tell them apart. Here that is a constraint on
  the whole computation, held in the state and applied when it stops.
- **A wrong learned constraint is worse than none:** seed 202's "five → 4"
  rejects every right 5-step answer (0.000, against 0.200 without the
  constraint). Evidence the runtime trusts must be learned reliably, or
  weighted by how sure the learner is of it.
- **The 7-step failure is about meaning, not state.** Reading "seven" would
  need number words learned as a system, or a constraint learned to
  extrapolate. Nothing here does that.

## Revision 1: diagnostics and uncertain meanings

Against the plan's revision 1. This is exploratory: designed after the
first results, and tried first on seed 202. It was confirmed once on fresh
seeds 301 to 303. Tables (all arms, both labellings):
- [tables/state-001-r1-shortest.txt](tables/state-001-r1-shortest.txt);
- [tables/state-001-r1-em.txt](tables/state-001-r1-em.txt);
- [tables/state-001-r1-confirm-shortest.txt](tables/state-001-r1-confirm-shortest.txt);
- [tables/state-001-r1-confirm-em.txt](tables/state-001-r1-confirm-em.txt).

### 1. Is the 7-step failure one of grounding? Yes.

With the true length supplied (S-oracle, diagnostic only), 7-step accuracy
on the noisy worlds rises well above E's:

| worlds | E | S-oracle |
|---|---|---|
| comparison, shortest labels | 0.267, 0.333, 0.200 | 0.733, 0.900, 0.600 |
| fresh 301–303, shortest labels | 0.067, 0.167, 0.333 | 0.467, 0.533, 0.933 |
| fresh 301–303, EM labels | 0.067, 0.133, 0.367 | 0.467, 0.567, 0.900 |

So the evidence, read correctly, is enough to choose between alternatives
at 7 steps as well. What fails is giving "seven" a meaning.

### 2. Is a per-entity step count needed? No.

S-global (entity-only states, the length enforced by the global pass
index) equals S in every cell, on all 24 world-and-labelling runs. With
synchronous passes, the pass index is the step count. The gain in
STATE-001 comes from the evidence, not from a richer state.

### 3. Uncertain meanings

**Shortest-walk labels:** the wrong meaning ("five" → 4) recurred on fresh
seed 303, as on 202.
- **Hard S collapses:** 0.000 at 5 steps.
- **S-soft avoids the collapse but gains nothing:** 0.267 on 303, the same
  as E. P(4 | five) is 0.48 and P(5 | five) 0.29, so the right length is
  still down-weighted.
- **Where the meaning is right, S-soft costs accuracy.** A spread
  distribution discriminates less (301: 0.467 hard, 0.267 soft).

**EM labels:** "five" is learned as 5 on every world, comparison and
fresh, with P(5 | five) = 0.98 to 1.00. The collapse does not occur.

**5 steps on fresh seeds 301 to 303, arm S:**

| labels | 301 | 302 | 303 | mean |
|---|---:|---:|---:|---:|
| shortest | 0.467 | 0.800 | 0.000 | 0.422 |
| EM | 0.533 | 0.600 | 0.733 | 0.622 |

### 4. Does EM improve the routing itself? Barely.

Node accuracy under EM is within ±0.013 of shortest labels on every world
(noisy: 0.882, 0.914 and 0.854 against 0.887, 0.906 and 0.841). EM's gain
comes from the meanings: re-weighting walks by the policy removes the
spurious short walks that taught "five → 4". It is not uniformly better:
seed 302 loses 0.2 at 5 steps.

### What it says

- **The learned computation works when its inputs are right:** the oracle
  shows the runtime can use the evidence at every depth tested.
- **The weak link is the learned meaning of the evidence.**
  - Committing to one explanation per training example (the shortest
    walk) can teach a wrong meaning, and a wrong hard constraint is
    destructive.
  - Keeping all explanations and re-weighting them by the learned policy
    (EM, no gradient) fixes that here.
  - Softening the meaning afterwards does not.
- **"Seven" is still unreadable.** It needs meaning beyond the lengths
  seen in training: number words as a system, or meaning grounded in
  counting. Not attempted.
