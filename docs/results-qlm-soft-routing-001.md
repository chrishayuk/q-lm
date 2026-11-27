# Results: QLM-SOFT-ROUTING-001, keeping uncertainty over operations

Against [qlm-soft-routing-001-plan.md](qlm-soft-routing-001-plan.md).
Code: `v3/softroute.py`. Tables:
- [tables/soft-routing-001.txt](tables/soft-routing-001.txt), all arms
  but B, with accounting;
- [tables/soft-routing-001-armB.txt](tables/soft-routing-001-armB.txt),
  arm B's cost, from the first run.

**Probability accounting, added after review, before these numbers.** Each
query's mass is reported as completed (stopped), dead end (a read found
nothing), pruned (floor, threshold or beam) and unfinished (active at the
cap). Only completed mass is the answer; the rest is abstention.
- In every arm on every world: dead end 0 and unfinished 0.
- Pruned: up to 0.089 for the beam (D), up to 0.019 for F, 0 for C and E.

So the calibration gains below are not mass moved into the projection's
floor.

## 7 steps and bits for the true answer (noisy worlds)

| world | A (hard) | C (top 2) | D (beam 8) | E (merged) | F (pruned, tuned) | bits A | bits E | bits D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| noisy s1 | 0.333 | 0.333 | 0.333 | 0.333 | 0.333 | 12.44 | 2.57 | 2.64 |
| noisy s2 | 0.467 | 0.400 | 0.367 | 0.367 | 0.367 | 10.26 | 2.18 | 2.18 |
| noisy s3 | 0.233 | 0.233 | 0.233 | 0.233 | 0.233 | 15.23 | 3.47 | 3.65 |

- At 2 to 5 steps, soft arms gain at most 0.067 on any world, and lose up
  to 0.067 on others.
- Clean latent and explicit worlds: every arm has the same accuracy as A.
  Bits for the true answer go from 0.9–2.8 (A) to 0.14–0.51 on the clean
  worlds, and from 0.000 to 0.09–0.16 on the explicit ones.

## Cost (noisy s1)

| arm | max active states | expansions per query | ms per query |
|---|---:|---:|---:|
| A | 1 | 5.8 | 0.13 |
| B (no merging) | 640,207 | 4,425,915 | 6,673 |
| C | 501 | 4,454 | 6.2 |
| D | 8 | 245 | 0.64 |
| E | 1,013 | 26,427 | 38.6 |
| F | 401 | 3,082 | 5.0 |

On noisy s3, B exceeded 2,000,000 active states in one query and was
stopped.

## Against the criteria

- **Uncertainty helps (+0.10 at 7 steps): FAILS.** The best soft arm,
  averaged over the noisy seeds, is −0.033 against A (0, −0.100, 0). The
  confirmation on fresh seeds was to be run only for a passing arm, so it
  was not run.
- **No cost when certain: passes.** No accuracy is lost on the explicit or
  clean worlds.
- **Merging matters: passes.** E's maximum active states is 1/632 of B's at
  the same accuracy, and B is infeasible on s3.
- **Calibration: passes.** The true answer costs 2.2 to 3.5 bits under E,
  against 10.3 to 15.2 under A. The beam of 8 keeps almost all of that at
  0.64 ms per query.

## What it says

Keeping a distribution over the next entity makes the model much less
confidently wrong, but rarely changes which answer it picks. Each
alternative is weighted only by local evidence, the same evidence that
made the hard choice. Nothing later in the walk bears on it. Merging
equivalent states is what makes keeping alternatives affordable:
dynamic programming over the walk, as in Colmerauer's shared graphs.
