# Agent Operating Contract

Read this file before changing this repository or an instance derived from it.

## Repository mode

The canonical repository is template mode when `.open-study-path/template.yml` exists and `.open-study-path/instance.yml` does not. It may improve reusable contracts, but must not contain learner-specific state or curriculum.

An instance is valid only when `.open-study-path/instance.yml` exists. Its `repository` field is the persistent identity. Stop writes when it conflicts with the explicit Project repository.

Repository metadata such as reported size, code-search status, search results or an incomplete local checkout is not authoritative evidence that a repository is empty. Before setup writes, read the target repository sentinels directly: `.open-study-path/template.yml`, `.open-study-path/instance.yml`, `AGENTS.md`, `instructions/manifest.yml` and `.github/ISSUE_TEMPLATE/create-study-path.yml`.

A derived instance retains `.open-study-path/template.yml`; the instance marker takes precedence without replacing the inherited template marker. Never delete reusable workflows, validators, schemas, templates, instructions or documentation during normal setup. Apply `instructions/02-setup-execution.md` during the first chat.

A GitHub intake is ready only when the form contains the current intake marker, explains that the course name comes from the issue title and repository labels `study-request` and `intake:imported` exist. Provision missing labels before reporting setup success. Only the current marked intake form is accepted. During import, preserve the issue title as `path.name`, preserve the complete main answer as `path.learning_request`, derive only a concise `path.subject` label and repair the discovery label only after unique resolution. Matching headings alone never prove intake identity.

## Guided lifecycle

Read `instructions/manifest.yml`, `instructions/phase-completion.md`, `instructions/31-topic-first-safe-publication.md` and `docs/learner-facing-language.md` before lifecycle work.

Internal validation, review, correction, safe merge and rolling materialization belong to the active operation. Complete them before responding.

The learner-facing response describes what is ready, where to go and what to do next. Do not lead with PR, CI, hashes, branches, changed files or internal classifications after success. Technical details remain in GitHub and are surfaced only when requested or required to resolve a blocker.

Resolve the next learner command from persisted state with `scripts/lifecycle_next_action.py`. Curriculum generation does not authorize evaluation while publication remains incomplete. A recorded partial publication must return the resume command produced by that resolver and reuse every recorded external resource.

When the agent itself suggested `sem publicar tarefas ainda`, that phrase is a one-operation safety deferral. The agent must restore publication as the next visible action after generation; never treat its own suggestion as a learner decision to skip integrations.

## Independent review framework

Read `docs/review-framework.md` and `instructions/04-review-generated-artifacts.md` for every artifact-producing lifecycle, migration or synchronization operation.

Every generated artifact changed by an instance operation must be covered by an approved review artifact changed in the same pull request. Store durable review evidence under `state/reviews/` using the phase profile declared in `instructions/manifest.yml`.

Authoring and review are separate passes even when the same runtime performs both. The reviewer reconstructs evidence from approved inputs, repository outputs and harmless external read-backs; it does not trust the authoring pass's success claim.

The shared framework uses specialized reviewers for setup, intake, diagnostic, curriculum, publication, assessment, progress, replan and migration. Specialized review remains additive: materialized teaching content requires `instructions/36-review-course-content.md`, study slides require `instructions/37-review-study-slides.md`, and selected integrations require their own resolution and projection checks.

Before merge, the review must record exact SHA-256 fingerprints for every generated artifact in the operation diff, pass every required profile check and contain no blocking findings. Missing review, partial coverage, stale fingerprints or skipped checks block CI, merge and a success response.

## Setup, intake and diagnostic

- Never convert the canonical template into an instance.
- Never request API keys, tokens or passwords.
- Import only an approved intake source.
- Preserve the complete learning request separately from its concise subject label.
- Persist structured summaries, not raw submissions or diagnostic transcripts.
- Treat diagnostic as bounded placement, not teaching.
- Ask one short question at a time.
- For beginner or no prior knowledge, target 3–5 and hard-limit 7 unless comprehensive assessment is explicitly requested.
- Do not recommend or probe providers before diagnostic and curriculum context exist.

## Roadmap and adaptive content

Initial generation creates the complete roadmap, every topic overview and an integration plan. Detailed lessons follow configured content-generation strategy.

A small course may prepare every lesson. A larger course prepares the configured lookahead and automatically creates future lessons as verified progress advances.

Keep internal `planned` and `materialized` values in metadata. In visible copy use “aula futura” and “aula pronta”. Do not expose rolling-window, topological-order or generation-threshold terminology unless technical details are requested.

Read `instructions/31-topic-first-safe-publication.md` before generating or revising a roadmap. `planning.unit: topic` is authoritative. Do not create fixed durations in weeks, week-numbered groups or weekly roadmap tables unless the learner explicitly requests a calendar projection. An optional time constraint may guide priority and feasibility language, but it must not silently remove mastery-required content or redefine partial coverage as completion. Show estimated effort per topic, prerequisites and flexible pace instead.

