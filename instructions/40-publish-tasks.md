# Publish tasks

Use the task manager and optional integrations configured in `study.config.yml`. Run this phase only after the curriculum has been validated, approved and merged.

## Approved curriculum invariant

Treat these approved artifacts as immutable inputs during publication:

- `study/roadmap.md`;
- `study/topics/`;
- `study/modules/`;
- `study/assessments/`;
- `.github/ISSUE_TEMPLATE/assessment-topic-*.yml`.

The `publish` phase may transform them into tasks, cards, checklists, events, notifications and integration state, but it must not add, remove, rewrite or reinterpret pedagogical objectives, teaching content, activities, prerequisites, effort estimates, deliverables, evidence, assessment questions, scoring rules, resources or mastery criteria.

The owner does not need to restate this invariant. The standard command is:

`Publique as tarefas da trilha nas integrações configuradas.`

If a provider requires a choice that would change approved pedagogical content, create no affected resource and ask one concise, specific question. Operational formatting choices that preserve content do not require confirmation.

## Connection preflight

Before any external write, read and execute `instructions/42-integration-preflight.md`.

Derive required providers from `study.config.yml` and verify actual access with a harmless read-only probe through every required connector. Configuration values or available tool definitions are not sufficient proof of authorization.

Run the preflight atomically. If any required connection is unavailable, create no board, card, issue, event, email or integration-state write. When all probes pass, continue immediately without another confirmation.

## GitHub assessment forms

The per-topic assessment Issue Forms are generated with the curriculum. Do not create empty placeholder issues during publication. Verify that every topic has a working direct form URL:

`https://github.com/OWNER/REPOSITORY/issues/new?template=assessment-topic-<number>.yml`

Use the exact instance repository from `.open-study-path/instance.yml`.

## Trello

Create or select a board with lists `Planejado`, `Pronto para estudar`, `Em andamento`, `Em avaliação` and `Concluído`.

Create one card per topic. Each card description must include:

- objective and prerequisites;
- estimated effort;
- direct link to the complete module;
- direct link to the topic contract;
- direct link to the assessment Issue Form;
- deliverable and mastery threshold;
- the completion command `Finalizei o TOPIC-000. Avalie a issue #<número>.`.

Create granular checklist items for prerequisite check, lesson sections, worked examples, guided practice, independent practice, deliverable preparation and assessment submission. Do not compress several distinct activities into one vague checklist line. Trello is the execution index, not the course-content repository.

Put only dependency-ready topics in `Pronto para estudar`; keep blocked topics in `Planejado`.

## Markdown-only task management

When the configured task manager is `markdown`, keep execution state in the topic and roadmap artifacts without duplicating full module content.

## Calendar and notifications

When Google Calendar is enabled, create the configured study schedule only after preflight. Treat dates as projections and preserve topic dependencies. Event descriptions should link to the module, task card and assessment form.

When Gmail notifications are enabled, send only the publication messages required by the approved plan. The initial message should link the first module, task card and assessment form and state the exact completion command.

## Idempotency and state

Before creating resources, inspect `state/integrations.json` when it exists and search providers for exact matching resources. Reuse valid identifiers rather than creating duplicates.

Store external identifiers in `state/integrations.json`; do not place secrets there. If publication is interrupted after writes begin, report exactly which resources were created and which remain pending.

The publication command supplies approval for configured external-resource creation. Intake, diagnostic and curriculum merge policies do not.

## Completion

Complete the phase using `instructions/phase-completion.md`. Link the first complete module, task card and assessment form. Do not start an improvised lesson in chat by default.

The standard learner handoff is:

`Ao concluir o TOPIC-000 e enviar o formulário, escreva: "Finalizei o TOPIC-000. Avalie a issue #<número>."`