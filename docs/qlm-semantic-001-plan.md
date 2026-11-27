# QLM-SEMANTIC-001 plan: learning relations, not just grammar

Written before any language or learner for it exists.

## Question

So far every language has been syntax: any noun fits wherever any noun
fits. Natural text also carries **facts**. "France has capital Paris" is
true and "France has capital Berlin" is false, though the two are equally
grammatical. Can a learner given only sentences learn:
- which words go together as facts;
- that two relations are inverses;
- that relations compose;
- that one fact has several phrasings;

and use them to predict words it has never seen in that combination?

## The language

A seeded generator, `qlm semantic DIR SEED`, makes a world and its text.

**The world:**
- 24 countries, each on one of 4 continents;
- each country with one capital (24 cities);
- 48 people, each living in one city.

All names are made-up words.

**Relations and phrasings.** There are at least two phrasings of every
relation, and every fact can be stated in every phrasing of its relation.

| relation | phrasings |
|---|---|
| capital(country → city) | `C has capital K .` / `the capital of C is K .` |
| located(city → country), the inverse | `K is located in C .` / `K is a city of C .` |
| continent(country → continent) | `C is in T .` / `C lies on T .` |
| lives(person → city) | `P lives in K .` / `P is from K .` |
| lives-on(person → continent), the composition lives ∘ located ∘ continent | `P lives on T .` |

**Texts** are one to three sentences, each a true statement. Every fact is
stated in at least one phrasing in training.

## Held out (never in training, in any phrasing)

| test | what is held out | what it asks |
|---|---|---|
| phrasing | for 25% of capital facts, the second phrasing | a known fact in a known phrasing it was never seen in |
| inverse | for 25% of countries, every located(city → country) statement | given only "C has capital K", predict C after "K is located in" |
| composition | for 25% of people, every lives-on statement | predict T after "P lives on", from lives, located and continent |
| new entity | 4 people, each seen in one lives statement only | the composition for an entity seen once |

The held-out sets are disjoint and fixed by the seed. The development and
confirmation texts are drawn from facts and phrasings that are in training,
as before.

## Measures

For each test, at the position where the answer comes:
- **Accuracy.** Is the answer the most probable word among its type (the
  24 cities, 24 countries or 4 continents)?
- **Bits** on the answer.
- **Contrast.** log2 of the probability of the true answer over the
  average of the same type's false answers. 0 means the model knows the
  type but not the fact.

Also development bits per token, as before, and samples judged for truth.
A sample is true if every sentence states a fact of the world, and
grammatical if every sentence fits a phrasing.

## Learners

- The grammar learned by substitutability, converged.
- The custom transformer and the Llama arm, 3 seeds each.
- Kneser–Ney n-grams.

## What is expected, and why it is still worth running

- **The grammar.** Substitutability will probably merge all countries into
  one category, since they share contexts, and all cities into another. A
  context-free grammar over those categories cannot tell France's capital
  from Germany's, so its contrast would be near 0 on every test. If that
  happens, it is the finding: it is the point where categories from
  substitution stop being enough, and a learner of relations (lexicalised
  rules, or categories split by what they co-occur with) has to be
  designed.
- **The transformers.** Neural language models are known to learn facts
  in the direction they were trained and to fail on the inverse (the
  "reversal curse": Berglund et al. 2023). Whether that holds at this scale
  is measured here, not assumed.

## What would count

- **A learner knows facts** if its contrast on seen facts in seen
  phrasings is above 3 bits (8 to 1).
- **It generalises** a test if its accuracy there is above 50% and its
  contrast above 1 bit.
- **Chance** is 1/24 for cities and countries, and 1/4 for continents.
