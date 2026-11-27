# Q-LM v3 plan: a learned computational runtime (address, read, transform, write)

Written before anything is built. v2, the statistical architecture, is
closed at its results: v2 at 4.024 bits per token on TinyStories at
100,000 sentences, with every successive-lookup arm failing its criterion
(results-qlm-key-001-cde.md). Its code and every negative result stay as
baselines.

## The idea

v2's successive arms factorise a prediction: a category, then a word in
it. v3 executes a computation whose result changes what is looked up next.

- **Persistent knowledge:** relations between entities, learned from the
  text as counted bindings (entity, relation, entity).
- **Working state:** the entities bound so far for the current query, with
  their weights (a distribution, not one hard value), and what relation
  each came through.
- **The cycle, repeated for a number of passes:**
  - ADDRESS: build (entity, relation) from the working state;
  - READ: look it up in the persistent knowledge;
  - TRANSFORM: turn the read distribution into the next state;
  - WRITE: update the working state.
- **Projection:** at the end, the working state becomes a next-token
  distribution over the answer's type, mixed with the language model for
  everything else.

## The task first, not TinyStories

The version-3 semantic worlds (QLM-SEMANTIC-001):
- **Training text holds only one-hop facts:** P lives in K; K is located
  in C (for the countries whose inverse is not held out; otherwise "C has
  capital K"); C is in T.
- **The test is composed:** "P lives on ?" for the 16 held-out people per
  world, whose continent never appears with them in any text. That is
  three hops.
- **Baselines already measured there (version 2 of the worlds):** Llama
  65% (38 to 94), custom transformer 41%, the grammar learner 25%
  (chance).

## Stages: from oracle to learned, one supply removed at a time

| stage | entities | relations | which relation sequence answers a query | what it shows |
|---|---|---|---|---|
| O | given (the world's names) | given (the world's relations) | given (lives, located, continent) | the runtime executes correctly: a check, **not** learning |
| L1 | given | **learned:** relation = the word frame between two entities ("_ lives in _", "_ is located in _"), frames grouped when they link the same pairs | given as frames | relations can be found from text |
| L2 | **learned:** entity = a word whose context class (v2's PPMI classes) is entity-like, judged by taking part in frames | learned | given | entities can be found from text |
| L3 | learned | learned | **learned:** for a query frame (e.g. "_ lives on _"), the chain of learned relations, length 1 to k, whose execution gives the training answers for the people whose lives-on is seen. It is chosen by held-out accuracy on a tenth of them | the program can be found from examples |

**Not counted as learning:**
- traversing a supplied graph (stage O);
- anything that reads the world file, relation names or held-out answers.

Stage L3 gets only the training text.

## Passes

Each stage runs with the number of passes fixed at 1, 2, 3, 4 and 8, plus
"learned": the chain length L3 chooses. A pass is one
address–read–transform–write cycle.
- **The expectation:** 1 and 2 passes fail the three-hop test, and 3 or
  more pass.
- **The question that matters:** does L3 learn to use 3, and does it stop
  there?

## Controls

- **Flat predictor:** v2 (the 5-gram plus class models), trained on the
  same text.
- **Direct retrieval:** one pass.
- **Matched budget:** a v2 mixture given bindings equal in number to v3's
  persistent knowledge, as composite keys.
- **The transformers' existing numbers on the same test.**

## Tests

- **Held-out composition:** "P lives on ?" for the 16 held-out people,
  three worlds. Accuracy over the 4 continents (chance 25%), and contrast.
- **Paraphrase:** the query in a phrasing never used for it in training,
  e.g. "P is from a city on ?", added as a test-only frame.
- **Distractors:** the same people's other relation, "P was born in ?".
  It must not be answered with their home chain.
- **Depth beyond training:** a version-4 world with one more level
  (continent → hemisphere, one-hop facts only), queried at four hops.

## Measures, and the gate

- **Normalisation:** every predictive component passes the admission gate
  (sums to 1 within 1e-6 on prefixes including unknown words and sentence
  ends).
- **Storage:** serialised model bytes, written to disk and measured, not
  estimated.
- **Time:** learning time, end to end.
- **Inference:** time per full next-token distribution, over the whole
  vocabulary.

## What would count

- **The runtime works:** stage O reaches at least 99% on held-out
  composition with 3 passes.
- **v3 learns computation:** L3 reaches at least 90% on held-out
  composition, with the chain length it learned, on all three worlds.
  Meanwhile:
  - 1 pass is at most 35%;
  - the flat predictor and the matched-budget control are at most 50%.
- **It generalises the program:**
  - the paraphrase test is at least 75%;
  - the distractors are answered by their own chain in at least 75%;
  - the four-hop world works with the chain extended by learning, not by
    hand.
