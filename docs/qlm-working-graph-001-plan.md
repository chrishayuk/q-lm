# QLM-WORKING-GRAPH-001 plan: a graph-native working state (Q-LM v4 candidate)

Written before any code. It follows QLM-TINYSTORIES-V3-001, whose stories
read as local fragments: grammatical clauses, the opening repeated, and a
different character in every sentence. Every component there reads the raw
words and votes on the next one independently. Nothing builds a
representation that a later operation can read.

## The hypothesis

Next-token prediction improves, beyond more retrieval of the same kind,
when operations write intermediate results onto a working graph of the
current story, and later operations address and read those results.

## The working graph

- **Nodes:** every token occurrence of the story prefix, kept individually
  (no merging of identities).
- **Each node holds a sparse set of features:**
  - **initially:** its word, its class under each of v2's 4 class models,
    its position in its sentence (bucketed) and its sentence's position in
    the story (bucketed);
  - **written by operations:** any feature an operation produces.
- **No feature is given a meaning.** Whether a feature tracks an entity, a
  construction, a sense or nothing nameable is left to what survives
  selection.

## Operations

An operation (q, k) has a query feature type q and a key feature type k.
At the current position:
1. **Address:** every prefix node is weighted by lift(q-feature of the
   current node, k-feature of that node). Lift tables are counted on the
   training stories, as D's binding was, but over feature types, not words.
2. **Read:** the addressed nodes' features, weighted.
3. **Write:** the read features, as new features with weights, onto the
   current node and onto the addressed nodes. Example: "this node is
   addressed by the current one".

A pass applies one operation. A later pass can use written features as its
q or k: this is the "residual stream".

