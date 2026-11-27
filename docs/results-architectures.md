# Results: the depth gap is the transformer's, not transformers'

The earlier comparisons set the learned grammar against one transformer,
the custom model of `transformer/train.py`:
- learned absolute positions;
- a GELU feed-forward;
- an output layer separate from the input embedding, with a bias.

A Llama-architecture model of about the same size (`ARCH=llama`) was added
for LARQL, because VINDEX3 admits it. It has rotary positions, RMSNorm, a
gated SiLU feed-forward and tied embeddings. It was trained identically:
same data, steps, optimiser and checkpoint choice, three seeds.

It changes the headline. **The Llama model is about as good as the
converged grammar on deeper sentences, and better on the corpus.** The
large depth advantage reported so far was over the custom transformer, not
over transformers.

All numbers are development numbers. The confirmation set has not been
read.

## Colmerauer's language, the same sentences

Development: the first 200 sentences. Deeper: the first 100 deeper
sentences with corpus words. These are the sets of `qlm prefix` and
`qlm em`. In bits per token:

| training sentences | model | development | deeper |
|---:|---|---:|---:|
| 1,000 | converged grammar (40 rounds) | 1.0346 | **1.8124** |
| 1,000 | Llama, seeds 1 / 2 / 3 | 1.0513 / 1.0505 / 1.0553 | 2.3685 / 2.3718 / 2.1686 |
| 1,000 | custom transformer, seed 1 | 1.0620 | 2.9696 |
| 10,000 | converged grammar | 1.0392 | **2.1928** |
| 10,000 | Llama | 1.0284 / 1.0292 / 1.0294 | 2.2841 / 3.0270 / 2.4851 |
| 10,000 | custom transformer | 1.0339 | 3.6941 |
| 105,138 | converged grammar | 1.0387 | **2.3650** |
| 105,138 | Llama | **1.0279 / 1.0269 / 1.0285** | 2.4458 / 2.9721 / 2.3865 |
| 105,138 | custom transformer | 1.0278 | 4.7464 |

- **The grammar is still best at depth at every size**, but at full size
  by only 0.02 to 0.6 bits over Llama, depending on the seed. At 1,000
  sentences its lead is 0.36 to 0.56.
- **Llama gets worse with more data, but only a little.** On all 300 deeper
  sentences with corpus words, from 1,000 to 105,138:
  - seed 1: 2.37 to 2.41;
  - seed 2: 2.36 to 2.93;
  - seed 3: 2.18 to 2.34.

  This passes gate 0 of LARQL-QLM-001: it rises on every seed. But the
  effect is weak and noisy, where the custom transformer's was 2.9 to 4.8.
- **On the corpus, Llama and the custom transformer are level**, and both
  are about 1% better than the grammar.

## Not a length effect

The custom transformer learns one embedding per position. Deeper sentences
are longer: up to 27 words, where training sentences have at most 20. In
all, 175 of the 300 deeper sentences with corpus words are longer than
every training sentence. Positions past the training lengths never get any
gradient, so the custom transformer's failure could have been about length
rather than depth.

It is not. On the 125 deeper sentences no longer than 20 words, it is as
bad as on the rest. At 105,138 training sentences, in bits per token:

| model | 20 words or fewer (125) | more than 20 words (175) |
|---|---:|---:|
| converged grammar | 2.7236 | 2.1390 |
| Llama, seeds 1 / 2 / 3 | 2.7576 / 3.2317 / 2.6057 | 2.2257 / 2.7580 / 2.1959 |
| custom transformer, seed 1 | 4.9677 | 4.5670 |

(`qlm score` for the grammar. The shorter sentences cost more per token
for every model.)

Which part of the architecture makes the difference has not been tested.
Several things changed at once: positions, normalisation, feed-forward and
tied embeddings. A GPT-2 arm (learned positions, LayerNorm, GELU, tied
embeddings) gave 2.78 at 1,000 sentences, seed 1, between the two.

## What this changes

- **"Superior recursive prediction" is withdrawn as a general claim.** The
  grammar leads the Llama model on deeper sentences at every size. The lead
  is large at 1,000 sentences and small, seed-dependent, at full size.
- **What still separates them:**
  - the grammar derives every deeper sentence, and its mechanism is
    explicit;
  - it is better at depth from little data.
- **What does not:** depth at full size, where the two are close.
- **For LARQL-QLM-001**, the Llama model is a weaker case of the behaviour
  than the custom transformer was. The custom transformer cannot be loaded
  by VINDEX3, but it could be studied in PyTorch. The plan may need a
  second subject; that is a change, to be made before probing.
- **For QLM-005**, the families were run with the custom transformer only.
  A Llama arm on each family is needed before any comparison there can be
  called a comparison with transformers.
