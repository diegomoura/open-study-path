# Agent Operating Contract

Read this file before changing this repository or any repository derived from it.

## Repository mode

The canonical repository is in template mode when `.open-study-path/template.yml` exists and `.open-study-path/instance.yml` does not. Template mode may improve reusable instructions, schemas, validators and templates, but must never create learner-specific state, curriculum or external resources.

A derived repository is in instance mode only when `.open-study-path/instance.yml` exists. Its `repository` field is the persistent source of truth. Stop writes when it conflicts with the explicit Project repository.

## Guided lifecycle

Read `instructions/manifest.yml` and `instructions/phase-completion.md` before every lifecycle operation. Internal validation, review, correction, safe merge and configured rolling-window materialization belong to the active operation and must finish before responding.

At a phase boundary, return a brief result, primary links, PR review status, material attention items, next action and one exact command.

## Setup, intake and diagnostic

- Never turn the canonical template into an instance.
- Never request API keys, tokens or passwords.
- Import only an explicitly approved intake reference.
- Treat diagnosis as bounded placement, not teaching.
- Ask one short diagnostic question at a time.
- For `none` or `beginner`, target 3–5 and hard-limit 7 questions unless comprehensive assessment is explicitly requested.
- For `intermediate` or `advanced`, target 4–7 and hard-limit 10.
- Persist structured summaries, not raw transcripts.

## Complete roadmap and adaptive content generation

Initial generation always creates:

- the complete dependency graph in `study/roadmap.md`;
- one concise approved contract for every topic in `study/topics/`;
- objectives, prerequisites, effort, deliverables, evidence, mastery criteria and precise resources for the entire path.

Read `content_generation` from `.open-study-path/instance.yml`.

The default `adaptive_rolling_window` strategy behaves as follows:

- a curriculum within both `full_upfront_max_topics` and `full_upfront_max_hours` may materialize every topic immediately;
- a larger curriculum materializes only `lookahead_topics` in deterministic topological order;
- future topic contracts remain `content_status: planned` until they enter the active window;
- planned topics must not contain broken links or imply that detailed content exists.

For every materialized topic, create a complete module, 100-point rubric and discoverable assessment Issue Form. Set `content_status: materialized`, increment `content_version` and record `materialized_at`.

## Granularity

A topic is one coherent independently assessable capability. It is not merely a reading or an administrative task.

Use configured granularity defaults:

- three to seven focused actions per topic;
- normally 10–25 minutes per action;
- normally 45–90 minutes per topic;
- split a topic above 120 minutes when it contains separable assessable capabilities.

Prefer small independently checkable tasks, but do not inflate the number of topics by turning every exercise into a separate assessment.

A topic contract is not the lesson. Every materialized module must teach with explanatory content, prerequisite retrieval, a granular execution plan, at least two worked examples, misconceptions, guided practice, independent practice, active recall, deliverable instructions and precise references.

## Mermaid visual learning

Read `content_generation.visual_learning` and `docs/mermaid-visual-learning.md`.

- Every generated roadmap must contain a Mermaid diagram of the actual topic dependency graph.
- Every materialized module must contain at least the configured minimum number of useful Mermaid diagrams; the default is one.
- Introduce each diagram and explain afterwards what the learner should notice and what the model omits.
- Use conceptual maps, decision trees, causal flows, timelines and state changes for nontechnical subjects.
- Use architecture, dependency, sequence, state, class and data-flow views for programming, AWS and other technical subjects.
- Prefer multiple focused diagrams for complex topics rather than one crowded diagram.
- Ensure Mermaid syntax renders in GitHub. Avoid raw HTML, unsupported features, decorative diagrams and generic diagrams unrelated to the topic.
- A diagram supplements prose, examples and practice; it never replaces them.

## Curriculum review and merge

Read `instructions/30-generate-path.md`, `instructions/35-review-curriculum.md` and `workflow.curriculum_merge_policy`.

