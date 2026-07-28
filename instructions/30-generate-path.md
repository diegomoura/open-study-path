# Generate and approve learning path

Generate a complete dependency-aware roadmap and concise contract for every topic. Materialize detailed teaching content according to the configured strategy. Generate a contextual integration plan, but do not publish external resources during this phase.

Read before generating:

- `docs/learner-facing-language.md`;
- `docs/content-quality-and-sources.md`;
- `docs/mermaid-visual-learning.md`;
- `docs/integration-capabilities.md`.

## Planning contract

Always create upfront:

- `study/roadmap.md` with the complete topic graph and estimated schedule;
- one concise contract per topic under `study/topics/` using `templates/topic.md`;
- observable objectives, prerequisites, effort, deliverables, evidence, completion criteria and precise resources;
- `study/integrations.md` using `templates/integrations-plan.md`.

The learner must be able to understand the whole path without reading workflow terminology. In learner-facing prose, translate `materialized` to “aula pronta” and `planned` to “aula futura”. Keep internal values in frontmatter and state files.

## Personalization

Use intake and diagnostic evidence to personalize:

- why each topic matters;
- examples and scenarios;
- difficulty and prerequisite retrieval;
- preferred formats and accessibility;
- practice balance;
- source and media selection;
- next-step language.

Do not manufacture intimacy or expose unnecessary personal data. A personalized sentence must be traceable to an approved learner goal, preference or diagnostic observation.

## Topic and task granularity

A topic is an independently assessable capability, not a reading or administrative action. Use three to seven focused actions, normally 10–25 minutes each. Prefer topics around 45–90 minutes and split above 120 minutes when responsibly separable.

## Content-generation strategy

For `adaptive_rolling_window`:

1. generate the complete roadmap and every topic contract;
2. generate all detailed content only when the curriculum is within both configured full-upfront thresholds;
3. otherwise materialize only the first deterministic lookahead window;
4. choose it in topological order;
5. keep future contracts `content_status: planned` without broken module, rubric or form links.

For every materialized topic, create:

- a complete module under `study/modules/`;
- a 100-point rubric under `study/assessments/`;
- a GitHub Issue Form under `.github/ISSUE_TEMPLATE/`;
- paired Markdown and TSV flashcards when useful;
- positive content version and materialization date.

## Complete-content contract

Every ready lesson must be self-contained for the configured time and level. It must include:

1. a personal orientation and clear outcome;
2. a granular study session;
3. prerequisite retrieval;
4. actual explanatory content;
5. definitions, relationships, limits and nuance;
6. at least one explained Mermaid model;
7. at least two worked examples;
8. common errors and corrections;
9. guided practice with hints;
10. independent practice and deliverable;
11. active-recall synthesis;
12. direct assessment action;
13. **How this content was built** provenance;
14. **Other ways to learn** when useful;
15. **Sources and paths to deepen** with verified links and locators.

Reject modules that merely instruct the learner to read, study, watch, reflect or discuss without teaching the underlying content.

## Source and provenance contract

For every materialized module:

- inspect every source before including it;
- use three to seven curated sources by default;
- include at least one primary or official source when one exists;
- include at least one reliable explanatory source;
- include a complementary format such as video, open lecture, podcast, interactive demonstration or precise course lesson when it adds real pedagogical value and is available;
- explain how each source was used;
- record chapter, section, page, DOI, version, lesson, exercise or timestamp;
- distinguish sourced claims from agent-created diagrams, examples and exercises;
- do not cite a plugin response instead of the original document;
- provide a free or official alternative for potentially paid resources;
- keep the lesson understandable without opening external links.

For empirical, scientific, medical, legal, financial, product or current claims, verify current authoritative sources. For technical subjects, prefer official documentation, standards and primary repositories. For books, papers, TCCs and dissertations, describe their evidential role accurately rather than treating every publication as consensus.

## Videos and courses

Use videos when they provide a useful alternative explanation or demonstration. Include title, creator or institution, direct link, duration or recommended timestamp, language/legends when relevant and one active task.

Use Coursera, edX, Udemy, Khan Academy or other catalogs only at the exact section, lesson or exercise level. Include purpose, effort, access condition and evidence. Never assign an entire course as one vague task.

## Visual learning with Mermaid

The roadmap must show the actual topic dependency graph. Every materialized module contains at least the configured number of explained Mermaid diagrams. A diagram is a teaching artifact, not decoration. Use multiple focused diagrams when one would mix distinct structures or flows.

## Contextual integration recommendation

Recommend only capabilities supported by concrete course signals. Explain them in learner language in the visible part of `study/integrations.md`; keep preflight, authority and state classifications inside its technical details section and `state/integrations.json`.

Apply contextual defaults:

- Consensus supports empirical research but never replaces original citations;
- Quizlet supports meaningful atomic recall and always has Markdown/TSV fallback;
- Trello is preferred for rich courses; Todoist may be simpler or reminder-only;
- Reclaim supports adaptive scheduling; Google/Outlook provide fixed blocks;
- Habitify supports consistency only;
- Mermaid remains canonical even with an external visual workspace;
- Google Drive may hold deliverables;
- Airtable remains a `github_to_airtable` projection;
- course and media platforms are resource discovery, not progress authority.

### Optional research probes

Use harmless reads when a selected research provider supports them. If unavailable, continue with primary sources, official documentation and web research. Every externally discovered claim or resource included in a lesson must have a durable original reference.

### Durable and usable flashcards

When useful, generate:

- `study/flashcards/TOPIC-000.md` with expandable `<details>` cards;
- `study/flashcards/TOPIC-000.tsv` with `Front`, `Back` and `Tags`.

Link the Markdown deck first, the TSV second and the external set only after it exists in integration state.

## Assessments

Each assessment contains five substantial prompts covering understanding, analysis, transfer, misconception correction and evidence. Issue Forms include labels, hidden topic marker and complete prefilled title.

Use a natural learner command in visible copy:

`Terminei <título da aula>. Avalie minhas respostas.`

Continue accepting:

`Finalizei o TOPIC-000. Avalie minhas respostas.`

The module contains the direct clickable Issue Form URL. Never expose only the YAML filename. Deterministic resolution relies on labels, hidden marker and history; the editable title is a useful signal, not the sole authority.

## Roadmap and contracts language

Roadmaps and topic contracts should emphasize:

- what the learner will be able to do;
- why it matters for their goal;
- what is ready now;
- what will be prepared next;
- how to know the stage is complete;
- where the supporting sources are.

Do not foreground generation thresholds, topological order, PR status, CI or internal classifications in learner-facing sections.

## Pull request and automatic review

Open a draft PR containing only allowed curriculum artifacts. Run `instructions/35-review-curriculum.md`, correct resolvable issues, validate, self-review and merge under the configured policy when no material decision remains.

Operational review and CI are recorded in GitHub. The learner-facing response does not require a fixed PR-status sentence.

## Completion

Create no external tasks, sets, events, notifications or workspaces during generation. Complete using `instructions/phase-completion.md` and guide naturally to:

`Organize minha trilha nas ferramentas que escolhemos.`

Continue accepting `Publique as tarefas da trilha nas integrações configuradas.` as an alias.
