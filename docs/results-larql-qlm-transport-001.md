# Results: LARQL-QLM-TRANSPORT-001, how the entity reaches the answer position

Reported against
[larql-qlm-transport-001-plan.md](larql-qlm-transport-001-plan.md). Full
tables: [tables/transport-001.md](tables/transport-001.md). The models are
the 18 of SEM-001 (version 2): Llama and the custom transformer, seeds 1 to
3, three worlds. Recipient `the capital of C' is`, donor `the capital of C
is`, the same 120 pairs per model.

**Instrument checks.**
- The custom transformer's explicit forward, which exposes every head,
  matches the module's own to 1e-4 at the output.
- Patching a prompt with its own state changes nothing. Its answer
  matches the true capital in 23 or 24 of 24: the 6 held-out phrasings
  were never gated, and one of them is wrong in some models.

## 1. Which attention steps move it

The country-position transplant, read at three points in each block: the
share of pairs in which the donor's capital wins. Means over 9 runs.

| block | custom: input | after attention | after feed-forward | Llama: input | after attention | after feed-forward | random, matched |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.96 | 0.96 | 1.00 | **0.21** | 0.21 | ≤ 0.02 |
| 2 | 0.96 | **0.46** | 0.46 | 0.21 | **0.00** | 0.00 | ≤ 0.01 |
| 3 | 0.46 | **0.02** | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

- **"After attention" and "after feed-forward" are equal in every row of
  every model, 72 of 72, by construction, not as a finding.** The
  feed-forward acts on each position on its own, so information can only
  leave a position through attention. Patching the state after attention
  necessarily gives the same result as patching it after the feed-forward.
  (A first draft of this note read the equality as evidence that the
  feed-forward does not move the entity; that was wrong.) What the
  measurement shows is which attention steps carry the hand-off.
- **Where:**
  - in the custom transformer, across blocks 2 and 3 (0.96 to 0.46 to
    0.02);
  - in Llama, across blocks 1 and 2 (1.00 to 0.21 to 0.00).
- **Against the plan's criterion,** which asks for a single block's
  attention step to take the share from at least half to under a tenth of
  that: no single block does it. The hand-off is spread over two
  consecutive attention steps in both architectures.

## 2. A few heads carry it

Per head, the last position's output was patched from the donor. Single
heads move little on their own (at most 0.06 in the first model
inspected). The three best heads of each model, patched together, against
three other heads:

| | custom transformer | Llama |
|---|---|---|
| top three heads together: donor's capital wins | 0.50 (0.00 to 0.91) | 0.73 (0.31 to 0.96) |
| three other heads | 0.01 | 0.00 |
| restoring only the top three from the clean run: clean answer returns | 0.49 (0.00 to 0.93) | 0.75 (0.34 to 0.97) |
| restoring three other heads | 0.01 | 0.00 |
| models passing the plan's criterion (at least half in both, random under a tenth) | 4 of 9 | **8 of 9** |
| where the top heads are | blocks 2 and 3, mostly | block 1, mostly |

- The top heads attend strongly from the last position to the country:
  weights of 0.64 to 0.84 in the first model inspected.
- In the custom transformer, the models that fail the criterion have their
  hand-off spread over more heads, or have their top heads chosen in
  block 1, where patching does not help. Which heads matter differs from
  model to model.

## 3. What the heads carry: unclear from this measure

Each top head's output at the last position was read through the output
head (a logit lens on that head alone). How often is the prompt's country,
or its capital, the top of its type, out of 24?

| | custom: top heads | custom: other heads | Llama: top heads | Llama: other heads |
|---|---:|---:|---:|---:|
| country | 2.9 | 1.9 | 2.9 | 2.2 |
| capital | **9.3** | 3.4 | 5.6 | 5.6 |

- In the custom transformer, the top heads' outputs name the capital far
  more often than other heads' do, and more often than the country. By the
  plan's rule, the answer is at least partly looked up before or inside the
  head. A probable reading: the feed-forward at the country position in
  block 1 enriches the country with its facts, and attention then moves the
  capital out. That is the subject-enrichment-then-extraction mechanism
  reported in large models (Geva et al., 2023, "Dissecting recall of
  factual associations").
- In Llama the lens reads the top heads no better than other heads, so this
  measure says nothing there.
- A logit lens on one head, without the final norm or the later layers, is
  a weak instrument. A decoder trained per head would be stronger.

## What this adds to SEM-001

SEM-001 found an entity state at the country's position, read by later
blocks. TRANSPORT-001 adds:
- it is spread over two consecutive attention steps: blocks 2 and 3 in the
  custom transformer, 1 and 2 in Llama (it can only move by attention);
- it is carried by a few heads that attend from the answer position to the
  entity. Those heads are sufficient (patching them moves the answer) and
  restoring them alone recovers it: for 8 of 9 Llama models and 4 of 9
  custom ones;
- in the custom transformer, what they move looks at least partly like the
  answer already.

So the picture is a lookup at the entity's position, then transport by a
few attention heads to the answer position. Whether the lookup happens at
the entity position is the next test. Patching the country position's
feed-forward output in block 1 alone would show it.

## Addendum: heads chosen on held-out pairs, and their interactions

Full tables: [tables/transport-001-heldout.md](tables/transport-001-heldout.md).

**Held-out selection.** Above, the top three heads were chosen and judged
on the same 120 pairs. Now they are chosen on the first 60 and judged on
the other 60:

| | custom transformer | Llama |
|---|---|---|
| top three together: donor's capital wins | 0.39 (0.00 to 0.78), was 0.50 | 0.69 (0.17 to 0.97), was 0.73 |
| three other heads | 0.04 | 0.00 |
| restoration | 0.38 (0.00 to 0.85), was 0.49 | 0.70 (0.15 to 0.98), was 0.75 |
| three other heads | 0.03 | 0.01 |
| models passing | 4 of 9 | 8 of 9 |

Selection on the judged pairs inflated the shares by 0.04 to 0.11. The
pass counts are unchanged.

**Interactions.** Every nonempty subset of the three heads was patched, on
the judged pairs. The measure is the mean change in log2 P(donor's capital)
− log2 P(own capital), with all three together compared against the sum
of the three patched alone:

| | sum of singles, bits | all three, bits | together ÷ sum, per model |
|---|---:|---:|---|
| custom transformer | +11.1 (1.2 to 17.7) | +11.7 (1.2 to 18.4) | 1.04, 1.06, 0.99, 1.09, 1.05, 1.06, 1.08, 1.03, 1.05 |
| Llama | +12.6 (7.1 to 17.4) | +18.3 (10.4 to 23.2) | 1.58, 1.35, 1.57, 1.37, 1.20, 1.46, 1.60, 1.33, 1.79 |

- **In the custom transformer the heads add.** Each head adds its share of
  log-odds. The jump from 4% to 6% alone to 78% together, in the first
  model inspected, is a threshold: only together do they push the donor's
  capital past the recipient's.
- **In Llama the heads interact.** Together they move the answer 1.2 to 1.8
  times as far as the sum of their separate effects, in all 9 models.
  - Its top heads are mostly in block 1, so they cannot read each other.
    The superadditivity must come from later blocks combining their outputs
    non-linearly.
  - Which part of the later blocks does that is not tested.
- For a circuit-level description, then:
  - in the custom transformer, the three heads can be described one by
    one, and their effects summed;
  - in Llama they cannot. The unit is the heads together with what reads
    them.