Create curriculum and materialization PRs as drafts. Correct every resolvable issue, run required checks, self-review the final diff and merge under `agent_review_then_merge` when no pedagogical decision remains.

Do not formally approve a PR authored by the same account. CI, contract checks and final diff review constitute operational review.

Use one status:

- `Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`
- `Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

Never ask for a generic second review command when no unresolved decision exists.

## Publication and integrations

Read `instructions/40-publish-tasks.md` and `instructions/42-integration-preflight.md` before external writes.

Initial publication is atomic across configured required providers. Verify each connection with a harmless read-only operation. If a required probe fails, create no partial initial publication unless partial publication was explicitly requested.

Create one task per topic:

- materialized topics receive module, topic and assessment links plus the granular module checklist;
- planned topics receive objective, prerequisites, topic-contract link and a clear future-materialization state;
- never attach nonexistent module or assessment links;
- only dependency-ready materialized topics enter `Pronto para estudar`.

Trello is the execution index, not the course-content repository. Reuse exact matching cards, events and state identifiers.

Ensure assessment labels exist: `assessment`, `assessment:submitted`, `assessment:graded`, `assessment:recovery-required`.

After publication, use:

`Ao concluir o TOPIC-000 e enviar o formulário, escreva: "Finalizei o TOPIC-000. Avalie minhas respostas."`

## Deterministic assessment resolution

Read `instructions/55-evaluate-topic.md`.

The standard command requires a topic ID but not an issue number:

`Finalizei o TOPIC-000. Avalie minhas respostas.`

Resolve the assessment using all of these signals:

- labels `assessment` and `assessment:submitted`;
- title prefix `[Avaliação] TOPIC-000`;
- hidden body marker `open-study-path:assessment topic_id=TOPIC-000`;
- absence from prior recorded attempts;
- absence of `assessment:graded`;
- creation after the previous attempt when applicable.

Evaluate automatically when exactly one candidate remains. Provide the form link when none remains. Ask for a specific issue only when multiple valid candidates remain. Never select an arbitrary newest issue.

Grade every response independently, calculate 0–100, comment on the resolved issue, persist a versioned attempt and update progress. Mastery requires passing score, usable evidence and no unresolved critical misconception.

## Automatic next-content materialization

After mastery, execute `instructions/57-materialize-next-content.md` inside the same evaluation operation.

- Restore the configured lookahead window without another learner command.
- Select eligible planned topics in deterministic topological order.
- Use the roadmap, topic contract, intake, diagnosis and verified assessment evidence.
- Use prior modules as consistency references, not as the sole template.
- Adapt examples, emphasis, prerequisite retrieval, visual models and practice difficulty when evidence supports it.
- Never silently rewrite approved objectives, prerequisites, deliverables, effort or mastery criteria; structural changes belong to replan.
- Create a small draft PR limited to selected topics, their modules/rubrics/forms and roadmap materialization status.
- Review, validate and safely merge before returning the next ready module.
- Probe connectors and update existing task cards and event descriptions after repository merge. Missing connectors may defer synchronization but must not undo repository materialization.

When mastery fails, create focused recovery and targeted reassessment. Ace Quiz Maker and chat quizzes may supplement practice but never replace durable GitHub evidence and rubrics.

## Source of truth

1. `.open-study-path/instance.yml`: repository identity, workflow and generation strategy.
2. `study.config.yml`: learner and integration preferences.
3. `instructions/manifest.yml`: phase contracts.
4. `state/diagnostic-summary.json`: placement evidence.
5. `study/roadmap.md`: complete approved graph, Mermaid dependency view and materialization overview.
6. `study/topics/`: complete topic contracts.
7. `study/modules/`: materialized teaching content and visual models.
8. `study/assessments/` and Issue Forms: materialized assessments.
9. `state/assessments/`: evaluated attempts.
10. `state/progress.json`: verified progress.

## Safety

Never commit credentials, secrets, raw submissions, diagnostic transcripts or unnecessary personal data. Prefer pull requests for structural and material changes. Ask before destructive operations.
