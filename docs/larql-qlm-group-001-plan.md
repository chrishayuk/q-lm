# LARQL-QLM-GROUP-001 plan: do transformers group words as the grammar does?

Written before any measurement, and amended once before any measurement.

**Amendment.** A linear probe reads a word's class from its input
embedding alone, because every word has its own vector. So probe accuracy
for class cannot show grouping: it is near 100% at layer 0 by
construction. Grouping is measured by geometry instead:
- the distance between the mean states of words of one class, over the
  distance between words of different classes;
- the clustering's agreement with the true classes.

The probes stay, as measures of what is decodable.

## Question

The grammar learner groups words, and phrases, into categories by
substitution, and in doing so it loses their identity. A transformer has a
separate embedding for every word, so it can group without losing identity,
if it groups at all. At each layer, does it group by category? Does it keep
identity? Does a word's representation depend on its role? Do its groupings
resemble the categories the grammar learner found independently?

## Models and gate

- The Llama arm and the custom transformer on the three QLM-005 families
  and on Colmerauer's language: seed 1, full size and 1,000 sentences.
- Controls:
  - the same architectures randomly initialised (seed 1, untrained);
  - the input embeddings alone (layer 0).
- Hidden states are read in PyTorch. Before any result is reported, the
  Llama arm's per-layer states are checked against LARQL's
  `vindex3 exec` layer dump on 20 sentences (largest relative difference
  reported), so that the LARQL instrument and the PyTorch one are known to
  agree.

## Data

Every token of the first 1,000 development sentences, at every layer
(after each block's residual add), at the token's own position.
- For the families, each token is labelled with its word class (N, V, C,
  D, M, P), and each noun with its role:
  - the argument slot it fills (first or second X of its clause);
  - its clause depth (0 or 1).

  Both are read from the judge's CYK parse.
- For Colmerauer's language, word classes are read from its grammar
  (names, verbs, abstract nouns, prepositions and markers). Roles are not
  labelled: the analysis there has no word spans.

## Measures, per layer

1. **Category.** Accuracy of a linear probe for word class, trained on half
   the sentences and tested on the other half.
2. **Identity within category.** Accuracy of a probe for the word itself,
   within each class with at least 3 words. Chance is 1 over the number of
   words in the class.
3. **Role.** For nouns, probes for the argument slot and for the depth.
   Controlled, as in LARQL-QLM-001, against position and sentence length
   alone.
4. **Correspondence with the grammar.**
   - Words are clustered by their mean state at the layer.
   - The clustering is compared with the grammar learner's lexical
     categories (each word's most probable category), and with the true
     classes, by the adjusted Rand index.
   - Because the grammar's lexical categories may simply equal the true
     classes, both comparisons are reported, and correspondence with the
     grammar only counts where the two differ.
5. **Causal substitution.** At layer l, the state at one noun position is
   replaced by the state of another noun from another sentence, at the
   same role and the same position, or failing that the same role.
   - The next-token distributions that follow are measured: their total
     variation over word classes, and over words.
   - Grouping that is functional predicts that class-level predictions
     barely change while word-level ones do.
   - Repeated with a word of another class, as the control.

## What would count

- **Grouping by category at a layer:** the within/between distance ratio
  is below 0.5, and below both the untrained model's ratio at that layer
  and the trained model's ratio at layer 0.
- **Grouping without losing identity:** the grouping criterion holds and
  the identity probe is above 90% at the same layer.
- **Functional grouping:** under same-class substitution, the class-level
  total variation is under a quarter of the word-level one, and under a
  quarter of the other-class control's.
- Measure 4 is descriptive. No threshold.

The semantic worlds (QLM-SEMANTIC-001) add a later part: do people group by
city or continent, layer by layer? That waits until the transformers on
those worlds are trained.
