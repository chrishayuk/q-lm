# Results: QLM-002 (qualification) and QLM-003 (a learned grammar)

The first run is kept as the baseline in [results-run1.md](results-run1.md).
This file is the qualified rerun, and the first learner of hierarchical
structure.

## What changed from the first run

- **The split.** 105,138 training sentences, 13,143 development sentences,
  and 13,143 confirmation sentences. The confirmation set has not been read
  by anything. Every number here is on the development set.
- **Normalisation.** Every model's next-token distributions are checked to
  sum to 1 (the last column of the main table, at most 5e-14).
  - The transformer no longer gives probability to PAD or the start token.
  - The merged graph is uniform once a prefix leaves it, where before it
    gave zero.
- **A second deeper test** of 300 sentences uses only words of the
  training sentences. That separates depth from the unseen word `CE`, which
  occurs only in sentences with two levels of embedding. All 300 use only
  words found in every training subset, down to 100 sentences.
- **A negative test** of 300 development sentences with two words swapped,
  each rejected by the report's analysis. It measures overgeneration without
  sampling.
- **Seeds.** The transformer was run with three seeds at each size. The
  n-gram and merged-graph learners are deterministic.
- **Sampling.** In the merged-graph rows, bits come from the graph with a
  floor mixed in, and samples from the graph alone. The rows say so.

## The transformer: better on the corpus, worse at depth, on every seed

Bits per token, lower is better. All three seeds agree closely.

| training sentences | development | deeper, corpus words only | grammatical samples (of 300) | deeper samples |
|---:|---:|---:|---:|---:|
| 100 | 1.77, 1.86, 1.88 | 3.42, 3.53, 3.61 | 197, 214, 196 | 0, 0, 0 |
| 1,000 | 1.065, 1.070, 1.065 | 2.92, 2.94, 2.82 | 262, 271, 254 | 0, 0, 1 |
| 10,000 | 1.043, 1.041, 1.042 | 3.65, 3.58, 3.47 | 289, 295, 294 | 0, 0, 0 |
| 105,138 | 1.038, 1.038, 1.038 | 4.67, 4.79, 4.93 | 296, 300, 296 | 0, 0, 0 |

- **On the corpus it reaches the floor.** The true distribution gives the
  development set 1.0361 bits.
- **Away from the corpus it gets worse.** From 1,000 sentences on, more
  training makes the deeper sentences less likely, on every seed. This
  happens even when every word is known.
- **It almost never generates depth.** One deeper sentence in 3,600
  samples.
- **The learning curves are coarse.** They are logged every 250 steps, and
  every run with 1,000 sentences or more is within 5% of the floor at the
  first point. Within 1% takes 1,500 to 2,500 steps at 10,000 and 105,138
  sentences. Runs with 1,000 sentences never get within 1%.

## QLM-003: a grammar learned by substitutability

`src/subst.rs` is given only the training sentences and the vocabulary.

1. **Categories.** Every substring of every sentence is grouped with every
   other substring that ever occurs in the same context (the words before
   and after it). This is the substitutability of Clark and Eyraud (2007).
   Each group is a category.
2. **Rules.** Each split of each member, `w = u v`, gives a binary rule,
   and each one-word member a word rule.
3. **Probabilities.** These are re-estimated by five rounds of
   inside–outside on the training sentences, with a smoothing count of 1e-3
   per rule.

Nothing about the generating grammar is given. The report's analysis is
used only to judge the results, never to choose rules.

