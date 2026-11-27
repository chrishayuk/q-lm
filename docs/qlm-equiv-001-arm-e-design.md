# QLM-EQUIV-001 arm E: design (draft, not yet built)

Arms B, C and C′ showed the cost of keeping distinctions with the present
representation.

| | arm A | arm C′, θ = 0.05 |
|---|---:|---:|
| categories, 1,000 left sentences | 45 | 254 |
| rules | 298 | 9,335 |
| fresh ungrammatical sentences accepted | 166 of 300 | 28 of 300 |
| development bits per token | 1.300 | 1.515 |

The stricter arms leave tens of thousands of categories and hundreds of
thousands of rules, too large for inside–outside. Every distinct substring
is a category candidate, and every split of it is a rule. Keeping
distinctions that way multiplies both.

Arm E has to keep distinctions **without** multiplying categories.
Principles, each with what would test it:

1. **Identity is never merged away.**
   - Every word, and every phrase that recurs, stays a node of its own.
   - Categories are separate nodes, linked to their members by weighted
     membership edges: abstraction by accumulation.
   - So `France` keeps its own facts while belonging to the country
     category.
2. **Not every substring is a node.**
   - A substring becomes a node only if it recurs (in at least 2
     sentences) and is bounded: the words around it vary more than the
     words inside it. That is branching entropy at both edges.
   - The rest are paths through nodes, derived when a sentence is parsed,
     never stored as rules.
   - Test: the stored node count against the training size (QLM-SCALE-001).
3. **Membership is conditional and sparse.**
   - A node's membership weights come from its context overlap with each
     category (Jaccard, as in C′).
   - Only the top m categories per node are kept (m = 4).
   - Parsing uses a node through its categories, weighted. A rule
     `X → Y Z` is over categories.
   - A frequent string and a rare one sharing one context get a weak
     membership in each other's category, not a merge.
4. **Probabilities are local.** Stepwise (online) EM: each sentence's
   expected counts update only the rules its parse touched, with a
   decaying step size. It is checked against batch inside–outside on the
   1,000-sentence grammars, for development bits and samples, before it is
   used at scale.

**What arm E must beat, on the plan's measures:**
- **A:** overgeneration (166 of 300).
- **C′:** corpus fit (1.515) and size (9,335 rules).
- **Inference:** the exact next-token prefix computation must still run.
  Memberships are unary edges, so it needs the unary closure the plan
  already names.

## Revisions to the draft

- **Storing, promoting and computing are separate.**
  - Every observation is stored, including phrases seen once.
  - Promotion into a reusable node needs a recurrence of at least r, where
    r is a setting tested at 1, 2 and 3, not a rule.
  - Computing uses only what the current input activates. One-shot
    understanding has to stay possible.
- **Branching entropy is evidence, not a gate.** It weights a candidate
  node's promotion score beside its recurrence. It does not decide alone.
- **Sparsity is tested, not fixed:** m = 1, 2, 4, 8 category memberships,
  and an adaptive m. The adaptive m keeps a node's memberships until they
  cover a fixed share (0.9) of its total membership weight.
- **Memberships must depend on context.**
  - Static Jaccard weights say how similar two strings are overall, not
    whether they are interchangeable here.
  - At parse time, a membership is used in a context only if the context
    is among those that support it: the contexts its Jaccard weight was
    built from, or contexts of the category's other members, matched to a
    bounded width of k words on each side.
  - This is the mechanism to build first.
- **Stored graph against active graph.** The stored graph holds everything
  learned. A sentence activates only the nodes its words reach and the
  memberships its contexts support. Cost is measured on the active graph
  (QLM-SCALE-001).
- **Local estimation is checked first.** Stepwise EM is run beside batch
  inside–outside on the 1,000-sentence grammars of all four languages. The
  differences in development bits and in samples are reported before
  stepwise EM is used anywhere else.
- **Semantics shapes it from the start.** The first workload is not only
  the four grammars but the version-3 semantic worlds, so that
  identity-keeping is tested where it matters. Per-entity facts must
  survive grouping.

Not yet built. It is planned in full before it is.
