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

Not yet built. It is planned in full before it is.