| training sentences | categories | rules | trained in | development derivable | bits/token | deeper, corpus words: derivable | ungrammatical: derivable | P(derivation finishes) | grammatical samples | of them not in training | of them deeper |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100, structure only | 4,432 | 42,072 | 0.01 s | 7 of 13,143 | 5.00 | 0 of 300 | 0 of 300 | 1.000000 | 298 | 9 | 1 |
| 1,000, structure only | 2,396 | 38,121 | 0.05 s | 13,143 of 13,143 | 2.78 | 300 of 300 | 1 of 300 | 0.000114 | none finish | – | – |
| 1,000, with inside–outside | 2,396 | 38,121 | 22.5 s | 13,143 of 13,143 | **1.0786** | 300 of 300 | 1 of 300 | 1.000000 | **283** | 280 | **44** |
| 10,000, structure only | 192 | 1,772 | 0.37 s | 13,143 of 13,143 | 2.77 | 300 of 300 | 1 of 300 | 0.000127 | none finish | – | – |
| 10,000, with inside–outside | 192 | 1,772 | 6.1 s | 13,143 of 13,143 | 1.1075 | 300 of 300 | 1 of 300 | 1.000000 | 280 | 259 | 42 |
| 105,138, with inside–outside | 192 | 1,772 | 64.8 s | 13,143 of 13,143 | 1.1075 | 300 of 300 | 1 of 300 | 1.000000 | 280 | 85 | 34 |

What it shows:

- **The recursion is found, from 1,000 sentences.** One learned category
  holds both `BENOIT` and `LE FAIT QUE BEAUCEVILLE EST CONSTATE PAR
  BEAUCEVILLE`: a name and an embedded clause, interchangeable as
  arguments.
  - Every deeper sentence made of known words is derivable.
  - 299 of the 300 swapped sentences are rejected.
  - 42 to 44 of its 300 samples have more embedding than any sentence it
    was trained on. The transformer produced one in 3,600.
- **Structure and probability are separate steps.** The structure alone
  recognises as well as it ever will, but its probabilities are
  supercritical: a derivation finishes with probability 0.0001, and no
  sample finishes. Inside–outside makes it consistent, so that derivations
  finish with probability 1. Maximum-likelihood estimates from finite data
  should do this. The 1.000000 is a numerical fixed point, not a proof.
- **More data, a smaller grammar.** From 10,000 sentences on, the learned
  grammar is the same: 192 categories and 1,772 rules, against 38,121 at
  1,000 sentences. It recognises exactly as well.
- **The smaller grammar predicts slightly worse**: 1.1075 bits against
  1.0786. Merging that makes the grammar smaller also merges distinctions
  that predict. Smaller is not simply better.
- **Against the transformer, at 1,000 sentences**: 1.0786 bits against
  1.065 to 1.070. The grammar is within about 1.2% of the transformer on
  the corpus. On deeper sentences it is far better (below). It is also far
  more inspectable: 2,396 categories and their rules, against 832,023
  weights.
- **It still overgenerates.** About 6% of its samples are ungrammatical,
  and the learned categories contain over-merges such as `BENOIT EST
  CONSTATE PAR LE FAIT QUE BEAUCEVILLE` beside `BENOIT`.

### Next-token prediction from the learned grammar

A grammar that scores whole sentences is not yet a language model.
`src/prefix.rs` computes exact next-token distributions from it by the
prefix probabilities of Jelinek and Lafferty (1991).
- The left-corner relation is closed once.
- Each next word is then a ratio of prefix probabilities, extended one
  column at a time as the sentence is read.

**Exact.** `tests/prefix.rs` learns a grammar from three sentences whose
language is finite. At every prefix of every sentence, the distributions
equal those got by listing the language (to 1e-12).

**On the grammar learned from 10,000 sentences** (`qlm prefix data 10000`):

| check | result |
|---|---|
| P(derivation finishes) | 1.000000000 |
| next-token probabilities (END included) against the prefix probability, worst relative difference | 5.2e-13 |
| next-token probabilities multiplied along a sentence against its inside probability, worst difference | 9.0e-13 bits |
| first word: exact distribution against 20,000 direct samples, total variation | 0.0066 |
| development, 200 sentences read word by word | 1.0955 bits/token |
| deeper, corpus words only, 100 sentences read word by word | **1.5883** bits/token |
| time per next-token distribution, one CPU core | 1.36 ms |

