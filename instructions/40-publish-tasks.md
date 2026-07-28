# Publish tasks and selected integrations

Use the approved roadmap, topic contracts, ready lessons, integration plan and current state. Publication creates execution and practice projections; it must not rewrite pedagogical content.

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

Create one task per topic in the single selected backend. The task is a clear index into the lesson, practice and assessment.

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
> **Aula:** <link direto>  
> **Pratique:** <Markdown>, <Quizlet quando real>, <TSV para importação>  
> **Avaliação:** <link direto>
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

Link only the topic overview or contract. Do not attach nonexistent module, rubric, flashcard or assessment links. Do not use `planned`, `materialized`, “janela ativa” or “ordem topológica” in learner copy.

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

When another task backend is selected, preserve the same human structure and links. Todoist reminders may be auxiliary only and must point to the primary task or lesson.

## Scheduling

Use the selected scheduling provider only as an aid to reserve time. Planned content links only to its current task or overview. Update existing matching schedule resources rather than creating duplicates.

## Formative practice

When Quizlet is selected and connected, create one real set from each approved current-version local deck. Prefer TSV as the structured source and Markdown as the review reference. Store the external ID and URL, then add **Praticar no Quizlet** to the current task while preserving local links.

When useful decks exist but Quizlet is not connected, render one nonblocking connection suggestion through Plugin Management. Use natural copy:

> Os flashcards já estão disponíveis no GitHub. Conectar o Quizlet acrescenta um modo interativo de praticar.

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

- habits support consistency only;
- external diagrams complement Mermaid;
- Drive or another workspace may hold deliverables;
- Airtable is a `github_to_airtable` read model;
- Gmail or Outlook may send only configured summaries;
- course platforms link precise approved lessons or exercises.

Use human labels in visible resources. Keep provider authority, preflight and synchronization terminology in `state/integrations.json` and technical plan details.

## Idempotency and state

Inspect `state/integrations.json` and matching provider resources before writing. Reuse or update exact resources when supported. Store capability, provider, safe ID, URL, topic, content version, authority, sync status and timestamp. Never persist credentials, tokens, OAuth details, raw submissions or unnecessary identity data.

## Completion

After publication, link the first ready lesson, primary task and assessment. Mention an optional alternative only when it changes what the learner can use now.

Do not lead with a publication report, provider inventory, PR status or CI result. Use:

`Terminei <título da aula>. Avalie minhas respostas.`

Continue accepting `Finalizei o TOPIC-000. Avalie minhas respostas.` as an alias.
