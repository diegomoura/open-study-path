# Materialize the next content window

Run this instruction automatically inside a successful topic-evaluation operation. It is not a separate user-facing phase and must not require another command.

## Purpose

Keep the approved roadmap complete while generating detailed teaching content only slightly ahead of the learner. This preserves coherence, reduces oversized pull requests and lets future lessons incorporate verified assessment evidence.

## Configuration

Read `content_generation` from `.open-study-path/instance.yml`.

Defaults when missing:

- `strategy: adaptive_rolling_window`;
- `lookahead_topics: 2`;
- `full_upfront_max_topics: 4`;
- `full_upfront_max_hours: 4`;
- `adapt_future_modules_from_assessments: true`;
- `visual_learning.mermaid_enabled: true`;
- `visual_learning.minimum_diagrams_per_materialized_module: 1`;
- `visual_learning.diagrams_must_be_explained: true`.

For `adaptive_rolling_window`, a curriculum at or below both full-upfront thresholds may materialize every topic during initial generation. Larger curricula must maintain a rolling window.

## Rolling-window calculation

After a topic is mastered:

1. read `study/roadmap.md`, every topic contract and `state/progress.json`;
2. identify topics whose `content_status` is `materialized` but which are not yet mastered;
3. identify planned topics in deterministic topological order;
4. select the next planned topic only when every prerequisite is already mastered or is itself materialized inside the lookahead chain;
5. materialize enough selected topics to restore `lookahead_topics`, unless no eligible planned topic remains.

Do not count recovery material as a normal lookahead topic. Do not materialize blocked branches merely to fill the number.

## Inputs for a new module

Use all of these sources:

- the approved roadmap and topic contract;
- intake and diagnostic evidence;
- verified assessment results and recovery history;
- `templates/module.md`, `templates/assessment-rubric.yml` and `templates/topic-assessment-issue-form.yml`;
- `docs/mermaid-visual-learning.md`;
- previously approved modules as a consistency reference.

A previous module is not the sole template. Do not copy its structure mechanically when the next capability requires a different teaching approach.

Assessment evidence may adapt examples, emphasis, prerequisite retrieval, practice difficulty and visual representations. It must not silently rewrite the approved objective, prerequisites, deliverable, effort or mastery criteria. A structural pedagogical change belongs to replan.

## Required changes

For every selected topic:

1. create the complete module;
2. include at least the configured minimum number of useful Mermaid diagrams and explanatory prose;
3. create the 100-point rubric;
4. create the discoverable assessment Issue Form with the topic marker and standard assessment labels;
5. set the topic's `content_status` to `materialized`;
6. increment `content_version` and set `materialized_at`;
7. update the roadmap's materialization status without changing the approved graph.

The module must contain three to seven focused execution actions, normally 10–25 minutes each. The topic should normally represent 45–90 minutes of coherent learning. Split a topic before approval when it exceeds 120 minutes and can be separated into independently assessable capabilities.

For nontechnical subjects, use Mermaid for decision paths, causal relationships, conceptual maps, timelines or state changes. For programming, AWS and other technical subjects, choose architecture, dependency, sequence, state, class or data-flow views. Complex topics should use multiple focused diagrams rather than one crowded diagram.

Every diagram must render in GitHub, be introduced in context and be followed by an explanation of what the learner should notice. Do not create decorative or generic diagrams unrelated to the topic.

## Pull request and validation

Create a small draft pull request limited to:

- the selected topic contracts;
- their new modules, rubrics and assessment Issue Forms;
- the roadmap materialization status.

Run the curriculum validator and all required checks. Review Mermaid syntax and pedagogical relevance alongside the rest of the content. Correct the branch. Under `workflow.curriculum_merge_policy: agent_review_then_merge`, mark ready and merge when CI passes and no new pedagogical decision is required.

Do not ask the owner for a separate generation or merge command.

## Integration synchronization

After repository materialization succeeds, update existing task resources for the newly materialized topics:

- add module, rubric and assessment-form links to their Trello cards or configured task backend;
- replace the planned-card checklist with the granular module execution plan;
- move only newly dependency-ready topics to `Pronto para estudar`;
- update future calendar-event descriptions when applicable.

Run harmless connector probes before these external updates. A missing connector must not undo or block the repository materialization; report the pending synchronization and provide the standard reconnection command for only the unavailable providers.

## Completion

Return the topic-evaluation result together with the next available module and assessment form. Mention the internal materialization PR only as an artifact; do not ask for another command before the learner starts the next topic.
