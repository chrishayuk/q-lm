# Results: LARQL-QLM-ENRICH-001, where the fact is looked up

Reported against [larql-qlm-enrich-001-plan.md](larql-qlm-enrich-001-plan.md),
plus one follow-up outside the plan, labelled as such. Full tables:
[tables/enrich-001.md](tables/enrich-001.md). The models are the 18
version-3 models: Llama and the custom transformer, seeds 1 to 3, three
worlds. Capitals use `the capital of C' is` and `the capital of C is`;
people use `P lives in` and `P was born in`. Choices are made on the first
60 pairs and judged on the other 60.

## The plan's tests: no enrichment at the entity's position

Means over 9 models, with ranges where not 0.

| measure | Llama | custom transformer | random, matched |
|---|---|---|---|
| patch only the feed-forward output at the country's position (donor's capital wins), best block | 0.01 (0 to 0.05) | 0.01 (0 to 0.03) | ≤ 0.02 |
| remove it (own-capital accuracy, from 0.98 / 0.97 unablated) | 0.97 to 0.98 | 0.96 to 0.98 | |
| control: remove it at position 2 instead | 0.98 | 0.97 | |
| restore only it after the country is swapped (clean answer returns) | ≤ 0.02 | ≤ 0.00 | 0.00 |
| reuse: one patch at the person's position makes both `lives in` and `was born in` give the donor's cities | **0.00** | **0.00** | 0.00 |

Every criterion fails, at every block, in every model. The feed-forward
output at the entity's own position carries nothing these tests can find:
- moving it moves no answer;
- removing it costs nothing;
- restoring it repairs nothing.

So the subject-enrichment account (Geva et al., 2023) does not describe
these models. The SEM-001 entity transplant (0.96 after block 1, custom
transformer) moved the country's own representation, its embedding plus
what attention added there, and not facts the feed-forward had attached.

## Follow-up, not in the plan: the feed-forward at the answer position

The same patch, at the last position instead (judged pairs: the share in
which the donor's capital wins):

| block | Llama | custom transformer | random, matched |
|---:|---:|---:|---:|
| 1 | 0.01 | 0.00 | 0.00 |
| 2 | 0.18 (0.07 to 0.33) | 0.01 | 0.00 |
| 3 | **0.77** (0.70 to 0.85) | 0.05 | 0.00 |
| 4 | **0.81** (0.65 to 0.92) | **0.57** (0.33 to 0.72) | 0.00 |

**The fact is written at the answer position, by the feed-forward of the
later blocks.**
- In Llama, by blocks 3 and 4.
- In the custom transformer, by block 4, which is also the block read
  straight by the output head.

## The sequence, across SEM-001, TRANSPORT-001 and ENRICH-001

In these small models, the evidence so far orders the computation this
way:
1. **The entity stays as itself at its own position.** It is not enriched
   there.
2. **A few attention heads carry it to the answer position:** blocks 1 and
   2 in Llama, 2 and 3 in the custom transformer.
3. **In Llama, after block 1, the answer position holds a relation
   component that can be separated from the entity and recombined** (SEM-001
   version 3).
4. **The feed-forward at the answer position then writes the answer:**
   blocks 3 and 4 in Llama, 4 in the custom transformer.

That is closer to "transport the entity, then execute the relation where
the answer is needed" than to "enrich the entity, then extract".

**For the external FFN idea:** in these models, the place to put an
external lookup would be the answer position's feed-forward in the later
blocks, given the transported entity and the relation component. It would
not be the entity's own position.

**Not shown:** whether larger models do the same. The enrichment account
comes from models with far more layers, and four blocks may leave no room
for a separate enrichment stage.
