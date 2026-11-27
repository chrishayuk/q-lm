# QLM-SCALE-001 plan: how does the learner's cost grow?

Written before measurement. It applies to the present learner (arm A), to
arm C′ (θ = 0.05) and, when built, to arm E.

## Question

Does the learned graph, and the cost of learning it, grow with the amount
of text, or with the amount of new structure the text contains? Only the
second could scale to TinyStories.

## Corpora

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

- **Sublinear storage:** the stored graph grows more slowly than the
  corpus. The exponent of the log-log fit of rules against sentences,
  from 10,000 up, is below 0.5.
- **Bounded active graph:** the active rules per sentence stop growing
  beyond 10,000 sentences, staying within 20% of their value there.
- **Linear-or-better learning:** learning time grows at most linearly with
  the corpus, from 10,000 up.

Whichever fails says where the learner must change before TinyStories.
