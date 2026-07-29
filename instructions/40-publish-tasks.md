# Publish tasks and selected integrations

Use the approved roadmap, topic contracts, ready lessons, integration plan and current state. Publication creates execution and practice projections. It must not regenerate or rewrite pedagogical content, but it may synchronize bounded integration-reference blocks whose content is derived deterministically from approved artifacts and durable state.

Read `docs/learner-facing-language.md` before writing task descriptions or the completion response.

The natural command is:

`Organize minha trilha nas ferramentas que escolhemos.`

Continue accepting `Publique as tarefas da trilha nas integrações configuradas.` as an alias.

## Connection preflight

Run `instructions/42-integration-preflight.md` before external writes. Required providers must pass harmless verification before the required publication set. Optional missing providers use their documented alternatives and may receive one nonblocking connection suggestion.

Do not wait for an optional connection click before completing work that can use a repository-native alternative.

## Authority model

GitHub stores approved curriculum, lessons, assessments and verified progress. Exactly one task backend tracks operational execution. External practice, reminders, calendars, habits, analytics and course platforms never establish learning completion.

This is an internal contract. Do not repeat it verbatim in every learner-facing card.

## Standard assessment labels

Ensure labels exist:

- `assessment`;
- `assessment:submitted`;
- `assessment:graded`;
- `assessment:recovery-required`.

Do not create empty assessment issues during publication.

## Task backend

Create one task per topic in the single selected backend. The task is the learner's concise entry point into the lesson, primary practice and assessment. It is not an inventory of every repository artifact.

### One primary resource per capability

Show one primary learner-facing resource per capability in the task:

- one lesson link;
- one current practice link for the same practice capability;
- one direct assessment link.

When an external integration is connected and its current resource was created successfully, show that external resource as the primary practice link. Keep local Markdown and TSV alternatives in the lesson and repository, but do not duplicate them in the task.

When the external resource is unavailable, show the best local learner-facing alternative instead. Prefer the Markdown study deck. Show the TSV only when import is the intended action or the learner explicitly asks for it.

Do not link internal topic contracts under `study/topics/`, rubric YAML files under `study/assessments/`, state files or synchronization records from the primary task. Summarize the useful parts of those artifacts directly in the card.

### Human card titles

Prefer:

`1. <título da aula>`

Do not use `[TOPIC-001]` in the visible title unless the learner explicitly prefers technical IDs. Keep the topic ID in state and links.

### Ready lesson card

Use a description equivalent to:

> **Você pode começar por aqui.**
>
> **O que você vai aprender:** <capacidade em linguagem clara>  
> **Tempo sugerido:** <estimativa>
>
> **Recursos**
>
> - **Aula:** <link direto para o módulo>
> - **Prática:** <um único recurso principal disponível agora>
> - **Avaliação:** <link direto para o formulário>
>
> **O que você vai produzir:** <entregável>  
> **Para concluir:** <critério de aplicação e pontuação em linguagem simples>
>
> Quando terminar, envie a avaliação e escreva:  
> **“Terminei <título da aula>. Avalie minhas respostas.”**

Do not append “Este cartão registra execução; somente a avaliação no GitHub estabelece domínio.” Use the friendlier completion sentence above.

Create a checklist named **Sua sessão de estudo** using the three to seven granular actions from the module. The checklist intro may say:

> Siga estas etapas no seu ritmo. Os tempos são sugestões, não limites.

### Future lesson card

Use:

> **Esta etapa vem depois de <pré-requisitos em linguagem simples>.**
>
> **O que você vai aprender:** <objetivo>  
> **Tempo sugerido:** <estimativa>  
> **O que você vai produzir:** <entregável>
>
> A aula completa será preparada automaticamente quando você concluir as etapas anteriores. Você não precisa pedir a geração manualmente.

The future card must stand on its own. Do not link the internal topic contract merely to provide a destination. Link a roadmap only when it genuinely helps the learner understand the wider sequence. Do not attach nonexistent module, rubric, flashcard or assessment links. Do not use `planned`, `materialized`, “janela ativa” or “ordem topológica” in learner copy.

Only dependency-ready lessons enter the ready list. Keep future lessons in the planned list.

### Trello structure

For a rich course, create or reuse one course board with lists equivalent to:

- Planejado;
- Pronto para estudar;
- Em andamento;
- Em avaliação;
- Revisão necessária;
- Concluído.

Use “Revisão necessária” in visible copy instead of “Recuperação” when the latter could sound punitive. Internal state may retain recovery terminology.

### Todoist or GitHub Issues

When another task backend is selected, preserve the same human structure and projection rules. Todoist reminders may be auxiliary only and must point to the primary task or lesson.

## Scheduling

Use the selected scheduling provider only as an aid to reserve time. Future content links only to its current task when a link is useful. Update existing matching schedule resources rather than creating duplicates.

## Formative practice

