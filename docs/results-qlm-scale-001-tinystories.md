# Results: QLM-SCALE-001, a first TinyStories run of the present learner

A feasibility run, not a modelling result. It used the present learner
(arm A: one shared whole-sentence context merges), on sentences from
TinyStories:
- the first 20,000 training stories;
- split at `.`, `!` and `?`;
- lowercased, with punctuation as tokens;
- 2 to 40 tokens, 12 on average.

That gives 346,098 training sentences, 13,959 development sentences and
10,952 words. Each size ran in its own process, with a 15-minute limit.
Grammars over 200,000 rules have their structure reported without
estimation. Table: [tables/scale-001-tinystories.md](tables/scale-001-tinystories.md).

| sentences | distinct substrings | categories | rules | development bits per token | peak memory, MB |
|---:|---:|---:|---:|---:|---:|
| 100 | 9,615 | 9,063 | 56,642 | 13.75 | 3,119 |
| 300 | 23,241 | 21,093 | 145,716 | 13.70 | 15,555 |
| 1,000 | 85,085 | 77,587 | 584,876 | not estimated | 408 |
| 3,000 | 284,098 | 259,456 | 2,127,959 | not estimated | 935 |
| 10,000 | 785,287 | 691,404 | 5,613,178 | not estimated | 1,854 |
| 30,000 | 1,945,559 | 1,626,255 | 13,582,110 | not estimated | 3,940 |
| 100,000 | 6,607,023 | 5,373,773 | 49,056,462 | not estimated | 13,812 |

## What breaks, and why

- **Almost nothing merges.**
  - Categories are 81% to 94% of distinct substrings at every size: 5.4
    million categories from 6.6 million substrings at 100,000 sentences.
  - Whole-sentence contexts almost never recur in natural text, so two
    substrings rarely share one.
  - In the synthetic languages, a few thousand sentences were enough for
    the grammar to collapse to tens of categories. Here it never begins
    to.
- **So the model grows with the text, faster than linearly.** Rules: 0.58
  million at 1,000 sentences, 5.6 million at 10,000, 49 million at
  100,000. The opposite of kind 1's result, where the grammar stopped
  growing.
- **Nothing generalises.**
  - At 100 and 300 sentences, development bits are 13.7 per token. That is
    the floor: uniform over 10,952 words is 13.4 bits.
  - Almost no development sentence can be derived from 300 training
    sentences' worth of near-unique categories.
- **Memory follows the grammar.**
  - The next-token computation's dense left-corner closure is categories
    squared. At 300 sentences, 21,093 categories, it needs 15.5 GB.
  - Structure alone needs 13.8 GB at 100,000 sentences.

## What it says for arm E

Every piece of arm E's design is needed, and one more:
- **Bounded contexts.** Substitution must be judged on a few words either
  side, not the whole sentence, or nothing in natural text will ever
  share a context. This is now the first thing to build.
- **Promotion.** Most substrings occur once (6.6 million distinct at
  100,000 sentences). Storing them as categories is what explodes;
  storing them as observations and promoting only recurring, bounded
  phrases is the design's answer.
- **Sparse prediction.** The dense closure (categories squared) cannot
  work beyond a few thousand categories. Next-token prediction has to run
  on the active graph.
- **Identity kept, with memberships that depend on context.** With short
  contexts, single-context merging would merge far too much: in natural
  text, almost anything can follow "the". That is exactly the
  overgeneration of the left family, at scale. This is where C′'s Jaccard
  rule, and arm E's conditional memberships, come in.
