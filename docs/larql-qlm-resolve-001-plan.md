# LARQL-QLM-RESOLVE-001 plan: does the late feed-forward retrieve the fact, and can an external table stand in for it?

Written before any measurement. It follows ENRICH-001's follow-up. There,
patching the feed-forward output at the answer position moved the answer:
in Llama at blocks 3 and 4 (0.77, 0.81), in the custom transformer at block
4 (0.57). That alone cannot tell retrieval from amplification,
transformation or selection.

The models are the 18 version-3 models. The prompts are `the capital of C
is` (24 countries) and, for the external part, `P lives in` too. Block b*
is the block with the largest effect in ENRICH-001's follow-up: 4 in both
architectures, with 3 also reported for Llama. Choices are made on the
first 60 pairs and judged on the other 60.

## Part A: retrieval or amplification?

1. **Is the answer already there before the feed-forward?** At the answer
   position, the residual state just before block b*'s feed-forward is read
   through the final norm and the output head (logit lens). Is the true
   capital the top city?
   - If yes, mostly, the feed-forward can at most amplify or transform.
   - If no, and it is the top city after the feed-forward, the
     feed-forward produced it.
2. **Removal.** The block-b* feed-forward output at the answer position is
   mean-ablated (over the 24 prompts). The measure is own-capital accuracy,
   against ablating the same feed-forward at position 2.
3. **Answer-free input.**
   - The feed-forward is given its normal input, with every city's
     output-embedding direction projected out: the span of the 24 city rows
     of the output head.
   - Its output is added to the unchanged residual, in place of its normal
     output.
   - Does the true capital still win?
   - If yes, the feed-forward computes the answer from something that is
     not the answer's own direction (the entity and relation), which is
     retrieval. If no, it needs the answer already present, which is
     amplification.
   - Control: projecting out a random subspace of the same dimension.

**Reading:**
- **Retrieval at b*:**
  - the lens before the feed-forward has the true capital top in under
    half the prompts;
  - removal lowers accuracy by at least 25 points more than the control
    position;
  - with the answer-free input, the true capital still wins in at least
    half the prompts.
- **Amplification:** the lens before the feed-forward already has it top in
  at least three quarters, and the answer-free input does not recover it
  (under a quarter).
- Anything else is reported as found.

## Part B: an external table in place of the feed-forward

The **answer vector** of a city K is the mean of the block-b* feed-forward
output at the answer position over prompts whose answer is K, taken from
**other relations and other subjects** than the test prompt: `P lives in`
for the two residents of K. The capital prompt itself is never used to
build its own answer vector.

1. **Lookup.** For `the capital of C is`, the block-b* feed-forward output
   at the answer position is replaced by the answer vector of the city a
   table gives for capital(C). The table is the world's true capitals. Does
   the model then give the table's city?
2. **Changing a fact without changing weights.** The table is edited so
   that capital(C) is a different city K*, a random derangement of the
   capitals. The output is replaced with K*'s answer vector. Does the model
   now say K*?
3. **Side effects.** With the replacement active only for C's prompt,
   every other country's `the capital of X is` and every `P lives in` are
   unchanged, by construction. So this is measured instead: the edited
   prompt's distribution over non-city tokens, and its END after the
   answer, if generated.
4. **Controls:**
   - the answer vector of a random city, which should give that city, as a
     check of the vectors themselves;
   - a magnitude-matched random vector, which should give no particular
     city;
   - the answer vector built from the capital prompts themselves
     (leave-one-country-out), as a ceiling.

**What would count:**
- **The external lookup works** if, at b* and before the last block where
  possible, it gives the table's city in at least 90% of prompts, with true
  capitals as the table.
- **An edited fact works** if it gives K* in at least 75% of prompts.
- In both, the magnitude-matched random vector gives the table's city in
  under 5%.

The last block (4) is read by the output head directly, so success there is
partly by construction: an answer vector added just before the head
favours its city. It is therefore reported as the weaker result. A success
at block 3 in Llama, with block 4 still running on it, is the stronger one.
