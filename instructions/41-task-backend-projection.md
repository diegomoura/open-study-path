# Project the active learning window to the task backend

Apply this contract during initial publication, successful assessment, focused recovery and provider reconciliation.

GitHub remains authoritative for curriculum, lesson content, assessment results, mastery and verified progress. Exactly one task backend is the operational projection for the learner.

## Provider-independent model

Resolve exactly one primary task backend:

- `trello`;
- `todoist`;
- `github_issues`;
- another explicitly supported adapter.

Do not require an external account. When no external backend is selected or available, use `github_issues` and keep the course usable.

Use these internal canonical states:

- `planned` — Planejado;
- `ready` — ready for the learner;
- `in_progress` — Em estudo;
- `in_assessment` — Em avaliação;
- `review_required` — Revisão necessária;
- `completed` — Concluído.

A task backend may split internal `ready` into two visible locations:

- **Próxima aula** — exactly one primary next lesson;
- **Disponível em paralelo** — other eligible materialized lessons.

Provider adapters may represent states as lists, sections, labels, status fields or completion flags, but they must preserve the same meaning.

## Learner-facing visual order

When the provider supports ordered columns or sections, use this exact left-to-right order:

`Planejado → Disponível em paralelo → Próxima aula → Em estudo → Em avaliação → Revisão necessária → Concluído`

The order presents the course from backlog to available choices, then to the primary action and execution. It does not change prerequisite semantics. Exactly one unfinished eligible lesson is placed in **Próxima aula**; other eligible materialized lessons are placed in **Disponível em paralelo**.

## Active learning window

Read `content_generation.lookahead_topics` from `.open-study-path/instance.yml`. Default to `2` when missing.

This is the single source of truth for the number of complete, non-mastered lessons kept available ahead of the learner. Do not create a separate Trello, Todoist or GitHub setting for the window size.

For large curricula:

1. materialize, review, render and publish up to `lookahead_topics` eligible lessons;
2. select the earliest unfinished eligible lesson in roadmap order as **Próxima aula**;
3. place other complete eligible lessons in **Disponível em paralelo**;
4. never place a lesson in `in_progress` automatically;
5. after mastery, materialize only enough eligible lessons to restore the window;
6. do not count recovery material as a normal lookahead topic;
7. do not materialize blocked topics merely to fill the number.

## Learner responsibility

The only normal manual state transition is from **Próxima aula** or **Disponível em paralelo** to **Em estudo**.

The learner performs it when study actually begins.

The course performs all later transitions after durable GitHub evidence exists:

- valid submission found: `in_progress` → `in_assessment`;
- mastered result: `in_assessment` → `completed`;
- insufficient result: `in_assessment` → `review_required`;
- valid recovery submission: `review_required` → `in_assessment`;
- replacement lesson: new task enters **Próxima aula** or **Disponível em paralelo**, according to roadmap order.

Manual movement to `completed` never establishes mastery. Reconcile it from GitHub state.

## Orientation resource

Create or reuse exactly one orientation resource in the provider's planned area.

Visible title:

`📌 Leia antes de começar — Como usar este acompanhamento`

It must:

- explain the visible lists or states in their exact visual order;
- explain that normally two complete lessons remain available, subject to roadmap dependencies;
- explain the difference between **Próxima aula** and **Disponível em paralelo**;
- explain that lessons, slides, practice, assessments, review and replacement tasks are prepared automatically;
- ask the learner not to create or rename managed states, create lesson tasks manually, or alter managed titles, descriptions, labels, checklists and links;
- state that the only expected manual movement is from an available lesson to **Em estudo**;
- tell the learner to submit the assessment and use the command shown in the lesson task;
- explain that GitHub assessment evidence, not task position, determines approval;
- remain throughout the course and be updated in place.

When supported, apply a distinctive `Instruções do curso` label or equivalent visual marker and keep the resource first. Identification must also use a stable title and a durable external ID recorded in `state/integrations.json`; color or ordering support is optional.

The orientation resource is auxiliary. It does not count as one of the roadmap topic tasks when validating projection completeness.

## Learner-visible metadata boundary

Task titles and descriptions are learner interfaces. Never expose synchronization metadata in them.

Do not place any of the following in a visible title, description, checklist or comment:

