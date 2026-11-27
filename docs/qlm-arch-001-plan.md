# QLM-ARCH-001 plan: which part of the architecture carries depth?

Written before any ablation run.

## Question

On Colmerauer's language, a Llama model nearly matches the converged
grammar on deeper sentences. The custom transformer does far worse
(results-architectures.md), and not because of sentence length. Several
things differ between the two at once. Which one matters?

## Arms

One code path, `ARCH=ablate transformer/train.py`, has four switches:

| arm | change from the base | parameters |
|---|---|---:|
| base | none: learned positions, LayerNorm, GELU feed-forward of width 512, separate output layer | 832,023 |
| rope | rotary positions, no position table | 799,255 |
| rms | RMSNorm | 830,871 |
| swiglu | gated SiLU feed-forward of width 341 (to match parameters) | 832,191 |
| tie | output tied to the input embedding | 829,056 |
| all | all four | 795,304 |

- Every arm has 4 layers, width 128 and 4 heads, with the same attention
  code (fused QKV with biases, causal scaled dot product).
- Training is the transformer's: 6,000 steps, AdamW, the best of every 200
  steps on a tenth of the training sentences.
- Seeds 1, 2 and 3, at 1,000 and 105,138 training sentences.

The base arm reimplements the custom transformer. If its results differ
from the custom transformer's by more than the spread between seeds, the
reimplementation is itself a finding, and the arms are compared with base,
not with the custom transformer.

## Measures

- Development bits per token.
- Deeper bits per token, and deeper with corpus words (all 300).
- Grammatical, novel and deeper samples, of 300.

## Reading

An arm "carries depth" if, at 105,138 sentences, its mean on deeper
sentences with corpus words is lower than base's by more than both arms'
seed ranges combined.
- Each single change is read against base.
- The combined arm is read against Llama, which differs from it only in
  the details of Hugging Face's implementation.

Interactions are not resolved by this design. If no single change carries
depth but the combined arm does, that is what is reported.