**On the grammar learned from 1,000 sentences** (`qlm prefix data 1000`),
with 2,396 categories and 38,121 rules, every check passes as well:
- relative difference at most 4.6e-13;
- chain against inside probability at most 3.7e-13 bits;
- total variation 0.0056;
- development 1.0708 bits per token, deeper 1.6003.

But each next-token distribution takes **176 ms**, about 130 times the
smaller grammar's 1.4 ms. The training saving of the larger grammar is
paid back in inference. Its slightly better prediction (1.07 against 1.10)
costs two orders of magnitude at every token. The transformer's inference
cost has not been measured on the same footing.

On the deeper sentences of known words, the transformer gives 2.82 to 4.93
bits, depending on size and seed, and gets worse as it is trained on more.
The learned grammar gives 1.59.

## What is not shown

- **The confirmation set has not been read.** These are development
  numbers.
- **The grammar is not shown to be the generating grammar.** The rules
  recovered are behaviourally recursive, but they are not shown to be
  Colmerauer's.
- **The comparison of cost is loose.** The grammar ran on one CPU core and
  the transformer on a GPU. The transformer had 6,000 steps at every size,
  with no tuning. Inside–outside had five rounds, with no study of
  convergence.
- **One language.** Everything is on one small, unambiguous language. A
  different synthetic grammar is needed to show this is not a property of
  this one.

## The full table (`qlm report data`)

EOF
cat data/report.md >> docs/results.md
git add -A && git commit -q -m "QLM-002 results and QLM-003: exact next-token prediction from the learned grammar

src/prefix.rs computes next-token distributions from a binary grammar by
Jelinek-Lafferty prefix probabilities: exact against listing a finite
language (tests/prefix.rs), and on the grammar learned from 10,000
sentences consistent with the sentence probabilities to 1e-12, at 1.4 ms
a token. The termination probability is reported for every learned
grammar. docs/results.md has the qualified rerun: three seeds of the
transformer, which gets worse at depth on every seed as it trains on
more, and the learned grammar, which derives every deeper sentence of
known words and gives them 1.59 bits a token." && git push -q && git log --oneline -1105138 training sentences, 13143 for development (the confirmation set is not read), 300 deeper (of which 65 contain CE), 300 deeper with only corpus words; 300 samples per model