For beginner paths, explain a technical term in plain language at its first meaningful roadmap occurrence. A requested topic is desired scope, not proof that the learner knows its vocabulary.

A topic number is not a prerequisite rule. The dependency graph and each topic's direct prerequisite list are authoritative. In a branched course, TOPIC-009 may be ready without TOPIC-008. Do not infer adjacency from numbering.

## Granularity and teaching quality

A topic is one coherent independently assessable capability. Use three to seven focused actions, normally 10–25 minutes each, and prefer 45–90 minutes per topic.

Read `docs/beginner-first-pedagogy.md`. Subject level and transferable experience are separate dimensions. Seniority in an adjacent field may make examples and exercises more sophisticated, but it must never remove first principles that the learner declared or demonstrated they do not know.

A topic overview is not a lesson. Every ready module must teach with:

- personal orientation and clear outcome;
- first-principles onboarding when required by level or diagnostic;
- progressive vocabulary and acronym expansion;
- prerequisite retrieval;
- explanatory content and nuance;
- a bounded analogy or labeled concrete example;
- at least two worked examples, normally including a recognizable situation and a domain-relevant case;
- useful Mermaid visual models;
- misconceptions and corrections;
- guided and independent practice;
- active recall;
- deliverable and assessment instructions;
- provenance, inspected sources and useful alternative formats;
- a direct link to the current slide PDF.

A beginner module must explain the object before its mechanism and include `## Começando do zero`, `### Vocabulário desta aula` and `## Intuição antes dos detalhes`. If it uses an analogy, it must say where the analogy helps and where it stops working. A realistic teaching scenario must not be presented as a real event; documented real cases require sources.

Read `docs/content-quality-and-sources.md`. Every ready lesson normally uses three to seven curated sources, including a primary or official source when available and a reliable explanatory source. Add videos, open lectures, podcasts, interactive resources or precise course lessons only when they improve learning. Record purpose, access and a precise locator or timestamp.

Do not cite a plugin response instead of the original source. Do not add uninspected links, invent citations or turn a lesson into a reading list.

## Independent course-content review

Read `instructions/35-review-curriculum.md` and `instructions/36-review-course-content.md` as different roles.

The curriculum reviewer verifies scope, graph, topic contracts and course architecture. The course-content reviewer independently verifies that every materialized lesson, practice and assessment delivers what the contract promised.

For new review-contract instances:

- every topic defines stable `learning_outcomes` and required concepts;
- every materialized lesson contains one hidden outcome marker per approved outcome;
- every rubric question maps to one or more outcome IDs;
- every materialized topic has a current `state/content-reviews/TOPIC-000.yml`;
- a stale review, missing outcome, false prerequisite, learner-navigation mismatch or blocking finding prevents merge;
- CI checks traceability, but the reviewer remains responsible for semantic honesty.

Authoring and review are separate passes even when the same runtime performs both. During review, read repository artifacts as evidence, actively look for contradictions and do not approve because the authoring pass appeared confident.

## Mermaid visual learning

Every roadmap contains the actual topic dependency graph. Every ready module contains the configured minimum number of explained Mermaid diagrams. A diagram supplements prose and practice; it does not replace them.

## Study slides and PDF

Read `docs/study-slides.md` and `instructions/37-review-study-slides.md` whenever a topic is materialized.

After the lesson, practice and assessment pass course-content review:

1. create semantic HTML, CSS and JavaScript under `study/slides/TOPIC-000/` using `templates/study-slides/`;
2. summarize the reviewed lesson without new research or unsupported claims;
3. represent every approved outcome with honest `data-outcome-ids` values;
4. include at least one focused Mermaid diagram rendered as SVG;
5. use no generated raster illustrations or full-slide images under the current contract;
6. run the independent study-slides review and persist it under `state/slide-reviews/`;
7. render and validate `slides.pdf` and `slides.meta.json` before merge.

HTML is build input only. Never link it, its CSS/JavaScript, render metadata or review evidence to the learner. The module and task link only:

`https://github.com/OWNER/REPOSITORY/raw/HEAD/study/slides/TOPIC-000/slides.pdf`

The lesson, slide sources, PDF, metadata and specialized reviews must share the same `content_version` and the same curriculum or materialization PR. A failed render, stale source hash, overflow, Mermaid error, page mismatch or missing PDF blocks merge and publication.

## Capability-based integrations

Read `docs/integration-capabilities.md`, `study.config.yml`, `study/integrations.md` and `state/integrations.json`.

GitHub stores curriculum, lessons, assessments and verified progress. Exactly one task backend tracks execution. Other tools enrich practice, time, reminders, artifacts or analytics.

