# Safe instance setup execution

Apply this contract during `bootstrap_instance` and `configure_intake`. It governs repository discovery, allowed changes, validation and merge behavior for the first chat.

## Connector-first repository access

When the connected GitHub app or connector is available and exposes the required operation, use it as the primary and exclusive repository transport for reads, writes, branches, pull requests, labels and workflow inspection.

During normal connected setup:

- do not test `gh` availability or run `gh auth status`;
- do not inspect environment variables for GitHub tokens or credentials;
- do not run `git clone`, `git fetch`, `curl` or direct GitHub network requests merely to rediscover repository content or capabilities already exposed by the connector;
- do not treat a missing CLI, blocked DNS or unavailable direct network access as a repository defect;
- do not fall back from a working connector to a less capable transport.

## Resolve repository state from files

Repository metadata such as reported size, code-search status, an empty search result or an incomplete local checkout is not authoritative evidence that the repository is empty. Read repository sentinels directly, including `.open-study-path/template.yml`, `.open-study-path/instance.yml`, `AGENTS.md`, `instructions/manifest.yml` and `.github/ISSUE_TEMPLATE/create-study-path.yml`. Do not reconstruct the repository when inherited files exist.

A configured instance retains `.open-study-path/template.yml`; the instance marker takes precedence without replacing inherited infrastructure.

## Verify intake repository metadata

When `github_issue` is selected:

- verify the form contains `<!-- open-study-path:intake form_id=create-study-path version=4 -->`;
- require repository labels `study-request` and `intake:imported` before importing a real submission;
- provision missing labels through the GitHub labels API when available, or through the inherited **Prepare ChatGPT Project Instructions** workflow, which runs `scripts/ensure_repository_labels.py` on the default-branch push;
- never ask the learner to run that workflow manually;
- never ask the learner to create, inspect or repair technical labels;
- never ask the learner to edit an issue to add a technical marker.

The checked-in form plus the inherited automatic provisioning workflow is sufficient for `intake_entrypoint_ready` during setup. A connector that cannot list or create repository labels is not, by itself, a setup blocker when all of the following are true:

1. the current form marker is present;
2. the workflow has `issues: write`;
3. the workflow contains the step `Ensure intake labels` and invokes `scripts/ensure_repository_labels.py`;
4. the workflow runs automatically on a push to the default branch;
5. the label script is present and covered by `scripts/test_repository_labels.py`.

In that case, record setup as ready, approve the setup review and merge normally. The merge push provisions labels automatically. Label existence remains a strict gate at intake candidate discovery and import: a real intake must not be selected or marked imported until the labels can be verified and the unique candidate is safely identified.

If neither direct label operations nor a verified automatic provisioning path exists, leave setup blocked with a precise internal defect. Do not transfer the repair to the learner.

## Allowed setup diff

The complete first-chat setup may change only `.open-study-path/instance.yml`, `study.config.yml`, `state/intake-summary.json`, `state/progress.json`, `state/integrations.json`, `state/reviews/<setup-operation>.yml`, `study/roadmap.md`, `README.md` and obsolete `.gitkeep` files. Preserve reusable infrastructure.

## Build and review once

Assemble one coherent setup proposal, compare the final head against the base, run the setup reviewer, and repair deterministic findings before responding. The setup review must approve the generated diff and must not retain blocking findings that are recoverable by the inherited workflow.

## Validation and merge gate

A setup pull request may be merged when:

- the final diff is within the setup allowlist;
- both repository markers remain present;
- the instance identifies the exact repository;
- the GitHub Issue Form and current marker exist;
- labels already exist **or** the verified default-branch automatic provisioning path above exists;
- an approved setup review covers the diff with no blocking findings;
- every required check for the current unchanged pull-request head succeeds;
- no owner decision remains.

A failing, pending, cancelled, missing or unreadable required check is not success. Fix deterministic failures in the same operation. Do not claim that the instance is configured while the PR remains open or validation is red or unknown.

## Bounded check observation

Observe checks only for a bounded period. Do not expose repeated polling as progress. If checks remain queued or running, report that validation is in progress without declaring success. Any optional monitor must handle success, failure, cancellation, missing checks and continued execution for the same head.
