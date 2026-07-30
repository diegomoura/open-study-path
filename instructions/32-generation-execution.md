# Efficient curriculum generation execution

Apply this contract during initial curriculum generation and later rolling materialization. It governs how repository work is performed; the pedagogical and integration requirements remain in the phase-specific instructions.

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
- specialized curriculum, course-content and study-slide reviews are complete;
- every materialized topic has a current rendered PDF and render metadata;
- an approved shared review artifact covers every generated change;
- required local or contract checks pass;
- required GitHub Actions checks succeed;
- the pull request is mergeable;
- no unresolved review thread remains;
- no pedagogical or integration-policy decision requires owner input.

At that point, do not perform further research, regenerate content or rerun unchanged checks. Mark the draft ready, merge according to the configured policy and return the phase-completion response.

## Diagnostic artifacts

Logs, rendered slide artifacts and ZIP artifacts produced by failed CI runs are internal debugging aids. Do not attach or list them as primary learner artifacts after the final operation succeeds. Mention a diagnostic artifact only when the final state remains blocked and the owner must inspect it to make a concrete decision.
