# Results: QLM-SCALE-001, kind 1 (more of the same structures), present learner

Reported against [qlm-scale-001-plan.md](qlm-scale-001-plan.md), as revised
before measurement. Arm A (one shared context merges), 20 rounds of
inside–outside, nested subsets of two fixed languages. Each size ran in its
own process; peak memory is from `/usr/bin/time -l`. Full table:
[tables/scale-001-kind1.md](tables/scale-001-kind1.md).

| language | sentences | distinct substrings | categories | rules | active rules per sentence (mean / 95th pct) | estimation, s | development bits | ms per next token | peak MB |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| right | 100 | 2,672 | 1,489 | 10,634 | 73 / 138 | 0.1 | 4.180 | 0.33 | 72 |
| right | 300 | 6,429 | 1,448 | 15,518 | **4,925 / 7,340** | 10.3 | 1.387 | **103.6** | 225 |
| right | 1,000 | 15,238 | 124 | 1,017 | 317 / 440 | 1.3 | 1.381 | 1.25 | 35 |
| right | 3,000 | 31,662 | **52** | **351** | **129 / 160** | 1.8 | 1.380 | 0.42 | 39 |
| right | 10,000 | 67,227 | 52 | 351 | 129 / 160 | 5.8 | 1.380 | 0.33 | 59 |
| right | 36,000 | 137,059 | 52 | 351 | 129 / 160 | 20.6 | 1.380 | 0.33 | 90 |
| Colmerauer | 100 | 6,917 | 4,432 | 42,072 | 184 / 381 | 0.3 | 5.001 | 0.61 | 967 |
| Colmerauer | 300 | 17,083 | 6,390 | 85,969 | **23,948 / 49,114** | 109.4 | 1.059 | **613.1** | **2,203** |
| Colmerauer | 1,000 | 43,645 | 2,396 | 38,121 | 8,337 / 13,186 | 81.7 | 1.046 | 132.9 | 652 |
| Colmerauer | 3,000 | 98,249 | 292 | 3,280 | 547 / 1,112 | 7.4 | 1.058 | 1.34 | 141 |
| Colmerauer | 10,000 | 230,935 | **192** | **1,772** | **454 / 742** | 22.7 | 1.058 | 0.97 | 212 |
| Colmerauer | 30,000 | 488,978 | 192 | 1,772 | 454 / 742 | 67.1 | 1.058 | 0.97 | 340 |
| Colmerauer | 105,138 | 1,086,642 | 192 | 1,772 | 454 / 742 | 238.4 | 1.058 | 1.05 | 607 |

(At 100 sentences, most development sentences cannot be derived, so their
bits are the floor's, and their charts are small.)

## Against the plan's criteria

| criterion | right | Colmerauer |
|---|---|---|
| **storage tracks information:** rules at the largest size within 20% of those at 10,000 | **holds**: identical from 3,000 | **holds**: identical from 10,000 |
| **computation tracks the input:** active rules per sentence stop growing | **holds**: 129 from 3,000 | **holds**: 454 from 10,000 |
| **learning time at most linear in the corpus** | holds: estimation 5.8 / 17.5 / 20.6 s at 10k / 30k / 36k | holds: 22.7 / 67.1 / 238.4 s at 10k / 30k / 105k |
| **adding a tenth costs a tenth** | **fails by design**: the learner relearns from scratch | **fails by design** |

## What it shows

- **Once a language's structure is learned, more of it adds nothing to the
  model.** The grammar, the rules each sentence uses, and the cost per
  next token are all identical from 3,000 (right) or 10,000 (Colmerauer)
  sentences to the full corpus: 52 categories and 351 rules for right, 192
  and 1,772 for Colmerauer.
- **The cost is not monotonic. It peaks with little data.** Before merging
  has saturated, the grammar is large, and it is expensive both to train
  and to run:
  - at 300 Colmerauer sentences, 85,969 rules, 23,948 active rules per
    sentence, 613 ms per next token and 2.2 GB of memory;
  - at 10,000 sentences, 1,772 rules, 454 active rules, 0.97 ms and 212 MB.

  The model really does become smaller and faster as it learns more, but
  only after an expensive phase of too little evidence.
- **What does grow with the corpus is the learner's own bookkeeping, not
  the model.**
  - Distinct substrings grow roughly linearly: 1.09 million at 105,138
    sentences.
  - So does peak memory, to 607 MB, because the learner enumerates every
    substring of every sentence with its whole-sentence context.
  - Estimation re-reads every training sentence on every round, so it
    grows linearly too.

  The model is fixed in size; the cost of finding and fitting it is not.
- **That is where natural text would break it.**
  - Substrings per sentence grow with the square of its length, and
    whole-sentence contexts almost never repeat.
  - Relearning from scratch has no incremental path.

  Arm E's promotion step (store everything, promote only what recurs) and
  local estimation are aimed at exactly these. Bounded contexts would be
  needed too.

## Next

- Kinds 2 (more facts) and 3 (more structure).
- The same table for arm E, once built.
