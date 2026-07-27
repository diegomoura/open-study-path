# Generate and approve learning path

Generate a complete dependency-aware roadmap and concise contract for every topic. Materialize detailed teaching content according to the configured content-generation strategy. Do not publish external tasks during this phase.

## Planning contract

Always create upfront:

- `study/roadmap.md` with the complete topic graph and estimated schedule;
- one concise contract per topic under `study/topics/` using `templates/topic.md`;
- observable objectives, prerequisites, effort, deliverables, evidence, mastery criteria and precise resources for every topic.

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
- `content_status: materialized`, a positive `content_version` and `materialized_at` in the topic contract.

`study/topics/` is the compact contract and index. `study/modules/` contains the content the learner actually studies. A planned topic must never contain broken module links or imply that its detailed lesson already exists.

## Complete-content contract

Every materialized module must be self-contained enough for the configured study time and learner level. It must include:

1. objectives and usage guidance;
2. a granular execution plan;
3. prerequisite retrieval questions;
4. actual explanatory content written in clear language;
5. definitions, relationships, limits and nuances;
6. at least two worked examples;
7. common misconceptions and corrections;
8. guided practice with hints;
9. independent practice and the required deliverable;
10. active-recall synthesis;
11. exact assessment-submission instructions;
12. precise references.

Do not generate modules that merely say “read”, “study”, “reflect” or “discuss” without teaching the underlying content.

## Assessments

Every materialized topic assessment must contain five substantial prompts covering conceptual understanding, analysis, transfer to a new case, misconception correction and independent evidence. The rubric must total 100 points, define `passing_score`, identify critical misconceptions and support focused recovery.

Issue Forms are the durable submission channel. They must include:

- labels `assessment` and `assessment:submitted`;
- the hidden marker `open-study-path:assessment topic_id=TOPIC-000`;
- the standard learner command:

`Finalizei o TOPIC-000. Avalie minhas respostas.`

An explicit issue number is supported only as a disambiguation fallback. Never assume that an arbitrary newest repository issue is the assessment.

Ace Quiz Maker or chat quizzes may be offered as optional formative practice, but they do not replace the GitHub assessment, rubric and durable evidence history.

## Scope and effort

Make the scope explicit. When the proposed effort cannot satisfy the learner's complete long-term objective, label the result as an introductory cycle rather than implying comprehensive mastery.

Distinguish active study time from elapsed time required for real-world practice. Weekly dates are projections, not structural curriculum units.

## Resources

Prefer primary or official resources. Every required resource must name a specific work and canonical locator such as section, chapter, book or letter number. Edition, translation and URL selection may remain pending when clearly identified.

## Pull request and automatic review

Open a draft pull request. The initial-generation diff may include:

- `.open-study-path/instance.yml`;
- `study/roadmap.md`;
- `study/topics/`;
- modules, rubrics and Issue Forms only for topics selected by the configured initial window.

Set `status.curriculum_proposed: true` and keep `status.curriculum_approved: false` while drafting.

Before completing this phase, automatically execute `instructions/35-review-curriculum.md`. Correct every issue that can be resolved from approved intake, diagnostic evidence and repository contracts.

For `workflow.curriculum_merge_policy: agent_review_then_merge`:

1. review and correct the proposal branch;
2. run all required checks;
3. self-review the final diff and rolling-window selection;
4. set `status.curriculum_approved: true` only when review passes;
5. rerun checks;
6. mark the draft ready;
7. merge when no pedagogical decision remains unresolved.

Do not attempt to formally approve a pull request authored by the same account. Contract verification, final diff review and successful CI constitute operational review.

## Review status in chat

After successful review and merge, use:

`Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`

When owner input is genuinely required, add concrete annotations to the PR and use:

`Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

Do not ask the owner to review the entire PR when no unresolved decision exists.

## Completion

Do not create Trello cards, calendar events or notifications during generation. Complete the phase using `instructions/phase-completion.md` and guide to:

`Publique as tarefas da trilha nas integrações configuradas.`
