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

## Revision 1 (data hygiene and stronger retrieval, before any C to E code)

**Exact story boundaries.**
- The 353 development sentences that did not align all contain `<unk>`;
  aligned with `<unk>` as a wildcard, every sentence aligns, none
  guessed.
- `tools/ts_prep.py` then reproduces data-ts's preprocessing exactly:
  lowercase; sentences end at . ! ? followed by whitespace; tokens are
  letter runs, digit runs and single other characters; 2 to 40 tokens;
  out-of-vocabulary words as `<unk>`.
  - It reproduces all 13,959 development and all 346,098 training
    sentences, line for line.
  - So the story ids are exact; `data-ts/*.story` are its output.
- The first B result (5.770 at 1,000) used the earlier assignment, in
  which about 40 development sentences had an inherited story. Rerun.

**An untouched, story-disjoint confirmation set: confirm3.**
- TinyStories validation stories 1,000 to 1,999, prepared the same way:
  14,227 sentences.
- No experiment has read them.
- They live in `data-ts-c3/`: its dev.txt is data-ts's first 11,000
  development sentences (so the fit split, 0 to 999, is unchanged),
  followed by confirm3 (indices 11,000 onwards). `--split confirm3`.
- It is used once, for the final arms.
- confirm2 (development 7,000 to 10,999) has been read by earlier v2
  experiments, so it is no longer a confirmation set.

**Stronger retrieval controls:** B3 = B + B2 + a trigram cache (the
prefix's own continuations of the last two words) + recency-weighted
caches (decay 0.95 and 0.99), all as components mixed by EM. Computation
must beat B3.

## Revision 2: designs of C and D (before their code)

The tokens and vocabulary stay frozen. No pronoun rules, grammatical
categories or annotations are supplied.

**C, direct span retrieval (`--story spans`).**
- Learned spans: from the n training sentences, every 2- to 4-word
  sequence seen at least max(5, n / 20,000) times. They overlap; no
  segmentation is chosen.
- At each position, the longest learned span ending the context is the
  key. The component predicts what followed that span in the story
  prefix, backing off to the previous-word cache and the word cache as in
  B3.
- It differs from B3's trigram cache in its keys: variable-length learned
  spans, not a fixed two words.

**D, reference binding and successive retrieval (`--story bind`).**
- **Learned binding.** On the training stories, for each position t with
  previous word r and next word y, and each other word a in the story
  prefix:
  - count a trial for (r, a);
  - count a hit if y followed a somewhere in the prefix.
  - Then lift(r, a) = P(hit | r, a), smoothed towards the overall hit
    rate, divided by that rate.
  - So "she" binds to the words whose continuations predict what follows
    "she": learned from co-occurrence of continuations, not from a
    pronoun list.
- **Inference, two reads, the second using the first's result:**
  1. a distribution over the prefix's words a, given the current word r:
     weight ∝ max(lift(r, a) − 1, 0) × the number of times a occurs in
     the prefix;
  2. the next word from what followed each a in the prefix, mixed by
     those weights, smoothed by the training unigram.
- **Uncertainty is kept:** step 1 is a distribution, never one referent,
  and nothing is merged permanently.

**Controls:**
- **D0, matched reads without the learned binding:** step 1 uniform over
  the prefix's other words (the same two reads).
- **B3:** direct retrieval, which must be beaten.
- D's improvement must be over B3 + D0, not only over A.

**Causal diagnostics, after a first result:**
- rename an entity throughout the prefix;
- move an object from one character to another;
- add a competing referent.

Each is measured as the change in D's next-word distribution after a
referring word, against the change predicted by the edit.

**Criteria (unchanged from the plan):** "computation helps" if C or D
lowers bits below B3 by at least 0.005 at 10,000 and at 100,000, and
confirms on confirm3. "Successive" if D lowers bits below B3 + D0 by at
least 0.003.
