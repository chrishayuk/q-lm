# q-lm

Experiments in language modelling on a language whose grammar is known
exactly: the French of Alain Colmerauer's Q-systems report of 1970, as
rebuilt in [q-systems](https://github.com/chrishayuk/q-systems).

**Nothing here is historical.** The historical machine is the `qsystems`
crate, and nothing in this repository changes it. It is used for three
things:

- **The corpus.** Every sentence of every tree with at most one level of
  embedding, synthesised by the report's rules: 131,424 sentences. In a
  fixed shuffle, one tenth (13,143) is for development, measured during
  experiments. Another tenth (13,143) is for confirmation, and is not read
  until a final evaluation. The rest (105,138) are training sentences.
- **The deeper tests.**
  - 300 sentences of trees with two levels of embedding.
  - 300 more that use only words of the training sentences, so that depth
    is tested apart from unseen words. Some of these words occur only in
    the deeper sentences: `CE`, as in `DE CE QUE`.
- **The judge.** A sentence is grammatical if the report's system, inverted,
  analyses it to exactly one tree. Its depth is read from that tree.

The learners see the training sentences and the vocabulary, and nothing
else: no rules and no trees.

## The question

Can a learner that sees only sentences recover the structure that generated
them, and how many sentences does it need? That is Q-LM-001 and
Q-LM-SAMPLE-001. Each learner is trained on 100, 1,000, 10,000 and 105,138
sentences, and measured on:

- **Development cross-entropy.** Bits per token, END included, on the
  13,143 development sentences.
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
| transformer | 4 layers, width 128, 4 heads, 832,023 parameters; AdamW, 6,000 steps of 64 sentences; the best of every 200 steps on a tenth of its training sentences is kept; three seeds | `transformer/train.py` |

## Running it

```sh
cargo build --release
./target/release/qlm data data              # the corpus split, subsets, deeper test, vocabulary
for s in 1 2 3; do for n in 100 1000 10000 105138; do python3 transformer/train.py data $n 6000 $s; done; done
./target/release/qlm report data            # every model, as a table
./target/release/qlm em data 10000          # inside–outside, round by round
./target/release/qlm mdl data 10000         # pruning by expected rule count
python3 transformer/bench.py data 10000 1   # transformer cost per next token
```

The first run, kept as the baseline, is
[docs/results-run1.md](docs/results-run1.md). QLM-002, which corrects it,
is [docs/results.md](docs/results.md). Inside–outside convergence,
rule pruning (QLM-004) and matched inference cost (QLM-PERF-001) are
[docs/results-qlm004.md](docs/results-qlm004.md). The Llama arm, which
narrows the depth gap to the grammar to almost nothing at full size, is
[docs/results-architectures.md](docs/results-architectures.md). QLM-005,
three generated languages, is [docs/results-qlm005.md](docs/results-qlm005.md).
Which part of the transformer carries depth (rotary positions) is
[docs/results-qlm-arch-001.md](docs/results-qlm-arch-001.md). Facts and
relations (the grammar learner fails; transformers transfer phrasings and
Llama composes, but neither reverses) are
[docs/results-qlm-semantic-001.md](docs/results-qlm-semantic-001.md). Inside
the transformers (answer states, and an entity state before the query is
computed): [docs/results-larql-qlm-sem-001-v2.md](docs/results-larql-qlm-sem-001-v2.md);
how it reaches the answer position (a few attention heads):
[docs/results-larql-qlm-transport-001.md](docs/results-larql-qlm-transport-001.md);
a relation component separable from the entity, and a recombined query, in
Llama: [docs/results-larql-qlm-sem-001-v3.md](docs/results-larql-qlm-sem-001-v3.md);
where the fact is looked up (at the answer position, not the entity's):
[docs/results-larql-qlm-enrich-001.md](docs/results-larql-qlm-enrich-001.md);
where the answer forms, and a fact edited from an external table with no
weight changed: [docs/results-larql-qlm-resolve-001.md](docs/results-larql-qlm-resolve-001.md);
an external graph driven only by activations (relation readable, entity
the bottleneck; facts edited and added at 42 to 62%):
[docs/results-larql-qlm-external-001.md](docs/results-larql-qlm-external-001.md).
How the learner's cost grows (the model stops growing; its bookkeeping
does not): [docs/results-qlm-scale-001-kind1.md](docs/results-qlm-scale-001-kind1.md).
On TinyStories it breaks (whole-sentence contexts never recur; nothing
merges): [docs/results-qlm-scale-001-tinystories.md](docs/results-qlm-scale-001-tinystories.md).
Q-LM v2 on TinyStories: bounded-context classes beat the 5-gram, and the
transformer with little data ([docs/results-qlm-v2-e1-e3.md](docs/results-qlm-v2-e1-e3.md));
abstractions-as-contexts (E4) add nothing beyond ensembling
([docs/results-qlm-v2-e4.md](docs/results-qlm-v2-e4.md)); counted
association attention adds nothing, and the transformer's lead splits into
local generalisation and long context
([docs/results-qlm-attention-001.md](docs/results-qlm-attention-001.md)).
A transformer trained with a 5-gram's window splits v2's 0.29-bit gap into
0.12 of local generalisation and 0.17 of long context
([docs/results-qlm-key-001-b.md](docs/results-qlm-key-001-b.md)). Keys learned
by held-out gain widen with data and recover about 14% of long context's
value ([docs/results-qlm-key-001-cde.md](docs/results-qlm-key-001-cde.md)).

## Direction

The long-term target is a learned, executable grammar that models language
as well as GPT-2 Small (124M parameters). TinyStories is the first
natural-language milestone. In order:

1. Colmerauer's language: done, with the corrections in
   [docs/results-qlm004.md](docs/results-qlm004.md).
2. Independently generated grammar families: QLM-005,
   [docs/qlm005-plan.md](docs/qlm005-plan.md).
3. Facts and compositional relationships in a synthetic language.
4. TinyStories.
5. WikiText, then GPT-2 Small and SmolLM2 (135M) for comparison.

**What stands between steps 2 and 4.** The learner as built does not scale
to natural text.
- It takes the context of a substring to be the whole rest of the
  sentence. In natural text, almost no two contexts match.
- It enumerates every substring of every sentence.

TinyStories needs a different way of finding categories, such as bounded
or clustered contexts, not a larger run of this one. The way the
probabilities are fitted (inside–outside) also suppresses rarely exercised
rules (results-qlm004.md). A learner meant to keep capabilities its data
rarely shows needs an answer to that as well.

## Licence

Apache-2.0, as q-systems.
