# Independent course-content review

Run this review after an authoring pass creates or changes any materialized lesson, assessment, flashcard deck or learner-facing task projection. It is a separate internal role from curriculum planning and from content authorship. Do not ask the learner for a generic review command.

## Role

Act as the **course-content reviewer**, not as the original author. Re-read the approved intake, diagnostic, roadmap, topic contract, lesson, rubric, Issue Form, practice materials and proposed task copy from the repository. Do not approve content merely because CI passes or because the same agent wrote it.

The reviewer answers a different question from the author:

> Does the delivered course teach and assess what the approved plan promised, at the declared level, without introducing a false sequence or silently dropping content?

## Required traceability

Every topic contract created under the review contract defines stable `learning_outcomes` with IDs such as `LO-1` and the concepts that must be taught.

For every materialized topic:

1. the lesson contains one hidden `open-study-path:outcome` marker for each approved outcome, placed beside content that genuinely teaches it;
2. every rubric question declares the outcome IDs it evaluates;
3. every approved outcome is both taught and assessed;
4. `state/content-reviews/TOPIC-000.yml` records the independent review for the current `content_version`;
5. the review artifact maps each outcome to the assessment questions that actually evaluate it.

Markers and mappings are evidence locations, not proof by themselves. Reject dishonest or superficial mappings.

## Review dimensions

Review all of the following before approval.

### 1. Scope and promise

- The lesson preserves the topic objective, learning outcomes, required concepts, effort, deliverable, evidence and mastery criteria.
- Materialization may adapt examples and emphasis from assessment evidence, but it does not silently replace the approved capability.
- A concept promised by the topic contract is not omitted, renamed into a different subject or deferred without an explicit replan.

### 2. Prerequisite integrity

- The topic uses only the prerequisites declared in its contract.
- Prerequisite retrieval in the lesson recalls knowledge that was actually taught by those prerequisite topics.
- The lesson does not assume knowledge merely because a topic has a smaller number or appears immediately before it in a table.
- When the graph branches, learner-facing copy names the direct prerequisites and never implies that the numerically previous card is automatically required.

### 3. Outcome coverage

For each learning outcome:

- find the explanation that teaches it;
- find at least one worked example, practice step or application that exercises it when appropriate;
- find the assessment question or evidence criterion that measures it;
- verify that the required concepts are defined at the declared level;
- reject a marker placed beside content that only mentions the term without teaching it.

### 4. Lesson, practice and assessment alignment

- Guided and independent practice prepare the learner for the assessment without copying answers.
- The deliverable requested in the topic, lesson, Issue Form and rubric is the same artifact or performance.
- Critical misconceptions in the rubric are taught and corrected in the lesson.
- Flashcards reinforce approved definitions and contrasts; they do not introduce unsupported claims or substitute for the lesson.

### 5. Learner navigation

- Roadmap, lesson, assessment and task use the same human title and capability.
- A future task says **Pré-requisitos desta etapa** and lists direct prerequisites.
- A future task says to follow the prerequisite list rather than the card number.
- Ready tasks are ready because dependencies are satisfied, not because their number is next.
- No card says “etapas anteriores” when the dependency graph branches and that wording could imply a linear sequence.

### 6. Level and pedagogy

- The declared subject level remains authoritative.
- Terms are introduced before they are required.
- The lesson is self-contained, progressive and substantial enough to teach rather than merely assign reading.
- Examples, diagrams and exercises support the approved outcomes instead of adding unrelated breadth.

### 7. Sources and factual support

- Central claims are supported by inspected sources with precise locators.
- Sources match the content actually taught.
- Agent-created analogies, diagrams and scenarios are identified correctly.
- Current or unstable claims are verified with current authoritative sources.

### 8. Projection consistency

- Learner-facing task copy is a concise projection of the approved topic, not a new curriculum artifact.
- Direct prerequisites, objective, effort and deliverable in the task match the topic contract.
- External links point to the current reviewed content version.

## Findings and disposition

Classify findings as:

- `blocking`: the course promise, prerequisite graph, learning outcome, assessment alignment, factual support or learner navigation is wrong;
- `non_blocking`: a useful improvement that does not invalidate the current lesson.

Correct resolvable blocking findings on the proposal branch. When the topic contract itself is wrong, stop materialization and use the replan operation instead of rewriting the contract silently.

Approve only when:

- every required check in `templates/content-review.yml` is `passed`;
- every learning outcome is `covered`;
- `blocking_findings` is empty;
- the review references the exact current `content_version`;
- deterministic review validation passes.

A stale approval never authorizes a changed lesson. Incrementing `content_version` requires a new review.

## Independence boundary

The same runtime may execute authoring and review, but they must be separate passes with separate instructions and artifacts. During the review pass, inspect the repository output as evidence and actively search for contradictions. Do not rely on the authoring rationale or mark the review approved by default.

## Merge boundary

Course-content review is required before a curriculum or materialization PR can merge when `content_review.required_for_materialized_topics` is enabled. CI validates traceability and review state; the reviewer remains responsible for semantic honesty.
