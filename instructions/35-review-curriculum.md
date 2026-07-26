# Internal curriculum review checklist

Run this checklist automatically inside the generation phase after the draft curriculum pull request exists. The generation command already authorizes this review. Do not ask the owner to send a separate review command.

## Scope

Review the proposal against:

- the approved intake in `study.config.yml` and `state/intake-summary.json`;
- `state/diagnostic-summary.json`;
- `instructions/30-generate-path.md`;
- `templates/topic.md`;
- `templates/module.md`;
- `templates/assessment-rubric.yml`;
- `templates/topic-assessment-issue-form.yml`;
- the configured weekly availability and learning preferences.

Do not publish tasks or create Trello cards, calendar events or notifications during review.

## Review checklist

Confirm that:

1. the roadmap objective matches the approved goal;
2. the topic graph is acyclic and every prerequisite exists;
3. each topic has an observable objective, realistic effort, activities, deliverable, evidence and mastery criteria;
4. every topic links to a complete module, rubric and Issue Form;
5. every module teaches the content rather than merely listing actions;
6. modules include prerequisite retrieval, explanations, worked examples, misconceptions, guided practice, independent practice, active recall and submission instructions;
7. each assessment has five substantive prompts and a rubric totaling 100 points;
8. rubrics define a passing score, critical misconceptions and focused recovery rules;
9. the total effort and schedule projection are consistent with weekly availability;
10. the scope is explicitly introductory when it does not satisfy the complete long-term goal;
11. required resources name a specific work and canonical locator;
12. unverified editions, translations or links are identified without vague required-resource placeholders;
13. the proposal does not publish tasks or create external resources;
14. the pull-request diff is limited to `.open-study-path/instance.yml`, `study/roadmap.md`, `study/topics/`, `study/modules/`, `study/assessments/` and topic assessment Issue Forms.

Reject a module as incomplete when it could be replaced by a short checklist without losing meaningful teaching content. Correct problems directly on the proposal branch. Keep the pull request in draft while material corrections are being made.

## Automatic review and merge policy

Read `workflow.curriculum_merge_policy` from `.open-study-path/instance.yml`. If it is missing, use `manual`.

- `manual`: finish the review, report findings and leave the pull request open.
- `agent_review_then_merge`: correct the branch, run all required checks, self-review the final diff, set `status.curriculum_approved: true`, rerun checks, mark the draft ready and merge when no unresolved pedagogical decision remains.

Do not attempt to formally approve a pull request authored by the same account. Contract verification, final diff review and successful CI constitute the operational review.

Leave the pull request open only when:

- the goal or scope remains ambiguous;
- competing topic structures require the owner's preference;
- effort estimates cannot be reconciled with availability;
- a required resource cannot be identified precisely;
- an assessment decision materially changes what mastery means;
- CI fails or the diff includes files outside the allowed scope.

When owner input is required, add concrete annotations or a summary comment to the PR and ask only the smallest decision needed. Use a chat status equivalent to:

`Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

After a successful merge, use:

`Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`

Never ask the owner to perform the entire review or merge merely because the pull request exists. Preserve `status.curriculum_proposed: true` and `status.curriculum_approved: true` after merge.