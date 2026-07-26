# Generate and approve learning path

Generate a dependency-aware set of topics instead of fixed weeks. The generation phase must create both the curriculum structure and the actual study content.

## Required artifacts

Create:

- `study/roadmap.md` with the topic graph and estimated schedule;
- one concise contract per topic under `study/topics/` using `templates/topic.md`;
- one complete lesson per topic under `study/modules/` using `templates/module.md`;
- one scoring rubric per topic under `study/assessments/` using `templates/assessment-rubric.yml`;
- one GitHub Issue Form per topic under `.github/ISSUE_TEMPLATE/assessment-topic-<number>.yml` using `templates/topic-assessment-issue-form.yml`;
- a schedule projection derived from total effort and weekly availability.

`study/topics/` is the compact contract and index. It is not a substitute for the lesson. `study/modules/` must contain the content the learner will actually study.

## Complete-content contract

Every module must be self-contained enough for the configured study time and learner level. It must include:

1. objectives and usage guidance;
2. prerequisite retrieval questions;
3. actual explanatory content written in clear language;
4. definitions, relationships, limits and nuances;
5. at least two worked examples;
6. common misconceptions and corrections;
7. guided practice with hints;
8. independent practice and the required deliverable;
9. active-recall synthesis;
10. exact assessment-submission instructions;
11. precise references.

Do not generate modules that merely say “read”, “study”, “reflect” or “discuss” without teaching the underlying content. Do not compress several distinct activities into one vague checklist item.

## Assessments

Each topic assessment must contain five substantial prompts covering conceptual understanding, analysis, transfer to a new case, misconception correction and independent evidence. The rubric must total 100 points, define `passing_score`, identify any critical misconceptions and support focused recovery.

Issue Forms are the durable submission channel. The module must tell the learner to submit the topic form and then return with:

`Finalizei o TOPIC-000. Avalie a issue #<número>.`

Never instruct the agent to assume the newest issue.

Ace Quiz Maker or chat quizzes may be offered as optional formative practice, but they do not replace the GitHub assessment, rubric and durable evidence history.

## Scope and effort

Make the scope explicit. When the proposed effort cannot satisfy the learner's complete long-term objective, label the result as an introductory cycle rather than implying comprehensive mastery.

Use realistic estimates. A topic may span more than one week when its evidence and mastery criteria cannot responsibly fit within the learner's weekly availability. Distinguish active study time from elapsed time required for real-world practice.

## Resources

Prefer primary or official resources. Every required resource must name a specific work and canonical locator such as section, chapter, book or letter number. Do not use vague placeholders as required resources.

Edition, translation and URL selection may remain pending, but say so explicitly and preserve the canonical locator. Do not claim a resource, edition, translation or link was verified when it was not checked.

## Pull request and automatic review

Open a draft pull request. Limit the curriculum diff to:

- `.open-study-path/instance.yml`;
- `study/roadmap.md`;
- `study/topics/`;
- `study/modules/`;
- `study/assessments/`;
- `.github/ISSUE_TEMPLATE/assessment-topic-*.yml`.

Set `status.curriculum_proposed: true` and keep `status.curriculum_approved: false` while drafting.

Before completing this phase, automatically execute `instructions/35-review-curriculum.md`. Correct every issue that can be resolved from the approved intake, diagnostic evidence and repository contracts.

Read `workflow.curriculum_merge_policy` from `.open-study-path/instance.yml`. If it is missing, use `manual`.

For `agent_review_then_merge`:

1. review and correct the proposal branch;
2. run all required checks, including module, rubric and Issue Form validation;
3. self-review the final diff against the allowed scope;
4. set `status.curriculum_approved: true` only when the review has passed;
5. rerun required checks after the final status change;
6. mark the draft pull request ready;
7. merge it when no pedagogical decision remains unresolved.

Do not attempt to formally approve a pull request authored by the same account. Contract verification, final diff review and successful CI constitute the operational review.

## Review status in chat

After successful review and merge, include a concise status equivalent to:

`Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`

When owner input is genuinely required, add concrete annotations or a summary comment to the PR and say:

`Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

Do not ask the owner to review the entire PR when no unresolved decision exists.

Do not publish tasks, create Trello cards, calendar events or notifications during this phase.

## Completion

Complete the phase using `instructions/phase-completion.md`.

After a successful merge, guide directly to publication with:

`Publique as tarefas da trilha nas integrações configuradas.`

Curriculum immutability during publication is enforced by `instructions/40-publish-tasks.md`; do not ask the owner to repeat that invariant.