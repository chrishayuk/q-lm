# QLM-ATTENTION-001 plan: graph-native attention, learned without backpropagation

Written before any measurement. It follows E4's failure. v2 learns static
representations, but nothing selects, per prediction, which earlier
information matters. That is attention's job.

## Setting

TinyStories `data-ts`, sentence by sentence: the transformer was trained
on single sentences, so attention stays within the sentence too. Sizes
10,000 and 100,000. The splits are as for E4:
- development 1 to 1,000: fitting (mixture weights by EM, and each arm's
  temperature or decay, by grid);
- 1,001 to 3,000: comparing arms;
- 3,001 to 7,000: one confirmation run of the final comparison.

## The retrieval component

At position t, the earlier positions i < t of the sentence are weighted by
a_i. The prediction is P_attn(w) = Σ_i a_i · A(w | x_i), where:

- **The values.** A(· | u) is an association distribution: how often w
  follows u anywhere later in the same sentence, at distance at least 1,
  over the training sentences. It is counted, not trained.
- **The keys and the query.** These are the distributional vectors of
  pass 1 (PPMI, SVD). The key is k_i = E[x_i]; the query is
  q_t = E[x_{t-1}].
- **The temperature τ and the relative-position bias b(d).** Fitted on the
  fitting split by grid.

P_attn is one more component in the mixture: with the 5-gram and the 4
class models of v2 (seeds, E4's best).

## Arms

| arm | weights a_i | what it controls for |
|---|---|---|
| A | (none: v2 alone, 5-gram + 4 class models) | the baseline |
| B | (none: an 8-gram word model in place of the 5-gram) | a longer fixed window |
| C | uniform over i < t | association values, no selection |
| D | ∝ ρ^(t−i), ρ fitted | recency, no content |
| E | ∝ exp(cos(q_t, k_i) / τ) | content-based selection |
| F | ∝ exp(cos(q_t, k_i) / τ + b(t − i)), with b log-linear in distance, its slope fitted | content plus relative position |
| G | F, plus a second head at the level of classes: values A(class of w \| class of x_i) · P(w \| class) | several retrieval mechanisms |

Arm H (repeated attention, with an updated state) waits for G's result.

## What would count

- **Dynamic selection helps** if E or F beats each of B, C and D by at
  least 0.02 bits per token on the comparison split, at both sizes. If
  only C or D helps, the gain is long-range association, not selection.
- **Closing the gap:** report the share of the 0.31-bit confirmation gap
  to the transformer that the best arm closes, on the confirmation split.
- **Long-range use:** bits per token on positions t ≥ 6 (beyond the
  5-gram's window), reported apart for every arm. Selection should help
  most there.
