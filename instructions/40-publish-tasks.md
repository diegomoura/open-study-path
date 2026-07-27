# Publish tasks and selected integrations

Use the approved `study/integrations.md`, configured capability providers and fallbacks only after the roadmap, topic contracts and initial content window have been validated, approved and merged.

## Approved curriculum invariant

Treat the approved roadmap, integration plan, topic contracts and every existing module, flashcard file, rubric and assessment form as immutable inputs during publication. Publication may create external representations, resolve permitted provider fallbacks and update integration state, but it must not change pedagogical content.

The standard command is:

`Publique as tarefas da trilha nas integrações configuradas.`

The command authorizes publication through providers already selected in the approved integration plan. It does not authorize installing unknown apps, requiring a paid plan or enabling capabilities marked declined. A learner click on a course-specific connection suggestion plus the normal app permission flow may select a previously recommended optional provider for its documented capability.

## Connection preflight

Before external writes, execute `instructions/42-integration-preflight.md`. Classify connections by capability rather than testing every known app.

- Required selected providers must pass harmless read-only probes before the atomic required publication set begins.
- Optional providers use harmless probes when available; missing access may trigger one nonblocking Plugin Management connection suggestion, then the documented fallback continues.
- Disabled, declined, forbidden or irrelevant providers are not probed or suggested.

When every required probe passes, continue without another confirmation. Do not wait for a click on an optional connection suggestion before completing work that can use the fallback.

## Authority model

GitHub is the only source of truth for curriculum, content, assessment, mastery and verified progress.

Exactly one task backend is authoritative for execution state. Other task-like tools may be auxiliary reminders only.

The following never establish mastery:

- checklist completion;
- Todoist reminder completion;
- calendar attendance;
- Habitify streaks;
- Quizlet or Ace Quiz Maker scores;
- Whimsical edits;
- Airtable values;
- completion markers from external course platforms.

## Standard GitHub assessment labels

Ensure these repository labels exist before the learner submits assessment forms:

- `assessment`;
- `assessment:submitted`;
- `assessment:graded`;
- `assessment:recovery-required`.

Assessment Issue Forms are created only for materialized topics. Do not create empty assessment issues during publication.

## Authoritative task backend

Create one task or card per topic so the learner can see the complete roadmap. Use the single provider selected in `integrations.task_manager.provider`.

### Trello

Prefer Trello for rich or long courses. Create or reuse one course board with lists equivalent to `Planejado`, `Pronto para estudar`, `Em andamento`, `Em avaliação`, `Recuperação` and `Concluído`.

### Todoist

When Todoist is the authoritative backend, create or reuse one project and represent topic states using supported sections, labels or task metadata. Include direct repository links. Do not attempt to reproduce Trello-specific visual structures when the provider does not support them.

### GitHub Issues or Markdown

Use GitHub Issues when explicitly selected as the task backend, while keeping assessment issues distinguishable by their labels and markers. Use repository Markdown when no external task service is desired.

### Materialized topic

A materialized topic task must include:

- objective, prerequisites and estimated effort;
- direct link to the complete module;
- direct link to the topic contract;
- direct link to the assessment Issue Form;
- deliverable and mastery threshold;
- the command `Finalizei o TOPIC-000. Avalie minhas respostas.`;
- granular checklist items derived from the module execution plan;
- flashcard link when a local or external formative set exists.

Create separate checklist items for focused actions. Do not compress several distinct activities into one vague line. The task backend is the execution index, not the content repository.

### Planned topic

A planned topic task must include:

- objective, prerequisites and estimated effort;
- direct link to the topic contract;
- expected deliverable and mastery criteria;
- a clear statement that the complete module and assessment will be materialized automatically when the topic enters the active rolling window.

Do not add nonexistent module, rubric, flashcard or assessment-form links. Use a short planning checklist rather than pretending the full lesson is ready.

Put only dependency-ready materialized topics in the provider's ready state. Keep planned topics and blocked materialized topics in the planned state.

## Auxiliary Todoist reminders

When `integrations.reminders.provider: todoist` and Todoist is not the authoritative task backend, create only reminders or recurring review actions. Every reminder must link to the authoritative task, module or flashcard set.

Persist `authority: reminder_only`. Completing an auxiliary Todoist item must not move the authoritative task, complete a topic or modify verified progress.

## Scheduling

Use the selected scheduling provider:

- `reclaim`: create or synchronize adaptive focus tasks or blocks within capabilities actually available to the connected account;
- `google_calendar` or `outlook_calendar`: create fixed focus events with reminders;
- `none`: publish no schedule.

Respect `integration_preferences.free_tier_only` and `integrations.calendar.free_tier_only`. Do not require paid scheduling capabilities. When Reclaim is unavailable or lacks a needed free capability, use the approved calendar fallback or continue without external scheduling.

Calendar may show the complete schedule projection. For a planned topic, link only its authoritative task and topic contract. When the topic is later materialized, update the existing schedule resource rather than creating a duplicate.

