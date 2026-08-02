# Publish tasks and selected integrations

Use the approved roadmap, topic contracts, ready lessons, reviewed slide ZIP packages, integration plan and current state. Publication creates only the external organization that helps the learner act now. It must not regenerate pedagogical content, slide sources or packages.

Read `docs/learner-facing-language.md` and `docs/study-slides.md` before writing task descriptions or the completion response.

The natural command is:

`Organize minha trilha nas ferramentas que escolhemos.`

Continue accepting `Publique as tarefas da trilha nas integrações configuradas.` as an alias.

## Connection preflight

Run `instructions/42-integration-preflight.md` before external writes. Required providers must pass harmless verification. Optional providers are activated only when the learner supplied the information required to create a useful resource now.

Do not advertise, probe or summarize tools merely because they were mentioned in intake. Do not report an inventory of inactive integrations.

## Authority model

GitHub stores approved curriculum, lessons, slide ZIP packages, assessments and verified progress. Exactly one task backend tracks operational execution. Reminders and calendars support routine only; they never establish learning completion.

## Standard assessment labels

Ensure labels exist:

- `assessment`;
- `assessment:submitted`;
- `assessment:graded`;
- `assessment:recovery-required`.

Do not create empty assessment issues during publication.

## Task backend

Create one task per topic in the single selected backend. The task is the learner's concise entry point into the lesson, practice and assessment. It is not an inventory of repository artifacts or integrations.

### One primary resource per capability

For every ready topic, show these learner-facing capabilities in this order:

1. one **Slides** link to the current reviewed ZIP package;
2. one **Aula** link to the complete module;
3. one **Prática** link only when a separate approved exercise or laboratory is useful;
4. one direct **Avaliação** link.

When practice is already contained in the lesson, do not create or link a duplicate deck. Never create flashcard Markdown, TSV exports or Quizlet sets.

Build the slide URL from the exact instance identity and topic contract:

```text
https://github.com/OWNER/REPOSITORY/raw/HEAD/study/slides/TOPIC-000/slides.zip
```

Describe it as an arquivo ZIP and state that the learner extracts it and opens `slides.html` in a browser. Do not show internal source HTML, CSS, JavaScript, metadata, slide reviews, topic contracts, rubric YAML, state files or synchronization records.

### Human card titles

Prefer the learner-facing lesson title without a numeric prefix. Use `Etapa <n> · <título>` only when the course is genuinely linear or the learner explicitly prefers numbering.

### Ready lesson card

Use a description equivalent to:

> **Você pode começar por aqui.**
>
> **O que você vai aprender:** <capacidade em linguagem clara>  
> **Tempo sugerido:** <estimativa>
>
> **Recursos**
>
> - **Slides:** <link para o arquivo ZIP da versão atual> — extraia e abra `slides.html`
> - **Aula:** <link direto para o módulo completo>
> - **Prática:** <somente quando houver um exercício separado útil>
> - **Avaliação:** <link direto para o formulário>
>
> **O que você vai produzir:** <entregável>  
> **Para concluir:** <critério de aplicação e pontuação em linguagem simples>
>
> Quando terminar, envie a avaliação e escreva:  
> **“Terminei <título da aula>. Avalie minhas respostas.”**

Create a checklist named **Sua sessão de estudo** using the three to seven granular actions from the module.

### Future lesson card

Build the copy from direct prerequisites, never numeric adjacency. Explain that the complete lesson and its slide package will be prepared automatically after prerequisites are concluded. Do not link nonexistent modules, ZIP packages, assessments or internal contracts.

### Task backends

For Trello, Todoist, GitHub Issues or another selected backend, preserve the same human structure and projection rules. Use visible states equivalent to Planejado, Pronto para estudar, Em andamento, Em avaliação, Revisão necessária and Concluído when supported.

## Routine activation

Read `integration_preferences.routine` before creating reminders or calendar events.

- `fixed_calendar` uses one approved calendar provider when day, time, duration and timezone are resolved;
- `flexible_reminders` uses Todoist reminders and no duplicate calendar event;
- `none` and `decide_later` activate neither provider;
- missing timing details require one concise question before external writes.

## Email summaries

Email is available only on explicit request. Do not create filters, drafts, schedules or automatic sends merely because Gmail is connected.

## Other integrations

Activate another optional tool only when it has immediate value in the ready content window and the learner must use it now. Never finish with an inventory of inactive or merely connected providers.

## Task projection review

Read every created or updated task back when supported and verify:

- visible title matches the topic;
- objective, effort and deliverable match;
- prerequisite copy contains exactly direct prerequisite titles;
- ready status follows satisfied dependencies;
- resource order is Slides, Aula, optional Prática, Avaliação;
- the Slides resource names the ZIP and `slides.html` opening step;
- links point to current reviewed content;
- no internal artifact or inactive provider is exposed.

Correct mismatches before continuing. Persist direct prerequisite IDs and current content version with the resource.

## Idempotency and state

Inspect `state/integrations.json` and matching provider resources before writing. Reuse or update exact resources when supported. Store only safe identifiers, URLs and synchronization metadata. Never persist credentials, raw submissions or unnecessary identity data.

## Persist publication completion

Advance to evaluation only after the required task projection is durably recorded and its review has no blocking mismatch. On success, update synchronization state and retain safe resource identifiers. On partial or failed publication, persist the accurate state and return the appropriate retry or connection action.

Run `scripts/lifecycle_next_action.py` against final state before composing the response.

## Completion

After publication, answer with what is ready, the primary destination, the first concrete action, the natural evaluation command and at most one attention item that changes the action. Do not lead with a provider inventory, PR status or CI result.
