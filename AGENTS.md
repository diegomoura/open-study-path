# Agent Operating Contract

Read this file before changing this repository or an instance derived from it.

## Repository mode

The canonical repository is template mode when `.open-study-path/template.yml` exists and `.open-study-path/instance.yml` does not. It may improve reusable contracts, but must not contain learner-specific state or curriculum.

An instance is valid only when `.open-study-path/instance.yml` exists. Its `repository` field is the persistent identity. Stop writes when it conflicts with the explicit Project repository.

## Guided lifecycle

Read `instructions/manifest.yml`, `instructions/phase-completion.md` and `docs/learner-facing-language.md` before lifecycle work.

Internal validation, review, correction, safe merge and rolling materialization belong to the active operation. Complete them before responding.

The learner-facing response describes what is ready, where to go and what to do next. Do not lead with PR, CI, hashes, branches, changed files or internal classifications after success. Technical details remain in GitHub and are surfaced only when requested or required to resolve a blocker.

## Setup, intake and diagnostic

- Never convert the canonical template into an instance.
- Never request API keys, tokens or passwords.
- Import only an approved intake source.
- Persist structured summaries, not raw submissions or diagnostic transcripts.
- Treat diagnostic as bounded placement, not teaching.
- Ask one short question at a time.
- For beginner or no prior knowledge, target 3–5 and hard-limit 7 unless comprehensive assessment is explicitly requested.
- Do not recommend or probe providers before diagnostic and curriculum context exist.

## Roadmap and adaptive content

Initial generation creates the complete roadmap, every topic overview and an integration plan. Detailed lessons follow configured content-generation strategy.

A small course may prepare every lesson. A larger course prepares the configured lookahead and automatically creates future lessons as verified progress advances.

Keep internal `planned` and `materialized` values in metadata. In visible copy use “aula futura” and “aula pronta”. Do not expose rolling-window, topological-order or generation-threshold terminology unless technical details are requested.

## Granularity and teaching quality

A topic is one coherent independently assessable capability. Use three to seven focused actions, normally 10–25 minutes each, and prefer 45–90 minutes per topic.

A topic overview is not a lesson. Every ready module must teach with:

- personal orientation and clear outcome;
- prerequisite retrieval;
- explanatory content and nuance;
- at least two worked examples;
- useful Mermaid visual models;
- misconceptions and corrections;
- guided and independent practice;
- active recall;
- deliverable and assessment instructions;
- provenance, inspected sources and useful alternative formats.

Read `docs/content-quality-and-sources.md`. Every ready lesson normally uses three to seven curated sources, including a primary or official source when available and a reliable explanatory source. Add videos, open lectures, podcasts, interactive resources or precise course lessons only when they improve learning. Record purpose, access and a precise locator or timestamp.

Do not cite a plugin response instead of the original source. Do not add uninspected links, invent citations or turn a lesson into a reading list.

## Mermaid visual learning

Every roadmap contains the actual topic dependency graph. Every ready module contains the configured minimum number of explained Mermaid diagrams. A diagram supplements prose and practice; it does not replace them.

## Capability-based integrations

Read `docs/integration-capabilities.md`, `study.config.yml`, `study/integrations.md` and `state/integrations.json`.

GitHub stores curriculum, lessons, assessments and verified progress. Exactly one task backend tracks execution. Other tools enrich practice, time, reminders, artifacts or analytics.

- Consensus supports empirical research but original sources remain durable citations.
- Quizlet supports useful flashcards; Markdown and TSV remain local alternatives.
- Trello is preferred for rich courses; Todoist may be simpler or reminder-only.
- Reclaim supports adaptive scheduling; Google/Outlook provide fixed blocks.
- Habitify supports consistency only.
- Mermaid remains canonical with any external diagram workspace.
- Drive may store deliverables.
- Airtable remains a `github_to_airtable` projection.
- Coursera, edX, Udemy, Khan Academy, YouTube and other media sources must point to precise useful lessons, sections, exercises or timestamps.

Optional providers never block the GitHub/Markdown path. Before external writes, run `instructions/42-integration-preflight.md`. Store only safe external identifiers and synchronization metadata.

## Repository execution and review

Read `instructions/32-generation-execution.md` for generation and materialization. Keep every commit within phase scope. Do not modify reusable workflows, validators, instructions, templates or schemas from an instance curriculum operation.

Create curriculum PRs as drafts, correct resolvable issues, run checks, self-review and merge under the configured policy when no genuine decision remains. Record technical review state in GitHub.

Do not require a fixed “PR approved and merged” sentence in chat. Link a PR only when a concrete unresolved decision requires owner input or when technical details are requested.

## Publication and task language

Read `instructions/40-publish-tasks.md` and `instructions/42-integration-preflight.md`.

Create one task per topic. Use human titles such as `1. Agência sem garantia`, not `[TOPIC-001]`, unless technical IDs were requested.

A ready card says what the learner will do, how long it may take, where the lesson and practice are, what to produce and how to finish. A future card says that the lesson will be prepared automatically after prerequisites.

Do not repeat “source of truth”, “authority”, `planned`, `materialized`, preflight or synchronization language in every card.

Natural commands presented to the learner:

- `Preenchi o formulário. Pode continuar.`
- `Vamos fazer meu diagnóstico.`
- `Crie minha trilha de estudos.`
- `Organize minha trilha nas ferramentas que escolhemos.`
- `Conectei o Quizlet. Crie meus flashcards.`
- `Terminei <título da aula>. Avalie minhas respostas.`
- `Terminei a revisão de <título da aula>.`

Continue accepting existing topic-ID and technical commands as aliases.

## Assessment resolution

Read `instructions/55-evaluate-topic.md`. Resolve submissions using labels, hidden marker, history and title as a consistency signal. Never choose an arbitrary newest issue. Ask for an issue number only when multiple valid candidates remain.

Grade every response independently, calculate 0–100, comment on the issue, persist a versioned attempt and update progress. No external provider sets completion.

When mastered, run `instructions/57-materialize-next-content.md` automatically and return the next ready lesson. Do not foreground the content PR unless it failed or was requested.

When more work is needed, create focused review and targeted reassessment. Use supportive language such as “Revisão necessária”, not punitive copy.

## Safety

Never commit credentials, secrets, raw submissions, original uploaded files, diagnostic transcripts or unnecessary personal data. Prefer pull requests for structural and material changes. Ask before destructive operations.
