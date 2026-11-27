# Results: Q-LM v2, stages E1 to E3 on TinyStories (prototype)

Reported against [qlm-v2-plan.md](qlm-v2-plan.md). The prototype is
`v2/classes.py`.
- **E1:** context vectors, the w words before and after each word, at
  widths 1, 2, 4 and combinations.
- **E2:** PPMI weighted or binary, reduced by truncated SVD to 128
  dimensions.
- **E3:** abstraction nodes, by frequency-weighted k-means. Every word
  keeps its identity and gets soft memberships in its top m nodes.

The predictor:
- a class trigram over the nodes;
- interpolated with the Kneser–Ney word 5-gram;
- its weight fitted on development sentences 1 to 1,000;
- scored on 1,001 to 3,000, in bits per token with END included.

No backpropagation anywhere. Full grid:
[tables/v2-e1-e3-grid.txt](tables/v2-e1-e3-grid.txt).

## The grid

| training sentences | 5-gram alone | mixed, best | its setting | gain |
|---:|---:|---:|---|---:|
| 10,000 | 5.1298 | **4.9992** | widths 1+2+4, PPMI, 256 nodes, 1 membership | 0.131 |
| 100,000 | 4.1341 | **4.0583** | width 2, PPMI, 256 nodes, 1 membership | 0.076 |

Across the grid:
- **PPMI weighting beats binary contexts in every pair:** by 0.04 to 0.05
  bits mixed at 10,000 sentences, and 0.03 to 0.04 at 100,000.
- **Width:**
  - at 10,000 sentences, the widest combination is best (1+2+4: 4.999;
    width 1: 5.050);
  - at 100,000, width 2 alone is best (4.058; width 1: 4.084).
- **Number of nodes:** 256 beats 64 and 1,024 at both sizes. 64 is too
  coarse; 1,024 too thin per node.
- **More memberships help a little:** with widths 1+2, 4 memberships give
  5.000 and 4.068, against 5.021 and 4.072 with 1.
- **The class model alone is worse than the 5-gram** (5.77 to 6.46 at
  10,000). It is useful as a second opinion, mixed in at weights of 0.15
  to 0.30.
- **Cost:** about 2.5 seconds at 10,000 sentences, all stages.

## Against the plan

**E1 to E3 are useful** if the mix beats the 5-gram alone by at least 0.05
bits, at both 10,000 and 100,000 sentences.
- **Holds** for every PPMI setting at both sizes, except width 1 at
  100,000, which gains 0.0498.
- **Caveat:** the best setting is chosen on the scored sentences. Only the
  mixing weight was fitted separately. The claim that holds without that
  choice is the across-the-grid one: every PPMI setting but one passes.

## What it is, and what it is not

- **It is a known technique.** Distributional word classes interpolated
  with an n-gram, in the line of Brown et al. (1992). Learning classes from
  bounded contexts is the right first step for v2: the substitution
  grammar never got there on natural text. It is not yet anything new.
- **What is new in v2 is still to come:**
  - E4: abstractions as contexts for further abstraction;
  - phrases and recurring structure, not just words;
  - grammar-like composition over the nodes;
  - bindings and relations.
- **The gain shrinks with data,** 0.131 to 0.076, as class models' gains
  usually do. Whatever v2 adds has to keep paying at 100,000 sentences
  and beyond.
- **Not measured yet:**
  - the plan's "preserving distinctions" measure;
  - the transformer on exactly these sentences;
  - E4.
