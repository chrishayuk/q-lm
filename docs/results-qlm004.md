# Results: inside–outside convergence, QLM-004 (pruning), QLM-PERF-001

This continues [results.md](results.md) and corrects part of it.

**The correction.** results.md scored the learned grammar after five rounds
of inside–outside. That number of rounds was not chosen by anything. It
turns out to matter a great deal: five rounds is short of convergence, and
the grammar's advantage on deeper sentences shrinks as training runs on.
The grammar's 1.59 bits per token on deeper sentences, and its 34 to 44
deeper samples in 300, are the scores of a model stopped early.

All numbers are on the development and deeper sentences. The confirmation
set has still not been read.

## Inside–outside, run to convergence (`qlm em data N`)

The same structure as before, re-estimated for up to 40 rounds.
- Development: the first 200 sentences.
- Deeper: the first 100 deeper sentences that use corpus words, the sets
  `qlm prefix` reads.
- Bits per token include END and the usual floor (0.999 of the grammar's
  probability, 0.001 of a uniform spelling).

| training sentences | rounds | training | development | deeper | deeper samples, of 300 |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 2 | 1.1998 | 1.2082 | **1.3928** | 56 |
| 1,000 | 5 | 1.0655 | 1.0709 | 1.6004 | 44 |
| 1,000 | 8 | 1.0247 | 1.0339 | 1.8065 | 2 |
| 1,000 | 40 | 1.0225 | 1.0346 | 1.8124 | 1 |
| 10,000 | 2 | 1.2224 | 1.2145 | **1.3907** | 33 |
| 10,000 | 5 | 1.1102 | 1.0956 | 1.5884 | 42 |
| 10,000 | 12 | 1.0576 | 1.0429 | 2.1386 | 10 |
| 10,000 | 40 | 1.0541 | 1.0392 | 2.1928 | 12 |
| 105,138 | 2 | 1.2226 | 1.2142 | **1.3905** | 33 |
| 105,138 | 5 | 1.1100 | 1.0952 | 1.5901 | 34 |
| 105,138 | 12 | 1.0571 | 1.0422 | 2.2702 | 19 |
| 105,138 | 40 | 1.0538 | 1.0387 | 2.3650 | 12 |

The full curves are in [tables/](tables/) (`em-*.md`).

- **Inside–outside converges in about 12 to 20 rounds.** After that,
  development changes by less than 0.003 bits.
- **Each round makes the corpus likelier and deeper sentences less likely.**
  Deeper sentences are best after two rounds (1.39 bits) and worst at
  convergence: 1.81 at 1,000 sentences, 2.19 at 10,000, and 2.37 at
  105,138. Deeper samples fall from 33 to 56 in 300 to between 1 and 12.
- **More data makes depth worse here too**, once training converges. This is
  the transformer's pattern (results.md), at about half its size: the
  transformer gives 2.97, 3.69 and 4.75 on the same 100 sentences.
- **The structure keeps depth even where the probabilities don't.** At
  every size and every round, the grammar derives all 300 deeper sentences
  of corpus words. What inside–outside lowers is the probability of the
  recursive rules, because the training sentences never use them twice.
  Maximum likelihood on one level of embedding is doing what it should.

This answers, for the grammar, a question posed about the transformer. Does
it learn a reusable recursive mechanism and suppress its application, or a
bounded one? The grammar learns the mechanism and its training suppresses
it. Whether the transformer does the same is open (LARQL-QLM-001). The
grammar is now a reference case where the answer is known.

Choosing the number of rounds by the deeper scores would be fitting to the
test. The development set cannot choose it either: development sentences
have one level of embedding, and development scores keep improving to
convergence. The honest setting is convergence, and the comparison below
uses it.

## QLM-004: pruning by expected rule count (`qlm mdl data N`)

The grammar after 5 rounds loses every rule whose expected count on the
training sentences is below a threshold. The categories that can then no
longer finish a derivation, or be reached from the start, go too. Five more
rounds re-estimate what is left, so the grammar has had ten rounds in all.
The tables are in [tables/](tables/) (`mdl-*.md`). At 1,000 sentences, a threshold of 50 or more leaves nothing.

**Description length** is two parts, on the training sentences alone.
- **The grammar.** Each category's rule count (Elias gamma). Each rule
  costs one bit for its kind, then either two categories or a word, then
  (1/2) log2 N bits for its probability, where N is the number of training
  tokens.
- **The sentences.** Each one at -log2 of its floored probability.

Grammar learned from 1,000 sentences:

| threshold | categories | rules | description, bits | training not derivable | development | deeper | deeper derivable, of 300 | ms per next token |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 2,396 | 38,121 | 1,193,402 | 0 | 1.0402 | 1.8136 | 300 | 143 |
| 0.1 | 976 | 4,988 | 159,241 | 0 | **1.0395** | 2.0115 | 300 | 5.6 |
| 0.5 | 296 | 1,166 | 46,300 | 0 | 1.0413 | 2.3109 | 300 | 0.45 |
| 1 | 192 | 659 | 32,787 | 0 | 1.0443 | 2.8795 | 204 | 0.15 |
| **2** (shortest) | 149 | 422 | **27,212** | 11 | 1.0609 | 4.8415 | 5 | 0.09 |
| 5 | 77 | 180 | 42,171 | 321 | 2.3606 | 4.8403 | 5 | 0.03 |

Grammar learned from 10,000 sentences:

