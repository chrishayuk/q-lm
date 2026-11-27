# QLM-TOKEN-001 plan: learned representational units (separate track)

Written before any code. It does not change QLM-TINYSTORIES-V3-001, which
keeps the present word-level tokens and vocabulary frozen.

## The question

Which surface units make Q-LM predict TinyStories best per byte of text,
and do learned multiword or overlapping hierarchical units help beyond
what a fixed tokenizer gives?

## Arms

| arm | units |
|---|---|
| A | the present tokens (lowercased words, punctuation, digits apart) |
| B | the same, case preserved |
| C | characters |
| D | BPE at 1k, 4k and 16k merges, learned on the training text only |
| E | learned morphological units (segmentations chosen by description length) |
| F | learned multiword units (spans merged when they reduce description length) |
| G | overlapping hierarchical units: words and learned spans both kept, the model choosing per position |

## Rules

- **Bits per byte,** never bits per token. All arms are scored on one
  common text: the raw TinyStories stories, as UTF-8 bytes, story by story,
  over the same stories.
  - This needs a new evaluation path: the present one scores data-ts's
    preprocessed sentences, which lose case and spacing.
  - Each arm's model must give a probability to the exact byte sequence:
    its tokenizer must be lossless, or its losses charged.
- **The same model family for every arm:** v2's mixture (n-gram, class
  models, keys, story caches), retrained per arm. Also a transformer per
  arm, as a reference.
- **Units are learned from the training stories only.**

## Measures

- Bits per byte.
- Vocabulary, serialised model size, learning time, inference cost.
- Entity and relation recovery: v3.1's learner run on each arm's units,
  scored by hand-checkable samples.
- Unseen-word generalisation: bits per byte on words absent from
  training.

## Order

After QLM-TINYSTORIES-V3-001's arms C and D have a first result. The
lossless byte-level scorer comes first.
