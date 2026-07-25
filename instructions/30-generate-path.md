# Generate learning path

Generate a dependency-aware set of topics instead of fixed weeks. Each topic must include an objective, prerequisites, estimated effort, learning activities, deliverable, evidence and mastery criteria.

Create:

- `study/roadmap.md` with the topic graph and estimated schedule;
- one file per topic under `study/topics/` using `templates/topic.md`;
- a schedule projection derived from total effort and weekly availability.

## Scope and effort

Make the scope explicit. When the proposed effort cannot satisfy the learner's complete long-term objective, label the result as an introductory cycle rather than implying comprehensive mastery.

Use realistic estimates. A topic may span more than one week when its evidence and mastery criteria cannot responsibly fit within the learner's weekly availability. Distinguish active study time from elapsed time required for real-world practice.

## Resources

Prefer primary or official resources. Every required resource must name a specific work and canonical locator such as section, chapter, book or letter number. Do not use vague placeholders such as “a passage to select” as required resources.

Edition, translation and URL selection may remain pending, but say so explicitly and preserve the canonical locator. Do not claim a resource, edition, translation or link was verified when it was not checked.

## Pull request

Open a draft pull request for the curriculum proposal. Limit the diff to:

- `.open-study-path/instance.yml`;
- `study/roadmap.md`;
- `study/topics/`.

Set `status.curriculum_proposed: true`. Do not mark the curriculum approved during generation.

Do not merge the proposal during this phase. Do not publish tasks, create Trello cards, calendar events or notifications.

## Completion

Complete the phase using `instructions/phase-completion.md`. Link the curriculum PR and surface only material assumptions or unresolved choices.

Guide the owner to the explicit review phase with a command equivalent to:

`Revise o PR #<number> contra o intake, o diagnóstico e o contrato da trilha. Corrija problemas encontrados. Se o CI passar e não houver decisão pedagógica pendente, marque o PR como pronto e faça merge. Não publique tarefas ainda.`
