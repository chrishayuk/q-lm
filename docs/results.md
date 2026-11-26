# Results: Q-LM-001 and Q-LM-SAMPLE-001, first run

One run of every model, with fixed seeds: `qlm data data`, the four
transformer runs, then `qlm report data`. The full table, as printed, is
below. Every number is from one seed; differences of a few hundredths of a
bit, or of a few samples in 300, should not be read as real until repeated.

## What the table says

**The floor.** The true distribution of the corpus is the graph of all
131,424 sentences (QSYS-E16). On the held-out sentences it gives 1.0361
bits per token. It gives every deeper sentence zero.

**The transformer learns the corpus, and almost nothing beyond it.**
- **The corpus.** Trained on all 118,281 sentences, it is within 0.0025 bits
  of the floor (1.0386). Trained on 1,000, it is within 0.031 (1.0670). It
  needs only 1,000 sentences, under 1% of the corpus, to come within 3% of
  the floor.
- **Grammar.** At full size 294 of its 300 samples are grammatical; at
  1,000 sentences, 260, and 255 of those are sentences it never saw.
- **Depth.** It produced 2 deeper sentences at 1,000 sentences and none at
  any other size.
- **More data made it worse on deeper sentences**: 3.18, 4.49 and 5.26 bits
  at 1,000, 10,000 and 118,281 sentences. Trained on more sentences of one
  depth, it is surer they are all there is.
- **Cost.** 832,023 parameters, about 100 seconds of GPU time per size.

**The n-gram models generalise blindly.**
- The best on held-out sentences is the 6-gram at full size, 1.1472 bits,
  0.11 above the floor.
- At most 98 of 300 samples are grammatical.
- The 3-gram's samples include a few deeper sentences (up to 25), produced
  by stringing local patterns together.

**The merged graphs show the trade-off of merging.**
- They are built from the training sentences in under a second.
- Small k merges too much. At k = 1, 17 of 300 samples are grammatical.
- Large k barely generalises. At k = 3 and 4 with 100 sentences, every
  sample is grammatical, but most held-out sentences are not allowed at
  all, which costs 8-9 bits per token.
- At full size, k = 3 reaches 1.1384 bits on held-out sentences, better
  than any n-gram, in 11,822 arrows.
- **k = 2 at full size is the one learner that found depth.** 28 of its
  300 samples are grammatical sentences with two or more levels of
  embedding, which it never saw. Merging states with the same two-word
  future closes loops in the graph, and some of the loops are the grammar's
  recursion. It also allows 16 of the 300 deeper test sentences. It pays
  for this in grammar: only 84 of its 300 samples are grammatical.
- No merged graph allows a deeper sentence containing `CE`.

**No learner can predict `CE`.** `DE CE QUE` needs two levels of embedding,
so `CE` never occurs in the corpus. It is in the vocabulary every learner
is given, and that is all.

**The open grammar (E17) is the reference, not a competitor.**
- It is given the grammar.
- Its distribution, a prior over trees, is not the corpus's, so its
  held-out bits (1.3621) are above the floor.
- Every sample is grammatical, and 61 of 300 are deeper.
- It gives the deeper sentences 1.38 bits per token, where the best learner
  gives 2.19.

## The questions it raises

- **Why does the transformer get worse at depth as it gets better at the
  corpus?** Is the effect stable across seeds, and does it hold for
  sentences deeper by one level in the subject or the object alone?
