# Publish tasks

Use the configured task manager and optional integrations only after the roadmap, topic contracts and initial content window have been validated, approved and merged.

## Approved curriculum invariant

Treat the approved roadmap, topic contracts and every existing module, rubric and assessment form as immutable inputs during publication. Publication may create task representations and integration state, but it must not change pedagogical content.

The standard command is:

`Publique as tarefas da trilha nas integrações configuradas.`

## Connection preflight

Before external writes, execute `instructions/42-integration-preflight.md`. Complete every required harmless read-only probe before creating or updating external resources. When all probes pass, continue without another confirmation.

## Standard GitHub assessment labels

Ensure these repository labels exist before the learner submits assessment forms:

- `assessment`;
- `assessment:submitted`;
- `assessment:graded`;
- `assessment:recovery-required`.

Assessment Issue Forms are created only for materialized topics. Do not create empty assessment issues during publication.

## Trello and other task backends

Create one task or card per topic so the learner can see the complete roadmap.

### Materialized topic

A materialized topic card must include:

- objective, prerequisites and estimated effort;
- direct link to the complete module;
- direct link to the topic contract;
- direct link to the assessment Issue Form;
- deliverable and mastery threshold;
- the command `Finalizei o TOPIC-000. Avalie minhas respostas.`;
- granular checklist items derived from the module execution plan.

Create separate checklist items for focused actions. Do not compress several distinct activities into one vague line. Trello is the execution index, not the content repository.

### Planned topic

A planned topic card must include:

- objective, prerequisites and estimated effort;
- direct link to the topic contract;
- expected deliverable and mastery criteria;
- a clear statement that the complete module and assessment will be materialized automatically when the topic enters the active rolling window.

Do not add nonexistent module, rubric or assessment-form links. Use a short planning checklist rather than pretending the full lesson is ready.

Put only dependency-ready materialized topics in `Pronto para estudar`. Keep planned topics and blocked materialized topics in `Planejado`.

## Calendar and notifications

Calendar may show the complete schedule projection. For a planned topic, link only its task card and topic contract. When the topic is later materialized, update the existing event description with module and assessment links rather than creating a duplicate event.

The initial Gmail publication message should link the first ready materialized topic. It may link the roadmap for visibility into later planned topics.

## Idempotency and state

Inspect `state/integrations.json` and exact matching provider resources before writes. Reuse cards, events, labels and identifiers. Store safe external identifiers without secrets.

## Completion

Link the first complete module, task card and assessment form. Do not start an improvised lesson in chat by default.

Use:

`Ao concluir o TOPIC-000 e enviar o formulário, escreva: "Finalizei o TOPIC-000. Avalie minhas respostas."`
