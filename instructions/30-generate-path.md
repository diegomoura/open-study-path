# Generate and approve learning path

Generate a dependency-aware set of topics instead of fixed weeks. Each topic must include an objective, prerequisites, estimated effort, learning activities, deliverable, evidence and mastery criteria.

Create:

- `study/roadmap.md` with the topic graph and estimated schedule;
- one file per topic under `study/topics/` using `templates/topic.md`;
- a schedule projection derived from total effort and weekly availability.

## Scope and effort

Make the scope explicit. When the proposed effort cannot satisfy the learner's complete long-term objective, label the result as an introductory cycle rather than implying comprehensive mastery.

Use realistic estimates. A topic may span more than one week when its evidence and mastery criteria cannot responsibly fit within the learner's weekly availability. Distinguish active study time from elapsed time required for real-world practice.

## Resources

Prefer primary or official resources. Every required resource must name a specific work and canonical locator such as section, chapter, book or letter number. Do not use vague placeholders such as “a passage to select” as required resources.

Edition, translation and URL selection may remain pending, but say so explicitly and preserve the canonical locator. Do not claim a resource, edition, translation or link was verified when it was not checked.

## Pull request and automatic review

Open a draft pull request for the curriculum proposal. Limit the diff to:

- `.open-study-path/instance.yml`;
- `study/roadmap.md`;
- `study/topics/`.

Set `status.curriculum_proposed: true` and keep `status.curriculum_approved: false` while drafting.

Before completing this phase, automatically execute the internal checklist in `instructions/35-review-curriculum.md`. Do not ask the owner to request a separate review. Correct every issue that can be resolved from the approved intake, diagnostic evidence and repository contracts.

Read `workflow.curriculum_merge_policy` from `.open-study-path/instance.yml`. If it is missing, use `manual`.

For `agent_review_then_merge`:

1. review and correct the proposal branch;
2. run all required checks, including the curriculum validator;
3. self-review the final diff against the allowed scope;
4. set `status.curriculum_approved: true` only when the review has passed;
5. rerun required checks after the final status change;
6. mark the draft pull request ready;
7. merge it when no pedagogical decision remains unresolved.

Do not attempt to formally approve a pull request authored by the same account. Contract verification, final diff review and successful CI constitute the operational review.

Leave the pull request open only when a material decision genuinely requires the owner. In that case, ask only the specific decision needed; do not give a generic instruction to review, correct or merge the pull request.

Do not publish tasks, create Trello cards, calendar events or notifications during this phase.

## Completion

Complete the phase using `instructions/phase-completion.md`.

After a successful merge, report the approved curriculum and merged pull request, then guide directly to publication with:

`Publique as tarefas da trilha nas integrações configuradas. Não altere o conteúdo pedagógico aprovado.`

When blocked by an unresolved pedagogical decision, report the pull request and ask one concise, concrete question that enables the agent to finish review and merge.