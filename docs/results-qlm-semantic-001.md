# Results: QLM-SEMANTIC-001, facts and relations

Reported against [qlm-semantic-001-plan.md](qlm-semantic-001-plan.md),
including its two changes after results:
1. composition and new-entity people held out by city, after a city-mate
   shortcut was found;
2. a held-out inverse never has its capital before its country, after an
   ordering leak was found.

These are the version-2 worlds. Version-1 numbers are kept in
`tables/facts-*-v1.md`. Full tables:
- [tables/facts-transformers.md](tables/facts-transformers.md);
- `data-semW/facts.md`, for the grammar and the n-gram shortcut baselines.

Three entity-permuted worlds. The transformers are the custom transformer
and Llama, seeds 1 to 3, so 9 runs each, trained on all 20,004 texts. The
grammar is converged (20 rounds). Every probability is floored at 0.999
model + 0.001 uniform. Accuracy is strict (the answer alone at the top of
its type). Contrast is log2 of the answer's probability over the mean of
its type's false answers.

| test (items per world) | chance | grammar | custom transformer | Llama |
|---|---:|---|---|---|
| seen facts (100) | | 42–43%, contrast 6.3 | 100%, 13.9 | 100%, 13.9 |
| new phrasing of a known fact (6) | 1/24 | 0%, contrast −12.3 | 98% (83–100), 7.5 | 98% (83–100), 9.2 |
| composition: P lives on ? (16) | 1/4 | 25%, 0.0 | 41% (19–69), −0.6 | **65% (38–94), 3.2** |
| inverse: K is located in ? (12) | 1/24 | 0%, abstains on all 12 | 0%, −1.7 | 5% (0–42), −0.6 |
| new entity, seen once (4) | 1/4 | 0%, about 0 | 25% (0–75), −4.2 | 44% (0–100), −1.8 |

The n-gram shortcut baselines are at chance on every test except seen
facts.

## Against the plan's criteria

**A learner knows facts** if its contrast on seen facts is above 3 bits.
All three know facts: the grammar at 6.3, both transformers at 13.9.

**It generalises a test** if its accuracy there is above 50% and its
contrast above 1 bit.

| test | grammar | custom transformer | Llama |
|---|---|---|---|
| phrasing | no | **yes** | **yes** |
| composition | no | no | **yes**, on the mean (7 of its 9 runs pass alone) |
| inverse | no | no | no |
| new entity | no | no | no (4 items per world; too few to tell) |

## What it shows

- **The grammar learner holds facts as unrelated strings.**
  - It remembers some seen facts.
  - On a new phrasing, it gives confidently wrong answers.
  - It cannot continue an inverse prompt at all.
  - It does no composition.

  As predicted, substitution alone does not learn relations.
- **The transformers carry a fact across phrasings,** almost perfectly,
  where the grammar fails completely.
- **Llama composes two relations**: P lives in K, and K's continent. That
  passes the plan's criterion (accuracy above 50%, contrast above 1 bit) in
  7 of 9 runs, with no text ever stating the person and the continent
  together. The custom transformer is mixed: 41%, and its
  mean contrast is negative.
- **The reversal curse holds for both transformers.** Once no text puts a
  held-out city before its country, inverse accuracy is 0% for the custom
  transformer in all 9 runs. For Llama it is 0% in 8 of 9 runs, and 5 of
  12 in one. In version 1, where "K . C" appeared in two-statement texts,
  they scored 87% to 95%: an ordering leak, not reversal.
- **The plan's shortcut controls had to be extended twice.** Each time the
  extension was found by a result that was too good. Both are recorded in
  the plan, with the evidence.

## Not shown

- How the transformers carry a fact across phrasings, or compose: that is
  LARQL-QLM-SEM-001.
- Whether any of this holds with more relations, ambiguity, or a larger
  world.
- The confirmation texts have not been read.