- HTML comments such as `<!-- ... -->`;
- the text `open-study-path` used as a machine marker;
- raw `TOPIC-000` identifiers used only for synchronization;
- `content_version` fields;
- serialized prerequisite arrays;
- roadmap fingerprints, provider IDs or other internal state.

Store topic IDs, visible lesson numbers, content versions, direct prerequisite IDs, roadmap fingerprints and provider resource IDs in `state/integrations.json` or in genuinely non-visible provider metadata when the provider supports it. Do not use a hidden-looking HTML comment as a substitute for private metadata: Trello and similar tools may render or expose it.

After writing, read every managed task back. Publication fails when a learner-visible field contains `<!--`, `open-study-path`, a raw synchronization marker or another internal metadata fragment. Correct the provider resource before reporting success.

## Provider adapters

### Trello

Create or reuse lists in this exact left-to-right order:

1. Planejado;
2. Disponível em paralelo;
3. Próxima aula;
4. Em estudo;
5. Em avaliação;
6. Revisão necessária;
7. Concluído.

Keep the orientation card first in **Planejado**. Lesson cards use the normal resource order: Slides, Aula, optional Prática, Avaliação. There must be exactly one lesson card in **Próxima aula**. Other eligible materialized lessons belong in **Disponível em paralelo**.

### Todoist

Create or reuse one project. Use sections that preserve the same learner-facing order and ready-state distinction when supported. Keep the orientation task first in **Planejado**; make it uncompletable when supported. Move tasks by section. A native Todoist completion is only a projection and must be reconciled from GitHub mastery.

### GitHub Issues

Use one issue per roadmap lesson. Represent execution state with exactly one managed status label:

- `study:planned`;
- `study:ready-primary`;
- `study:ready-parallel`;
- `study:in-progress`;
- `study:in-assessment`;
- `study:review-required`;
- `study:completed`.

Create one pinned-or-clearly-linked orientation issue when pinning is unavailable. Close a lesson issue only after verified mastery. A manually closed issue must not mark the topic mastered and may be reopened during reconciliation.

Do not claim GitHub Projects support unless the active connector or workflow can create and update the project, fields and items durably.

## Safe reconciliation

Before every write, read `state/integrations.json` and inspect the exact provider resource when harmless reads are available.

- reuse resources by durable ID before matching by title;
- never delete unknown learner-created lists, sections, labels, tasks, cards or issues;
- never remove learner comments, attachments or personal notes;
- update managed fields only when the resource identity is unambiguous;
- preserve content and request a decision when reconciliation would be destructive or ambiguous;
- journal every successful external write before the next write;
- re-running an unchanged operation must create no duplicate resource.

Record at least: capability, provider, resource type, safe external ID, URL, topic ID when applicable, visible lesson number, content version, direct prerequisite IDs, canonical state, managed-field version, roadmap fingerprint, sync status and timestamp.

## Assessment result notification

Chat always reports the reviewed result.

When Gmail or Outlook is selected, connected and configured with `after_each_assessment`, send one idempotent notification after the final result is reviewed and persisted in GitHub.

For mastery, include:

- lesson title;
- score and approval;
- direct link to the durable response-by-response correction;
- confirmation that the task moved to `Concluído`;
- lessons currently in **Próxima aula** and **Disponível em paralelo**;
- accurate wording about automatic window replacement.

For an insufficient result, include:

- lesson title and score;
- `Revisão necessária` language;
- direct correction link;
- focused recovery task or reassessment link;
- the other available lesson when one exists.

Never include raw learner answers or unnecessary personal data. Record provider message ID, attempt, result type, status and timestamp. Do not send the same notification twice. Optional email failure must not undo assessment, task movement or materialization.

## Operational checkpoints

Use a durable operation record under `state/operations/` when the active review profile permits it; otherwise keep the complete resumable checkpoint in `state/integrations.json`.

A publication or assessment projection checkpoint includes:

- `operation_id`;
- operation type;
- provider and mode;
- status;
- current batch;
- topics;
- attempt;
- external read and write counts;
- last checkpoint;
- last error;
- started and updated timestamps.

One operation ID maps to one convergent branch and pull request. Resume the same operation instead of creating competing recovery branches.

## Completion response

After initial publication, show the task-backend link, orientation resource and available lessons. Say:

`Quando começar uma aula, mova somente esse cartão ou tarefa para Em estudo.`

After evaluation, report score, result, correction link and either focused review or the available lessons. Do not require a separate command to replace the learning window.
