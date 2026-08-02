# Independent course-content review

Run this review after an authoring pass creates or changes any materialized lesson, assessment or learner-facing task projection. It is a separate internal role from curriculum planning and content authorship. Do not ask the learner for a generic review command.

This review approves the complete teaching content before slide authoring begins. It does not approve the visual summary or offline ZIP package. After it passes, generate the internal slide sources and run `instructions/37-review-study-slides.md` as another independent role.

## Role

Act as the **course-content reviewer**, not as the original author. Re-read the approved intake, diagnostic, roadmap, topic contract, lesson, rubric, Issue Form and proposed task copy. Do not approve content merely because CI passes or because the same agent wrote it.

The reviewer asks:

> Does the delivered course teach and assess what the approved plan promised, at the declared level, without introducing a false sequence or silently dropping content?

## Required traceability

Every topic contract defines stable `learning_outcomes` and the concepts that must be taught.

For every materialized topic:

1. the lesson contains one hidden `open-study-path:outcome` marker for each approved outcome beside content that genuinely teaches it;
2. every rubric question declares the outcome IDs it evaluates;
3. every approved outcome is taught and assessed;
4. `state/content-reviews/TOPIC-000.yml` records the review for the current `content_version`;
5. the review maps each outcome to assessment questions that genuinely evaluate it.

Markers and mappings are evidence locations, not proof by themselves. Review requires semantic honesty.

## Review dimensions

### 1. Scope and promise

- The lesson preserves objective, outcomes, required concepts, effort, deliverable, evidence and mastery criteria.
- Materialization may adapt examples and emphasis, but does not replace the approved capability.
- Promised concepts are not omitted or silently deferred.

### 2. Prerequisite integrity

- The topic uses only declared prerequisites.
- Retrieval recalls knowledge actually taught by those prerequisites.
- The lesson does not infer prerequisites from numbering.
- Branched navigation names direct prerequisites and never implies numeric adjacency.

### 3. Outcome coverage

For each learning outcome, find the explanation, relevant worked example or practice, assessment evidence and required concepts. Reject markers beside content that only mentions vocabulary.

### 4. Lesson, practice and assessment alignment

- Guided practice, independent practice and `## Confira sem consultar` prepare the learner for the assessment without copying answers.
- The deliverable is consistent across topic, lesson, Issue Form and rubric.
- Critical misconceptions are taught and corrected.
- No Markdown deck, TSV export or Quizlet set is required or generated.

### 5. Learner navigation

- Roadmap, lesson, assessment and task use the same human title and capability.
- Future tasks list direct prerequisites and do not imply a false linear sequence.
- Ready tasks are ready because dependencies are satisfied.

### 6. Level and pedagogy

- The declared subject level remains authoritative.
- Terms are introduced before they are required.
- The lesson is self-contained, progressive and substantial enough to teach.
- Examples, diagrams and exercises support approved outcomes.

### 7. Sources and factual support

- Central claims are supported by inspected sources with precise locators.
- Sources match content actually taught.
- Agent-created analogies, diagrams and scenarios are identified correctly.
- Current or unstable claims use current authoritative sources.

### 8. Projection consistency

- Task copy is a concise projection, not a new curriculum artifact.
- Direct prerequisites, objective, effort and deliverable match the topic contract.
- External links point to the current reviewed version.
- A separate **Prática** link appears only when a distinct approved exercise or laboratory adds value.

## Findings and disposition

Classify findings as `blocking` or `non_blocking`. Correct resolvable blocking findings on the proposal branch. When the topic contract itself is wrong, use replan instead of silently rewriting it.

Approve only when every required check is `passed`, every learning outcome is covered, `blocking_findings` is empty, the review references the current content version and deterministic validation passes.

## Study-slide handoff

Only after approval:

1. derive a concise visual narrative from the reviewed lesson;
2. generate HTML, CSS and JavaScript under `study/slides/TOPIC-000/`;
3. preserve outcomes through `data-outcome-ids`;
4. avoid new research, unsupported claims and raster slide images;
5. run `instructions/37-review-study-slides.md`;
6. build and validate the deterministic `slides.zip` package containing `slides.html`.

The course-content reviewer does not pre-approve the slide summary.

## Independence boundary

The same runtime may execute authoring and review, but as separate passes with separate instructions and artifacts.

## Merge boundary

Course-content review is required before a curriculum or materialization PR can merge when enabled. When study slides are enabled, the same PR must subsequently contain a current approved slide review, offline ZIP package, matching metadata and passing deterministic slide validation.
