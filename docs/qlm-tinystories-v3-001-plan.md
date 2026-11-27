# QLM-TINYSTORIES-V3-001 plan: does learned computation improve v2 on TinyStories?

Written before any code. v3 on the synthetic worlds is closed for now
(STATE-001 closed; numerical grounding is a separate synthetic track).

## The question

Does adding computation over a story-local working state to the frozen
v2 next-token distribution lower its bits per token, and is the gain due
to computation, not to retrieval or extra storage?

## Data

The existing `data-ts`: the same sentences, splits and vocabulary.
- **Story boundaries recovered.** data-ts kept no story boundaries.
  `tools/story_ids.py` aligns every sentence, unchanged, to the raw
  TinyStories stories by its whitespace-free characters, in order.
  - It finds exactly 20,000 training and 1,000 development stories, as
    the data was built.
  - 0.6% of training and 2.5% of development sentences do not match
    exactly; they inherit the previous sentence's story.
  - 70% of recovered stories begin "once upon a".
- **The story prefix:** for a development sentence, its story's earlier
  sentences (and the earlier words of the sentence itself). That is all a
  component may read: no future tokens.

## A fairness point that changes the comparison

v2 (4.024) and the transformers (3.760, 3.935) were trained and scored
**one sentence at a time**. Story context is information none of them
had. So:
- **Arm B (story-local retrieval) is the control that sets the bar.** Any
  gain from story context alone shows up there. Computation must beat B,
  not only A.
- **A transformer given the same story context** is the fair neural
  comparison. It is deferred to stage T5, and until then no comparison to
  the transformers' numbers is claimed.

## Arms

All arms are added, as components, to the frozen v2 mixture (5-gram plus
class models, E's composite keys, weights by position bucket). Mixture
weights are fitted by EM on the fit split.

| arm | component |
|---|---|
| A | frozen v2 (KEY-001 arm E with buckets: 4.024 at 100,000 sentences) |
| B | + story cache: P(w) from the words of the story prefix, by count (direct retrieval) |
| B2 | + story cache keyed by the previous word: P(w \| v) from the prefix's own bigrams (direct retrieval, more specific) |
| C | + learned relational bindings: v3.1 frames learned on the training text; the prefix's sentences parsed into (subject, frame, object) bindings; a binding whose subject and frame match the current context predicts its object |
| D | + successive operations: C, plus one more read from what C retrieved (e.g. pronoun → entity → its binding) |
| E | D with weighted interpretations: several frames and referents kept, weighted, merged by entity |

**Controls:**
- **Matched storage:** B and B2 given at least as many stored items as C
  to E use.
- **Matched computation:** D against C given the same number of reads,
  but each a direct one (no read uses the result of another).

## Measures

- Bits per token on the full vocabulary, all positions and by position
  bucket.
- The admission gate on every new component: next-token probabilities
  sum to 1 over the vocabulary and END.
- Learning time, serialised model size, inference time per token, and
  active states.

## Stages

| stage | training sentences | split for numbers |
|---|---:|---|
| T1 | 1,000 | select (dev 1,000–2,999) |
| T2, T3 | 10,000 | select |
| T4 | 100,000 | select, then confirm2 (dev 7,000–10,999) once |
| T5 | full corpus | with a story-context transformer |

## Criteria

- **Story context helps:** B below A at 10,000 sentences.
- **Computation helps:** C, D or E below B and B2 by at least 0.005 bits
  at 10,000 and at 100,000 sentences, and confirmed on confirm2.
- **Successive computation helps:** D below C, and below C with matched
  reads, by at least 0.003.

## Not allowed

- future-token access;
- supplied semantic annotations;
- hand-written story rules;
- tuning on select or confirm2.

Mixture weights come from the fit split; the select split is for
choosing among arms; confirm2 is used once.
