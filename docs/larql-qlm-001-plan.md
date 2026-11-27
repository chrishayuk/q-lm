# LARQL-QLM-001 plan: does the transformer keep depth and suppress it?

Written before any probing. Results are reported against this plan.

## Question

The learned grammar keeps the machinery for two levels of embedding at
every size and round. It derives all 300 deeper sentences of corpus words,
while inside–outside lowers their probability (results-qlm004.md). The
transformer also gets worse at depth as it sees more data. Which of these
is it doing?

- **Kept, suppressed.** Somewhere inside, it represents the second level
  and computes the right continuation, and later computation overrides it.
- **Bounded.** It never represents more than one level. Nothing inside it
  computes the right continuation at depth 2.
- **Something else**: neither of these, described as found.

## The model under study

LARQL's VINDEX3 admits Llama-family checkpoints. It does not yet admit
GPT-2, nor the custom transformer of the earlier runs: that one's output
layer is separate from its input embedding and has a bias. So the model
under study is a **Llama arm**.
- `ARCH=llama transformer/train.py`: LlamaForCausalLM with 4 layers, width
  128, 4 heads, a gated SiLU feed-forward of width 512, rotary positions
  and tied embeddings.
- Trained exactly as the transformer: same data, steps, optimiser and
  checkpoint choice.

**Gate 0, before any probing.**
- The Llama arm must show the transformer's pattern on Colmerauer's
  language. Over 3 seeds, its deeper bits must rise from 1,000 to 105,138
  training sentences.
- LARQL's execution must match PyTorch on it.

If gate 0 fails, the question is asked of a model that doesn't show the
behaviour, so it stops there. First check, at 1,000 sentences, seed 1:
- development 1.058 bits per token, deeper with corpus words 2.37 (the
  custom transformer gave 2.82 to 2.94);
- LARQL `observe --backend reference` matches PyTorch's log-probabilities
  on all ten top candidates to 4 decimals.

## Measures, in order

1. **Where the bits go.** Per-position surprisal on the 100 deeper
   sentences, for the Llama arm at each size and for the converged grammar.
   Each position is labelled by the judge's tree as one of:
   - opening a second level (the marker that starts the inner clause);
   - inside the inner clause;
   - closing it (the first word after the inner clause ends);
   - elsewhere.

   The question is whether the transformer's loss is concentrated where
   the second level must be opened, where it must be closed, or spread
   out. The grammar gives the same breakdown, for a mechanism whose
   suppression is known.
2. **Depth in the residual stream.** LARQL `observe` records of the
   carrier writes at every layer and position.
   - A linear probe for the current depth (0, 1, 2) is trained on
     development prefixes, which only reach depth 1.
   - It is tested on deeper prefixes. Does depth 2 have a direction, or
     does it collapse onto depth 1?
   - Separately, a probe trained on depth 0, 1 and 2 (half the deeper
     sentences) and tested on the other half tells whether depth 2 is
     linearly present at all.
3. **The right continuation at intermediate layers.** At the deeper
   positions with the largest loss, the rank and probability of the
   correct next word are read through each layer's normalisation and
   output head (a logit lens).
   - Kept and suppressed predicts that an intermediate layer ranks the
     correct word higher than the output does.
   - Bounded predicts that no layer does.
4. **Causal check**, only if measure 3 finds a layer that does better.
   Ablate or patch the later components that lower the correct word, then
   measure deeper bits and development bits. Done through LARQL's
   intervention surface, under its contract for causal claims. A projected
   contribution is not a counterfactual.
5. **Across training size.** Measures 1 to 3 on the models trained on
   1,000 and 105,138 sentences. Does the larger model lose the internal
   signal, or keep it and override it more strongly?

## What would count

- **Kept, suppressed:**
  - measure 3 finds a layer whose correct-word rank beats the output's on
    most high-loss deeper positions, and
  - measure 4 recovers at least a third of the gap to the 1,000-sentence
    model's deeper bits, at a cost of under 1% on development.
- **Bounded:**
  - no layer beats the output in measure 3, and
  - the depth-2 probe of measure 2 does no better than chance at separating
    depth 2 from depth 1.
- Any other combination is reported as found, without a label.

The deeper sentences are a test set here as in QLM-004. Nothing is tuned on
them except where a measure says it trains on half of them, and then it is
tested on the other half.
