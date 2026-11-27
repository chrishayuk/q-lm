# QLM-KEY-001 plan: learned addressing (which keys to construct), without backpropagation

Written before any measurement. It follows ATTENTION-001. There, selecting
among earlier words by static similarity, with "appears later" as the
values, added nothing. The point taken: the learner must learn **which
keys to build**, not only which stored keys match.

## What the transformer's lead is made of (development 1,001 to 3,000)

| training sentences | positions 2–4 (both see the whole history) | positions 5+ |
|---:|---:|---:|
| 10,000 | 0.17 bits (4.985 against 5.152) | −0.00 (4.981 against 4.985) |
| 100,000 | **0.29** (3.727 against 4.020) | **0.49** (3.430 against 3.923) |

(The transformer against the 5-gram. Position 5 is in the second bucket:
there the transformer already sees one more word than the 5-gram.)

**Generalisation is shown.** At positions 2 to 4, both models see exactly
the same history; the transformer is 0.29 bits better from it.

**Long context is not yet shown causally.** Cutting the trained
transformer to its last 4 words at test time makes it worse than the
5-gram beyond position 4: 4.190 against 3.923. So most of that loss is the
shift to unfamiliar inputs, not lost context. The control is a transformer
**trained** with the same context as the 5-gram:
- Mistral's sliding window;
- window 2 × 4 layers = the 4 previous tokens;
- `ARCH=mistralw`, at 10,000 and 100,000 sentences.

Its gap to the full transformer at positions 5+ is what long context is
worth.

## Arms (each a component of the v2 mixture: 5-gram + 4 class models)

| arm | key | value |
|---|---|---|
| A | exact recent history: the 5-gram, already in v2 | the counted next-word distribution |
| B | **similar** recent histories: training histories (u, v) with v = x_{t−1} and u near x_{t−2} (distributional cosine, top k) | their next words, weighted by similarity |
| C | recent word plus one earlier word: (x_{t−1}, x_i) for i < t−1, selected among the earlier words | the counted P(next \| x_{t−1}, x_i), skipping the words between |
| D | as C, with x_i's abstraction node in place of x_i | P(next \| x_{t−1}, node(x_i)) |
| E | **learned combinations:** for each recent word v, the earlier positions (by distance) and the levels (word or node) whose pairing with v most lowers H(next \| v) on training sentences: G = H(Y\|v) − H(Y\|v, k), kept if G is at least γ | as C or D, for the kept keys only |
| F | several of E's keys as separate components, each a head | each head's counted distribution |
| G | E, with a retrieved value's argmax node used to build the next key | waits on F |

**Budgets are matched.** Each arm's stored counts are reported. B to F are
compared with v2 plus one more class model of the same number of stored
counts: storage alone must not win.

## Splits and criteria

The splits are as before (fit 1 to 1,000; compare 1,001 to 3,000; confirm
3,001 to 7,000).
- **Generalisation is captured** if B lowers bits on positions 2 to 4 by
  at least 0.05 at 100,000 sentences, against v2 alone.
- **Learned addressing helps** if E beats C and D, and the matched-storage
  control, by at least 0.02 on positions 5+ at 100,000 sentences.
- **What is reported:** the keys E keeps, by distance and level. They are
  readable, which is the point.
