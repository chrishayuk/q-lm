# LARQL-QLM-FFN-001 plan: which components build the grouping, causally?

Written before any intervention. It follows LARQL-QLM-GROUP-001, whose
attention/feed-forward split is correlational.

## Why geometry is not enough

GROUP-001 measures grouping on each word's state averaged over its
contexts. Attention mostly adds context-dependent variation, which
averaging removes, so that measure leans towards showing change at the
feed-forward steps. Every claim here is therefore made on **prediction**,
with geometry reported beside it.

## Models

- Llama, the custom transformer, and the QLM-ARCH-001 arms (base, tie,
  rope), seed 1, full size.
- On the right and left families, and on Colmerauer's language.

All interventions are done in PyTorch on hidden states. A sample of
intervened runs is repeated in LARQL, once it supports overrides, or
otherwise checked against LARQL's unintervened dump (parity 1e-6,
GROUP-001).

## Interventions, at each block l separately

| intervention | what is changed | control |
|---|---|---|
| attention removed | the block's attention output replaced by its mean over the development tokens (mean-ablation; zeroing is also reported) | a random vector of the same norm added instead |
| feed-forward removed | the same, for the feed-forward output | the same |
| feed-forward patched within class | at one noun position, the feed-forward output replaced by that of another noun of the same slot, depth and position | the same from a token of another class |
| grouping direction removed | the residual stream projected off the subspace spanned by the class-mean differences at that layer (fitted on the first half of the development sentences) | projected off a random subspace of the same dimension |
| direction restored | after removal, the removed component added back from a different sentence's token of the same class | added back from a token of another class |

## Measures

On the second half of the development sentences, which are not used to fit
anything:
- **Prediction:**
  - development bits per token;
  - next-token class accuracy (the most probable next token's class
    against the true next token's);
  - the probability mass on tokens of the right class.
- **Behaviour:** the grammaticality of 300 samples, judged.
- **Geometry:** the within/between class distance ratio at every later
  layer.

## What would count

- **A component builds the grouping causally** if removing it at block l
  does all three of these, while the matched random control moves each by
  under a tenth as much:
  - raises the distance ratio at block l + 1 by at least 0.1;
  - lowers next-token class accuracy by at least 5 points;
  - raises development bits by at least 5%.
- **The grouping is functional** if removing the class subspace lowers
  class accuracy by at least 5 points where a random subspace of the same
  dimension does not, and restoring it from a same-class token recovers at
  least half the loss.
- Restoring from another class is the control.

## Not in this experiment

Replacing a component with a symbolic operation: an operation needs to be
identified and qualified first. If an intervention above finds a component
that builds class grouping, a later experiment tries replacing it with an
explicit map from words to class directions, measured by the same
prediction measures.
