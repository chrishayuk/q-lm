# QLM-005 plan: independently generated grammar families

Written and committed before any family was generated or any learner run on
one. Whatever the results, they are reported against this plan. Any change
to the plan after results exist is listed as a change, with its reason.

## Question

Which findings from Colmerauer's grammar hold on other languages, and which
are properties of that one? These are the findings under test.

1. **Depth.** The learned grammar derives sentences with two levels of
   embedding from training sentences with at most one.
2. **Corpus fit.** On the corpus, the transformer is within about 1% of the
   grammar, and ahead at convergence.
3. **Depth with more data.**
   - The transformer gets worse at depth as it is trained on more.
   - The grammar gets worse at depth as inside–outside converges, and with
     more data, but less than the transformer.
4. **Pruning.** Pruning by expected count shrinks the grammar at almost no
   cost on the corpus. Minimum description length, as coded, chooses a
   grammar that has lost the recursion.

## The families

`qlm family DIR KIND SEED` makes a language from a seeded random grammar
and writes the same files as `qlm data`, plus `family.txt`, the grammar.
There are three kinds, by where an embedded clause sits in the argument
that holds it:

| kind | embedding rule | shape |
|---|---|---|
| right | `E → c S` | the clause follows its marker, like Colmerauer's `QUE` |
| centre | `E → c S d` | the clause sits between two markers |
| left | `E → S c` | the marker follows the clause |

**Random parts.**
- Every word is a made-up two-syllable string.
- A noun class (3 to 6 words), a verb class (2 to 4) and a modifier class
  (2 to 4). Two marker words, used only in the embedding rule; the second
  only in centre.
- One or two other markers, used in clause templates.
- 2 or 3 clause templates for `S`. Each is drawn from a fixed pool of
  orders of arguments `X`, verbs, modifiers and markers, and has at least
  one `X`.
- 1 or 2 base argument templates for `X` (a noun, optionally with a
  modifier), and `X → E`.

**The only recursion is `X → E` and `E → … S …`.** The depth of a tree is
the number of `S` nested inside an `E`. The depth of a sentence is the
least depth of any of its trees.

**The corpus** is every distinct sentence of every tree of depth at most 1.
The grammar is redrawn (from the same seed, deterministically) until the
corpus has between 20,000 and 250,000 trees. The split, the subsets, the
seeds and the 300 samples are as for Colmerauer.

**Deeper sentences.** These are drawn by a random top-down derivation.
- Each `X` is an embedded clause with probability 1/3. Otherwise it is
  one of its base templates, chosen uniformly; everything else is uniform
  too.
- The derivation is bounded at depth 2. A sentence is kept if its depth is
  exactly 2 and it has at most 60 words.
- Deeper with corpus words: the same, with every word among the training
  sentences.

**Ungrammatical sentences.** Two words of a development sentence are
swapped, and the result is kept if the generating grammar cannot derive it.

**The judge** is the generating grammar, by CYK. A sentence is grammatical
if the grammar derives it. Its depth is the least over its trees. Unlike
Colmerauer's judge, an ambiguous sentence counts as grammatical. The rate of
ambiguity is reported for each family.

## Families run

Three kinds, seed 1 each. A second seed per kind follows only if the first
three disagree with each other.

## Learners and settings (fixed)

**The transformer.** As before: 4 layers, width 128, 6,000 steps, seeds 1,
2 and 3, at 100, 1,000, 10,000 and all training sentences.

**The grammar learned by substitutability** at the same four sizes, scored:
- after 2 and 5 rounds of inside–outside, as diagnostics;
- after 20 rounds (converged, by QLM-004), the reported model;
- pruned by expected count. The threshold is chosen by development bits
  from {0, 0.1, 0.5, 1, 2, 5, 10, 20}, with the description-length choice
  reported beside it. The pruned grammar has 5 rounds before pruning and 5
  after, as in QLM-004.

**The floor** is the corpus distribution, uniform over the corpus:
log2(corpus size) bits per sentence.

## Measures

For each family, size and model:
- development bits per token;
- deeper bits per token, and deeper with corpus words;
- deeper sentences derivable (grammar);
- ungrammatical sentences derivable (grammar);
- of 300 samples: grammatical, not in training, deeper;
- for the grammar: categories, rules, and ms per next-token distribution
  on the first 50 development sentences.

## What would count against each finding

1. **Depth.** On some family, the converged grammar derives fewer than
   half the deeper sentences with corpus words, at the full size.
2. **Corpus fit.** The grammar is more than 5% behind the transformer on
   development at the full size.
3. **Depth with more data.** On some family:
   - deeper bits for the transformer do not rise with training size, or
   - the converged grammar is not better than the transformer on deeper
     sentences at the full size.
4. **Pruning.** On some family:
   - pruning at the development-chosen threshold costs more than 1% of
     development bits, or
   - the description-length choice keeps more than half the deeper
     sentences derivable.

The confirmation sets are not read.

## Changes after results existed

1. **A Llama arm is added to every family.** It runs on 3 seeds at the same
   four sizes, as `ARCH=llama transformer/train.py`.
   - **When.** Decided after the right family's results were seen, and
     before the centre and left families finished.
   - **Why.** On Colmerauer's language, a Llama model of the same size
     nearly closes the depth gap that the custom transformer showed
     (results-architectures.md). A comparison with one transformer
     architecture is not a comparison with transformers.
   - **How it is reported.** The custom transformer stays as planned. The
     plan's criteria apply to it. The Llama arm is reported beside it, under
     the same criteria, labelled as added.
