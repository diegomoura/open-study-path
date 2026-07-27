# Open Study Path

Open-source, AI-assisted template for creating, managing and adapting personalized learning paths.

> **This repository is the template, not a learning-path instance.** Learner curricula, progress and external resources belong only in a fork or repository created from this template.

## Core model

Open Study Path separates four concerns:

1. **Roadmap** — the complete dependency-aware learning path.
2. **Topic contracts** — concise approved definitions of capability, effort, evidence and mastery.
3. **Materialized content** — complete lessons, rubrics and assessment forms for the active study window.
4. **Execution integrations** — Trello, Calendar, Gmail, GitHub Issues or Markdown representations.

GitHub is the source of truth. Trello is an execution index, not the course-content repository.

## Adaptive rolling generation

Initial curriculum generation always creates the full roadmap and every topic contract. Detailed content follows `content_generation` in `.open-study-path/instance.yml`.

The default strategy is:

```yaml
content_generation:
  strategy: adaptive_rolling_window
  lookahead_topics: 2
  full_upfront_max_topics: 4
  full_upfront_max_hours: 4
  adapt_future_modules_from_assessments: true
```

A small curriculum within both thresholds may be generated completely upfront. A larger curriculum materializes only the first two topics. After a topic is mastered, the agent automatically materializes the next eligible content in the same evaluation operation, validates and merges the small PR, and updates existing task integrations.

The learner does not need to request generation of each next topic.

## Topic and task granularity

A topic is one coherent independently assessable capability. It should not be a large chapter, but it should also not be a single administrative action.

Default planning targets:

- three to seven focused activities per topic;
- 10–25 minutes per activity;
- 45–90 minutes per topic;
- split above 120 minutes when the capability can be separated responsibly.

This keeps tasks approachable while avoiding dozens of trivial assessments.

## Assessment workflow

Every materialized topic has:

- a complete module in `study/modules/`;
- a 100-point rubric in `study/assessments/`;
- a GitHub Issue Form with five open-response prompts;
- deterministic assessment metadata and labels.

After submitting the form, the normal command is:

`Finalizei o TOPIC-001. Avalie minhas respostas.`

The learner does not normally copy the issue number. The agent resolves exactly one valid submission using the topic title, labels, hidden marker and assessment history. It asks for an issue number only when multiple valid candidates remain.

When mastery is insufficient, the agent creates focused recovery and targeted reassessment. Ace Quiz Maker or chat quizzes may supplement practice but are not the durable source of mastery evidence.

## Start a new learning path

1. Fork this repository or create a repository from it.
2. Create a dedicated ChatGPT Project.
3. Connect GitHub and authorize the instance repository.
4. Copy `templates/chatgpt-project-instructions.md` into the Project Instructions.
5. Replace `OWNER/REPOSITORY` with the exact repository identifier.
6. Ask the first chat to set up the instance and configure an intake provider.
7. Complete intake, bounded diagnostic and curriculum generation using the exact commands returned by the agent.
8. Authorize task publication only after the curriculum PR is approved and merged.

## Guided lifecycle

`setup → intake → diagnostic → roadmap and initial content generation → publication → evaluation → automatic next-content materialization or recovery → tracking and replanning`

Each operation ends with a brief result, primary artifact links, material attention items, PR status and one exact command.

Curriculum review, correction, CI validation and safe merge are internal to generation and materialization. The owner is asked only about a genuine unresolved pedagogical decision.

## Integration safety

Before initial publication, the agent verifies every configured connector with a harmless read-only operation. If one required provider is unavailable, initial publication is paused before external writes. No API key or token is requested or stored.

Publication creates one task per topic:

- materialized topics receive module, assessment and granular execution links;
- planned topics show their approved objective, prerequisites and future-materialization state;
- only dependency-ready materialized topics are ready to study.

## Repository map

- `.open-study-path/template.yml` — template-mode guard.
- `AGENTS.md` — operating contract.
- `templates/instance.yml` — instance workflow and rolling-generation defaults.
- `instructions/manifest.yml` — lifecycle ordering and internal operations.
- `instructions/30-generate-path.md` — complete roadmap and initial content window.
- `instructions/35-review-curriculum.md` — automatic pedagogical review.
- `instructions/40-publish-tasks.md` — integration publication.
- `instructions/55-evaluate-topic.md` — deterministic assessment resolution and grading.
- `instructions/57-materialize-next-content.md` — automatic rolling materialization.
- `templates/topic.md` — concise topic contract.
- `templates/module.md` — complete teaching module with granular execution plan.
- `templates/topic-assessment-issue-form.yml` — discoverable assessment submission.
- `scripts/validate_curriculum.py` — rolling curriculum and content validator.
- `scripts/validate_guided_lifecycle.py` — lifecycle regression guard.

## Privacy

Do not commit raw form submissions, diagnostic transcripts, uploaded reference files, credentials, email addresses or unnecessary personal data. Persist only normalized information and durable assessment results needed to generate and adapt the learning path.
