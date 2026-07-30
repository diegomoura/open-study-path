# Independent study-slide review

Run this review after the complete lesson, practice and assessment have passed `instructions/36-review-course-content.md` and after the HTML slide sources have been authored. It is a separate role from lesson authorship, course-content review and PDF rendering.

## Role

Act as the **study-slides reviewer**. Re-read the approved topic contract, the reviewed lesson, its Mermaid diagrams, the slide HTML/CSS/JavaScript and the learner-facing links. Do not trust the slide author's summary and do not approve because the deck looks polished.

The reviewer answers:

> Does this concise visual presentation faithfully represent the reviewed lesson and every promised outcome without introducing new claims, hiding important limits or becoming unreadable?

## Review sequence

1. Confirm the lesson's current `content_version` already has an approved course-content review.
2. Inspect the deck as HTML source and in the browser's final rendered state.
3. Compare every slide with the lesson section or outcome it represents.
4. Correct blocking findings in the slide sources.
5. Record the final evidence in `state/slide-reviews/TOPIC-000.yml` using `templates/slide-review.yml`.
6. Only after approval, render `slides.pdf` and run deterministic PDF validation.

The PDF is not a second semantic review target. A failed render, page mismatch, missing background, overflow, Mermaid error or stale metadata is a technical blocker and must be corrected before merge.

## Required dimensions

### 1. Lesson fidelity

- The deck is derived from the reviewed lesson and topic contract.
- It does not add facts, sources, recommendations or promises absent from the lesson.
- It preserves important qualifications, limits and misconception corrections.
- It summarizes rather than copying long paragraphs or replacing the complete lesson.

### 2. Outcome coverage

- Every approved learning outcome appears in one or more `data-outcome-ids` attributes.
- The corresponding slide genuinely represents the outcome; a hidden identifier beside unrelated content is invalid.
- The deck may combine related outcomes, but it must not silently omit one because the assessment still depends on it.

### 3. Narrative and summary quality

- The opening states the topic and useful result.
- The sequence moves from orientation to core model, example or application, limits and synthesis.
- Each slide has one principal conceptual move.
- Text is concise enough for presentation while retaining explanatory value.
- The final slide points to the complete lesson, primary practice and assessment only when those links are current.

### 4. Visual hierarchy and accessibility

- Every slide has a semantic `h1` or `h2` heading.
- Text has strong contrast and remains readable at the 16:9 size.
- Information is not encoded by color alone.
- Lists, code, labels and diagrams are not crowded or clipped.
- Decorative elements do not compete with the main explanation.
- Generated raster slide images are absent. Inline SVG icons are decorative or labelled appropriately.

### 5. Mermaid quality

- At least one useful Mermaid diagram is present for each deck under the current contract.
- Diagrams are chosen for the concept: flow, sequence, state, architecture, components, dependencies, class or data relationships as appropriate.
- A diagram is focused enough to read on a slide and is accompanied by a short interpretation.
- Complex lesson diagrams are simplified or split without changing their meaning.
- Mermaid source uses the strict security configuration and renders without errors.

### 6. Link consistency

- The deck may link to the complete lesson, practice and assessment.
- No learner-facing content links to the HTML source, CSS, JavaScript, metadata or review evidence.
- The module and task use the direct PDF route under `https://github.com/OWNER/REPOSITORY/raw/HEAD/.../slides.pdf`.
- Links use the exact instance repository and current topic.

## Durable review evidence

The review artifact records:

- exact topic and `content_version`;
- reviewer role and independent-pass mode;
- current lesson SHA-256;
- current aggregate slide-source SHA-256;
- exact learning outcomes reviewed;
- required checks;
- blocking and non-blocking findings.

Approve only when every required check is `passed`, every topic outcome is listed, both source hashes are current and `blocking_findings` is empty. A changed lesson, HTML, CSS or JavaScript invalidates the approval.

## Merge boundary

A materialized topic cannot merge when study slides are enabled and any of these is missing or stale:

- HTML/CSS/JavaScript slide sources;
- approved slide review;
- rendered PDF;
- current render metadata;
- deterministic slide validation.

The slide PDF, metadata and review belong to the same curriculum or materialization pull request as the lesson version they represent. Do not publish an external task until its PDF link points to the approved current version.
