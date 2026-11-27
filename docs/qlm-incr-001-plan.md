# QLM-INCR-001 plan: learning more without relearning everything

Written before any implementation. QLM-SCALE-001 (kind 1) found the
present learner relearns from scratch: adding a tenth more data costs the
whole corpus again. This experiment asks whether a learned model can take
new data, and new information above all, at a cost proportional to the new
data.

## Arms

All start from the grammar learned on a base corpus B and saved.

| arm | on new data N |
|---|---|
| batch | relearn from B + N (the reference) |
| probabilities only | keep the structure; inside–outside on N alone, the saved expected counts of B kept and added to |
| structure | parse N with the saved grammar; for sentences it cannot derive, learn new substrings and merges from N alone, against the saved contexts of B; then the update above |
| structure + consolidation | as structure, then every k additions, recheck merges among the categories the additions touched |

## Two kinds of new data

1. **More of the same:** B is 10,000 sentences of Colmerauer's language, N
   the next 1,000.
2. **New information:** B is a version-3 semantic world with 4 of its
   people left out entirely; N is every training statement about those 4
   (about 4% of the corpus). The model has never seen their names.

## Measures

- **Cost:** the time and peak memory of the update against batch; the
  sentences read (N only, against B + N).
- **Quality:**
  - development bits;
  - fresh ungrammatical sentences derived;
  - for kind 2, the new people's facts (QLM-SEMANTIC-001's measures, for
    the 4).
- **Retention:** development bits and the fact tests on B's own material,
  before and after the update. Nothing already known may get worse by
  more than 1%.
- **Equivalence:** for kind 1, the update's grammar against batch's, by
  canonical fingerprint (QLM-EQUIV-001), and the difference in
  development bits.

## What would count

- **An incremental learner:** at least one arm, on both kinds:
  - is within 1% of batch on development bits;
  - retains B within 1%;
  - costs at most 3 × (N / (B + N)) of batch's time. That is about a
    quarter of batch for kind 1.
- **Learning new information incrementally:** on kind 2, the new people's
  seen facts are known at least as well as batch knows them, without B
  being read again.

The present learner (arm A) can run the first two arms. The structure arms
need arm E's store of observations, so they wait for it.
