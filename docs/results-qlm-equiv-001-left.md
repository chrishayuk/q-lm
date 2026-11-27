# Results: QLM-EQUIV-001 on the left family (arms A and C′)

Reported against [qlm-equiv-001-plan.md](qlm-equiv-001-plan.md), including
its changes after a pilot:
- exact context counts;
- arms B and C cannot merge rare substrings;
- the added Jaccard arm C′;
- the order check.

The left family is the language QLM-LEFT-001 diagnosed. 20 rounds of
inside–outside. Ungrammatical sentences are the fresh development
negatives. Table: [tables/equiv-001-left.md](tables/equiv-001-left.md).

| training sentences | arm | categories | rules | development | deeper, corpus words | deeper derivable | fresh ungrammatical derived | grammatical samples (novel; deeper) | learned in |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| 1,000 | A | 45 | 298 | 1.2995 | 2.3748 | 300 | 166 of 300 | 299 (290; 35) | 1.2 s |
| 1,000 | C′, θ = 0.05 | 254 | 9,335 | 1.5151 | 3.2125 | 300 | 28 of 300 | 291 (234; 0) | 0.9 s |
| 21,066 | A | 40 | 257 | 1.3444 | **2.2710** | 300 | 166 of 300 | 300 (119; 72) | 22.8 s |
| 21,066 | C′, θ = 0.05 | 3,228 | 32,839 | **1.2197** | 3.1208 | 300 | **35 of 300** | 300 (60; 0) | 7,503 s |

The floor (uniform over the corpus) is 1.2192. Llama, on all development
sentences, gives 1.2214 to 1.2218, and 3.53 to 3.77 on the deeper ones
(results-qlm005.md). C′ at θ = 0.1 to 0.5 is over 60,000 rules at full
size and was not estimated. θ = 0.05 is the shortest-description choice at
both sizes.

## Against the plan (left family, full size)

| criterion | C′ |
|---|---|
| fresh ungrammatical derived below 10% (A: 55%) | **fails narrowly**: 11.7% (35 of 300) |
| development within 1% of A | holds, in the better direction: 9.3% *better* than A |
| every deeper sentence with corpus words derivable | holds: 300 of 300 |

The other three languages have not been run with C′. The plan requires
them.

## What it shows

- **With enough data, Jaccard merging fixes the left family's corpus fit.**
  It goes from A's 1.3444 to 1.2197, essentially at the floor (1.2192),
  and level with the transformer. It also cuts overgeneration from 55% to
  12%.
  - At 1,000 sentences, it had cost 16% in corpus fit. At 21,066 it gains
    9%: the rarer evidence it refuses to merge on at small sizes becomes
    frequent enough at large ones.
  - That is the diagnosis of QLM-LEFT-001 put to work. Merging a frequent
    string with a rare one on one shared context was the error; refusing
    it, and only it, nearly removes it.
- **The cost:**
  - **Depth.** Deeper bits rise from 2.27 to 3.12. That is still better
    than Llama (3.53 to 3.77), and every deeper sentence is still
    derivable, but the samples include no deeper sentences (A's had 72).
    The stricter grammar puts less probability on recursion.
  - **Size and time.** 32,839 rules against 257, and two hours against
    23 seconds. This is the cost problem SCALE-001 and arm E are about.
    The result says the learning principle is right. The representation
    (a category per kept substring, inside–outside over all of them)
    cannot afford it.
