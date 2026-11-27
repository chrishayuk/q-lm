# LARQL-QLM-ENRICH-001 plan: is the fact looked up at the entity's position?

Written before any measurement. It follows TRANSPORT-001. There, a few
heads carry the answer to the last position, and in the custom transformer
what they carry already looks partly like the capital. So it is possible
that the feed-forward at the country's own position enriches the country
with its facts, and attention then extracts the relevant one: the
subject-enrichment account of Geva et al. (2023).

## Models and prompts

- The 18 version-2 models, for capitals:
  - recipient `the capital of C' is`;
  - donor `the capital of C is`;
  - the country at position 4.
- The 18 version-3 models, once trained, for the reuse test.
- Pairs: 120 per model. Choices (blocks, components) are made on the first
  60 and judged on the other 60, as in TRANSPORT-001's addendum.

## Interventions, at the entity's position, block by block

1. **Patch the feed-forward output only.** The feed-forward's output (the
   amount it adds) at the country position in block b is replaced by the
   donor's. The country's own state, and the attention output, are kept.
   - The share in which the donor's capital wins.
   - The mean change in log2 P(K) − log2 P(K').
2. **Remove it.** The feed-forward output at the country position in block
   b is replaced by its mean over all 24 countries' prompts (mean-ablation).
   The measure is accuracy on the recipient's own capital, against
   mean-ablating the same block's feed-forward at a non-entity position
   (`capital`, position 2).
3. **Restore it.** The recipient is corrupted by replacing the country's
   embedding with another country's. Only the feed-forward output at the
   country position in block b is restored from the clean run. The share
   in which the clean answer returns.
4. **Reuse across queries (version 3).** For a person P, the feed-forward
   output at P's position in block b is patched from another person Q. It
   is read under two queries:
   - `P lives in`, which should then give Q's home city;
   - `P was born in`, which should then give Q's birth city.

   If one patch changes both answers, each to the donor's, the enrichment
   carries both facts at once, for later selection by the query. That is
   reusable knowledge. Reported against a magnitude-matched random patch.

## What would count

- **Enrichment at the entity position in block b:**
  - patching the feed-forward output alone gives the donor's capital in at
    least half the judged pairs;
  - removing it lowers own-capital accuracy by at least 25 points more
    than the control position does;
  - restoring it alone recovers at least half the corrupted answers;
  - a magnitude-matched random patch does each under a tenth as often.
- **Reusable enrichment:** in version 3, at the block chosen on the first
  half, one patch makes both the home-city and the birth-city query give
  the donor's cities, in at least half the judged people. The random patch
  does so in under a tenth as many.
- If no block passes, the entity's state after block 1 (SEM-001) was
  carrying what attention brought in or what the embedding gave, not what
  the feed-forward added. That is the result reported.

## Afterwards: an external representation

If enrichment passes, the following experiment replaces the feed-forward
output at the entity position with a constructed vector:
- the mean feed-forward output, over the training prompts, of entities that
  share the relevant facts;
- or a vector built from the facts by a fitted linear map.

It asks whether the downstream heads extract the right answer from it.
That is the first test of putting an external graph operation in the place
of one neural computation.
