# Results: LARQL-QLM-SEM-001, version-3 worlds (relation of the same type, recombined query)

Reported against [larql-qlm-sem-001-plan.md](larql-qlm-sem-001-plan.md),
amendments 2 and 3. Full tables: [tables/sem-001-v3.md](tables/sem-001-v3.md).
The models are 18: Llama and the custom transformer, seeds 1 to 3, on the
three version-3 worlds. Every person also has a birth city, never the city
they live in. Sections 1 to 5 of each table repeat the version-2
measurements on these models.

**Gate.** In every model, 44 of the 48 people answer both `P lives in` and
`P was born in` correctly. The 4 single-observation people have no birth
fact, so they are never admitted. That leaves 33 people for fitting and 11
for testing.

**Directions.** The relation subspace is fitted on wording 2 (`P is a
native of` against `P is from`) over the 33. It is the mean difference
plus its top 3 directions. It is applied on wording 1 (`P was born in`,
`P lives in`) to the 11.

## 1. A relation of the same type: born against lives

Only the relation component of `P was born in` is moved into `P lives in`,
for the same person. Does P's birth city then beat P's home city? Both are
cities, 24 of them. So switching the answer type cannot do it, and a
4-dimensional subspace fitted on other people cannot carry which city.

| block | Llama: birth city wins, mean (range) | random, matched | custom: birth city wins | random |
|---:|---:|---:|---:|---:|
| 1 | **0.70** (0.36 to 1.00) | 0.00 | 0.13 (0 to 0.45) | 0.00 |
| 2 | 0.18 | 0.00 | 0.05 | 0.00 |
| 3 | 0.05 | 0.00 | 0.00 | 0.00 |
| 4 (control) | 0.00 | 0.00 | 0.00 | 0.00 |

- **Llama passes the plan's criterion in 8 of 9 models**, all at block 1.
  The criterion: at least half the held-out people at some block before
  the last, with the random control under a tenth as many.
- **The custom transformer passes in 0 of 9.**
- After block 1 the swap stops working in Llama. By block 2, the answer is
  formed (SEM-001, version 2).

## 2. A recombined query: A's entity, B's relation

At the last position of `A lives in`, after block b, B's relation
difference (`B was born in` minus `B lives in`, projected on the relation
subspace) is added. B is another admitted person whose birth city is
neither A's birth city nor A's home city. Up to 5 Bs per A, so up to 55
pairs per model. Which city wins?

| block | Llama: A's birth city (composed) | B's birth city (injected) | A's home city (no effect) | random | custom: A's birth city | B's | A's home |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | **0.51** (0.29 to 0.78) | **0.00** | 0.49 | 0.00 | 0.10 | 0.00 | 0.89 |
| 2 | 0.01 | 0.01 | 0.95 | 0.00 | 0.03 | 0.00 | 0.97 |
| 3 | 0.00 | 0.01 | 0.98 | 0.00 | 0.00 | 0.00 | 1.00 |
| 4 (control) | 0.00 | 0.02 | 0.98 | 0.00 | 0.00 | 0.00 | 1.00 |

- **In Llama, after block 1, B's relation turns A's query into A's birth
  city in half the pairs.** That is an answer neither donor holds.
  - B's own birth city never wins: 0.00. So this is not answer injection.
  - When it fails, the intervention has no effect: A's home city stays.
  - The random control: 0.00.
- **Llama passes the plan's criterion in 4 of 9 models** (A's birth city in
  at least half the pairs, B's and random under a tenth). In the other 5,
  A's birth city wins in 29% to 49%.
- **The custom transformer: 0 of 9.**

## What it shows

- **In Llama, after its first block, a relation component at the last
  position is separable from the entity.**
  - It is fitted on other people and in another wording.
  - It moves which fact is retrieved (birth city against home city, both
    cities) without moving whose.
  - Taken from one person and applied to another, it retrieves the other
    person's fact, and never the donor's.

  That is the plan's "relation state separable from the entity", met
  without the answer-type confound of version 2, and a composed query at
  block 1 in 4 of 9 models.
- **The window is narrow:** block 1 only. From block 2 the answer has been
  formed, and changing the relation component changes nothing.
- **The custom transformer shows no such component** where it was looked
  for: the last position, before its answer forms at block 3. Its block-1
  relation swap reaches 0.13. Its relation may be represented elsewhere,
  for example at the person's position, or not linearly. That is not
  tested.

## Not shown

- Whether the relation component is a direction the model uses for other
  relations, beyond these two.
- Llama's 5 models where the composed query wins less than half the time
  (29% to 49%), against the single relation swap's 70%, suggest the
  component taken from another person is a weaker version of the one
  taken from the same person.
- 11 test people per world. The fitted subspace has 4 dimensions,
  following the plan. Other dimensions are not tried.
