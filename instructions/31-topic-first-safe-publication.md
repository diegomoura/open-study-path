# Topic-first planning and safe external publication

Use this contract during curriculum generation, integration preflight, task publication and partial-publication recovery.

## Topics are the course structure

`planning.unit: topic` is authoritative. Organize the learning path as areas, dependency-aware topics, lessons, activities, evidence and assessments.

The intake does not collect a structured weekly schedule, preferred days or study periods. It may contain an optional free-text `path.time_constraints` value such as a relevant date or approximate weekly availability. Do not invent missing values and do not use the constraint to impose:

- a fixed course duration in weeks;
- week-numbered structural groups;
- a weekly roadmap table;
- deadlines, due dates or an implied late state;
- Trello lists, labels or cards organized by week.

A time constraint does not authorize silently removing mastery-required topics, reducing evidence requirements or claiming that an unrealistic scope fits. Generate the complete dependency-aware course. When the constraint is useful, identify a priority order, distinguish essential progression from optional enrichment and explain feasibility honestly. The learner may choose how far to progress within the available time; the course must not redefine partial coverage as completion.

Without an explicit learner request for a calendar projection, show total estimated effort and effort per topic. Say that the pace is flexible and follows prerequisites and verified progress.

When the learner explicitly requests a dated or weekly projection, collect the minimum missing scheduling details at activation, keep topics as the canonical structure and add this hidden marker to the optional projection:

`<!-- open-study-path:calendar-projection explicitly_requested=true -->`

A date or availability statement is a constraint to discuss, not permission to silently invent a week-by-week plan.

## Required-operation preflight

Before the first external write, inspect the connector operations that are actually available for the complete required publication set.

For a Trello task backend, confirm that the current connector exposes the operations needed to:

1. read or find the canonical board;
2. create and read lists;
3. create and read cards;
4. create checklists when the approved card contract requires them.

A successful board-list read proves connection only. It does not prove that list, card or checklist publication can finish. If any required operation is unavailable or its required identifiers cannot be obtained, stop before creating the board.

## No disposable production probes

Never create `tmp`, `test`, `probe`, numbered variants or any other disposable board, list, card, set, event or workspace to discover a connector schema or test access.

Use harmless reads and the exposed tool schema. When no harmless operation exists, the first write must be an intended canonical resource that can be adopted immediately and recorded durably. Do not create a second resource merely because the first response shape was unexpected.

## Journal every successful write

After each successful external creation or update, persist its safe identifier, URL, capability, provider, type and status in `state/integrations.json` before the next external write.

For a newly created task board, also set `integrations.task_manager.board_or_project` in `study.config.yml` immediately. This journal is required even when the broader publication later becomes partial or blocked.

An interrupted run must be resumable from recorded state and must reuse the exact board, lists and cards already created. Never wait until final success to record all resources.

## Unexpected side effects and cleanup

After an unexpected external creation:

1. stop further exploratory writes;
2. record the exact resource identifier and URL;
3. attempt safe cleanup in the same operation only when the connector exposes a supported archive or delete action and the resource is unambiguously agent-created;
4. otherwise mark the resource as orphaned and keep cleanup as an explicit technical pending action;
5. never make the learner reconstruct what was created from names alone.

The agent owns cleanup of its own probes whenever the connected capability permits it. Do not present manual deletion as a normal learner responsibility. If the connector cannot clean up, explain the limitation and provide exact resource links.

## Partial publication response

Do not speculate about quotas, workspace limits, permissions or provider defects without verified evidence.

When the canonical resource exists but publication is incomplete:

- state what is usable now;
- state what remains unpublished;
- confirm that the existing resource was recorded and will be reused;
- mention cleanup only when it changes the learner's next action;
- return the state-derived command from `scripts/lifecycle_next_action.py`.

The natural continuation for a recorded partial publication is:

`Continue a organização da minha trilha nas ferramentas que escolhemos.`

Do not require the learner to repeat a board URL or technical identifier.
