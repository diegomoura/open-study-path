# Review curriculum proposal

Run this phase only after the generation phase has opened a curriculum pull request and the owner explicitly authorizes review of that exact PR.

## Scope

Review the proposal against:

- the approved intake in `study.config.yml` and `state/intake-summary.json`;
- `state/diagnostic-summary.json`;
- `instructions/30-generate-path.md`;
- `templates/topic.md`;
- the configured weekly availability and learning preferences.

Do not publish tasks or create Trello cards, calendar events or notifications during review.

## Review checklist

Confirm that:

1. the roadmap objective matches the approved goal;
2. the topic graph is acyclic and every prerequisite exists;
3. each topic has an observable objective, realistic effort, activities, deliverable, evidence and mastery criteria;
4. the total effort and schedule projection are consistent with weekly availability;
5. the scope is explicitly introductory when it does not satisfy the complete long-term goal;
6. required resources name a specific work and canonical locator such as section, chapter, book or letter number;
7. unverified editions, translations or links are identified without leaving vague required-resource placeholders;
8. the proposal does not publish tasks or create external resources;
9. the pull-request diff is limited to `.open-study-path/instance.yml`, `study/roadmap.md` and `study/topics/`.

Correct problems directly on the proposal branch. Keep the pull request in draft while material corrections are being made.

## Review and merge policy

Read `workflow.curriculum_review_policy` from `.open-study-path/instance.yml`. If missing, use `manual`.

- `manual`: report the review findings and wait for the owner to merge.
- `agent_review_then_merge`: after correcting the branch, run all required checks, self-review the final diff, mark the pull request ready and merge when there is no unresolved pedagogical decision.

Do not attempt to formally approve a pull request authored by the same account. Contract verification, final diff review and successful CI constitute the operational review.

Leave the pull request open when:

- the goal or scope remains ambiguous;
- competing topic structures require the owner's preference;
- effort estimates cannot be reconciled with availability;
- a required resource cannot be identified precisely;
- CI fails or the diff includes files outside the allowed scope.

After a successful merge, update the instance marker with `status.curriculum_approved: true` and preserve `status.curriculum_proposed: true`.

## Completion

Follow `instructions/phase-completion.md`. Report only the review result, pull-request link, merge state, material decisions still needed and the exact publication command:

`Publique as tarefas da trilha nas integrações configuradas. Não altere o conteúdo pedagógico aprovado.`
