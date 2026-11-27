# Results: Q-LM v2, stage E4 (abstractions as contexts): no gain beyond ensembling

Reported against [qlm-v2-plan.md](qlm-v2-plan.md). Prototype `v2/hier.py`,
with the fixes asked for after E1 to E3:
- START is never a predicted class, and next-class probabilities are
  checked to sum to 1.000000;
- the SVD has a fixed start vector;
- the vocabulary is from training text only;
- three splits of the development sentences:
  - 1 to 1,000 for fitting the mixture weights, by EM;
  - 1,001 to 3,000 for comparing settings;
  - 3,001 to 7,000 for one confirmation run.

**E4.** Pass 1 learns nodes from word contexts. Pass k rewrites every
context in pass k−1's nodes and learns new nodes from those. The predictor
mixes the word 5-gram with one class trigram per pass.

**Two controls, as asked:**
- **flat:** one pass with as many nodes as the passes together;
- **seeds:** as many independent pass-1 models, with different seeds, as
  there are passes. That is the same number of mixture components, with no
  hierarchy.

Grid: [tables/v2-e4-grid.txt](tables/v2-e4-grid.txt).

## Selection split (development 1,001 to 3,000)

| training sentences | passes / components | hierarchy | seeds (same count) | flat (same nodes) |
|---:|---:|---:|---:|---:|
| 10,000 | 1 | 5.0297 | – | – |
| 10,000 | 2 | 4.9902 | 4.9994 | 5.0320 |
| 10,000 | 3 | 4.9757 | 4.9782 | 5.0386 |
| 10,000 | 4 | **4.9635** | 4.9740 | 5.0490 |
| 10,000 | 8 | 4.9434 | | |
| 100,000 | 1 | 4.0682 | – | – |
| 100,000 | 2 | 4.0624 | **4.0560** | 4.0629 |
| 100,000 | 3 | 4.0593 | **4.0535** | 4.0806 |
| 100,000 | 4 | 4.0575 | **4.0516** | 4.0783 |
| 100,000 | 8 | 4.0548 | | |

(The 5-gram alone: 5.1298 and 4.1341.)

## Confirmation split (development 3,001 to 7,000), 100,000 sentences

| model | bits per token |
|---|---:|
| 5-gram | 4.2449 |
| v2, one pass | 4.1741 |
| v2, four hierarchical passes | 4.1615 |
| v2, four independent seeds | **4.1563** |
| Llama (2.1M parameters, seed 1) | **3.8440** |

## Against the plan

**E4 is useful** if one pass of abstraction contexts beats lexical
contexts alone by at least 0.02 bits, at either size. Read fairly, that
means against the seeds control, which has the same number of components.

| comparison | 10,000 | 100,000 |
|---|---:|---:|
| 2 passes against 1 | gains 0.040 | gains 0.006 |
| 2 passes against 2 seeds | gains 0.009 | **loses** 0.006 |
| 4 passes against 4 seeds | gains 0.010 | **loses** 0.006 |
| confirmation, 4 passes against 4 seeds | | **loses** 0.005 |

**E4 fails.** Nearly all of what extra passes add comes from having more
mixture components, which independent class models give as well or
better. At 100,000 sentences, abstractions built on abstractions are
slightly worse than independent ones.

The flat control also shows that more nodes in one model hurt.

## What this says

- **Re-labelling contexts by hard clusters, pass after pass, does not
  learn anything the first pass did not.** A word's pass-2 context is its
  neighbours' pass-1 nodes, and pass 1 already grouped those neighbours.
  So pass 2 mostly re-finds pass 1's clustering, at a coarser grain. The
  small gain is a second opinion, the same as a second seed gives.
- **The gap to the transformer is unchanged:** 0.31 bits on the
  confirmation sentences (4.156 against 3.844).
- **What E4 would need to add something:** contexts the first pass cannot
  see.
  - Longer-range structure: the clause or the sentence so far, summarised
    by nodes.
  - Phrases as units: a node for `a little girl`, not only for `girl`.
  - Soft, context-dependent memberships, so a word's node depends on its
    context, rather than one hard label per word.

  Each is a different mechanism, not more passes of this one.

## Next

The 0.31-bit gap is about what the model conditions on. The class trigram
and the 5-gram both see at most four words back. The transformer sees the
whole sentence. The next experiment is longer, structured context:
- phrase nodes;
- a sentence-so-far summary built from nodes;

against the same controls.
