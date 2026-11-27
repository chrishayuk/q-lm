# QLM-EQUIV-001 plan: equivalence that needs evidence, or depends on role

Written before any arm is built or run.

## Question

QLM-LEFT-001 found that one shared context is enough for the learner to
merge two strings, and that merging is permanent and transitive. Where a
language is not substitutable, under 0.5% of wrong unions corrupt whole
categories. On the left family, 172 of 300 ungrammatical sentences are
derived. Does equivalence that needs more evidence, or that holds only
within a role, keep what substitutability gets right and lose what it gets
wrong?

## Arms

| arm | equivalence | parameter |
|---|---|---|
| A | one shared context merges, permanently (the present learner) | none |
| B | merge only strings that share at least k distinct contexts | k ∈ {2, 3, 5} |
| C | merge when the two strings' context sets overlap enough: shared / smaller set ≥ θ, with at least 2 shared | θ ∈ {0.1, 0.25, 0.5} |
| D | roles first: a string's occurrences are split into roles by clustering its contexts (two contexts are linked if they share at least 2 fillers). Categories are then formed over (string, role) pairs by B's rule | k = 2 |
| E | no unions: every substring keeps its own category, and equivalence is a weighted unary rule A → B with weight from the context overlap of A and B. The grammar is a mixture over substitutions, not a partition | weights normalised per category; overlap floor θ = 0.1 |

**The parameter is chosen from training sentences only**, by the shortest
two-part description (QLM-004's code), within each arm.
- Development sentences are all grammatical, so they cannot penalise
  overgeneration. Choosing by them would favour the loosest arm.
- If the description-length choice looks wrong, it is reported, not
  overridden.

**E needs the exact next-token code extended to unary rules.** The prefix
probabilities need the unary closure (I − P_U)⁻¹ beside the left-corner
closure. E is not scored word by word until that extension passes
`tests/prefix.rs`'s comparison against enumeration.

**After learning, every arm gets 20 rounds of inside–outside.**

## Languages

- The three QLM-005 families.
- Colmerauer's language, which must not get worse.

All at the full training size, and at 1,000 sentences.

## Fresh negatives

The existing ungrammatical sentences, `negative.txt`, informed the
diagnosis, so they are not used to judge these arms. New sets are made,
`qlm negatives DIR`:
- `negative-dev.txt`: 300 from development sentences, seed 501. Used
  during the experiment.
- `negative-confirm.txt`: 300 from confirmation sentences, seed 502. Read
  once, at the end.

Each is made by swapping two words of a sentence, and kept only if the
generating grammar derives no tree of it. A sentence is never called
ungrammatical for being unseen.

## Measures

For each arm, language and size:
- **Corpus fit:** development bits per token.
- **Depth:** deeper bits per token, and deeper sentences derivable.
- **Overgeneration:**
  - fresh ungrammatical sentences derived (development set);
  - samples judged grammatical, and of those, novel and deeper.
- **Size:** categories, rules, and for E, substitution edges.
- **Cost:** learning time, and ms per next-token distribution.

## What would count

An arm **fixes the overgeneration without breaking anything else** if, on
the left family at full size:
- fresh ungrammatical sentences derived fall below 10% (from 57%);
- development bits are within 1% of arm A's;
- every deeper sentence with corpus words stays derivable;

and on the other three languages, none of these gets worse by more than
the same margins. The best arm on development is then run once on the
confirmation negatives.

Separately, D and E are reported as **representations**: how many roles
per string D finds, and how E's substitution weights are spread. A worse
score with a more faithful structure is still a finding.