**Prediction:** the continuations of the nodes addressed in the final
pass, weighted (as D's second read). It is a component in the frozen mixture.

## Credit assignment (learning which operations to compose)

- **Candidates:** every (q, k) over the feature types available at that
  pass, written features included.
- **Selection:** greedy, pass by pass.
  - Pass p keeps the candidate whose addition most lowers bits on held-out
    training stories (the last 10% of the n training sentences, by story),
    with the earlier passes fixed.
  - Counting for the lift tables uses the first 90%.
  - Selection stops when no candidate gains at least 0.001 bits.
- **No development data is used to choose operations.** The fit split
  (development 0 to 999) fits mixture weights only.

This is credit assignment by measured downstream gain, not a gradient. It
can only find compositions that greedy addition reaches; that is a known
limit.

## Arms

| arm | what |
|---|---|
| A | B3 + D (the current best, frozen) |
| P | A with mixture weights also bucketed by sentence-in-story (0, 1, 2+): the cheap story-position baseline |
| B | A + independent retrieval: the operations C to F would select, each run as its own component on the original features only (no written features) |
| C, D, E, F | A + the working graph with 1, 2, 4 and 8 selected passes |
| G | matched computation without sharing: as many operations as the best of C to F, each reading only original features, their predictions mixed |

## Measures

- **Bits per token:** select split at 10,000 and 100,000; confirm3 once,
  for the best arm, A, P and G.
- **Generation:** 20 stories per arm, the same seeds and opening, unrestricted
  and top-p 0.9. Counted automatically:
  - restarts of the opening per story;
  - "the end" before the last sentence;
  - character persistence: the fraction of sentences after the first that
    reuse a name from an earlier sentence;
  - distinct names per story.
- **Costs:** CPU time, peak memory, serialised model size and working-graph
  size per story.

## Criteria

- **The working graph helps:** the best of C to F below A, P, B and G by at
  least 0.005 bits at 10,000 and 100,000, and below A on confirm3.
- **Composition helps:** the best multi-pass arm below C by at least 0.003,
  and below G.
- **Generation improves:** fewer opening restarts and higher character
  persistence than A and P, over the 20 stories.

## Separate, not part of this experiment

- **The encoding fix** (mis-decoded quotes, "â € œ", in the corpus): a
  versioned data experiment. The present benchmark stays as it is.
- **Story-position alone** (arm P) is in this experiment only as a
  baseline.

## Revision 1 (after review, before any code)

**A fresh confirmation set, confirm4.**
- confirm3 is being opened for v3, so v4 gets its own: TinyStories
  validation stories 2,000 to 2,999, prepared by `tools/ts_prep.py`
  (16,614 sentences).
- `data-ts-c4/`, `--split confirm4`, used once for the final v4 arms. Not
  read until then.

**Credit assignment that can find "useless now, useful later".**
- **Greedy (as above) is the baseline.**
- **Beam (new arm C-beam):** the 4 best partial compositions are kept at
  each pass, and pass p's candidates are scored by the best gain any
  continuation achieves within 2 further passes (lookahead 2). A pass that
  gains nothing alone but enables a later gain can be kept.
- Both use only held-out training stories.

**Arm B, exactly.** For every operation C to F selects, B runs it as its
own component with the q and k feature types replaced by their nearest
original type:
- a written feature's original type is the type of the features it was
  read from (a written feature derived from a word feature becomes a word
  feature);
- each B component reads the original features only, and the components
  are mixed independently.

**Feature propagation, bounded.**
- **Weights:** each node's features carry weights that sum to 1 per
  feature type, normalised after every write.
- **Deduplication:** a feature written twice is one feature, with summed
  weight.
- **Pruning:** features below 0.01 are dropped after each pass.
- **Maximums:** 16 written features per node per type; 64 addressed nodes
  per operation (the highest-weighted), so cost is linear in the prefix,
  not quadratic.

**Causal correctness.** The prediction at position t may depend only on
tokens before t and on writes made while processing them.
- The working graph is rebuilt position by position, never revised from
  later tokens.
- Checked by `tools/check_story_leak.py`'s method: changing later words or
  sentences must not change any earlier probability.

**Transform, the FFN analogue.** One more operation kind, added in a
second stage after address, read and write work: a conjunction.
- A new feature is written where two features co-occur on a node (or on
  a node and its addressed node), if that conjunction lowers held-out
  bits.
- It derives new information instead of moving it.
- **Consolidation:** two written features whose node sets overlap above
  Jaccard 0.9 on the held-out stories are merged.

**Generation quality, beyond names and openings.**
- **Grammaticality proxy:** the mean per-token bits of each generated
  sentence under the sentence-level Llama baseline. It is independent of
  Q-LM, and a lower value means more like TinyStories.
- **Contradictions and overall coherence:** read by a person, blind to
  the arm. 10 stories per arm, shuffled, from the same seeds, each scored
  0 to 2 for coherence and with contradictions noted. The procedure is
  fixed here; the scores are reported with the reader's notes.

**Computational budgets, as architectural limits.**
- 64 addressed nodes per operation;
- 16 written features per node per type;
- at most 8 passes;
- a working graph of at most 4,096 nodes per story (older nodes are dropped
  first).

These are limits, not tuned values. Exceeding one is reported, never
silently raised.

**Clarification: two directions of writing, and revision.**
- **Across passes, at one position:** each pass reads the graph as the
  earlier passes left it and adds its writes. A written feature can be the
  query or key of a later pass: a result becomes an address.
- **Across positions, as the story grows:** new nodes are added.
- **Earlier nodes may be revised.** At position t an operation may write
  onto any earlier node, using only tokens before t. The prediction at t
  reads the graph as it stands at t.
- The causal rule is only that nothing is derived from tokens at or after
  the position being predicted, unlike a transformer's cache, whose earlier
  states are fixed.
- **The control, arm C-frozen:** C to F's best arm with writes onto earlier
  nodes disabled (writes onto the current node only). It measures what
  revision adds.

**Final clarifications (before code).**
- **Indexed addressing.** Choosing the 64 best nodes by scanning the whole
  prefix is still quadratic in total. The graph keeps an inverted index:
  key feature → the nodes holding it, with weights. An operation looks up
  only the nodes that share a key feature with its query, so the work per
  position is proportional to the matches, not to the prefix.
- **Uncertainty is kept, not sharpened.**
  - Normalising a feature type's weights on a node never raises them above
    the evidence for them: what pruning removes is recorded on the node as
    discarded mass, and the weights are normalised over kept plus
    discarded.
  - A feature's absence (no evidence) and a feature with weight driven
    down by a write (evidence against) are distinct states.
- **Revision can suppress.** A write carries a signed weight. A negative
  write lowers a feature's weight on a node, multiplicatively, down to its
  removal. Operations may learn negative writes when those lower held-out
  bits. Example: evidence that weakens an earlier interpretation.
- **confirm4 compares** the winning arm with the strongest controls
  (P, B, G and C-frozen), not only with A.