- **What did k = 2 merge?** Which loops in its graph are the grammar's
  recursion, and which are the overgeneration? Can a learner keep the first
  and not the second, for instance by merging only where the merged graph
  still analyses (by the report's grammar) as well as before?
- **What is a fair amount of training?** The transformer had 6,000 steps
  at every size. A learning curve over steps, and an energy measure, are
  needed before comparing cost.

## The table

118281 training sentences, 13143 held out, 300 deeper; 300 samples per model

| model | bits/token, held out | bits/token, deeper | grammatical samples | of them not in training | of them deeper |
|---|---:|---:|---:|---:|---:|
| the corpus distribution (E16 graph, given every sentence) | 1.0361 | ∞ (0 of 300 at zero) | – | – | – |
| the report's rules as an open grammar (E17, given the grammar) | 1.3621 | 1.3775 | 300 | 89 | 61 |
| Kneser–Ney 2-gram, 100 sentences (97 n-grams stored, trained in 0.00 s) | 1.7191 | 2.2579 | 1 | 1 | 0 |
| Kneser–Ney 3-gram, 100 sentences (332 n-grams stored, trained in 0.00 s) | 1.4065 | 2.1875 | 43 | 43 | 16 |
| Kneser–Ney 4-gram, 100 sentences (759 n-grams stored, trained in 0.00 s) | 1.4166 | 2.2290 | 57 | 57 | 17 |
| Kneser–Ney 5-gram, 100 sentences (1421 n-grams stored, trained in 0.00 s) | 1.4615 | 2.3053 | 51 | 50 | 17 |
| Kneser–Ney 6-gram, 100 sentences (2254 n-grams stored, trained in 0.00 s) | 1.4744 | 2.3488 | 70 | 68 | 10 |
| Kneser–Ney 2-gram, 1000 sentences (102 n-grams stored, trained in 0.00 s) | 1.6658 | 2.3306 | 3 | 3 | 0 |
| Kneser–Ney 3-gram, 1000 sentences (411 n-grams stored, trained in 0.00 s) | 1.2984 | 2.2907 | 71 | 71 | 16 |
| Kneser–Ney 4-gram, 1000 sentences (1269 n-grams stored, trained in 0.00 s) | 1.2562 | 2.2847 | 77 | 75 | 14 |
| Kneser–Ney 5-gram, 1000 sentences (3079 n-grams stored, trained in 0.01 s) | 1.2840 | 2.3377 | 72 | 71 | 17 |
| Kneser–Ney 6-gram, 1000 sentences (6061 n-grams stored, trained in 0.01 s) | 1.2487 | 2.3915 | 89 | 83 | 2 |
| Kneser–Ney 2-gram, 10000 sentences (102 n-grams stored, trained in 0.03 s) | 1.6608 | 2.4734 | 2 | 2 | 0 |
| Kneser–Ney 3-gram, 10000 sentences (414 n-grams stored, trained in 0.03 s) | 1.2848 | 2.5035 | 83 | 78 | 25 |
| Kneser–Ney 4-gram, 10000 sentences (1469 n-grams stored, trained in 0.04 s) | 1.2248 | 2.4628 | 70 | 66 | 15 |
| Kneser–Ney 5-gram, 10000 sentences (4265 n-grams stored, trained in 0.05 s) | 1.2302 | 2.4924 | 74 | 69 | 16 |
| Kneser–Ney 6-gram, 10000 sentences (10582 n-grams stored, trained in 0.06 s) | 1.1657 | 2.5391 | 98 | 84 | 0 |
| Kneser–Ney 2-gram, 118281 sentences (102 n-grams stored, trained in 0.32 s) | 1.6602 | 2.6312 | 2 | 0 | 0 |
| Kneser–Ney 3-gram, 118281 sentences (414 n-grams stored, trained in 0.39 s) | 1.2835 | 2.7551 | 72 | 23 | 21 |
| Kneser–Ney 4-gram, 118281 sentences (1624 n-grams stored, trained in 0.48 s) | 1.2209 | 2.6657 | 79 | 19 | 13 |
| Kneser–Ney 5-gram, 118281 sentences (5422 n-grams stored, trained in 0.56 s) | 1.2213 | 2.6803 | 81 | 19 | 13 |
| Kneser–Ney 6-gram, 118281 sentences (14156 n-grams stored, trained in 0.64 s) | 1.1472 | 2.7072 | 95 | 6 | 0 |
| merged graph, k = 1, 100 sentences (41 states, 196 arrows, built in 0.00 s) | 2.2501 | 13.0237 (7 of 300 allowed) | 12 | 12 | 0 |
| merged graph, k = 2, 100 sentences (144 states, 345 arrows, built in 0.00 s) | 6.8792 | 13.1629 (0 of 300 allowed) | 166 | 164 | 18 |
| merged graph, k = 3, 100 sentences (252 states, 429 arrows, built in 0.00 s) | 8.3605 | 13.1805 (0 of 300 allowed) | 300 | 275 | 36 |
| merged graph, k = 4, 100 sentences (330 states, 496 arrows, built in 0.00 s) | 9.0403 | 13.1805 (0 of 300 allowed) | 300 | 205 | 0 |
| merged graph, k = 1, 1000 sentences (62 states, 522 arrows, built in 0.00 s) | 1.5466 | 11.6218 (18 of 300 allowed) | 8 | 7 | 2 |
| merged graph, k = 2, 1000 sentences (454 states, 1448 arrows, built in 0.01 s) | 1.7868 | 12.1462 (4 of 300 allowed) | 131 | 130 | 18 |
| merged graph, k = 3, 1000 sentences (866 states, 1997 arrows, built in 0.01 s) | 4.6686 | 12.3895 (1 of 300 allowed) | 300 | 267 | 3 |
| merged graph, k = 4, 1000 sentences (1183 states, 2389 arrows, built in 0.01 s) | 5.6706 | 12.4055 (0 of 300 allowed) | 300 | 227 | 0 |
| merged graph, k = 1, 10000 sentences (91 states, 1095 arrows, built in 0.03 s) | 1.4664 | 11.5192 (20 of 300 allowed) | 19 | 19 | 2 |
| merged graph, k = 2, 10000 sentences (1808 states, 7085 arrows, built in 0.05 s) | 1.2387 | 11.6751 (12 of 300 allowed) | 57 | 57 | 12 |
| merged graph, k = 3, 10000 sentences (3633 states, 11292 arrows, built in 0.07 s) | 1.4493 | 11.9666 (0 of 300 allowed) | 201 | 177 | 0 |
| merged graph, k = 4, 10000 sentences (5495 states, 13707 arrows, built in 0.09 s) | 2.6741 | 11.9665 (0 of 300 allowed) | 296 | 213 | 0 |
| merged graph, k = 1, 118281 sentences (50 states, 293 arrows, built in 0.28 s) | 1.4969 | 11.5360 (20 of 300 allowed) | 17 | 1 | 1 |
| merged graph, k = 2, 118281 sentences (457 states, 2589 arrows, built in 0.41 s) | 1.2851 | 11.5771 (16 of 300 allowed) | 84 | 35 | 28 |
| merged graph, k = 3, 118281 sentences (2343 states, 11822 arrows, built in 0.73 s) | 1.1384 | 11.8556 (0 of 300 allowed) | 106 | 10 | 0 |
| merged graph, k = 4, 118281 sentences (5264 states, 20008 arrows, built in 1.02 s) | 1.3876 | 11.8555 (0 of 300 allowed) | 129 | 10 | 0 |
| transformer-118281 (params=832023 steps=6000 train_secs=103 device=mps) | 1.0386 | 5.2593 | 294 | 29 | 0 |
| transformer-1000 (params=832023 steps=6000 train_secs=110 device=mps) | 1.0670 | 3.1799 | 260 | 255 | 2 |
| transformer-10000 (params=832023 steps=6000 train_secs=107 device=mps) | 1.0433 | 4.4861 | 291 | 262 | 0 |
| transformer-100 (params=832023 steps=6000 train_secs=101 device=mps) | 1.8302 | 3.4939 | 190 | 134 | 0 |
