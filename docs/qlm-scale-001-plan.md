# QLM-SCALE-001 plan: how does the learner's cost grow?

Written before measurement. It applies to the present learner (arm A), to
arm C′ (θ = 0.05) and, when built, to arm E.

## Question

Does the learned graph, and the cost of learning it, grow with the amount
of text, or with the amount of new structure the text contains? Only the
second could scale to TinyStories.

## Three kinds of growth, measured apart

1. **More observations of the same structures:** nested subsets of one
   fixed language (Colmerauer's: 100 to 105,138; right family: 100 to
   36,000). Does learning converge, and does storage stop growing?
2. **More vocabulary and facts:** semantic worlds with more entities (24,
   96, 384 countries, with people in proportion), the same relations and
   phrasings. What does a new fact cost?
3. **More complex structure:** families with more templates, or deeper
   corpora (depth at most 1, then 2), at a fixed number of sentences. What
   does a new capability cost?

Kind 1 runs first, on the present learner. It is the baseline.

## Corpora (the first draft, kept for kind 3)

The aim is 100, 1,000, 10,000, 100,000 and 1,000,000 training sentences.
- **Right family:** its corpus is 45,000 sentences. To go past that,
  sentences of depth 2 are drawn at random (the generator's derivation),
  so the language grows.
- **Colmerauer's language:** up to 105,138.
- **TinyStories:** the first n sentences of the cached dataset, as the
  first natural-text point. Only the structural statistics are taken; it
  is not a modelling run.

## Measures at every size

- Learning time, split into structure and estimation (inside–outside or
  stepwise).
- Peak resident memory, from `/usr/bin/time -l`.
- **Stored graph:** distinct substrings considered, categories, rules.
- **Active graph:** for each development sentence, the rules its inside
  chart touches (mean and 95th percentile).
- **Development bits per token,** and deeper bits on the families.
- **Throughput:** next-token distributions per second (`qlm prefix`'s
  timing).

## What would count

The criteria are revised from the first draft, before any measurement. A
learner that meets genuinely new facts may need storage roughly linear in
them, so a fixed storage exponent is the wrong test.
- **Storage tracks information, not repetition.** In kind 1 (the same
  structures again), the stored graph stops growing: rules at the largest
  size within 20% of those at 10,000. In kind 2, storage grows at most
  linearly in the number of facts.
- **Bounded active graph:** the active rules per sentence stop growing
  beyond 10,000 sentences, staying within 20% of their value there.
- **Computation tracks the input, not the store:** the active rules per
  sentence are within 20% across kind 2's world sizes.
- **Learning tracks new data:** learning time grows at most linearly with
  the corpus. In a separate run, adding a tenth more data costs time
  proportional to the tenth, not to the whole corpus again. Kind 1, from
  10,000 up.

Whichever fails says where the learner must change before TinyStories.
