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

Use these canonical states:

- `planned` — Planejado;
- `ready` — Pronto para estudar;
- `in_progress` — Em andamento;
- `in_assessment` — Em avaliação;
- `review_required` — Revisão necessária;
- `completed` — Concluído.

Provider adapters may represent states as lists, sections, labels, status fields or completion flags, but they must preserve the same meaning.

## Active learning window

Read `content_generation.lookahead_topics` from `.open-study-path/instance.yml`. Default to `2` when missing.

This is the single source of truth for the number of complete, non-mastered lessons kept available ahead of the learner. Do not create a separate Trello, Todoist or GitHub setting for the window size.

For large curricula:

1. materialize, review, render and publish up to `lookahead_topics` eligible lessons;
2. place every complete eligible lesson in `ready`;
3. never place a lesson in `in_progress` automatically;
4. after mastery, materialize only enough eligible lessons to restore the window;
5. do not count recovery material as a normal lookahead topic;
6. do not materialize blocked topics merely to fill the number.

## Learner responsibility

The only normal manual state transition is:

`ready` → `in_progress`

The learner performs it when study actually begins.

The course performs all later transitions after durable GitHub evidence exists:

- valid submission found: `in_progress` → `in_assessment`;
- mastered result: `in_assessment` → `completed`;
- insufficient result: `in_assessment` → `review_required`;
- valid recovery submission: `review_required` → `in_assessment`;
- replacement lesson: new task enters `ready`.

Manual movement to `completed` never establishes mastery. Reconcile it from GitHub state.

## Orientation resource

Create or reuse exactly one orientation resource in the provider's planned area.

Visible title:

`📌 Leia antes de começar — Como usar este acompanhamento`

It must:

- explain every canonical state in simple language;
- explain that normally two complete lessons remain ready, subject to roadmap dependencies;
- explain that lessons, slides, practice, assessments, recovery and replacement tasks are prepared automatically;
- ask the learner not to create or rename managed states, create lesson tasks manually, or alter managed titles, descriptions, labels, checklists and links;
- state that the only expected manual movement is from `Pronto para estudar` to `Em andamento`;
- tell the learner to submit the assessment and use the command shown in the lesson task;
- explain that GitHub assessment evidence, not task position, determines approval;
- remain throughout the course and be updated in place.

When supported, apply a distinctive `Instruções do curso` label or equivalent visual marker and keep the resource first. Identification must also use a stable title and a durable external ID recorded in `state/integrations.json`; color or ordering support is optional.

## Provider adapters

### Trello

Use lists equivalent to the six canonical states. Keep the orientation card first in `Planejado`. Lesson cards use the normal resource order: Slides, Aula, Prática, Avaliação.

### Todoist

Create or reuse one project. Use sections equivalent to the canonical states. Keep the orientation task first in `Planejado`; make it uncompletable when supported. Move tasks by section. A native Todoist completion is only a projection and must be reconciled from GitHub mastery.

### GitHub Issues

Use one issue per materialized lesson. Represent state with exactly one managed status label:

- `study:planned`;
- `study:ready`;
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

Record at least: capability, provider, resource type, safe external ID, URL, topic ID when applicable, content version, canonical state, managed-field version, sync status and timestamp.

## Assessment result notification

Chat always reports the reviewed result.

When Gmail or Outlook is selected, connected and configured with `after_each_assessment`, send one idempotent notification after the final result is reviewed and persisted in GitHub.

For mastery, include:

- lesson title;
- score and approval;
- direct link to the durable response-by-response correction;
- confirmation that the task moved to `Concluído`;
- lessons currently in `Pronto para estudar`;
- accurate wording about automatic window replacement.

For an insufficient result, include:

- lesson title and score;
- `Revisão necessária` language;
- direct correction link;
- focused recovery task or reassessment link;
- the other ready lesson when one exists.

Never include raw learner answers or unnecessary personal data. Record provider message ID, attempt, result type, status and timestamp. Do not send the same notification twice. Optional email failure must not undo assessment, task movement or materialization.

## Operational checkpoints

Use a durable operation record under `state/operations/` for publication and assessment projection. It must include:

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

After initial publication, show the task-backend link, orientation resource and ready lessons. Say:

`Quando começar uma aula, mova somente esse cartão ou tarefa para Em andamento.`

After evaluation, report score, result, correction link and either focused review or the ready lessons. Do not require a separate command to replace the learning window.