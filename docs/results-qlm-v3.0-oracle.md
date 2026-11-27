# Results: Q-LM v3.0, the oracle execution runtime

Against [qlm-v3-plan.md](qlm-v3-plan.md), revision 1, "What v3.0 must
show". Code: `v3/worlds.py` (the task worlds), `v3/runtime.py` (the
runtime). Full table: [tables/v3.0-oracle.txt](tables/v3.0-oracle.txt).

**This is not learning.** The knowledge, the program (task A) and the
policy with its stop rule (task B) are all supplied from the world's
truth. It qualifies the machine that the learned stages will replace
parts of.

## The worlds

Regenerate with `for t in A A-deep B; do for s in 1 2 3; do for r in T1 T2; do python3 -I v3/worlds.py data-v3/$t-s$s-$r $t $s $r; done; done; done`. The generator is deterministic for each seed.

18 in all: task A, A-deep and B, seeds 1 to 3, regimes T1 and T2.
- **A:** 96 people, 24 cities, 24 countries, 4 continents.
  - Held out: a quarter of the people, balanced by continent.
  - Tests: "P lives on ?" (3 hops); the distractor "P was born in ?"
    (1 hop, never the home city).
  - A-deep adds hemispheres and "P lives in hemisphere ?" (4 hops), with
    no composed statement at that depth anywhere.
- **B:** about 1,000 nodes with 6 kinds and 4 relations each.
  - The relation followed depends on the node's kind; 2 kinds stop.
  - Paths of 2, 3 and 5 steps, 60 each, 15 held out per length.
  - 30 paths of 7 steps, never composed in any text.

## Results (all 18 worlds identical)

**Task A, passes against accuracy on held-out queries:**

| passes | compose (3 hops) | depth (4 hops, A-deep) | distractor (1 hop) |
|---:|---:|---:|---:|
| 1 | 0.000 | 0.000 | 1.000 |
| 2 | 0.000 | 0.000 | 1.000 |
| 3 | 1.000 | 0.000 | 1.000 |
| 4 | 1.000 | 1.000 | 1.000 |
| 8 | 1.000 | 1.000 | 1.000 |

**Task B, with the supplied stop rule:**

| passes | 2 steps | 3 steps | 5 steps | 7 steps (never composed) |
|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 0 |
| 2 | 1 | 0 | 0 | 0 |
| 3 | 1 | 1 | 0 | 0 |
| 4 | 1 | 1 | 0 | 0 |
| 8 | 1 | 1 | 1 | 1 |

**Task B, control without a stop decision** (terminal nodes keep walking):

| passes | 2 steps | 3 steps | 5 steps | 7 steps |
|---:|---:|---:|---:|---:|
| 2 | 1 | 0 | 0 | 0 |
| 3 | 0 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 |
| 8 | 0 | 0 | 0 | 0.033 (one world) |

## Against the criteria

- **Executes correctly: passes.** 100% once passes reach the path length,
  on every world. Below it, 0%: the state holds an entity of the wrong type
  (a city or country, or a mid-path node), below the chance level of 25%
  for continents.
- **Uncertainty is carried: passes.** A held-out person's home split 0.5
  and 0.5 between cities on different continents gives each continent
  exactly 0.500.
- **The projection normalises: passes.** The worst |sum − 1| is 0 to
  printing precision on every world.

## Measures

- **Knowledge:** 240 to 244 entries (task A), 8 kB serialised with pickle;
  4,080 entries (task B), 126 kB.
- **Inference:** 0.011 ms per query (A) and 0.066 ms (B), including the
  full next-token distribution.
- **Learning:** none at this stage.

## What it says

- **The machine works.** Address, read, transform and write, repeated,
  answers compositions it was never shown, given the right knowledge and
  program.
- **Stopping is the dynamic part.** Without a stop decision, a fixed
  number of passes is right only at exactly the path length: 3 passes
  answer 3-step paths and break 2-step ones. On task B no fixed chain
  length can be right for all queries. This is why a learned fixed length
  is not counted as a learned stop.
- **Next, v3.1:** entities and relations learned from the training text,
  with the program still supplied. The runtime then executes over learned
  knowledge, under T1.
