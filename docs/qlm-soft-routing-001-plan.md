# QLM-SOFT-ROUTING-001 plan: keep uncertainty over operations

Written before any code. It follows the latent-condition experiment
([results-qlm-v3-latent-conditions.md](results-qlm-v3-latent-conditions.md)).
There, hard routing decisions compound: about 10% node error leaves
about a third of 7-step paths right.

## The question

The policy gives each node a posterior over actions (naive Bayes, learned
from computation labels). Does executing over that posterior, instead of
its most probable action, answer more held-out paths, at a bounded cost?

## Arms

All arms use the same learned knowledge, posterior and stop. A state is
(entity, weight); a stopped state's weight goes to the answer
distribution.

| arm | routing |
|---|---|
| A | hard: the most probable action only |
| B | weighted over all actions, states kept as separate paths (no merging) |
| C | the top two actions, renormalised, with merging |
| D | a beam: all actions, with merging, keeping the 8 heaviest active states each pass |
| E | weighted over all actions, states at the same entity merged (one weight per entity) |
| F | E, with active states below a threshold pruned; the threshold and a temperature on the posterior are chosen on the training composed pairs |

- **Answer:** the most probable entity in the final answer distribution.
  Weight still active at the cap (32 passes) is added to it.
- **Temperature:** B to E use the posterior as learned (temperature 1);
  only F tunes it.

## Worlds

- B-latent, noisy (P_SIG 0.75, P_NOISE 0.05) and clean (0.95, 0.02), seeds
  1 to 3.
- The explicit worlds B-s1 to B-s3, as a check that soft routing costs
  nothing when the evidence is certain.
- **Confirmation:** B-latent noisy, seeds 101 to 103, used once, for the
  best arm and A.

## Measures

- Accuracy by path length (2, 3, 5, 7).
- **Calibration:** mean bits for the true answer, −log2 p, with the
  projection's floor.
- **Active states:** the maximum per query, and the total state
  expansions per query (cost).
- Time per query.

## Criteria

- **Uncertainty helps:** an arm among B to F beats A at 7 steps on the
  noisy worlds, by at least 0.10 averaged over the three seeds, with at
  most 100 active states per query, and confirms on the fresh seeds by at
  least 0.05.
- **No cost when certain:** that arm loses at most 0.02 on the explicit
  worlds.
- **Merging matters:** E's maximum active states is at most a tenth of
  B's, at accuracy within 0.02.
- **Calibration:** the arm's mean bits for the true answer is lower than
  A's.

## Not a test of

Scalable learning. The posterior comes from the same walk-labelled naive
Bayes, which still enumerates walks.
