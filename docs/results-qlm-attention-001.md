# Results: QLM-ATTENTION-001, counted association attention adds nothing; where the transformer's lead is

Reported against [qlm-attention-001-plan.md](qlm-attention-001-plan.md).
Prototype `v2/attn.py`. The table is
[tables/attention-001-10k.txt](tables/attention-001-10k.txt).

## The arms, at 10,000 sentences (comparison split)

| arm | all positions | positions 6+ | the attention component's mixture weight |
|---|---:|---:|---:|
| A: v2 (5-gram + 4 class models) | 4.9740 | 4.7958 | – |
| B: 8-gram in place of the 5-gram | 4.9970 | 4.7960 | – |
| C: uniform over earlier words | 4.9738 | 4.7954 | 0.001 |
| D: recency (ρ = 0.85, fitted) | 4.9737 | 4.7954 | 0.001 |
| E: content (cosine, τ = 0.5, fitted) | 4.9739 | 4.7956 | 0.001 |
| F: content and relative position | 4.9740 | 4.7957 | 0.000 |
| G: F plus a class-level head | 4.9740 | 4.7957 | 0.000 |

**The criterion fails: no arm helps.**
- EM gives the attention component a weight of 0.001 or less in every
  arm, on the fitting sentences.
- The 8-gram is worse than the 5-gram, by sparsity.
- 100,000 sentences were not run, since none of the arms was used at all.

**Why the component is useless.** Its values A(w | u), "w appears later in
the same sentence as u", are too diffuse to add anything to a 5-gram and 4
class models. They say roughly which words go together in a sentence, but
not what comes next.

## Where the transformer's lead actually is

The transformer against the 5-gram alone, by position in the sentence. The
comparison split, development sentences 1,001 to 3,000:

| training sentences | positions 0–1 | positions 2–5 | positions 6+ |
|---:|---:|---:|---:|
| 10,000 | +0.096 (4,000 tokens) | +0.142 (7,860) | −0.004 (14,005) |
| 100,000 | +0.019 | **+0.347** | **+0.490** |

(bits per token by which the transformer is better)

At 100,000 sentences the transformer's lead has two parts:
- **Inside the 5-gram's window, 0.35 bits** at positions 2 to 5, where
  the 5-gram sees the whole history. This is generalisation from the same
  context, not more context.
  - The 5-gram's estimate of P(w | these 2 to 4 words) is from counts.
  - The transformer's comes from representations shared across similar
    histories.
  - The class models give a little of that (0.07 to 0.09 bits overall),
    far from 0.35.
- **Beyond the window, 0.49 bits** at positions 6 and later. That part
  does use longer context, which the counted association could not
  capture.

At 10,000 sentences, neither part has formed yet. The transformer is not
ahead beyond position 5 at all.

## What it says for v2

Two separate problems, needing two separate mechanisms.

1. **Generalising local prediction** (most of the gap at positions 2 to 5).
   The history should be smoothed by similarity: P(w | h) borrowed from
   histories h′ whose distributional vectors are near h's, weighted by
   that similarity. That is a nearest-neighbour or kernel estimate over
   the stored observations, learned by counting, not backpropagation. It
   is closer to what the transformer's shared representations do than
   word classes are, because it keeps each history's identity.
2. **Using long context** (positions 6+). The values must say what comes
   next given the earlier word and the local context jointly, not what
   appears anywhere later. Examples: retrieval over stored training
   positions whose local and longer contexts both match, or pairs of
   (distant word, recent word). The selection is the attention. The
   values have to be predictive.

Both are measured against the same controls, on the same splits.
