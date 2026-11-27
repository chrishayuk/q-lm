# LARQL-QLM-EXTERNAL-001 plan: an external graph driven by the model's own state

Written before any provider is built. It follows RESOLVE-001, where a city
vector chosen by an external table and injected at Llama's block-3
feed-forward changed the stated capital in 90% of prompts. There, the
table was told the entity and the relation. Here the provider gets only
activations and must work them out.

## The provider

**What it receives.** Only the residual stream at the answer position, after
block 1 (Llama) or block 2 (custom transformer), of the running prompt. Not
the prompt text, not the token ids, not the answer.

**What it does:**
1. **Entity.** Nearest key, by cosine. The keys are built once, from other
   prompts: for each entity, the same-position state of a different
   relation's prompt with the same entity.
   - A country's key: `C is in` (continent), wording 1.
   - A person's key: `P is from` (home), wording 2.

   The key prompt is never the query prompt.
2. **Relation.** Nearest centroid among capital, continent, home and birth.
   The centroids are mean states of wording-2 prompts (`the capital of C
   is`, `C lies on`, `P is from`, `P is a native of`) over three quarters of
   the entities. It is tested on wording-1 prompts (`C has capital`, `C is
   in`, `P lives in`, `P was born in`) for the other quarter.
3. **Lookup.** (entity, relation) in a graph: the world's facts, or an
   edited copy.
4. **Return.** The answer's vector is injected at the block-b feed-forward
   output at the answer position: Llama at block 3; the custom transformer
   at block 4, the only block where injection worked in RESOLVE-001.
   - A city's vector is the mean block-b feed-forward output over prompts
     answered by that city, of another relation than the query's. Capital
     and birth queries use `lives in` prompts; home queries use `was born
     in` prompts.
   - A continent's vector is built likewise from `lives on`.

## Arms

| arm | entity | relation | graph |
|---|---|---|---|
| oracle | given | given | true |
| A | from the state | given | true |
| B | given | from the state | true |
| C | from the state | from the state | true |
| D | from the state | from the state | **edited**: every country's capital and every person's home and birth city replaced by a different one, after the model is frozen |
| E | from the state | from the state | **new facts**: the 4 single-observation people, who have no birth fact in the model, given birth cities in the graph |

## Measures

On wording-1 prompts of the held-out quarter of the entities:
- **Decoding:** entity accuracy and relation accuracy, reported apart.
- **Answer:** the share in which the model's output (top of the answer's
  type) is the graph's answer.
- **Controls:**
  - **provider disabled** (no injection): the model's own answer;
  - **provider on a prompt it should not answer:** `the` (a bare start),
    where the provider's best relation match is reported, and its effect
    on the model's top token;
  - **magnitude-matched random injection;**
  - **paraphrase:** the same queries in wording 2, where the relation
    centroids were fitted. Reported, but not counted.

## What would count

- **A working activation-driven provider (arm C)** if:
  - entity and relation are both decoded in at least 90% of held-out
    prompts;
  - the model gives the graph's answer in at least 85%;
  - the random injection gives it in under 5%.
- **Editing knowledge through it (arm D)** if the model gives the edited
  answer in at least 75% of held-out prompts.
- **Adding knowledge through it (arm E)** if, for the 4 people per world
  the model never learned a birth city for, the model gives the graph's
  birth city in at least 3 of 4. That is 12 of 12 people over three worlds
  per architecture, and so only a small test.

All of it runs first on the version-3 worlds 1 to 3. It is then repeated,
unchanged, on the confirmation worlds 4 to 6. Those were trained after
this plan was written, as a confirmation run of RESOLVE-001 and of this
experiment.
