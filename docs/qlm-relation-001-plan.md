# QLM-RELATION-001 plan (draft): bindings, relations and layered graphs

A draft. It is fixed only after the transformers' fact scores on the
semantic worlds are in, and after LARQL-QLM-GROUP-001 has run, so that the
design starts from what both kinds of model fail at.

## The failures it starts from

On the semantic worlds (QLM-SEMANTIC-001), the grammar learner:
- **holds some seen facts:** 43% accuracy, contrast 6.2 bits;
- **composes none:** chance;
- **cannot continue any inverse prompt:** 12 of 12 abstentions;
- **answers a new phrasing of a known fact confidently wrong:** −12.3 bits;
- **groups people by continent** through shared contexts, and transfers a
  property through that group.

## Arms, staged so that each capability is measured on its own

| arm | adds |
|---|---|
| A | the grammar learner as it is |
| B | learned bindings: entity identities kept beside their categories (abstraction by accumulation, not by merging) |
| C | B, with learned relations between bound entities and composition of relations |
| D | separate syntactic and semantic stages over one shared graph state |
| E | D, with repeated refinement of that state until it stops changing |

**What no arm is given:** the world graph, relation names, entity types or
composition rules. Everything is learned from the same training text. A
hand-built graph of the world is run as an oracle, a positive control, and
reported apart.

## Measures

- Everything QLM-SEMANTIC-001 measures, on the three permuted worlds.
- Development bits.
- Grammaticality of samples.
- Cost of learning and of execution.
- **Incremental learning:** after training, one new person is introduced
  in a single statement (`P lives in K .`). The questions about that person
  that need composition are then answered, with the cost of adding them
  recorded: what changed in the model, and how long it took.

The thresholds are fixed when the draft is.
