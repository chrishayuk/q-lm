# LARQL-QLM-TRANSPORT-001 plan: what moves from the entity to the answer position, and how

Written before any measurement. It follows LARQL-QLM-SEM-001 (version 2).
There, after block 1, moving the country's state at its own position moved
the computed capital in 96% of pairs (custom transformer). After block 3 it
moved nothing. That is a hand-off between positions. This experiment asks
three questions:
- **Which operation** carries it: attention, or the feed-forward?
- **Which heads** carry it?
- **What is carried:** the entity, a partly resolved query, or the answer?

## Models and prompts

The 18 version-2 models: Llama and the custom transformer, seeds 1 to 3,
three worlds. The prompts are `the capital of C' is`, recipient, and
`the capital of C is`, donor, for every pair of countries the models know
(all 24, by SEM-001's gate). That is 120 sampled pairs, the same sample as
SEM-001. Positions: the country is position 4; the last position is 5.

## Interventions

At each block b, at a finer grain than SEM-001:

1. **Country position, before and after attention.** Replace the
   country-position state with the donor's at three points in block b:
   - its input;
   - after attention (residual added);
   - after the feed-forward (the block output, as in SEM-001).

   The share in which the donor's capital wins shows where in the block
   the hand-off closes.
2. **The heads that read the country.** At the last position, in block b,
   patch one head's output with the donor's (path patching: only that
   head's contribution at the last position, nothing else).
   - The share in which the donor's capital wins, per head.
   - Then the top heads together.
   - A head is a **transport head** if patching it alone gives the donor's
     capital in at least a quarter of the pairs.
   - Its attention weight from the last position to the country position
     is reported beside it.
3. **Restoration, the converse.** Corrupt the recipient by replacing the
   country's embedding with a different country's embedding. Then restore
   only the transport heads' outputs at the last position from the clean
   run. The share in which the clean answer returns.
4. **What is carried.** At the transport heads' output (last position):
   - **Entity:** is the donor country decodable, by nearest country under
     the same head's output for each country's `the capital of X is`
     prompt? Leave-one-out over the 24.
   - **Answer:** is the donor's capital already decodable there, by the
     output head (logit lens) on the head's output alone?
   - If the entity is decodable and the answer is not, the head moves the
     entity, and the answer is computed after it. If the answer is already
     decodable, the lookup happened before or inside the head.
   - A random-head control and an untrained model are reported beside.

## Controls

- Every patch has a magnitude-matched random replacement: the same norm of
  change, in a random direction.
- Patching from a donor with the same country as the recipient must leave
  the answer unchanged. This checks that the patching machinery itself
  changes nothing.

## What would count

- **Attention carries the entity at block b** if the hand-off closes
  across block b's attention step: the before-attention patch moves the
  answer in at least half the pairs, and the after-attention patch in
  under a tenth as many.
- **Transport heads are identified** if:
  - patching the top heads together moves the answer in at least half the
    pairs;
  - their restoration recovers at least half of the corrupted answers;
  - random heads of the same number do neither, under a tenth as often.
- **What is carried** is read from measure 4 by the rule above. If neither
  is decodable, that is the result.

## Instruments

Per-head outputs:
- For Llama, read from the input to `o_proj`, split by head.
- For the custom transformer (`nn.MultiheadAttention`), recomputed from
  its projection weights. The recomputation is checked against the module's
  own output to 1e-5 before use.
