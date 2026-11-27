# Results: QLM-005, three independently generated languages

Reported against [qlm005-plan.md](qlm005-plan.md), including its one
change: a Llama arm was added after the right family's results were seen.
Full tables are `qlm compare data-KIND` (kept locally in
`data-KIND/compare.md`); the grammars are in [families/](families/).

All three families are seed 1. Every argument is a bare noun, because the
corpus-size window rejected the modifier templates, and no sentence has two
trees. So the families are simpler than Colmerauer's language in these two
ways. The confirmation sets have not been read.

## At the full training size

Bits per token. Development is all development sentences. Deeper is the 300
deeper sentences with corpus words. The floor is the corpus distribution,
uniform over the corpus.

| family | floor | grammar, development | Llama, development | transformer, development | grammar, deeper | Llama, deeper | transformer, deeper |
|---|---:|---:|---:|---:|---:|---:|---:|
| right (45,000 sentences) | 1.3797 | 1.3816 | 1.3815–1.3818 | 1.3815–1.3823 | **3.25** | 3.45–3.58 | 4.60–4.76 |
| centre (147,852) | 1.2503 | 1.2505 | 1.2517–1.2522 | 1.2518–1.2519 | **2.91** | 3.77–4.43 | 4.73–5.12 |
| left (26,334) | 1.2192 | 1.3444 | 1.2214–1.2218 | 1.2225–1.2228 | **2.27** | 3.53–3.77 | 3.77–3.85 |

Ranges are over 3 seeds. The grammar derives all 300 deeper sentences on
every family.

At 1,000 training sentences:

| family | grammar, development | Llama | transformer | grammar, deeper | Llama | transformer |
|---|---:|---:|---:|---:|---:|---:|
| right | 1.3823 | 1.3966–1.4004 | 1.4163–1.4199 | **2.83** | 2.87–2.99 | 3.44–3.92 |
| centre | 1.2551 | 1.2758–1.2809 | 1.2891–1.2976 | **2.54** | 3.42–3.64 | 3.48–3.85 |
| left | 1.2995 | 1.2431–1.2479 | 1.2492–1.2514 | **2.37** | 3.13–3.30 | 2.98–3.29 |

## The plan's findings

| finding | right | centre | left |
|---|---|---|---|
| 1. The grammar derives deeper sentences (at least half, at full size) | holds: 300 of 300 | holds: 300 | holds: 300 |
| 2. The grammar is within 5% of the transformer on development | holds: 0.0% | holds: grammar 0.1% ahead | **fails**: 10% behind |
| 3a. The transformer is worse at depth with more data (1,000 to full) | holds | holds | holds |
| 3b. The converged grammar is better than the transformer on deeper sentences at full size | holds | holds | holds |
| 4a. Development-chosen pruning costs under 1% on development | **fails**: 2.6% | holds: under 0.01% | holds: 0.8% |
| 4b. The shortest description loses the recursion | **fails**: keeps 300 of 300 | holds: keeps 50 of 300 | **fails**: keeps 300 of 300 |

**Finding 3 under the added Llama arm:**
- Llama is also worse at depth with more data on every family, from 1,000
  to full.
- The grammar is better than Llama on deeper sentences at full size on
  every family, by 0.2 to 0.3 bits (right), 0.9 to 1.5 (centre) and 1.3 to
  1.5 (left).

## What generalises and what doesn't

- **Depth: generalises, and survives the stronger transformer here.** On
  Colmerauer's language, Llama nearly matched the converged grammar at
  depth (results-architectures.md). On these three it does not. Its
  deeper bits fall between the grammar's and the custom transformer's.
  - The share of deeper sentences longer than every training sentence is
    similar to Colmerauer's: 126, 114 and 83 of 300, against 175.
  - But their length relative to training is greater: up to 22, 33 and 24
    words against training maxima of 12, 14 and 12. Colmerauer's are at
    most 27 against 20.
  - Depth and length are not yet separated on the families as they were on
    Colmerauer's language.
- **Corpus fit: generalises, except on left.** On right and centre, all
  three models are at the floor. Being level at the floor shows that each
  learned the distribution; it does not show that they compute alike. On
  left, the grammar learner overgenerates (QLM-LEFT-001), and is 10% behind.
- **Both kinds of model get worse at depth with more data.** That holds on
  every language so far.
- **Minimum description length losing the recursion does not generalise.**
  It happened on Colmerauer's language and on centre, not on right or left.
- **Pruning chosen by development can delete depth.** On centre, the
  development-chosen threshold keeps development bits (1.2506) and leaves
  86 of 300 deeper sentences derivable. At 1,000 sentences it leaves 0.
  Development sentences cannot see depth, so choosing by them protects only
  what they exercise.
- **Pruning's development cost on right** is most likely training rounds,
  not pruning. The plan gives pruned grammars 5 rounds plus 5, against 20,
  and right has not converged at 10. It is reported as the plan specifies.

## Not shown

- Only one seed per family kind.
- No family is ambiguous, and none has modifiers.
- The left family breaks the grammar learner. Its cause is found
  (QLM-LEFT-001); a fix is QLM-EQUIV-001.
- The custom transformer and Llama were trained identically, with no
  tuning for these languages.
