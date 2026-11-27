# QLM-SEMANTIC-001 plan: learning relations, not just grammar

Written before any language or learner for it exists, and tightened
once before implementation (below).

**Tightened before implementation.**
1. The held-out statements are stated as exceptions to "every fact is in
   training".
2. Held-out compositions are balanced so that no frequency shortcut solves
   them.
3. Entity-permuted worlds test whether what is learned is reusable
   machinery or memorised strings.

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

**Texts** are one to three sentences, each a true statement.

Every fact is stated in at least one phrasing in training, **except** the
statements held out below.
- A held-out capital fact keeps its first phrasing in training and loses
  its second.
- A held-out inverse loses every `located` statement for that country's
  capital, in both phrasings. Its `capital` statements stay.
- A held-out composition loses every `lives-on` statement for that person.
  Its `lives`, `located` and `continent` facts stay.

Nothing else is withheld.

**No frequency shortcuts.**
- Each continent has 6 of the 24 countries, and each city 2 of the 48
  people. So the most frequent continent or city is right only by chance
  (1/4, 1/24).
- The held-out people of the composition test are spread evenly over the
  continents (3 each).
- A held-out person's name never appears in the same text as their
  continent's name.
- A unigram or bigram model is run and reported as the shortcut baseline.
  A test it passes is not counted as generalisation.

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

## Entity-permuted worlds

The whole experiment is run on 3 worlds with the same names and the same
relation structure. Each assigns the facts differently: which city is
whose capital, which continent each country is in, where each person
lives.
- Every world gets its own corpus and its own split.
- A learner that has learned the relations should pass the same tests on
  each world.
- A result that holds on one world and not the others points at the
  particular strings, not at the relations.

Results are reported per world and as the mean.

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

## Changes after a first result

1. **Composition and new-entity people are held out by city.**
   - **The evidence.** On world 1, the converged grammar scored 11 of 12 on
     composition (contrast 14.8 bits). 11 of the 12 held-out people had a
     city-mate (every city has two residents) whose `lives-on` statement
     was in training. Substitution merges people who share contexts such
     as `_ lives in K .`, so a held-out person inherited the city-mate's
     continent. That is a shortcut through a similar entity, not
     composition through the relations.
   - **The change.** Composition holds out both residents of 2 cities per
     continent: 16 people, 4 per continent. New entity holds out both
     residents of 2 further cities: 4 people. No held-out person has a
     city-mate whose answer is in training.
   - **When.** Made before any transformer was trained on these worlds. The
     first world-1 result is kept below, as the record of the shortcut.

   | model (world 1, first design) | composition accuracy | contrast |
   |---|---:|---:|
   | grammar, 20 rounds | 11 of 12 | 14.75 |
   | Kneser–Ney 3-gram | 3 of 12 (chance) | −0.02 |
