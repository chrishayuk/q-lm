# Q-LM v2 plan: a hierarchical, non-destructive, sparsely executed graph learner

v1 (the substitution grammar) is kept as the reference. It is exact, and it
learns recursive grammars from constrained languages. On TinyStories it
merges almost nothing, because whole-sentence contexts never recur
(results-qlm-scale-001-tinystories.md). v2 is a new learner, built in
stages, with TinyStories in the loop from the first stage.

## The data and the bar

`data-ts`:
- TinyStories sentences from the first 20,000 training stories (346,098);
- development sentences from validation (13,959);
- lowercased, with punctuation as tokens;
- a vocabulary of training words seen twice or more, plus `<unk>` (8,525
  in all), fixed for every model and size. Development has 0.21% `<unk>`.

Every model is scored on the first 2,000 development sentences, in bits
per token with END included.

| training sentences | unigram | bigram | trigram | 5-gram | Llama arm |
|---:|---:|---:|---:|---:|---|
| 1,000 | 8.145 | 6.149 | 5.951 | 5.981 | (training) |
| 10,000 | 8.031 | 5.440 | 5.044 | 5.032 | (training) |
| 100,000 | 7.935 | 4.921 | 4.233 | 4.084 | (training) |
| 346,098 | 7.929 | 4.817 | 4.004 | 3.759 | |

(The n-grams are interpolated Kneser–Ney with discount 0.75, from
`qlm baselines`.)

**The first bar is the 5-gram at the same size.** The transformer is the
second.

## Stages

| stage | builds | measured by |
|---|---|---|
| E1 | a sparse index of contexts of widths 1, 2, 4 and 8, each side, for words and recurring phrases | memory and time per million tokens |
| E2 | weighted similarities between words (then phrases) from their context vectors, exact via the inverted index | below |
| E3 | identity nodes and abstraction nodes: every word keeps its node, and abstractions are added as nodes with weighted memberships (top m, m tested at 1, 2, 4, 8 and adaptive) | below |
| E4 | contexts rewritten in terms of the abstractions, and similarities recomputed on them: learned abstractions become contexts for further learning | below |
| E5 | sparse probabilistic prediction over the active nodes | below |
| E6 | bindings and relations (QLM-RELATION-001) | the semantic worlds |
| E7 | incremental learning and consolidation (QLM-INCR-001) | its plan |

## How E1 to E4 are judged before any grammar is built

By **held-out prediction**, not by how many categories collapse. A
class-based predictor uses the learned abstractions:
- P(next | the previous k words' abstractions);
- interpolated with the Kneser–Ney word model;
- its weight fitted on the first 1,000 development sentences;
- scored on the next 2,000.

If the abstractions are useful, this beats the word n-gram alone at the
same size. The comparison grid:
- context widths 1, 2, 4 and 8;
- frequency-weighted (PPMI) against unweighted (binary) context vectors;
- lexical contexts against abstraction contexts (E4, one and two passes);
- exact similarity against approximate retrieval, only if exact is too
  slow.

**Preserving distinctions** is reported too. For pairs of words the
abstractions group together, does the word model still tell them apart
where the data does?
- The share of development positions where the two grouped words'
  word-model probabilities differ by more than 2×.
- Grouping should not make them equal.

## What would count

- **E1 to E4 are useful** if, at 10,000 and at 100,000 training sentences,
  the interpolated class predictor beats the 5-gram alone by at least 0.05
  bits per token on the scored development sentences.
- **E4 is useful** if one pass of abstraction contexts beats lexical
  contexts alone by at least 0.02 bits, at either size.
- **A first serious natural-language model:** a v2 model trained on 10,000
  TinyStories sentences that:
  - beats the 5-gram at 10,000 (5.03 bits);
  - uses under 4 GB;
  - takes no backpropagation.
