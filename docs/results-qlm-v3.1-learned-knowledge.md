# Results: Q-LM v3.1, knowledge learned from text (program still supplied)

Against [qlm-v3-plan.md](qlm-v3-plan.md), revision 1, stage v3.1. Code:
`v3/learn.py`. Tables: [tables/v3.1-learned.txt](tables/v3.1-learned.txt)
and [tables/v3.1-stress-repeat1.txt](tables/v3.1-stress-repeat1.txt).

## Changes to the worlds first (v3.0 requalified after them)

- **Task A has paraphrases.** "Lives" is written "P lives in K ." or "P is
  from K ."; "located" is "K is located in C ." or "K is a city of C .".
  Each fact, at each of its 4 repetitions, picks a wording at random.
- **Task B's routing is randomised for every world:** which kinds stop,
  and which relation each other kind follows. For seeds 1 to 3:
  - green→points to, yellow→holds, white→faces, red→calls;
  - green→calls, yellow→points to, blue→faces, black→holds;
  - red→faces, green→calls, yellow→holds, white→points to.
- **The v3.0 oracle results are unchanged** on the regenerated worlds:
  [tables/v3.0-oracle.txt](tables/v3.0-oracle.txt).

## What the learner does, and what it is given

It reads only `train.txt`.
- **Frames:** every way of replacing 1 or 2 positions of a distinct
  sentence with a slot is a candidate. Each sentence is parsed by its
  best-supported frame (supported by at least 3 distinct sentences).
- **Entities:** the slot fillers, kept as individual tokens.
- **Relations:** two-slot frames whose bound pairs overlap (Jaccard ≥ 0.5)
  are one relation with several wordings.
- **Bindings:** (subject, relation) → objects, with counts.

**Supplied:**
- the prior that a fact has at most 2 arguments;
- the program, named by one wording per relation ("{} lives in {} .");
- for task B, the routing rule and the stopping kinds.

`world.json` is read only to score.

## Results, all 18 worlds

| capability | measure | result |
|---|---|---|
| entity discovery | precision, recall | 1.000, 1.000 on every world |
| identity preservation | entity merges | 0, by construction: nothing merges entities |
| relationship discovery | true relations recovered exactly | all, on every world (4, or 5 with hemispheres; 5 in B) |
| | groups mixing two relations | 0 (lives and born link the same types and are kept apart: overlap 0) |
| paraphrase learning | wordings grouped | 2 of 2 on every task-A world (overlaps 0.79 to 0.86) |
| knowledge extraction | bindings, precision and recall | 1.000, 1.000 on every world |
| execution | accuracy over learned knowledge | the same as the oracle at every pass count, on every test |

- **Under T2** the composed statements ("P lives on T .", "from X the
  end is Z .") form one extra relation of their own. It is not used by the
  supplied program.
- **Cost:** learning takes 0.01 s (A) and 0.08 s (B). The whole learned
  model serialises to 9 to 12 kB (A) and 177 to 182 kB (B).

## The stress test: no fact seen in both wordings

The worlds above are generous: 87.5% of facts appear in both wordings.
With each fact written once (`REPEAT=1`, task A, seeds 1 to 3, T1):
- **The wordings are not grouped:** 0 of 2 paraphrases, because their
  pair sets do not overlap at all.
- **Composed accuracy at 3 passes falls to 0.375, 0.542 and 0.333:** the
  program's one wording reaches only the facts stated in it.
- **Bindings stay correct:** precision and recall 1.000.

So relation identity across wordings is learned only from shared
instances. Grouping wordings from context alone (the words around them,
v2-style) is not attempted.

## What it says, and what it does not

- **On clean template text, the knowledge graph is recoverable from text
  exactly,** and the runtime executes over it as well as over the truth.
  Every measure is perfect.
- **That is a statement about these worlds as much as about the learner.**
  Every sentence is a fact in a fixed template. There is no noise, no
  ambiguity of attachment, and no sentence that is not a fact. The real
  test of v3.1's method is text that is not like this: the stress test
  shows one place it breaks, and TinyStories would show many more.
- **Nothing here learns computation.** The program and the routing policy
  are still supplied. That is v3.2 (static programs, from T2's composed
  examples) and v3.3 to v3.4 (routing and stopping, task B).
