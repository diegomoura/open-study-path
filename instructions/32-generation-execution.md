# Efficient curriculum generation execution

Apply this contract during initial curriculum generation and later rolling materialization. It governs how repository work is performed; the pedagogical and integration requirements remain in the phase-specific instructions.

## Connector-first execution

When connected repository tools already provide file, pull-request, check, job and log access, use them as the authoritative execution path. Do not attempt `gh`, `git clone`, `curl` or direct unauthenticated network access merely to duplicate an available connector operation.

A local checkout is optional acceleration, not a prerequisite for safe repository work. When command execution or network access is unavailable, continue through the connector and the inherited GitHub Actions validation instead of spending turns proving that the unavailable path still fails.

Do not use fixed `sleep` loops to poll checks. Re-read the workflow or pull request through the connector with bounded attempts. A timeout, queued job or in-progress check is a pending technical state, not curriculum success and not a learner decision.

## Build before publishing

1. Work in an isolated checkout or proposal branch.
2. Read the active instance configuration, approved intake, diagnostic summary, templates and validators before generating files.
3. Assemble the complete allowed phase diff before opening the pull request. Do not publish topics, modules, slide sources, PDFs, rubrics or forms one file at a time while they are still incomplete.
4. Prefer one coherent proposal commit. Use additional commits only for focused corrections discovered by review or CI.
5. Every intermediate and final commit must respect the phase's allowed-diff contract.

For each materialized topic, the complete proposal includes the lesson, practice, assessment, approved course-content review, internal HTML slide sources, approved slide review, rendered PDF, render metadata and learner-facing PDF link. Do not merge a lesson first and add its PDF in a later operation.

## Local preflight

When a checkout and command execution are available, run the complete local validation suite before the first remote push or pull request:

```text
python scripts/validate_template.py all
python scripts/validate_intake_resolution.py
python scripts/validate_guided_lifecycle.py
python scripts/test_review_framework.py
python scripts/validate_review_framework.py
python scripts/validate_generation_efficiency.py
python scripts/test_generation_terminal_state.py
python scripts/test_curriculum_placeholder_detection.py
python scripts/test_study_slides.py
python scripts/validate_study_slides.py
python scripts/validate_curriculum_safe.py
```

After lesson and slide reviews pass, render current slide sources with the pinned browser toolchain:

```text
npm install --no-save --package-lock=false playwright@1.62.0 mermaid@11.16.0 pdf-lib@1.17.1
npx playwright install chromium
node scripts/render_study_slides.mjs
python scripts/validate_study_slides.py
```

Fix locally detectable YAML types, topic-contract frontmatter dates, durations, paths, placeholders, graph errors, slide overflow, Mermaid errors, stale PDF metadata and scope violations before the first remote CI run.

Keep operational metadata in `study/topics/TOPIC-000.md`. Generated learner modules under `study/modules/` must begin directly with their title and must not contain YAML frontmatter rendered as a table by GitHub. Slide HTML, CSS, JavaScript and render metadata are internal build sources; only `slides.pdf` is learner-facing.

GitHub Actions is the final confirmation, not the primary trial-and-error linter.

## Browser-render fallback

A runtime without a usable local Chromium may open the draft pull request only after the lesson, slide sources and both semantic reviews are complete. The inherited workflow then renders the same sources into the internal `study-slide-render-output` artifact.

The agent must download that artifact, add `slides.pdf` and `slides.meta.json` to the existing branch, rerun the semantic and deterministic checks, and wait for the current unchanged head to pass. The artifact is an internal transfer mechanism with short retention; it is never a learner resource and the learner never downloads or prints it manually.

Do not report generation success, publish tasks or merge while the current topic lacks the committed PDF and metadata. Do not let the workflow create a later commit after merge.

## Independent review before final validation

After the authoring pass, run specialized reviews in this order:

1. curriculum architecture through `instructions/35-review-curriculum.md`;
2. complete lesson, practice and assessment through `instructions/36-review-course-content.md`;
3. the derived visual summary through `instructions/37-review-study-slides.md`;
4. PDF rendering and deterministic slide validation;
5. `instructions/04-review-generated-artifacts.md` using the phase's `review_profile`.

Create or update the review artifact under `state/reviews/` only after actively checking the complete operation output. Cover every generated path changed by the pull request with its current SHA-256 fingerprint. Correct blocking findings before setting the review to approved.

A review file is part of the allowed phase diff. It is evidence, not learner-facing curriculum, and must not be linked as a study resource.

## Failure handling

When CI fails:

1. inspect the exact failed step and its log once;
2. reproduce the failure locally when possible;
3. correct the root cause in the allowed curriculum or slide files;
4. rerun the complete local suite and every affected independent review when a covered artifact changed;
5. push one focused correction and wait for the new head's checks.

A failed locator, fingerprint, schema, path, placeholder, render, integration-plan or review-coverage check is internal correction work. It is not a learner blocker and does not justify ending the operation with an open draft pull request.

Batch every failure of the same deterministic class before the next remote run. When one planned topic has an invalid source locator, inspect every planned topic for that rule. When one fingerprint is stale, recalculate every artifact changed by the correction. Do not wait for CI to reveal equivalent files one at a time.

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

Avoid repeated remote CI experimentation. After a second remote failure on the same operation, inspect the exact current log and resolve the complete deterministic failure class before another push. Never create workflow changes merely to print more diagnostics for curriculum content.

Do not emit a learner-facing completion response between correction runs. A pending or failed current head means the active operation is still internal unless a concrete material decision or an unavailable required capability genuinely prevents correction.

## Final current-head read-back

Apply `scripts/generation_terminal_state.py` before composing the response. The expected head SHA, pull-request state, required checks and unresolved-thread state must come from one final current read-back.

The resolver may return:

- `correct_and_revalidate` for failed editorial or deterministic checks;
- `wait_and_reread` for queued or in-progress checks;
- `merge_current_head` for a green open or draft pull request;
- `refresh_current_state` when the head moved or evidence is stale;
- `owner_action_required` only for a concrete material decision;
- `technical_blocked` only when current-head verification or safe repository execution is genuinely unavailable;
- `success` only for the exact checked head after merge confirmation.

Never say that the trail is generated while the pull request is open or draft. Never describe an auto-correctable editorial failure as the final result. Never compose the final response from a failed head after a newer head exists.

After the merge call, fetch the pull request again and read the persisted instance state from the default branch. The response must reflect that latest read-back. If the PR merged between two observations, report the merged result rather than repeating the earlier blocker.

## Terminal condition

The operation is complete when all of the following are true for the current, unchanged PR head:

- the final diff is within the allowed phase scope;
- specialized curriculum, course-content and study-slide reviews are complete;
- every materialized topic has a current rendered PDF and render metadata;
- an approved shared review artifact covers every generated change;
- required local or contract checks pass;
- required GitHub Actions checks succeed;
- the pull request is mergeable;
- no unresolved review thread remains;
- no pedagogical or integration-policy decision requires owner input.

At that point, do not perform further research, regenerate content or rerun unchanged checks. Mark the draft ready, merge according to the configured policy, perform the final current-head read-back and return the phase-completion response only when the resolver allows learner success.

## Diagnostic artifacts

Logs, rendered slide artifacts and ZIP artifacts produced by failed CI runs are internal debugging aids. Do not attach or list them as primary learner artifacts after the final operation succeeds. Mention a diagnostic artifact only when the final state remains blocked and the owner must inspect it to make a concrete decision.