When Quizlet is selected and connected, create one real set from each approved current-version local deck. Prefer TSV as the structured source and Markdown as the review reference. Store the external ID and URL, then show only **Praticar no Quizlet** as the flashcard-practice link in the current task. Keep local Markdown and TSV files available inside the lesson and repository as durable alternatives.

After every successful create or reuse operation, persist the resource with topic, `content_version`, URL and `status: success` before projecting the link elsewhere. Do not re-evaluate or regenerate the flashcards: the approved TSV and Markdown deck remain the reviewed content.

### Synchronize lesson practice links

After current-version formative resources are durably recorded, run:

`python scripts/sync_practice_links.py`

The script may change only the block delimited by:

- `<!-- open-study-path:practice-links:start -->`
- `<!-- open-study-path:practice-links:end -->`

That block lists the current Quizlet set when one exists and always retains the local Markdown and TSV alternatives. The rest of the lesson must remain byte-for-byte unchanged. Older Quizlet sets whose `content_version` does not match the topic must not be linked.

For legacy lessons without markers, the script may migrate only the link list inside `## Pratique e revise` and add the markers. It must preserve the surrounding explanation and every other section.

Run `python scripts/sync_practice_links.py --check` after synchronization. A current successful Quizlet set missing from its lesson, a stale external link, malformed markers or any further pending change blocks publication success.

When useful decks exist but Quizlet is not connected, render one nonblocking connection suggestion through Plugin Management. Use natural copy:

> Os flashcards já estão disponíveis na aula. Conectar o Quizlet acrescenta um modo interativo de praticar.

Until Quizlet is connected, show **Estudar os flashcards no GitHub** as the task's primary practice link. Do not also show the TSV unless import is the intended action.

Do not ask a separate yes/no question before the control and do not block publication.

If no harmless read operation exists, never create a disposable test set. The first intended set creation is the optional access check. On failure, retain local decks and record a short non-sensitive reason.

When a connector creates but cannot edit:

- reuse an existing exact current-version set;
- create a versioned replacement only after approved content changes;
- mark the prior record as `superseded`;
- update operational links to the newest successful set;
- never claim that an old set was updated when a new one was created.

Natural return command:

`Conectei o Quizlet. Crie meus flashcards.`

Technical alias:

`Conectei o Quizlet ao ChatGPT. Verifique novamente e publique os flashcards dos tópicos materializados.`

Do not publish sets for future topics without complete decks.

## Other integrations

Apply the same projection rule to other capabilities:

- show one current scheduler or task destination, not every calendar fallback;
- show one artifact workspace link when it is the actual place to work;
- show one external diagram only when it adds something beyond the canonical Mermaid view;
- habits support consistency only;
- Airtable is a `github_to_airtable` read model;
- Gmail or Outlook may send only configured summaries;
- course platforms link precise approved lessons or exercises.

Use human labels in visible resources. Keep provider authority, preflight, fallbacks and synchronization terminology in the lesson, integration state and technical plan instead of repeating them in tasks.

## Idempotency and state

Inspect `state/integrations.json` and matching provider resources before writing. Reuse or update exact resources when supported. Store capability, provider, safe ID, URL, topic, content version, authority, sync status and timestamp. Never persist credentials, tokens, OAuth details, raw submissions or unnecessary identity data.

Practice-link synchronization is idempotent. Re-running it with unchanged topic versions and integration state must produce no diff. When a topic version changes, the old external link is removed until a successful resource for the new version is recorded.

## Persist publication completion

The lifecycle may advance to evaluation only after publication state is durably recorded and learner-facing practice links are synchronized.

After the complete required publication set succeeds, all created or reused resources are represented in `state/integrations.json`, and `python scripts/sync_practice_links.py --check` passes:

- set `sync.status` to `success`;
- set `sync.last_success_at` to the current ISO 8601 timestamp;
- clear resolved entries from `sync.errors`;
- retain safe resource IDs and URLs needed for idempotent updates.

A Markdown or GitHub-native task backend still completes the publication phase; record the same successful sync state after its repository-native projection is ready.

When required publication is blocked, failed, partial, still in progress or practice links are out of sync:

- do not set a success status or `last_success_at`;
- persist the accurate non-success status and a short non-sensitive reason;
- do not present an evaluation command;
- return the provider-specific connection or retry command from `instructions/phase-completion.md`.

Run `scripts/lifecycle_next_action.py` against the final persisted state before composing the completion response.

## Completion

After publication, link the first ready lesson, primary task and assessment. Mention an alternative only when the primary resource is unavailable or the learner explicitly asks for it.

Do not lead with a publication report, provider inventory, PR status or CI result. Only after successful publication state is persisted, use:

`Terminei <título da aula>. Avalie minhas respostas.`

Continue accepting `Finalizei o TOPIC-000. Avalie minhas respostas.` as an alias.
