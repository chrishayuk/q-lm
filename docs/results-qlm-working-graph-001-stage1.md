# Results: QLM-WORKING-GRAPH-001, stage 1 (first prototype)

Against [qlm-working-graph-001-plan.md](qlm-working-graph-001-plan.md).
Code: `v4/wgraph.py`, `v4/run_select.py`, and the `wg=` component in
`v2/composite.py`. Tables:
[tables/wg-001-select-10k.txt](tables/wg-001-select-10k.txt),
[tables/wg-001-stage1-10k.txt](tables/wg-001-stage1-10k.txt).

## Corrections before these numbers

- **The first in-mixture run was stopped** before it finished, and is not
  reported. The exploratory 0.079-bit "composition gain" from the first
  selection is withdrawn.
- **Fixes after review:**
  - writes keep their absolute evidence strength (weights are scaled
    down, never up; pruned mass is recorded);
  - the index has no duplicates, and pruned features leave it;
  - the 4,096-node addressing window is enforced (a benchmarking
    constraint; it never binds here);
  - an accumulated-state prediction option;
  - selection fits its mixture weight on half of the held-out stories
    and scores on the other half, split by whole story.
- **Causality:** the leakage check covers the working graph: no probability
  changed when later text changed (105 checks, seven components).

## The selection (10,000 sentences; 150 counting stories, 30 held-out)

Greedy, by held-out gain over a story bigram cache:

| pass | kept | held-out bits | gain |
|---|---|---:|---:|
| 1 | (w, ss) | 6.5613 | 1.440 (over the cache alone, 8.0018) |
| 2 | (p1, p1b) | 6.3862 | 0.175 |
| 3 | (p2, p2b) | 6.3334 | 0.053 |

Passes 2 and 3 address with pass 1's written result against features pass
1 wrote backwards onto earlier nodes. The selection chose composition and
revision on its own.

## In the full mixture (10,000 sentences, select split)

| arm | bits per token | vs B3 + D |
|---|---:|---:|
| B3 + D | 4.5897 | |
| + working graph, 1 pass | 4.5897 | 0.0000 |
| + 2 passes | 4.5897 | 0.0000 |
| + 3 passes | 4.5897 | 0.0000 |
| + 3 passes, accumulated prediction | 4.5897 | 0.0000 |
| + 3 passes, frozen (no backward writes) | 4.5897 | 0.0000 |
| + B: independent (w, ss) and (w, w), original features | **4.5743** | **−0.0154** |

Costs, for the added components:
- 1.8 ms per token for 1 pass; 9.1 for 2; 11.4 for 3;
- peak memory 1.2 to 1.3 GB.

## Against the criteria

- **The working graph helps: FAILS.** No working-graph arm improves on
  B3 + D at all; the mixture gives it no weight.
- **Composition helps: FAILS** (no arm differs).
- **Revision helps:** not testable here, since every arm is at B3 + D.

## Why

The selection scored candidates against the wrong baseline: a story bigram
cache alone.
- It kept the operation that best replaces retrieval: (w, ss), which
  addresses earlier nodes by their sentence.
- B3's caches already do that.
- Passes 2 and 3 were then built on a first pass the full model does not
  need.

Credit assignment must measure an operation's gain on top of the model it
will join. That is the main lesson of stage 1.

## A finding from the control, not yet a result

Arm B includes (w, w): the current word addresses individual earlier
occurrences through a node-level lift table.
- On top of B3 + D it gains 0.015 bits, more than D itself added at this
  size (0.020 over B3).
- It came from a control, not from the registered selection. It counts
  only if a selection made against the full model picks it, and it
  confirms.

## Next (stage 1, revision 2, to be planned before running)

- **Selection against the full model:** each candidate's held-out gain is
  measured with the B3 and D components present, on held-out training
  stories.
- **Then the same arms,** with the frozen and independent controls.
