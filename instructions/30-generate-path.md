# Generate and approve learning path

Generate a complete dependency-aware roadmap and concise contract for every topic. Materialize detailed teaching content according to the configured content-generation strategy. Generate a contextual integration plan, but do not publish external resources during this phase.

## Planning contract

Always create upfront:

- `study/roadmap.md` with the complete topic graph and estimated schedule;
- one concise contract per topic under `study/topics/` using `templates/topic.md`;
- observable objectives, prerequisites, effort, deliverables, evidence, mastery criteria and precise resources for every topic;
- `study/integrations.md` using `templates/integrations-plan.md`, with recommendations derived from the actual course and learner preferences.

The learner must be able to see the whole path even when future lessons have not yet been materialized.

## Topic and task granularity

A topic is an independently assessable capability, not merely a small task. Prefer more focused topics when a capability can be split without losing conceptual coherence, but do not create a separate topic for every reading or exercise.

Read `content_generation.granularity` from `.open-study-path/instance.yml`. Defaults are:

- three to seven execution actions per topic;
- normally 10–25 minutes per action;
- normally 45–90 minutes per topic;
- split a topic above 120 minutes when it contains separable assessable capabilities.

Every activity must be independently checkable. Do not compress reading, several exercises, a deliverable and assessment into one vague checklist item.

## Content-generation strategy

Read `content_generation` from `.open-study-path/instance.yml`.

For `adaptive_rolling_window`:

1. generate the complete roadmap and every topic contract;
2. when the curriculum contains at most `full_upfront_max_topics` and at most `full_upfront_max_hours`, materialize every topic;
3. otherwise materialize only the first deterministic window of `lookahead_topics` topics;
4. choose the initial window in topological order, beginning with root topics and then topics whose prerequisites are already selected in the same lookahead chain;
5. mark future contracts with `content_status: planned` and do not create their module, rubric or assessment form yet.

For every materialized topic, create:

- one complete lesson under `study/modules/` using `templates/module.md`;
- one scoring rubric under `study/assessments/` using `templates/assessment-rubric.yml`;
- one GitHub Issue Form under `.github/ISSUE_TEMPLATE/assessment-topic-<number>.yml` using `templates/topic-assessment-issue-form.yml`;
- `content_status: materialized`, a positive `content_version` and `materialized_at` in the topic contract;
- a durable flashcard file under `study/flashcards/` when the topic contains enough atomic recall material and formative practice is selected or recommended.

`study/topics/` is the compact contract and index. `study/modules/` contains the content the learner actually studies. A planned topic must never contain broken module links or imply that its detailed lesson already exists.

## Complete-content contract

Every materialized module must be self-contained enough for the configured study time and learner level. It must include:

1. objectives and usage guidance;
2. a granular execution plan;
3. prerequisite retrieval questions;
4. actual explanatory content written in clear language;
5. definitions, relationships, limits and nuances;
6. at least one explained Mermaid visual model;
7. at least two worked examples;
8. common misconceptions and corrections;
9. guided practice with hints;
10. independent practice and the required deliverable;
11. active-recall synthesis;
12. exact assessment-submission instructions;
13. precise references.

Do not generate modules that merely say “read”, “study”, “reflect” or “discuss” without teaching the underlying content.

## Visual learning with Mermaid

Read `content_generation.visual_learning` from `.open-study-path/instance.yml`. When absent, use the template defaults documented in `docs/mermaid-visual-learning.md`.

The roadmap must contain a Mermaid diagram representing the actual topic dependency graph, not a generic lifecycle placeholder.

Every materialized module must contain at least `minimum_diagrams_per_materialized_module` fenced Mermaid diagrams. The default is one. Use more than one when a complex topic contains distinct structures, flows or interactions that benefit from separate views.

Choose a diagram type that matches the subject:

- nontechnical or conceptual topics: decision trees, causal flows, category maps, timelines, state changes and comparison paths;
- programming and software design: flowcharts, sequence diagrams, state diagrams, class diagrams, entity relationships and dependency graphs;
- cloud and infrastructure topics: architecture or data-flow views using flowcharts and subgraphs, plus sequence diagrams when interactions matter;
- processes and procedures: flowcharts, state diagrams and timelines.

A diagram is a teaching artifact, not decoration. Introduce what it represents and explain immediately afterwards what the learner should notice. Keep labels readable, avoid unsupported Mermaid features and raw HTML, and ensure the diagram renders in GitHub Markdown.

Do not use a diagram to replace necessary prose, examples or practice. Use it to make relationships, decisions, sequences, states or architecture easier to understand.

## Contextual integration recommendation

Read `study.config.yml`, `state/intake-summary.json`, `state/diagnostic-summary.json`, the complete roadmap and the initial materialized modules. Follow `docs/integration-capabilities.md` and create `study/integrations.md`.

Do not recommend every available provider. Select only capabilities supported by concrete signals from the course, learner, schedule or desired deliverables. For every recommended or explicitly requested provider, explain:

1. what it is in plain language;
2. why it fits this specific course;
3. how and when it will be used;
4. expected free-tier use and possible limitations;
5. minimum data read or written;
6. what authority it has and does not have;
7. a provider-independent fallback;
8. whether its preflight is required or optional;
9. the decision state: `selected`, `recommended`, `declined` or `unavailable`.

Resolve `auto` choices conservatively into concrete providers in `study.config.yml` only when the intake policy permits recommendation. Respect `already_uses`, `willing_to_connect`, `avoid`, `account_connections`, `experience` and `free_tier_only`. When external accounts are forbidden, use repository-native fallbacks.

