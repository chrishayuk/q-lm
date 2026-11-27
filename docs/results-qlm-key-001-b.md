# Results: QLM-KEY-001, arm B (similar histories), and what long context is worth

Reported against [qlm-key-001-plan.md](qlm-key-001-plan.md). TinyStories
`data-ts`, development sentences 1,001 to 3,000. Bits per token, END
included.

## The trained control: a transformer limited to the 5-gram's context

The control is `ARCH=mistralw`:
- the Llama arm's shape, with Mistral's sliding window of 2 across 4
  layers, so each position sees exactly the 4 previous tokens (checked:
  tokens further back do not change the output);
- trained exactly as the full-context arm: seed 1, 6,000 steps.

| training sentences | positions | full context | window of 4 | what long context is worth |
|---:|---|---:|---:|---:|
| 10,000 | all | 5.074 | 5.023 | −0.051 |
| 10,000 | 5+ | 4.981 | 4.925 | −0.056 |
| 100,000 | all | **3.760** | 3.935 | **+0.174** |
| 100,000 | 0–1 | 5.125 | 5.151 | +0.026 |
| 100,000 | 2–4 | 3.727 | 3.778 | +0.051 |
| 100,000 | 5+ | 3.430 | 3.688 | **+0.258** |

- **At 100,000 sentences, long context is worth 0.17 bits overall, and
  0.26 at positions 5+.** At positions 2 to 4, where the two see the same
  words, the two models still differ by 0.05: they are different trained
  models.
- **At 10,000 sentences, long context hurts** (−0.05). With little data,
  the full-context model fits worse.

## The decomposition of v2's gap, at 100,000 sentences

| model | bits per token |
|---|---:|
| 5-gram | 4.134 |
| v2 (5-gram + 4 class models) | 4.052 |
| transformer, window of 4 | 3.935 |
| transformer, full context | 3.760 |

- **Generalisation with the same context:** the windowed transformer beats
  the 5-gram by 0.199 bits, and v2 by 0.117.
- **Long context:** 0.174.
- **v2's whole gap to the full transformer, 0.292 bits, is therefore about
  0.12 local generalisation plus 0.17 long context.**

## Arm B: similar histories

The arm borrows across training histories (u, v) where v = x_{t−1} and u
is near x_{t−2} (cosine, top k, weight exp(cos / τ)). k and τ are chosen
on development 1 to 1,000.

| training sentences | v2: all | v2 + B: all | v2: 2–4 | v2 + B: 2–4 | v2: 5+ | v2 + B: 5+ | B's weight |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10,000 | 4.9740 | 4.9726 | 4.9629 | 4.9580 | 4.8201 | 4.8163 | 0.033 |
| 100,000 | 4.0516 | 4.0490 | 3.9060 | 3.9013 | 3.8305 | 3.8215 | 0.067 |

- **The criterion fails.** B lowers positions 2 to 4 by 0.005 at 100,000
  sentences, against the 0.05 required and the 0.12 that local
  generalisation is worth.
- **It makes positions 0 and 1 worse** (5.148 to 5.174). There it falls
  back to bigram counts, and one global mixture weight cannot switch it
  off by position.
- **Why it is too narrow:** it borrows only across histories with the same
  last word. The transformer generalises across whole histories.

## What it says

The two parts of the gap now have measured sizes, about 0.12 and 0.17
bits, and so have targets.
- **For 0.12 (local generalisation):** whole short histories compared by
  their combined vectors, not one-word-at-a-time smoothing. Also mixture
  weights that depend on position or on the history's count, so that a
  component is trusted only where it helps.
- **For 0.17 (long context):** KEY-001's arms C to E. These are the
  learned keys pairing the recent word with an earlier word or node,
  chosen by information gain.
