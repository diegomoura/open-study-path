# Publish tasks

Use the task manager configured in `study.config.yml`. Run this phase only after the owner has approved the generated roadmap and topics.

## GitHub Issues

Create one issue per topic with objective, prerequisites, deliverable, mastery criteria and links to the topic file. Use task lists for learning activities.

## Trello

Create or select a board with lists `Planejado`, `Pronto para estudar`, `Em andamento`, `Em avaliação` and `Concluído`. Create one card per topic and one checklist per activity group.

## Markdown

Keep tasks only in topic files and `study/roadmap.md`.

Store external identifiers in `state/integrations.json`; do not place secrets there.

Creating or changing an external task backend requires explicit owner approval for this phase. The intake merge policy does not authorize task publication or external-resource creation.

Complete the phase using `instructions/phase-completion.md`. Link the created task backend or repository artifact, report only material failures or skipped integrations, and give one exact command for the first progress synchronization or study check-in.