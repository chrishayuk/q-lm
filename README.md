# q-lm

Experiments in language modelling on a language whose grammar is known
exactly: the French of Alain Colmerauer's Q-systems report of 1970, as
rebuilt in [q-systems](https://github.com/chrishayuk/q-systems).

**Nothing here is historical.** The historical machine is the `qsystems`
crate, and nothing in this repository changes it. It is used for three
things:

- **The corpus.** Every sentence of every tree with at most one level of
  embedding, synthesised by the report's rules: 131,424 sentences. A fixed
  tenth (13,143) is held out, and the rest (118,281) are training sentences.
- **The deeper test.** 300 sentences of trees with two levels of embedding.
- **The judge.** A sentence is grammatical if the report's system, inverted,
  analyses it to exactly one tree. Its depth is read from that tree.

The learners see the training sentences and the vocabulary, and nothing
else: no rules and no trees.

## The question

Can a learner that sees only sentences recover the structure that generated
them, and how many sentences does it need? That is Q-LM-001 and
Q-LM-SAMPLE-001. Each learner is trained on 100, 1,000, 10,000 and 118,281
sentences, and measured on:

- **Held-out cross-entropy.** Bits per token, END included, on the 13,143
  held-out sentences.
  - The floor is the true distribution, the graph of all 131,424 sentences
    (QSYS-E16). It is uniform over the corpus.
- **Deeper sentences.** Bits per token on the 300 sentences with two levels
  of embedding.
  - The true distribution gives them zero.
  - The report's rules read as an open grammar (QSYS-E17) give them all a
    probability. That reference is given the grammar, so it is not a
    learner.
- **Samples.** 300 samples per model: how many are grammatical, how many of
  those are not among its training sentences, and how many are deeper than
  anything it was trained on.
- **Cost.** Training time and model size.

## The learners

| learner | what it is | where |
|---|---|---|
| Kneser–Ney n-gram, n = 2 to 6 | interpolated, one discount of 0.75 | `src/ngram.rs` |
| merged graph, k = 1 to 4 | the prefix tree of the training sentences, with states merged when their continuations of up to k words agree (k-tails, Biermann and Feldman 1972), counted | `src/ktails.rs` |
| transformer | 4 layers, width 128, 4 heads, 832,023 parameters; AdamW, 6,000 steps of 64 sentences; the best of every 200 steps on a tenth of its training sentences is kept | `transformer/train.py` |

## Running it

```sh
cargo build --release
./target/release/qlm data data              # the corpus split, subsets, deeper test, vocabulary
for n in 100 1000 10000 118281; do python3 transformer/train.py data $n 6000; done
./target/release/qlm report data            # every model, as a table
```

The results are in [docs/results.md](docs/results.md).

## Licence

Apache-2.0, as q-systems.