- Consensus supports empirical research but original sources remain durable citations.
- Quizlet supports useful flashcards; Markdown and TSV remain local alternatives.
- Trello is preferred for rich courses; GitHub Issues is the first fallback, Todoist may be simpler or reminder-only, and repository Markdown is the final internal fallback.
- Reclaim supports adaptive scheduling; Google/Outlook provide fixed blocks.
- Habitify supports consistency only.
- Mermaid remains canonical with any external diagram workspace.
- Drive may store deliverables.
- Airtable remains `github_to_airtable` projection.
- Coursera, edX, Udemy, Khan Academy, YouTube and other media sources must point to precise useful lessons, sections, exercises or timestamps.

When `integration_preferences.account_connections` is `no_external_accounts`, do not suggest, probe or write to apps requiring another account, even when listed under `already_uses`. Use GitHub Issues or repository Markdown, local flashcards, Mermaid, repository artifacts, primary sources, web research and chat.

Optional providers never block the GitHub/Markdown path. Before external writes, run `instructions/42-integration-preflight.md` and `instructions/31-topic-first-safe-publication.md`. Store only safe external identifiers and synchronization metadata.

## Repository execution and review

Read `instructions/32-generation-execution.md` for generation and materialization. Keep every commit within phase scope. Do not modify reusable workflows, validators, instructions, templates or schemas from an instance curriculum operation.

For every operation PR, correct resolvable issues, run specialized review, run the shared independent phase review, validate generated diff coverage and merge under the configured policy when no genuine decision remains. Record technical review state in GitHub.

For every repository phase, inspect required checks for the current unchanged PR head. A failing, pending, cancelled, missing or unreadable required check blocks merge and blocks a success response. Never merge because the diff looks correct while CI is red or unknown.

Do not require a fixed “PR approved and merged” sentence in chat. Link a PR only when a concrete unresolved decision requires owner input or when technical details are requested.

## Publication and task language

Read `instructions/40-publish-tasks.md`, `instructions/42-integration-preflight.md` and `instructions/31-topic-first-safe-publication.md`.

Create one task per topic. By default, use the human lesson title without a numeric prefix. Use `Etapa <n> · <título>` only for a genuinely linear course or an explicit learner preference. Do not organize Trello by week unless the learner explicitly requested an optional calendar projection.

### Human task titles

A ready card says what the learner will do, how long it may take, where the slides, complete lesson, primary practice and assessment are, what to produce and how to finish.

Show resources in exactly this order: **Slides**, **Aula**, **Prática**, **Avaliação**. Use the PDF raw route for Slides. When Quizlet or another external practice resource exists, show it as the single practice link and keep Markdown/TSV alternatives inside the lesson.

A future card begins with **Pré-requisitos desta etapa**, lists exactly the direct prerequisite titles and tells the learner to follow that list rather than card numbering. Never say “todas as etapas anteriores” when the graph branches. Do not attach nonexistent lesson, slide PDF, practice or assessment links.

A task backend is not a repository inventory. Do not link topic contracts, rubric YAML, state files or synchronization records from normal learner tasks. Also do not link slide HTML/CSS/JavaScript, render metadata or review evidence.

Do not repeat “source of truth”, “authority”, `planned`, `materialized`, preflight or synchronization language in every card.

Never create disposable external probe resources. Before the first write, verify that all required operations for the intended board, lists, cards and checklists are exposed. Persist every successful external write before starting the next one. If a write creates an unexpected resource, stop exploratory writes, record it and clean it up when the connector supports safe cleanup.

Natural commands presented to the learner, in lifecycle order:

- `Preenchi o formulário. Pode continuar.`
- `Vamos fazer meu diagnóstico.`
- `Crie minha trilha de estudos.`
- `Organize minha trilha nas ferramentas que escolhemos.`
- `Continue a organização da minha trilha nas ferramentas que escolhemos.`
- `Conectei o Quizlet. Crie meus flashcards.`
- `Terminei <título da aula>. Avalie minhas respostas.`
- `Terminei a revisão de <título da aula>.`

Do not present a later command while an earlier required phase remains incomplete.

## Assessment resolution

Read `instructions/55-evaluate-topic.md`. Resolve submissions using labels, hidden marker, history and title as a consistency signal. Never choose an arbitrary newest issue. Ask for an issue number only when multiple valid candidates remain.

Grade every response independently, calculate 0–100, comment on the issue, persist a versioned attempt and update progress. No external provider sets completion.

When mastered, run `instructions/57-materialize-next-content.md` automatically and return the next ready slide PDF and lesson. Do not foreground the content PR unless it failed or was requested.

When more work is needed, create focused review and targeted reassessment. Use supportive language such as “Revisão necessária”, not punitive copy.

## Safety

Never commit credentials, secrets, raw submissions, original uploaded files, diagnostic transcripts or unnecessary personal data. Prefer pull requests for structural and material changes. Ask before destructive operations.
