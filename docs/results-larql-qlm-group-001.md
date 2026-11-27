# Results: LARQL-QLM-GROUP-001, grouping inside the transformers

Reported against [larql-qlm-group-001-plan.md](larql-qlm-group-001-plan.md),
including its amendment (grouping is measured by geometry). Full tables:
[tables/group-001.md](tables/group-001.md). Models: seed 1, Llama and the
custom transformer, at 1,000 sentences and at full size, on the three
QLM-005 families.

**Instrument check.** On 20 development sentences of the right family, at
every layer from the embedding to the last block's output, LARQL's
reference and production backends (`vindex3 exec --dump-layers`) agree
with the PyTorch states this study reads. The largest relative difference
is 1.0e-6.

## Grouping by class, layer by layer

The measure is the distance between the mean states of words of one class,
over the distance between words of different classes. 1 means no grouping;
lower is tighter. The layers run 0 (embedding) to 4 (last block).

| model | layer 0 | 1 | 2 | 3 | 4 | untrained, layer 4 |
|---|---:|---:|---:|---:|---:|---:|
| right, Llama, 1,000 | 0.50 | 0.29 | 0.22 | 0.16 | 0.11 | 0.94 |
| right, Llama, 36,000 | 0.23 | 0.09 | 0.06 | 0.04 | **0.03** | 0.94 |
| right, transformer, 1,000 | 0.95 | 0.81 | 0.62 | 0.46 | 0.37 | 0.95 |
| right, transformer, 36,000 | 0.95 | 0.76 | 0.45 | 0.23 | **0.15** | 0.95 |
| centre, Llama, 1,000 | 0.48 | 0.40 | 0.31 | 0.20 | 0.11 | 1.02 |
| centre, Llama, 118,280 | 0.21 | 0.12 | 0.08 | 0.06 | **0.05** | 1.02 |
| centre, transformer, 1,000 | 1.00 | 0.86 | 0.69 | 0.50 | 0.39 | 1.01 |
| centre, transformer, 118,280 | 1.00 | 0.77 | 0.52 | 0.21 | **0.15** | 1.01 |
| left, Llama, 1,000 | 0.52 | 0.44 | 0.39 | 0.25 | 0.16 | 0.99 |
| left, Llama, 21,066 | 0.20 | 0.23 | 0.13 | 0.08 | **0.06** | 0.99 |
| left, transformer, 1,000 | 0.96 | 0.87 | 0.76 | 0.61 | 0.48 | 0.96 |
| left, transformer, 21,066 | 0.95 | 0.74 | 0.54 | 0.31 | **0.20** | 0.96 |

- **Every trained model groups words by class; no untrained model does.**
  The grouping tightens with depth and with more data.
- **The two architectures build it differently.**
  - In the custom transformer, the input embeddings are not grouped at all
    (0.95 to 1.00, the same as untrained). The grouping is built layer by
    layer.
  - In Llama, the embeddings are already grouped (0.20 to 0.52), and the
    layers tighten them.

  Llama ties its input embedding to its output head, and the output head
  must give the words of one class similar scores. The custom transformer
  has a separate output layer. Which of these differences causes the gap
  is not tested here.
- **Identity is kept.** A probe for which word, within nouns and within
  verbs, stays at 99% to 100% through layer 3 in every model. At the last
  layer it is 100% in the custom transformer, and 89% to 100% in Llama, the
  lowest at full size.
- **Plan criterion: grouping without losing identity.** At the last layer
  (and at layer 3 for Llama), every model has a ratio below 0.5 and an
  identity probe above 90%, so every model meets it there. The one
  exception is Llama on right at full size, at layer 4: 89% for nouns.
- **Plan criterion: functional grouping.** Replacing a noun's state with
  another noun's, at the same slot, depth and position, barely changes
  what follows: 0.000 to 0.047 total variation over the next tokens.
  Replacing it with a token of another class changes it by 0.14 to 0.24.
  This is under a quarter of the control everywhere, so it meets that part
  of the criterion. The other part (class-level change against word-level
  change) cannot be tested on these languages: every noun has the same
  continuations, so the two are equal. The plan did not foresee that.
- **Correspondence with the grammar learner.** Its lexical categories are
  exactly the true word classes on all three families. So agreement with
  the grammar and agreement with the truth are the same here: clustering
  recovers them perfectly at the last layer in 6 of the 12 models (all on
  right and left; none on centre, where it reaches 0.42 to 0.71). The
  phrase level, where the two could differ, is not measured yet.

