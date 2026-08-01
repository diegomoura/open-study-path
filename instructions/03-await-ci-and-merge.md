# Await CI and finish the operation

Use this internal contract whenever the current operation is configured to merge automatically after review.

## Preferred completion path

1. Keep one unchanged pull-request head after the final deterministic repair.
2. Enable auto-merge when the repository supports it and no learner decision is pending.
3. When auto-merge is unavailable, poll the required checks for that exact head until they reach a terminal state.
4. Mark the pull request ready and merge immediately after every required check succeeds.
5. Read the default branch after merge before presenting the next command.

A draft pull request is only a temporary authoring area. Pending CI is not a learner-facing terminal state.

## Bounded polling

Do not use one long fixed sleep. Poll with bounded backoff, for example 10, 15, 20, 30 and then 45 seconds. Re-read the head SHA before every status check. If the head changed, restart the observation window for the new head.

Use recent completed runs of the same required workflows to estimate the wait budget when timestamps are available. Prefer the median of the last 5 successful runs and allow at least twice that value, with these safe bounds:

- minimum observation budget: 3 minutes;
- normal maximum observation budget: 15 minutes;
- never wait indefinitely.

Store only aggregate operational timing when a state artifact already exists for the operation: workflow name, sample count, median seconds, p90 seconds and observation timestamp. Do not store logs, tokens, runner identifiers or learner data. Timing history is advisory and must never override current check status.

## Terminal outcomes

- `success`: mark ready, merge and verify the default branch.
- `failure`: inspect the failing step; repair deterministic findings on the same branch and restart polling for the new head.
- `cancelled` or `timed_out`: retry once when clearly transient; otherwise report an infrastructure blocker truthfully.
- missing required check: treat as blocked, not successful.
- observation budget exhausted while checks still run: do not claim that work will continue after the response. Prefer auto-merge if it was successfully enabled. Otherwise report that the operation remains incomplete and provide the exact PR only when the owner must intervene.

## Learner-facing rule

Never end with language such as `a validação ainda está em execução` when the operation is expected to merge automatically and the agent can still observe the checks. Complete the wait-and-merge loop first. Do not provide the next lifecycle command until the merged state is confirmed on the default branch.
