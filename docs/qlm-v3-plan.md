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


## Revision 1 (before any v3 code): corrections and a second task

Written after review, before implementation. Where this disagrees with the
text above, this governs.

**Two kinds of program.**
- **v3a, static:** a learned sequence of operations for a query type,
  executed whatever the intermediate results are. Stages L1 to L3 above.
- **v3b, dynamic:** at each pass the runtime inspects the working state,
  selects the next operation from it, executes it, and decides from the
  new state whether to stop. The operation chosen depends on what the last
  one returned. This is the property the runtime is eventually meant to
  have.

**Two training regimes, reported separately.**
- **T1, one-hop facts only:** no composed statement for anyone. A query
  type cannot be learned from examples here, so T1 tests the runtime with
  a supplied program, over learned entities and relations (stages O to
  L2).
- **T2, one-hop facts plus composed answers for training entities:** the
  program is learned from those examples and tested on held-out entities
  (L3, v3b). This is compositional generalisation from examples, not
  learning from one-hop facts alone, and is reported as that.

**Entities keep their identities.** An entity is the individual token, with
its occurrences and bindings. Context classes (v2's PPMI classes) are only
soft memberships used to propose candidates. Entity identity is never
reduced to a class.

**Stopping.** A learned fixed chain length is not a stopping decision. A
stop is learned only if it is conditioned on the state: on task B, where
paths of different lengths share one query type, a fixed-length program is
the control, and a learned stop must beat it.

**Depth, in two tests.**
- **D-extend:** a deeper world (one more level) with **no** composed
  answers at the new depth. The program must extend itself, for example
  by repeating an operation until a stop condition, not by being shown
  longer examples.
- **D-learn:** a deeper world with composed answers at the new depth: a
  new, longer program learned from them.

**Baselines on the exact task.** The transformers (Llama-shaped and the
custom one) and v2 are retrained on the v3 task data. The quoted
version-2 world numbers are not comparisons.

### Task B: state-dependent routing

A synthetic graph built so that the operation sequence is not predictable
from the query.
- **Nodes** have names and a kind (one of 6). Every node has 4 outgoing
  relations, each a different relation word; 3 of them are distractors.
- **The rule:** which relation to follow depends on the current node's
  kind. Two kinds are terminal: the walk stops there.
- **Paths** from start nodes are built to have length 2, 3 or 5, in equal
  numbers, under one query form ("from X the end is Z").
- **Text:** one-hop facts ("X is red .", "X points to Y ."). Under T2,
  also composed answers for training start nodes. Held-out start nodes
  never appear in a composed statement.
- **The learner must discover:** which relation each kind selects, which
  kinds stop the walk, and the identities of the nodes.
- **Tests:** accuracy by path length; depth 7 (D-extend, never seen
  composed); unseen start nodes; distractors at every step.

### Roadmap

| stage | what | state |
|---|---|---|
| v3.0 | oracle execution runtime (supplied knowledge and program) | next |
| v3.1 | entities and relations learned from text | planned |
| v3.2 | reusable operation sequences learned (v3a) | planned |
| v3.3 | state-dependent addressing (v3b) | proposed |
| v3.4 | dynamic computation depth: learned stopping | proposed |
| v3.5 | the computational state projected into next-token prediction | proposed |
| v3.6 | back to TinyStories | future |

v2's 4.024 bits per token stays frozen as the natural-language baseline.
Its 5-gram component is not yet under the normalisation gate.

### What v3.0 must show, and no more

- **The runtime executes correctly:** on both tasks, with the supplied
  knowledge and program, held-out accuracy is at least 99% once the number
  of passes is at least the path length, and is no better than chance
  below it.
- **Uncertainty is carried:** with one supplied fact made ambiguous (two
  objects, weights 0.5 and 0.5), the answer distribution splits in the
  same proportions.
- **The projection normalises:** the next-token distribution passes the
  admission gate.

None of this is learning. It qualifies the machine the learned stages will
replace parts of.
