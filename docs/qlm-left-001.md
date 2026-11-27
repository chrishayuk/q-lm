# QLM-LEFT-001: why the learner overgenerates on left embedding

On the left family, the converged grammar derives 172 of the 300
ungrammatical sentences. This note finds the cause before any fix is
chosen. The tool is `qlm trace DIR [N]`, with full output in
`data-*/trace.md`.
- It gives every substring its **true type**: the symbols of the
  generating grammar that derive it, or "none" if it is no constituent.
- It logs every union the learner makes, with the context that made it.
- It shows the most probable derivation of each accepted ungrammatical
  sentence, with the true type of every node.

## The cause: one shared context is taken as proof of interchangeability

The learner merges two substrings when they occur once in the same context
(the whole rest of the sentence). That is sound only if the language is
**substitutable**: two strings that share one context share all their
contexts. The theory the learner comes from (Clark and Eyraud 2007)
assumes this. The left family is not substitutable, and the first bad
union shows it.

- `bine rota` (a sentence, S → X V) and `zagu deka kake bopu zagu gize`
  (no constituent) occur in the same context `rota zagu bopu _ bopu zagu
  deka`, and are merged.
- But `bine rota` is a whole sentence, and the other string is not. They
  share one context and not the rest.

In that context, `bine rota` is not acting as a sentence. It is the start
`X V` of a longer clause `X V M X`, which is then closed by the marker into
an embedded `E → S C`. In this grammar a complete short clause (`X V`) is
also the beginning of a longer one, and the marker that closes an embedded
clause comes after it. So the same string occurs both as a constituent and
as a prefix of a constituent, and the context does not tell the two apart.

## The three families side by side

| family | clause marked | unions across true types | ungrammatical derived, of 300 |
|---|---|---:|---:|
| centre (`E → C S D`) | on both sides | 2 of 625,242 | 0 |
| right (`E → C S`) | before | 233 of 137,007 | 24 |
| left (`E → S C`) | after | 369 of 83,862 | 172 |

- **Centre.** Its 2 unions are of an embedded argument with a noun. Both
  are arguments `X`, so they are correct. When every embedded clause is
  bracketed on both sides, a context identifies a constituent, and the
  learner makes no wrong union. The language is effectively substitutable.
- **Right and left.** With a marker on one side only, a constituent and a
  non-constituent can share a context. In the left family, the category of
  sentences takes in 846 non-constituents, such as `rota toza`. Why left
  lets through seven times as many ungrammatical sentences as right, with
  a similar number of wrong unions, is not yet traced.

**Few wrong unions do the damage.** Only 369 of 83,862 unions in the left
family cross true types, under 0.5%. But union is transitive. A category
that once takes in a non-constituent takes in that string's whole
category. Category 0, which holds the arguments, ends with:
- 63 embedded arguments and 3 nouns;
- 6,722 non-constituents.

**The derivations of ungrammatical sentences run through non-constituent
categories.** In the four traced, almost every node spans a non-constituent.
Where one doesn't, it is a merged category holding both kinds.

## What this says about the missing abstraction

The hypotheses were:
- local context shared, global context different;
- provenance-blind equivalence;
- lost binding;
- one category doing several jobs.

The trace supports the first and the last, joined: **a string that plays
two roles, as a constituent here and as part of one there, is given one
category, because one shared context was enough to merge it.** What is
missing is evidence for a merge beyond one context.

Fixes the trace suggests, none of them tried yet:
- **Merge on enough evidence.** Require several shared contexts, or a large
  enough overlap of the two strings' context distributions, before merging.
  This is the distributional, k-substitutable direction (Yoshinaka 2008;
  Clark's distributional learners).
- **Split by role.** Keep one category per (string, role), where a role is
  given by the contexts that license it: contextual specialisation.
- **Undo unions that cause overgeneration.** Overgeneration is visible from
  the training sentences alone: a merged category that lets the grammar
  derive strings never seen in any context of its members' kind. That is a
  form of the category splitting QLM-004 left open.

Whichever is chosen has to be justified from training sentences only. The
ungrammatical test sentences are a test set, and choosing a fix by how
many of them it rejects would be fitting to the test.

The same weakness matters for natural text, which is far from
substitutable. It is one more reason the TinyStories step needs a
different way of finding categories (README, Direction).
