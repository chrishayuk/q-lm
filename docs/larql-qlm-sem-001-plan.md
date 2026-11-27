# LARQL-QLM-SEM-001 plan: does a fact have a state of its own, apart from its wording?

Written before any measurement, and amended once before any measurement
(the last section) to tell a fact state from an answer state, an entity
state and a query state. It runs on the version-2 semantic worlds
(QLM-SEMANTIC-001, change 2), after their transformers are trained.

## Question

The transformers carry a fact from one phrasing to another: for example,
from `C has capital K .` to `the capital of C is` → K, 83% to 100% in
version 1. Is there an internal state that stands for the fact
capital(C, K), the same under both wordings? And if so, can it be moved
from one wording to another, so that the fact goes with it and the wording
does not?

## Prompts

For every country C, two prompts ending where the capital comes next:
- wording 1: `C has capital`
- wording 2: `the capital of C is`

For the 6 countries whose second phrasing is held out, only wording 1 was
ever trained with the capital following. Those 6 are the test of transfer.
The other 18 are the control, seen in both.

## Measures, at every layer (embedding; after each attention step; after each block)

All at the last prompt position.

1. **Convergence.** The cosine similarity of the states of:
   - the same fact in the two wordings;
   - different facts in the same wording;
   - different facts in different wordings.

   A fact state predicts that the first is higher than the second at some
   layer, rising with depth. Reported for the 18 seen and the 6 held out
   separately.
2. **Fact decoding.** A linear probe, trained on wording 1's states over
   all 24 countries, reads the capital. It is tested on wording 2's states.
   Above chance (1/24) means a shared direction for the answer. Controlled
   against the same probe on an untrained model.
3. **Transplant.** At layer l, the last-position state of `the capital of
   C' is` is replaced by that of a donor, and the probability of K (C's
   capital) and of K' (C''s) is measured at the output. Donors:
   - `the capital of C is`, the same wording: the fact should move;
   - `C has capital`, the other wording: does the fact move without the
     wording?
   - `C is in`, the same country with another relation: control. The
     country moves, not the capital fact;
   - a random state of the same norm: control.

   The measures are:
   - the share of the 24 × 23 pairs where K becomes the most probable
     city;
   - the mean change in log2 P(K) − log2 P(K').
4. **The 6 held-out phrasings.** The same transplant, with the donor from
   wording 1 (the only one trained). If moving that state into wording 2's
   run gives K, the model's wording-2 failure, where there is one, lies in
   reading out, not in having the fact.

## What would count

- **A shared fact state at layer l:**
  - same-fact similarity exceeds different-fact similarity by at least 0.2;
  - the cross-wording probe reads the capital at 50% or better;
  - a transplant from the other wording makes K the top city in at least
    half the pairs, where the other-relation control does so in under a
    tenth as many.
- **Wording-independent transfer:** the cross-wording transplant does at
  least half as well as the same-wording one.

Models: Llama and the custom transformer, seeds 1 to 3, on the three
version-2 worlds. The same layer-by-layer check of LARQL against PyTorch as
in GROUP-001 comes first, on one model per architecture.

## Amendment before measurement: fact, entity, query or answer?

Converging states and successful transplants could mean that the model
represents **the answer** (K), not **the binding** capital(C, K). The
amendment separates four kinds of state:
- lexical (the words);
- entity (C);
- query (capital of C, answer not yet chosen);
- answer (K).

**Same answer, different relation.** Every city in the world is a capital
and has two residents. So for a resident P of K, `P lives in` and
`C has capital` share the answer K through different relations.
- Convergence (measure 1) is reported for same-fact pairs, and for
  same-answer, different-relation pairs.
- A transplant from `P lives in` into `the capital of C' is` is a further
  donor.
- If the same-answer pairs converge as much as same-fact pairs, and
  transplant as well, the shared state is the answer's, not the fact's.

**Probes that generalise past their training entities.** Measure 2 is
replaced by a regression from the state to the answer's output embedding
(the row of the output head for K). It is fitted on 18 countries' prompts,
in wording 1, and tested on the other 6, in both wordings, by the nearest
city. A probe that memorises 24 labels cannot do this. One that finds a
reusable map from state to answer can.

**Earlier positions.** The transplant is also done at the country's own
position (C in `the capital of C' is`), where the relation still has to be
applied after it. Moving C there and getting K tests an entity state, with
the query computed afterwards. Moving the final position tests a resolved
state.

**The final layer is a positive control.** A state transplanted
immediately before the output head carries its prediction with it by
construction. Results are read at the layers before it. A transfer only at
the last layer shows nothing about relations.

**Partial transplants: relation without entity.** At the last position:
- The **relation subspace** is spanned by the difference between the mean
  states of `C has capital` and `C is in` (capital against continent) over
  the 18 fitting countries, plus the leading directions of their per-country
  differences: the top 3 by variance.
- The **entity subspace** is spanned by the leading directions of the
  country-mean differences: the top 10.
- Swapping only the relation component from `C is in` into `C has capital`,
  for the same C, asks whether the output switches from C's capital to C's
  continent with C kept.
- Swapping only the entity component from `C2 has capital` into `C has
  capital` asks whether it switches to C2's capital with the relation kept.
- Controls are random subspaces of the same dimension. All of it is fitted
  on the 18 countries and measured on the other 6.

**What would count, added:**
- **A relation state separable from the entity:** the relation-only swap
  makes C's continent the most probable continent, ahead of the capital
  (most probable over cities plus continents), in at least half of the 6
  held-out countries, at some layer before the last. The random-subspace
  control does so in at most one.
- **An entity state separable from the relation:** the same, for the
  entity-only swap giving C2's capital.
- **A fact state, not an answer state:** the same-fact similarity exceeds
  the same-answer, different-relation similarity by at least 0.1 at the
  layer where measure 1 peaks.

## Second amendment before measurement: relation, wording, answer type and magnitude

The relation subspace above is fitted from capital against continent
prompts. That difference mixes four things:
- the wording;
- the type of the answer (a city against a continent);
- the answer itself;
- the relation.

Three controls are added.

1. **A relation that returns the same type.** A version-3 world adds
   `born(person → city)`, phrased `P was born in K .` and `P is a native
   of K .`.
   - Every person is born in a city other than the one they live in, two
     births per city, assigned by the world seed.
   - Version 3 is trained exactly as version 2: the same three worlds, the
     same models and seeds, everything else unchanged.
   - For a person P, the relation-only swap from `P was born in` into
     `P lives in` (or back) must change which city comes out, the birth
     city against the home city, with the answer type unchanged.
   - Counts when the target relation's city becomes the most probable city,
     ahead of the source relation's, for at least half the held-out people
     (fitted on three quarters, tested on the rest).
2. **Directions fitted on one wording, tested on another.**
   - Relation directions are fitted on wording 2 (`the capital of C is`
     against `C lies on`; `P is a native of` against `P is from`).
   - The swaps are measured on wording 1 (`C has capital` against `C is
     in`; `P was born in` against `P lives in`).
   - A direction that carries only wording fails this.
3. **Controls matched in magnitude.** Every random-subspace control is
   rescaled so that its perturbation of the residual stream has the same
   norm, position by position, as the intervention it controls. Matching
   dimension alone is not enough.

Version 2 is measured as planned. The same-type relation test is
reported from version 3.
