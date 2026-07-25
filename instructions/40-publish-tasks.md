# Publish tasks

Use the task manager and optional integrations configured in `study.config.yml`. Run this phase only after the generated roadmap and topics have been validated, approved and merged.

## Connection preflight

Before any external write, read and execute `instructions/42-integration-preflight.md`.

Derive the required providers from `study.config.yml` and verify actual access with a harmless read-only probe through every required connector. Configuration values or available tool definitions are not sufficient proof of authorization.

Run the preflight atomically: if any required connection is unavailable, create no board, card, issue, event, email or integration-state write. Tell the owner which providers must be connected and provide the exact standard return command from the preflight instruction.

When all required probes pass, continue publication immediately. Do not send a separate connection-success message and do not ask for another confirmation. The publication command already authorizes the configured external-resource creation for this phase.

## GitHub Issues

Create one issue per topic with objective, prerequisites, deliverable, mastery criteria and links to the topic file. Use task lists for learning activities.

## Trello

Create or select a board with lists `Planejado`, `Pronto para estudar`, `Em andamento`, `Em avaliação` and `Concluído`. Create one card per topic and one checklist per activity group.

## Markdown

Keep tasks only in topic files and `study/roadmap.md`.

## Calendar and notifications

When Google Calendar is enabled, create the configured study schedule only after the connection preflight passes. Treat dates as projections and preserve topic dependencies.

When Gmail notifications are enabled, create or send only the publication messages explicitly required by the approved plan. Do not expose unnecessary learner data.

## Idempotency and state

Before creating resources, inspect `state/integrations.json` when it exists and search the connected provider for exact matching resources. Reuse valid resources and external identifiers rather than creating duplicates.

Store external identifiers in `state/integrations.json`; do not place secrets there. If publication is interrupted after writes begin, report exactly which resources were created and which remain pending.

Creating or changing an external task backend requires explicit owner approval for this phase. The command to publish tasks supplies that approval; intake, diagnostic and curriculum merge policies do not.

Complete the phase using `instructions/phase-completion.md`. Link the created task backend or repository artifact, report only material failures or skipped integrations, and give one exact command for the first progress synchronization or study check-in.