| model | bits/token, development | bits/token, deeper | bits/token, deeper, corpus words only | grammatical samples | of them not in training | of them deeper | most a distribution strays from 1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| the corpus distribution (E16, given every sentence) | 1.0361 | ∞ (0 at zero) | ∞ (0 at zero) | – | – | – | – |
| the report's rules as an open grammar (E17, given the grammar) | 1.3621 | 1.3775 | 1.3787 | 300 | 109 | 61 | – |
| *100 training sentences: 300 of the 300 deeper sentences with corpus words use only words of these* | | | | | | | |
| Kneser–Ney 3-gram, 100 sentences (343 n-grams, 0.00 s) | 1.4051 | 2.1747 | 2.0355 | 52 | 52 | 18 | 6.7e-16 |
| Kneser–Ney 4-gram, 100 sentences (780 n-grams, 0.00 s) | 1.4192 | 2.2218 | 2.0951 | 51 | 51 | 8 | 6.7e-16 |
| Kneser–Ney 6-gram, 100 sentences (2275 n-grams, 0.00 s) | 1.4881 | 2.3399 | 2.2171 | 68 | 60 | 10 | 6.7e-16 |
| merged graph, k = 2, 100 sentences (148 states, 340 arrows, 0.00 s; bits with the floor, samples without) | 3.2396 | 4.5445 (1 allowed) | 4.5734 (0 allowed) | 175 | 168 | 21 | 6.7e-16 |
| merged graph, k = 3, 100 sentences (249 states, 420 arrows, 0.00 s; bits with the floor, samples without) | 3.5661 | 4.5537 (0 allowed) | 4.5768 (0 allowed) | 300 | 275 | 42 | 6.7e-16 |
| transformer-100-s1 (params=832023 steps=6000 seed=1 train_secs=117 device=mps) | 1.7746 | 3.4219 | 3.4175 | 197 | 143 | 0 | 6.7e-16 |
| transformer-100-s2 (params=832023 steps=6000 seed=2 train_secs=121 device=mps) | 1.8646 | 3.5209 | 3.5309 | 214 | 125 | 0 | 6.7e-16 |
| transformer-100-s3 (params=832023 steps=6000 seed=3 train_secs=89 device=mps) | 1.8798 | 3.6445 | 3.6064 | 196 | 106 | 0 | 6.7e-16 |
| *1000 training sentences: 300 of the 300 deeper sentences with corpus words use only words of these* | | | | | | | |
| Kneser–Ney 3-gram, 1000 sentences (411 n-grams, 0.00 s) | 1.2997 | 2.2847 | 2.0955 | 75 | 75 | 27 | 5.6e-16 |
| Kneser–Ney 4-gram, 1000 sentences (1269 n-grams, 0.00 s) | 1.2583 | 2.2806 | 2.1308 | 66 | 66 | 17 | 5.6e-16 |
| Kneser–Ney 6-gram, 1000 sentences (6019 n-grams, 0.01 s) | 1.2476 | 2.3861 | 2.2228 | 82 | 78 | 4 | 7.8e-16 |
| merged graph, k = 2, 1000 sentences (431 states, 1395 arrows, 0.01 s; bits with the floor, samples without) | 1.4074 | 4.3370 (4 allowed) | 4.3189 (2 allowed) | 119 | 117 | 24 | 1.8e-15 |
| merged graph, k = 3, 1000 sentences (831 states, 1950 arrows, 0.01 s; bits with the floor, samples without) | 2.3115 | 4.3864 (2 allowed) | 4.3536 (1 allowed) | 297 | 268 | 2 | 1.3e-15 |
| transformer-1000-s1 (params=832023 steps=6000 seed=1 train_secs=114 device=mps) | 1.0653 | 3.0810 | 2.9211 | 262 | 260 | 0 | 6.7e-16 |
| transformer-1000-s2 (params=832023 steps=6000 seed=2 train_secs=89 device=mps) | 1.0697 | 3.0873 | 2.9369 | 271 | 269 | 0 | 6.7e-16 |
| transformer-1000-s3 (params=832023 steps=6000 seed=3 train_secs=133 device=mps) | 1.0647 | 3.0411 | 2.8231 | 254 | 253 | 1 | 6.7e-16 |
| *10000 training sentences: 300 of the 300 deeper sentences with corpus words use only words of these* | | | | | | | |
| Kneser–Ney 3-gram, 10000 sentences (414 n-grams, 0.03 s) | 1.2849 | 2.5038 | 2.2610 | 80 | 76 | 26 | 5.6e-16 |
| Kneser–Ney 4-gram, 10000 sentences (1472 n-grams, 0.04 s) | 1.2250 | 2.4632 | 2.2788 | 72 | 69 | 17 | 6.7e-16 |
| Kneser–Ney 6-gram, 10000 sentences (10614 n-grams, 0.06 s) | 1.1656 | 2.5402 | 2.3319 | 91 | 72 | 0 | 8.9e-16 |
| merged graph, k = 2, 10000 sentences (1803 states, 7076 arrows, 0.05 s; bits with the floor, samples without) | 1.2331 | 4.2469 (11 allowed) | 4.2273 (9 allowed) | 61 | 58 | 14 | 8.9e-15 |
| merged graph, k = 3, 10000 sentences (3608 states, 11178 arrows, 0.08 s; bits with the floor, samples without) | 1.2435 | 4.3182 (0 allowed) | 4.2752 (0 allowed) | 213 | 182 | 0 | 5.6e-15 |
| transformer-10000-s1 (params=832023 steps=6000 seed=1 train_secs=127 device=mps) | 1.0425 | 3.8068 | 3.6517 | 289 | 262 | 0 | 8.9e-16 |
| transformer-10000-s2 (params=832023 steps=6000 seed=2 train_secs=102 device=mps) | 1.0410 | 3.7441 | 3.5842 | 295 | 273 | 0 | 6.7e-16 |
| transformer-10000-s3 (params=832023 steps=6000 seed=3 train_secs=143 device=mps) | 1.0421 | 3.6943 | 3.4703 | 294 | 266 | 0 | 6.7e-16 |
| *105138 training sentences: 300 of the 300 deeper sentences with corpus words use only words of these* | | | | | | | |
| Kneser–Ney 3-gram, 105138 sentences (414 n-grams, 0.36 s) | 1.2836 | 2.7429 | 2.4430 | 72 | 28 | 22 | 4.4e-16 |
| Kneser–Ney 4-gram, 105138 sentences (1622 n-grams, 0.43 s) | 1.2210 | 2.6557 | 2.4439 | 76 | 21 | 12 | 7.8e-16 |
| Kneser–Ney 6-gram, 105138 sentences (13948 n-grams, 0.61 s) | 1.1474 | 2.6974 | 2.4816 | 91 | 20 | 0 | 6.7e-16 |
| merged graph, k = 2, 105138 sentences (1054 states, 5929 arrows, 0.45 s; bits with the floor, samples without) | 1.2839 | 4.2112 (16 allowed) | 4.2047 (14 allowed) | 75 | 33 | 26 | 1.2e-14 |
| merged graph, k = 3, 105138 sentences (4454 states, 21613 arrows, 0.66 s; bits with the floor, samples without) | 1.1343 | 4.2930 (0 allowed) | 4.2663 (0 allowed) | 118 | 16 | 0 | 5.0e-14 |
| transformer-105138-s1 (params=832023 steps=6000 seed=1 train_secs=110 device=mps) | 1.0376 | 4.7136 | 4.6698 | 296 | 62 | 0 | 6.7e-16 |
| transformer-105138-s2 (params=832023 steps=6000 seed=2 train_secs=100 device=mps) | 1.0379 | 4.8076 | 4.7943 | 300 | 55 | 0 | 6.7e-16 |
| transformer-105138-s3 (params=832023 steps=6000 seed=3 train_secs=123 device=mps) | 1.0379 | 4.9866 | 4.9267 | 296 | 57 | 0 | 6.7e-16 |

**Transformer learning curves.** The floor is 1.0361 bits per token on the development sentences. Steps (of 64 sentences each) until the bits first come within 5% and within 1% of it, from the curve each run writes (bits on the first 2,000 development sentences, every 250 steps).

| run | within 5% | within 1% | best | at step |
|---|---:|---:|---:|---:|
| transformer-100-s1 | never | never | 2.0961 | 250 |
| transformer-100-s2 | never | never | 2.1239 | 250 |
| transformer-100-s3 | never | never | 2.1529 | 250 |
| transformer-1000-s1 | 250 | never | 1.0767 | 250 |
| transformer-1000-s2 | 250 | never | 1.0735 | 250 |
| transformer-1000-s3 | 250 | never | 1.0819 | 250 |
| transformer-10000-s1 | 250 | never | 1.0477 | 2750 |
| transformer-10000-s2 | 250 | 1750 | 1.0459 | 2250 |
| transformer-10000-s3 | 250 | 2500 | 1.0465 | 2500 |
| transformer-105138-s1 | 250 | 1500 | 1.0429 | 5250 |
| transformer-105138-s2 | 250 | 2500 | 1.0427 | 5000 |
| transformer-105138-s3 | 250 | 1500 | 1.0435 | 4250 |