## Formative practice

When Quizlet is selected and connected, create one real topic flashcard set from each approved current-version deck under `study/flashcards/`. Prefer the local TSV as structured source and use the Markdown deck as a human-review reference. Store the returned external set identifier and URL, then add the current external link to the authoritative topic task while preserving both local links.

When Quizlet is recommended or selected, useful local decks exist and access is missing, use Plugin Management as defined in `instructions/42-integration-preflight.md` to render one nonblocking Quizlet connection suggestion. Do not ask a separate yes/no question first. Continue publication with the local Markdown/TSV fallback whether or not the learner clicks the suggestion.

If the Quizlet connector does not expose a harmless read operation, do not create a disposable test set. The first intended topic-set creation is the access check after required publication can safely proceed. On failure, record a short `not_connected` or `unavailable` reason and keep the fallback.

Some Quizlet integrations can create new sets but cannot modify an existing set. In that case:

- reuse an existing current-version set only when its exact identifier is already recorded and usable;
- when approved flashcard content changes, create a versioned replacement such as `TOPIC-001 — <título> — v2`;
- mark the prior resource record as superseded instead of deleting history;
- update the operational task link to the newest successful set;
- never claim an old set was updated when a new one was created.

When Quizlet remains unavailable, retain and link the local Markdown/TSV fallback. Ace Quiz Maker may provide an interactive quiz in chat, but it is not required for publication and has no mastery authority.

Do not create flashcard sets for topics without useful atomic recall material merely to satisfy an integration. Do not publish sets for planned topics whose complete flashcard deck does not yet exist.

After a learner connects Quizlet following a fallback publication, accept:

`Conectei o Quizlet ao ChatGPT. Verifique novamente e publique os flashcards dos tópicos materializados.`

Re-run access verification, inspect state for existing exact resources, create only missing current-version sets and update derived task links without republishing unrelated resources.

## Habit tracking

When Habitify is selected and connected, create or reuse at most the configured maximum number of course habits, normally:

- study session;
- active recall;
- spaced review.

Persist `authority: consistency_only`. A habit event never changes topic, task, assessment or mastery state.

## External visual workspace

Mermaid remains canonical. When Whimsical or another approved external visual provider is selected, create external diagrams only when the integration plan identifies a concrete collaborative, editable or spatial use.

Link the corresponding canonical Mermaid module or roadmap and record `content_version`. An external diagram may not be the only representation necessary to understand the lesson.

## Artifact workspace

When Google Drive or another artifact workspace is selected, create only the folders, documents, sheets or presentations required by explicit course deliverables. Link each artifact from the topic task or assessment instructions.

External artifacts provide evidence; they do not replace the approved module or assessment result. Store safe file identifiers and URLs, never credentials or unnecessary personal data.

## Airtable analytical projection

When Airtable is selected, create or reuse an analytical base with the minimum useful tables among Courses, Topics, Attempts, Study Sessions and Integrations.

Synchronization is unidirectional: `github_to_airtable`. Populate rows from approved repository state and include source repository, source path or issue, content version and last synchronization time.

Airtable must never:

- promote a topic to mastered;
- overwrite scores or assessment attempts;
- rewrite the roadmap or module;
- become a required dependency for study;
- act as a second task backend.

If Airtable is unavailable, continue using repository state without blocking publication.

## Course-discovery providers

Coursera, edX, Udemy and Khan Academy are resource providers, not state backends. Publication links only the precise approved course sections, lessons or exercises already selected in the curriculum.

Include purpose, active effort, access condition and required evidence. Potentially paid resources require the approved free or official alternative.

## Notifications

When Gmail or Outlook email is selected and connected, send or draft only the configured publication summary. Link the first ready materialized topic, authoritative task, assessment form and roadmap. Chat remains the fallback.

## Idempotency and state

Inspect `state/integrations.json` and exact matching provider resources before every write. Reuse or update resources when the provider supports it; otherwise create versioned replacements only for changed approved content.

Every resource record must include:

- `capability`;
- `provider`;
- `external_type`;
- safe `external_id`;
- `external_url` when available;
- `topic_id` when applicable;
- `content_version`;
- `authority`;
- `sync_status`;
- `last_sync_at`.

For optional connection offers, also persist non-sensitive fields equivalent to `connection_offer_status`, `connection_offer_at` and `connection_reason` when publication state is being updated.

Update `selected_capabilities` with the actual provider or fallback used. Never persist tokens, passwords, OAuth details, raw submissions or unnecessary identity data.

## Completion

Link the integration plan, first complete module, authoritative task and assessment form. Summarize which optional providers used fallbacks without framing them as failures of the course. A displayed optional connection suggestion does not change the successful result.

Do not start an improvised lesson in chat by default. Use:

`Ao concluir o TOPIC-000 e enviar o formulário, escreva: "Finalizei o TOPIC-000. Avalie minhas respostas."`