Apply these defaults contextually:

- **Consensus:** preferred for empirical claims, scientific topics, psychology, education, health and evidence comparison. It is supporting research, not curriculum authority. For APIs, programming, cloud and standards, prefer official documentation and primary technical sources.
- **Quizlet:** preferred for meaningful sets of terms, definitions, commands, formulas, comparisons, classifications or common errors. Ace Quiz Maker and local Markdown/TSV flashcards are fallbacks. Formative scores never affect mastery.
- **Trello:** preferred task backend for rich or long courses with links, checklists, recovery and roadmap visibility.
- **Todoist:** may replace Trello for a short or simple course, or act only as an auxiliary recurring reminder. When auxiliary, it cannot change the authoritative task state.
- **Reclaim:** preferred when availability varies or focus blocks should be protected and rescheduled. Google Calendar or Outlook Calendar are fixed-schedule fallbacks. Do not require paid capabilities.
- **Habitify:** use only when consistency is a material risk, with at most three default habits. Habit completion never affects mastery.
- **Whimsical:** use for editable, collaborative or spatial external diagrams. Mermaid remains canonical and sufficient.
- **Google Drive:** use when the course needs Docs, Sheets, Slides or external deliverables. GitHub keeps the approved content and assessment result.
- **Airtable:** use only as a `github_to_airtable` analytical projection. It cannot promote mastery or overwrite canonical progress.
- **Coursera, edX, Udemy and Khan Academy:** use as resource discovery. Select precise sections or exercises with objective, time and evidence; never assign an entire course as one vague task. Paid resources require a free or official alternative.

### Optional research probes during generation

When Consensus or another optional research provider is selected and available, perform a harmless read-only probe before using it. If the probe fails, record the provider as unavailable in the integration plan and use primary sources, official documentation and web research. Optional research availability must not block generation.

Every externally discovered claim or resource included in the curriculum must be represented by a precise, reviewable reference in the module. A plugin response alone is not a durable citation.

### Durable flashcard fallback

When flashcards are pedagogically useful, generate `study/flashcards/TOPIC-000.tsv` with columns `Front`, `Back` and `Tags`. Include definitions, distinctions, retrieval prompts and misconception corrections. The file must be useful without Quizlet and importable when the provider is later connected.

## Assessments

Every materialized topic assessment must contain five substantial prompts covering conceptual understanding, analysis, transfer to a new case, misconception correction and independent evidence. The rubric must total 100 points, define `passing_score`, identify critical misconceptions and support focused recovery.

Issue Forms are the durable submission channel. They must include:

- labels `assessment` and `assessment:submitted`;
- the hidden marker `open-study-path:assessment topic_id=TOPIC-000`;
- the standard learner command:

`Finalizei o TOPIC-000. Avalie minhas respostas.`

An explicit issue number is supported only as a disambiguation fallback. Never assume that an arbitrary newest repository issue is the assessment.

Quizlet, Ace Quiz Maker, Habitify, Todoist completion and calendar attendance are optional practice or execution signals. They do not replace the GitHub assessment, rubric and durable evidence history.

## Scope and effort

Make the scope explicit. When the proposed effort cannot satisfy the learner's complete long-term objective, label the result as an introductory cycle rather than implying comprehensive mastery.

Distinguish active study time from elapsed time required for real-world practice. Weekly dates are projections, not structural curriculum units.

## Resources

Prefer primary or official resources. Every required resource must name a specific work and canonical locator such as section, chapter, book or letter number. Edition, translation and URL selection may remain pending when clearly identified.

For external course catalogs, identify the exact course, section, lesson or exercise. Mark whether access is public, requires an existing account or may be paid. A potentially paid resource must have a free or official alternative.

## Pull request and automatic review

Open a draft pull request. The initial-generation diff may include:

- `.open-study-path/instance.yml`;
- `study.config.yml` when resolving permitted `auto` capability choices;
- `study/roadmap.md`;
- `study/integrations.md`;
- `study/topics/`;
- modules, optional flashcard files, rubrics and Issue Forms only for topics selected by the configured initial window.

Set `status.curriculum_proposed: true` and keep `status.curriculum_approved: false` while drafting.

Before completing this phase, automatically execute `instructions/35-review-curriculum.md`. Correct every issue that can be resolved from approved intake, diagnostic evidence and repository contracts.

For `workflow.curriculum_merge_policy: agent_review_then_merge`:

1. review and correct the proposal branch;
2. run all required checks;
3. self-review the final diff, rolling-window selection, Mermaid rendering, references and integration recommendations;
4. set `status.curriculum_approved: true` only when review passes;
5. rerun checks;
6. mark the draft ready;
7. merge when no pedagogical or integration-policy decision remains unresolved.

Do not attempt to formally approve a pull request authored by the same account. Contract verification, final diff review and successful CI constitute operational review.

## Review status in chat

After successful review and merge, use:

`Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`

When owner input is genuinely required, add concrete annotations to the PR and use:

`Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

Do not ask the owner to review the entire PR when no unresolved decision exists.

## Completion

Do not create cards, tasks, calendar events, habits, flashcard sets, external diagrams, Drive artifacts, Airtable rows or notifications during generation. Complete the phase using `instructions/phase-completion.md`, link `study/integrations.md`, and guide to:

`Publique as tarefas da trilha nas integrações configuradas.`
