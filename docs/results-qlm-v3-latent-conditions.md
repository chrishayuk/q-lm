# Results: Q-LM v3, latent routing conditions (the node's kind never stated)

Code: `v3/latent.py`. Worlds: `v3/worlds.py` task `B-latent`. Table:
[tables/v3-latent.txt](tables/v3-latent.txt). This experiment was not
in the plan's revision 1; it is reported as exploratory.

## The worlds

Task B's graph and randomised rule, but **no "X is red ." sentence**.
- Each hidden kind has a signature of 3 of 12 properties. Signatures
  overlap: in seed 1, lamp, well, stair, bench, clock and bell each belong
  to two kinds or more.
- Each node shows each property of its kind's signature with probability
  P_SIG, and each other property with P_NOISE ("X has a bell .").
- **Noisy:** P_SIG 0.75, P_NOISE 0.05. **Clean:** 0.95 and 0.02.
- Three seeds each, T2 (composed answers for training starts).
- The explicit-colour worlds B-s1 to B-s3 are rerun with the same learner,
  for comparison.

## The learner: abstraction formed by computation

1. **Links and attributes,** from the learned relations' structure: a
   relation whose objects are mostly subjects of other facts is a link.
   Here: the four edge relations and the composed one. "Has a" is an
   attribute.
2. **Labels from computation:** for each composed training pair
   (s, o), the walks over links from s that end at o are enumerated
   (up to 5 steps). A walk giving one node two actions is dropped.
   - The shortest walk, if it is the only one of its length, labels each
     node on it with the action it needed, and o with STOP.
   - First version: any unique walk. It was ambiguous for 75 of 121
     examples, because long random walks reach o by chance; fixed before
     these results.
3. **Condition:** a Bernoulli naive Bayes over each node's attribute
   values predicts its action, by counting only. That is the policy for
   every node, including those on held-out paths, which are never
   labelled.

**Controls and references:**
- **Distributional:** nodes clustered by attribute values alone (k-means,
  k = 6 supplied, 10 restarts), each cluster given the majority action of
  its labelled nodes.
- **Bayes reference (scoring only), corrected after review:** each node's
  most probable **action**, from the true signatures and noise rates:
  - the posterior is summed over the kinds that share an action;
  - the likelihood includes the generator's rule that a node showing
    nothing is given one signature property.

  The first version took the most probable kind and ignored that rule; it
  was weaker, and the learner seemed to exceed it. The reference is the
  per-node optimum in expectation, not a bound on 15 to 30 test paths.

## Results, at 32 passes (the learned stop ends every walk)

**Accuracy on held-out paths:**

| world | accepted | node actions right | 2 steps | 3 steps | 5 steps | 7 steps (never composed) |
|---|---|---:|---:|---:|---:|---:|
| explicit s1, s2, s3 | yes | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| latent noisy s1 | no (0.643) | 0.876 | 0.667 | 0.600 | 0.400 | 0.333 |
| latent noisy s2 | no | 0.906 | 0.733 | 0.667 | 0.467 | 0.467 |
| latent noisy s3 | no | 0.839 | 0.600 | 0.333 | 0.333 | 0.233 |
| latent clean s1 | yes | 0.996 | 1.000 | 0.933 | 1.000 | 0.933 |
| latent clean s2 | yes | 0.986 | 0.867 | 1.000 | 1.000 | 0.767 |
| latent clean s3 | no | 0.980 | 0.933 | 0.867 | 0.933 | 0.833 |

**7 steps, against the control and the reference:**

| world | learned | distributional control | Bayes reference (corrected) | learned at 5 steps | reference at 5 steps |
|---|---:|---:|---:|---:|---:|
| latent noisy s1 | 0.333 | 0.233 | 0.367 | 0.400 | 0.600 |
| latent noisy s2 | 0.467 | 0.400 | 0.467 | 0.467 | 0.467 |
| latent noisy s3 | 0.233 | 0.167 | 0.233 | 0.333 | 0.400 |
| latent clean s1 | 0.933 | 0.967 | 0.967 | 1.000 | 1.000 |
| latent clean s2 | 0.767 | 0.900 | 0.900 | 1.000 | 0.933 |
| latent clean s3 | 0.833 | 0.667 | 0.833 | 0.933 | 0.933 |

## What it says

- **The walk-based learner replaces the exhaustive search.** On the
  explicit worlds it recovers every node's action (1,020 of 1,020), in
  about 4 s against 117 s. It needs no condition to be named, and no table
  to be enumerated.
- **With the kind hidden, it recovers the routing condition from
  properties,** at the level the evidence allows:
  - **noisy worlds:** above the distributional control on all three
    seeds at 7 steps, and at or below the corrected Bayes reference. It
    equals the reference at 7 steps on two seeds and is below it on one;
    at 5 steps it is below on two (s1 0.400 against 0.600);
  - **clean worlds:** 0.98 to 0.996 of nodes right, and 0.77 to 0.93 at
    7 steps.
- **The groups are formed by the computation.** The two stopping kinds
  are one group (they need the same action), which a clustering by
  properties alone would keep apart.
- **Errors compound with depth.** A node error rate of about 10% leaves
  about a third of 7-step paths right. On noisy worlds most of that is the
  evidence: the reference also gets 0.23 to 0.47. The rest, up to 0.2 at
  5 steps, is the learner: its naive Bayes is fitted on about 400 labelled
  nodes.
- **Computation-formed groups help only when the evidence is noisy.** On
  the noisy worlds they beat clustering by properties on all three seeds.
  On the clean worlds the clustering does as well or better on two of
  three.
- **The control has a weakness:** on explicit s2, k-means with one-hot
  colours leaves a cluster empty and merges two colours (0.533 at 7
  steps). This is an artefact of the control, not evidence for the
  learner.
- **The acceptance criterion (90% on a held-back tenth of 14 paths) is
  coarse:** clean s3 is rejected at 0.98 of nodes right.
