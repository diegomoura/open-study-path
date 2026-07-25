# Internal curriculum review checklist

Run this checklist automatically inside the generation phase after the draft curriculum pull request exists. The generation command already authorizes this review. Do not ask the owner to send a separate review command.

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

## Automatic review and merge policy

Read `workflow.curriculum_merge_policy` from `.open-study-path/instance.yml`. If it is missing, use `manual`.

- `manual`: finish the review, report any findings and leave the pull request open.
- `agent_review_then_merge`: correct the proposal branch, run all required checks, self-review the final diff, set `status.curriculum_approved: true`, rerun checks, mark the draft ready and merge when no unresolved pedagogical decision remains.

Do not attempt to formally approve a pull request authored by the same account. Contract verification, final diff review and successful CI constitute the operational review.

Leave the pull request open only when:

- the goal or scope remains ambiguous;
- competing topic structures require the owner's preference;
- effort estimates cannot be reconciled with availability;
- a required resource cannot be identified precisely;
- CI fails or the diff includes files outside the allowed scope.

When owner input is required, ask only the smallest concrete question needed to resolve the decision. Never ask the owner to perform the entire review or merge merely because the pull request exists.

After a successful merge, preserve `status.curriculum_proposed: true` and `status.curriculum_approved: true`.