## Role

The probes for a noun's argument slot and depth are near 100% at every
layer, untrained models included. Position and sentence length alone give
95% (slot) and 99% (depth). In these languages, where a noun stands
nearly fixes its role, so the role probes cannot show anything. A test of
roles needs sentences where position does not give the role away.

## What this shows and what it does not

- **Shown:** trained transformers put words of one class close together
  and keep each word distinguishable, which is grouping by accumulation,
  not by merging. Substituting within a class is nearly free; across
  classes it is not.
- **Not shown:** that they compute as the grammar does. In these languages
  the true distribution makes all words of a class interchangeable. Any
  model that learns the distribution has to treat them alike in its
  output. The interesting cases are where interchangeability is partial:
  - phrases, where the grammar's categories and the truth differ;
  - the left family, where the grammar over-merged;
  - the semantic worlds, where people of one city or continent are
    interchangeable for some questions and not others.

## Next

- **Phrase level.** Mean states of spans (the grammar's non-lexical
  categories against the true constituents), on the left family above all,
  where the grammar merged constituents with non-constituents. Does the
  transformer keep them apart?
- **The semantic worlds,** when their transformers are trained. Do people
  group by city, by continent, or not at all, layer by layer? And does
  swapping two people of one city preserve the city fact and the continent
  fact?

## Addendum: tied embeddings, and attention against feed-forward

Full tables: [tables/group-001-sub.md](tables/group-001-sub.md) (`SUB=1`).
The distance ratio is read after each attention step (marked `a`) as well
as after each block. Seed 1, full size.

### Tied embeddings do not explain Llama's grouped embeddings

The QLM-ARCH-001 arms on Colmerauer's language, ratio at layer 0 (the
embedding) and at the last layer:

| model | layer 0 | last layer |
|---|---:|---:|
| ablation base | 0.97 | 0.68 |
| ablation, tied embeddings only | 0.97 | 0.73 |
| ablation, rotary only | 0.99 | 0.69 |
| ablation, RMSNorm only | 0.97 | 0.68 |
| ablation, gated feed-forward only | 0.97 | 0.68 |
| ablation, all four | 0.99 | 0.82 |
| custom transformer | 0.97 | 0.70 |
| Llama (Hugging Face) | **0.74** | 0.64 |

- **Tying the output to the input embedding does not group the
  embeddings.** Nor do all four Llama changes together, in this code.
- So Llama's grouped embeddings come from something else in the Hugging
  Face model. One candidate is its initialisation: its embeddings start at
  a standard deviation of 0.02, the custom ones at 1. With weight decay,
  small initial embeddings may be dominated by what training adds. This is
  untested.
- On Colmerauer's language every ratio is high (0.64 to 0.82), because the
  word classes used there are coarse: the "function word" class mixes
  `FAIT`, `QUE`, `PAR`, `DE`, `CE`, `EST` and `.`. Its ratios are not
  comparable with the families'.

### Attention against feed-forward

How much each step lowers the ratio, block by block (attention; then
feed-forward), at full size on the families:

| model | block 1 | block 2 | block 3 | block 4 |
|---|---|---|---|---|
| right, custom | 0.01; 0.18 | 0.07; 0.24 | 0.09; 0.13 | 0.02; 0.06 |
| centre, custom | 0.02; 0.21 | 0.02; 0.23 | 0.13; 0.18 | 0.02; 0.04 |
| left, custom | 0.01; 0.20 | 0.04; 0.16 | 0.05; 0.18 | 0.04; 0.07 |
| right, Llama | 0.05; 0.09 | 0.01; 0.02 | 0.00; 0.02 | 0.00; 0.01 |
| centre, Llama | 0.04; 0.05 | 0.00; 0.04 | 0.00; 0.02 | 0.00; 0.01 |
| left, Llama | −0.02; −0.01 | 0.00; 0.10 | 0.00; 0.05 | 0.00; 0.02 |

- In the custom transformer, the feed-forward step does most of the
  grouping in every block. The one large attention step is block 3 on
  centre (0.13, against 0.18 for the feed-forward step).
- In Llama, little is left to do after the embedding, and again what there
  is comes mostly from the feed-forward steps.
- **This is still correlational, and the measure leans towards
  feed-forward** (LARQL-QLM-FFN-001, "why geometry is not enough"). The
  causal test is FFN-001.
