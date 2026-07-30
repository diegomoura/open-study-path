# Safe instance setup execution

Apply this contract during `bootstrap_instance` and `configure_intake`. It governs repository discovery, allowed changes, validation and merge behavior for the first chat.

## Resolve repository state from files

Repository metadata such as reported size, code-search status, an empty search result or an incomplete local checkout is not authoritative evidence that the repository is empty.

Before creating or copying anything, read these paths directly from the target repository when available:

- `.open-study-path/template.yml`;
- `.open-study-path/instance.yml`;
- `AGENTS.md`;
- `instructions/manifest.yml`;
- `.github/ISSUE_TEMPLATE/create-study-path.yml`.

Classify the repository only from those sentinels:

- template-derived and unconfigured: template marker exists and instance marker does not;
- configured instance: both template and instance markers exist;
- unsupported or incomplete: the expected sentinels cannot be read consistently.

If metadata says the repository is empty but template sentinels exist, trust the files and continue from the existing template. Do not reconstruct the repository from the canonical template.

## Preserve inherited infrastructure

An instance keeps `.open-study-path/template.yml`. The instance marker takes precedence when determining mode; it does not replace or delete the inherited template marker.

During setup, never delete, rename, recreate or modify reusable infrastructure merely to convert repository mode. Preserve:

- `.github/workflows/`;
- `AGENTS.md`;
- `docs/`;
- `instructions/`;
- `intake/`;
- `schemas/`;
- `scripts/`;
- `templates/`;
- `study.config.example.yml`;
- `.open-study-path/template.yml`.

Use the templates already present in the target repository. Consult the canonical repository only to diagnose a missing or corrupted reusable asset, and do not copy a replacement without surfacing that repository defect.

## Verify intake repository metadata

File sentinels determine repository mode, but a GitHub Issue Form is ready only when its repository metadata also exists.

When `github_issue` is selected:

- verify the form contains `<!-- open-study-path:intake form_id=create-study-path version=4 -->`;
- verify repository labels `study-request` and `intake:imported` exist;
- create only missing labels through the GitHub labels API or run the inherited **Prepare ChatGPT Project Instructions** workflow, which executes `scripts/ensure_repository_labels.py`;
- read the labels again after provisioning;
- do not set intake or setup status to ready while the marker or either label is absent or unverifiable.

Label creation is repository metadata, not a file diff. It must still complete before the setup merge gate and success response.

## Allowed setup diff

The complete first-chat setup may change only:

- `.open-study-path/instance.yml`;
- `study.config.yml`;
- `state/intake-summary.json`;
- `state/progress.json`;
- `state/integrations.json`;
- `state/reviews/<setup-operation>.yml` for the independent setup review;
- `study/roadmap.md`;
- `README.md` for the learner-facing current state and next action;
- `.gitkeep` when it is no longer needed.

Configuring the existing GitHub Issue Form normally changes only `.open-study-path/instance.yml`, `study.config.yml` and the setup review artifact. Do not edit the form just to make setup appear complete.

Reject and correct the proposal before review when any other path changes.

## Build and review once

1. Read all required source templates and contracts before the first write.
2. Assemble the complete allowed diff on one setup branch.
3. Prefer one coherent proposal commit; use later commits only for focused corrections.
4. Compare the final head against the base branch and verify the allowlist above.
5. Confirm that no intake response, diagnostic evidence or curriculum content was anticipated.
6. Run `instructions/04-review-generated-artifacts.md` with the `setup` profile and cover every generated setup path with current SHA-256 fingerprints.

Do not open a destructive or partial proposal and rely on later review to rediscover the repository mode.

## Validation and merge gate

Run the complete repository validation locally when command execution is available. Then open or update the setup pull request and inspect the required checks for the current unchanged head.

A setup pull request may be merged only when all of these are true:

- the final diff is within the setup allowlist;
- `.open-study-path/template.yml` is still present;
- `.open-study-path/instance.yml` identifies the exact target repository;
- the GitHub Issue Form exists when `github_issue` is selected;
- the current intake marker is present in that form;
- labels `study-request` and `intake:imported` exist in the target repository;
- an approved setup review covers the generated diff and has no blocking findings;
- every required check for the current head completed successfully;
- no unresolved review item or owner decision remains.

A failing, pending, cancelled, missing or unreadable required check is not success. Fix the failure or leave the pull request open and report the blocker. Never merge first and assume a later push or default-branch run will validate the setup.

Do not claim that the instance is configured until the merge gate is satisfied.
