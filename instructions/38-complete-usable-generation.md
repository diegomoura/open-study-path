# Complete the usable learning window before visual packaging

Apply this contract during initial curriculum generation and every rolling-window materialization.

The learner-facing operation has two completion dimensions:

1. **pedagogical readiness** — lesson, practice, assessment, content review and curriculum review are current;
2. **visual readiness** — slide sources are reviewed and the offline ZIP package is current.

## Durable states

For every materialized topic, persist:

- `lesson_ready`: `pending | ready | failed`;
- `slides_source_ready`: `pending | ready | failed | disabled`;
- `slides_package_status`: `pending | ready | failed | disabled`.

Persist `learning_window_usable` as soon as every eligible topic has `lesson_ready: ready`. A missing or failed ZIP never erases that checkpoint.

## Required order

1. Generate pedagogical artifacts for the active window.
2. Run content and curriculum review.
3. Refresh generated-artifact fingerprints in one deterministic batch.
4. Run lightweight pedagogical validation.
5. Persist `learning_window_usable`.
6. Generate and review slide sources.
7. Build deterministic offline ZIP packages.
8. Validate packages and learner links.
9. Publish external resources according to the selected backend policy.

Do not install Playwright or Chromium. Do not generate PDF files.

## Learner-facing response

When `learning_window_usable` exists, report which lessons are usable and whether slide ZIP packages are ready, pending or failed. When ready, explain that the ZIP contains `slides.html`, which opens in a browser after extraction.