| threshold | categories | rules | description, bits | training not derivable | development | deeper | deeper derivable, of 300 | ms per next token |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 192 | 1,772 | 219,375 | 0 | 1.0631 | 2.0821 | 300 | 1.10 |
| 2 | 192 | 1,229 | 205,620 | 0 | 1.0623 | 2.1785 | 300 | 0.38 |
| 10 | 182 | 781 | 193,872 | 0 | **1.0608** | 2.3292 | 300 | 0.28 |
| 20 | 169 | 588 | 190,021 | 0 | 1.0683 | 3.9333 | 123 | 0.11 |
| **50** (shortest) | 121 | 315 | **185,868** | 80 | 1.0870 | 4.8394 | 5 | 0.05 |
| 100 | 87 | 185 | 254,602 | 1,264 | 1.4985 | 4.8394 | 5 | 0.03 |

Development is scored on all 13,143 sentences here, deeper on the first 100.
The time per next token is measured on the first 50 development sentences.

- **Pruning shrinks the grammar a long way at almost no cost on the
  corpus.**
  - The 1,000-sentence grammar goes from 38,121 rules to 1,166, and from
    143 ms to 0.45 ms per token, at a cost of 0.001 bits of development.
  - The 10,000-sentence grammar goes from 1,772 rules to 781 at no cost,
    and from 1.10 ms to 0.28 ms.
- **Minimum description length, as coded here, chooses wrongly.** At both
  sizes the shortest description is a grammar that has lost the recursion.
  - It derives 5 of the 300 deeper sentences.
  - It can no longer derive some training sentences: 11 at 1,000, 80 at
    10,000.
  - The recursive rules are used rarely on sentences with one level of
    embedding, so the description saves more by dropping them than it
    loses.
  - A different code would choose differently. But changing the code until
    it keeps the recursion would be choosing by the deeper test.
- **Development chooses better, but not for a principled reason.** The best
  development score is at a threshold of 0.1 (1,000) and 10 (10,000), and
  both keep all 300 deeper sentences derivable. But the development
  sentences cannot see depth, and one step further (20 at 10,000) loses
  most of it.
- **The size of the grammar is not the number of abstractions.** At
  thresholds where nothing is lost, the grammars keep 182 to 296 categories.
  Tens of meaningful categories did not come out of pruning: the categories
  under 150 come only with the loss of the recursion. Splitting
  over-merged categories, and merging categories that only differ by
  substring, are still to be tried.

## QLM-PERF-001: inference cost on the same footing (`transformer/bench.py`)

The transformer was retrained for seed 1 at 1,000, 10,000 and 105,138
sentences, so that its weights could be kept. The scores reproduce the
published ones to about 1e-8 at 1,000 and 10,000. At 105,138 the deeper
score moved from 4.71 to 4.74, within the spread of the three seeds.

Both models were measured on the same 300 sentences as `qlm prefix` (200
development, 100 deeper), every prefix, END included: 5,467 next-token
distributions. Each ran on one CPU thread, one sentence at a time. The output is [tables/bench.txt](tables/bench.txt).

| model | development | deeper | ms per next-token distribution |
|---|---:|---:|---:|
| transformer, 1,000 sentences, KV cache | 1.0620 | 2.9696 | 0.264 |
| transformer, 10,000 sentences, KV cache | 1.0339 | 3.6941 | 0.264 |
| transformer, 105,138 sentences, KV cache | **1.0278** | 4.7464 | 0.260 |
| transformer, any size, whole prefix again | | | 0.41 |
| grammar, 10,000 sentences, 5 rounds | 1.0955 | 1.5883 | 1.36 |
| grammar, 10,000 sentences, converged (40 rounds) | 1.0392 | 2.1928 | 1.10 (measured at 10 rounds) |
| grammar, 10,000 sentences, pruned at 10 | 1.0608 (all) | 2.3292 | 0.28 |
| grammar, 1,000 sentences, 5 rounds | 1.0708 | 1.6003 | 176 |

- The cached next-token distributions agree with the uncached ones to
  2.2e-6.
- The transformer's speed is the same at every size: its cost is set by its
  architecture, not by what it learned.
- **The transformer is faster than the unpruned grammars**, by about 4× at
  10,000 sentences and by about 670× at 1,000.
- **Pruned, the grammar is level with it**: 0.28 ms against 0.26 ms.

These are wall times of unoptimised code: PyTorch called once per token,
against Rust with hash maps. Neither has been optimised. The transformer's
time is mostly per-call overhead rather than its 1.7 million operations per
token. Neither figure is a bound on what the architecture can do.

## Where this leaves the comparison

| | transformer, 105,138 | grammar, 105,138, converged |
|---|---:|---:|
| development (first 200) | **1.028** | 1.039 |
| deeper, corpus words (first 100) | 4.75 | **2.37** |
| deeper sentences derivable | not applicable: every string has probability | 300 of 300 |
| deeper samples, of 300 | 0 to 1 (3 seeds) | 12 |

- **On the corpus, the transformer is ahead** by about 1%.
- **On deeper sentences, the converged grammar is ahead** by about 2.4 bits
  per token. That is a smaller lead than results.md showed, but still a
  large one.
- **Both get worse at depth with more data.**
- **The grammar's structure keeps depth while its probabilities give it
  up.** For the transformer, which of these is true is unknown.
- **Inference cost is level once the grammar is pruned.** Unpruned, the
  grammar is slower. The claim that the compact grammar is the faster
  machine is withdrawn: it is faster than the larger grammar, not than the
  transformer.

## Next

- **Category splitting and merging.** Tens of meaningful categories did not
  come out of pruning.
- **A prior that does not punish recursion.** An example is tying the
  probabilities of rules that differ only in their depth. It must be
  justified from the training sentences, not from the deeper test.
- **An unseen synthetic grammar family (QLM-005).** This would show whether
  any of this is a property of this one language.
- **LARQL-QLM-001.** Does the transformer, like the grammar, keep a
  recursive mechanism that its training suppresses?
