# Materialize the next content window

Run this instruction automatically inside a successful topic-evaluation operation. It is not a separate user-facing phase and must not require another command.

## Purpose

Keep the approved roadmap complete while generating detailed teaching content only slightly ahead of the learner. This preserves coherence, reduces oversized pull requests and lets future lessons incorporate verified assessment evidence.

Every newly materialized lesson must pass `instructions/36-review-course-content.md` before slide authoring. Its derived slide deck must then pass `instructions/37-review-study-slides.md`, be packaged as an offline ZIP and pass deterministic validation before merge. These are distinct responsibilities inside the same operation.

## Configuration

Read `content_generation`, `content_review` and `study_slides` from `.open-study-path/instance.yml`, plus the current roadmap, integrations plan and state.

Defaults when missing:

- `strategy: adaptive_rolling_window`;
- `lookahead_topics: 2`;
- `full_upfront_max_topics: 4`;
- `full_upfront_max_hours: 4`;
- `adapt_future_modules_from_assessments: true`;
- `visual_learning.mermaid_enabled: true`;
- `visual_learning.minimum_diagrams_per_materialized_module: 1`;
- `study_slides.enabled: true`;
- `study_slides.contract_version: 2`;
- `study_slides.learner_format: zip_html`;
- `study_slides.archive_entrypoint: slides.html`;
- `study_slides.generated_images_enabled: false`;
- `study_slides.mermaid_required: true`.

A curriculum at or below both full-upfront thresholds may materialize every topic initially. Larger curricula maintain a rolling window.

## Rolling-window calculation

After a topic is mastered:

1. read roadmap, topic contracts and progress;
2. identify materialized topics not yet mastered;
3. identify planned topics in deterministic topological order;
4. select a planned topic only when its prerequisites are mastered or materialized inside the lookahead chain;
5. restore the configured lookahead without materializing blocked branches.

Topic numbers do not establish prerequisites. Use only direct prerequisite lists.

## Inputs

Use the approved roadmap and topic contract, stable outcomes, intake and diagnostic evidence, verified assessment results, canonical lesson and assessment templates, `templates/study-slides/`, slide-review template, Mermaid guidance, source-quality guidance and previously approved content as consistency references.

Assessment evidence may adapt examples, emphasis, retrieval and practice difficulty. It must not silently rewrite approved objectives, prerequisites, outcomes, deliverables, effort or mastery criteria. Structural changes belong to replan.

## Required repository changes

For every selected topic:

1. create the complete module;
2. include useful explained Mermaid diagrams;
3. preserve every approved outcome and its hidden teaching marker;
4. create the 100-point rubric with valid `outcome_ids`;
5. create the assessment Issue Form;
6. materialize and version the topic contract;
7. create a current approved course-content review;
8. generate semantic `index.html`, `slides.css` and `slides.js` from the reviewed lesson;
9. create a current approved slide review version 3;
10. run `python scripts/package_study_slides.py TOPIC-000`;
11. commit `slides.zip` and `slides.meta.json`;
12. add the ZIP link block to the module and explain that the learner extracts it and opens `slides.html`;
13. update roadmap materialization state without changing the graph;
14. update integrations only when verified evidence changes a recommendation.

Do not create flashcards, TSV exports or Quizlet sets. Retrieval practice remains in the lesson and assessment.

## Slide review and packaging

After course-content review:

1. create 8–18 focused slides using canonical templates;
2. represent every outcome honestly;
3. include at least one useful Mermaid diagram;
4. run `instructions/37-review-study-slides.md` and correct blocking findings;
5. build the deterministic ZIP with `scripts/package_study_slides.py`;
6. run `scripts/package_study_slides.py --check` and `scripts/validate_study_slides.py`.

The learner sees only `slides.zip`, described as a ZIP containing `slides.html`. Do not link source HTML, CSS, JavaScript, metadata or review evidence. Do not install Playwright or Chromium and do not generate PDF files.

## Pull request and validation

Create a small draft PR limited to selected topic contracts, modules, slide sources, ZIP packages, metadata, rubrics, Issue Forms, current reviews, roadmap status and justified integration changes.

Run curriculum, content-review and slide-package validations plus all required checks. Correct the branch and merge under the configured policy when CI passes and no genuine decision remains. Do not ask the owner for separate generation, review, packaging or merge commands.

## Capability synchronization

After repository materialization succeeds, update the selected task backend with resources in this order: slide ZIP, module, optional separate practice and assessment. Preserve prerequisite lists, current content version and idempotent resource identifiers. Optional provider failures never invalidate the ready GitHub content.

## Idempotency and failure handling

Re-running the package builder without source changes must produce identical ZIP and metadata bytes and require no new slide review. Any changed lesson or slide source invalidates the corresponding review and package.

A missing optional connector records a fallback and does not block the next topic. A missing task provider may pause external synchronization only; it must not hide or invalidate the module, slide ZIP and assessment.

## Completion

Return the evaluation result together with the next available slide ZIP, module, primary task and assessment form. Explain once that the ZIP should be extracted and `slides.html` opened in a browser. Do not foreground internal PR or CI details after success.
