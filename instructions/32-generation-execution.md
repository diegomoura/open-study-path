# Efficient curriculum generation execution

Apply this contract during initial curriculum generation and later rolling materialization. It governs how repository work is performed; the pedagogical and integration requirements remain in the phase-specific instructions.

## Build before publishing

1. Work in an isolated checkout or proposal branch.
2. Read the active instance configuration, approved intake, diagnostic summary, templates and validators before generating files.
3. Assemble the complete allowed phase diff before opening the pull request. Do not publish topics, modules, rubrics or forms one file at a time while they are still incomplete.
4. Prefer one coherent proposal commit. Use additional commits only for focused corrections discovered by review or CI.
5. Every intermediate and final commit must respect the phase's allowed-diff contract.

## Local preflight

When a checkout and command execution are available, run the complete local validation suite before the first remote push or pull request:

```text
python scripts/validate_template.py all
python scripts/validate_intake_resolution.py
python scripts/validate_guided_lifecycle.py
python scripts/validate_generation_efficiency.py
python scripts/test_curriculum_placeholder_detection.py
python scripts/validate_curriculum_safe.py
```

Fix locally detectable YAML types, frontmatter dates, durations, paths, placeholders, graph errors and scope violations before the first remote CI run.

GitHub Actions is the final confirmation, not the primary trial-and-error linter.

## Failure handling

When CI fails:

1. inspect the exact failed step and its log once;
2. reproduce the failure locally when possible;
3. correct the root cause in the allowed curriculum files;
4. rerun the complete local suite;
5. push one focused correction and wait for the new head's checks.

Do not search Gists, generic web pages or unrelated repositories for validator behavior when the active repository code and exact CI log are available.

Do not add instrumentation commits or temporarily modify repository infrastructure to diagnose learner content.

## Immutable infrastructure in instance mode

During curriculum generation or materialization in an instance repository, never modify these paths, even temporarily:

- `.github/workflows/`;
- `scripts/validate_*.py` or validator tests;
- `instructions/`;
- `templates/`;
- `schemas/`;
- reusable documentation belonging to the template.

If validation appears to expose a canonical template defect, use a semantically neutral curriculum wording adjustment only when it preserves the intended teaching content. Record the reusable defect for the canonical template separately; do not patch the instance's validation infrastructure.

## Bounded remote correction loop

Avoid repeated remote CI experimentation. After a second remote failure on the same operation, inspect the exact current log and resolve the root cause locally before another push. Never create workflow changes merely to print more diagnostics for curriculum content.

## Terminal condition

The operation is complete when all of the following are true for the current, unchanged PR head:

- the final diff is within the allowed phase scope;
- required local or contract checks pass;
- required GitHub Actions checks succeed;
- the pull request is mergeable;
- no unresolved review thread remains;
- no pedagogical or integration-policy decision requires owner input.

At that point, do not perform further research, regenerate content or rerun unchanged checks. Mark the draft ready, merge according to the configured policy and return the phase-completion response.

## Diagnostic artifacts

Logs and ZIP artifacts produced by failed CI runs are internal debugging aids. Do not attach or list them as primary learner artifacts after the final operation succeeds. Mention a diagnostic artifact only when the final state remains blocked and the owner must inspect it to make a concrete decision.