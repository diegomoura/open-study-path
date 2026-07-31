# Independent study-slide review

Run this review after the complete lesson, practice and assessment pass `instructions/36-review-course-content.md` and after semantic slide HTML has been authored. It is a separate role from lesson authorship and PDF rendering.

## Role

Act as the **study-slides reviewer**. Re-read the approved topic contract, the reviewed lesson, the browser-rendered deck and its learner-facing links. Do not approve because the required files exist or because every outcome ID appears somewhere.

The reviewer answers:

> Does this presentation transform the reviewed lesson into a coherent, useful visual explanation with real examples, limits and learner application?

## Review sequence

1. Confirm the lesson's current `content_version` has an approved course-content review.
2. Confirm `slides.css` and `slides.js` are unchanged copies of the current canonical template.
3. Inspect every slide in the final 1280×720 browser-rendered state.
4. Trace concept, diagram, example, misconception and application slides to their `data-lesson-section`.
5. Compare every outcome with the slide that genuinely represents it.
6. Correct all blocking findings in the HTML.
7. Record final evidence in `state/slide-reviews/TOPIC-000.yml` using `templates/slide-review.yml` version 2.
8. Only after semantic approval, render `slides.pdf` and run deterministic provenance validation.

## Required dimensions

### 1. Lesson fidelity

- The deck is derived from the reviewed lesson and topic contract.
- It preserves important qualifications and limits.
- It does not add facts, sources or recommendations absent from the lesson.
- `data-lesson-section` values point to real lesson sections.

### 2. Outcome coverage

- Every approved outcome appears in one or more `data-outcome-ids`.
- Each marked slide genuinely represents that outcome.
- Outcome coverage is not satisfied by an unrelated summary slide carrying every ID.

### 3. Narrative arc

- The first slide states the useful result.
- A map appears within the first three slides.
- The sequence moves through concept, model, worked example, misconception, learner application and synthesis.
- The final slide is a summary with current links.
- The presentation does not stop at definitions.

### 4. Worked-example quality

- At least one example is worked through from situation to decision, consequence and verification.
- Examples use specific details from the reviewed lesson.
- A second example is preferred when it demonstrates transfer rather than repetition.
- A title plus three vague labels is not a worked example.

### 5. Summary quality

- Each slide has one principal conceptual move.
- Non-title slides carry enough explanation to be useful.
- The deck reduces prose without reducing the lesson to slogans.
- The closing takeaways preserve the most decision-relevant ideas.

### 6. Visual variety

- The deck uses at least five canonical composition patterns.
- The same card grid is not repeated throughout the presentation.
- Layout choice follows the concept: flow for process, compare for distinction, steps for sequence, case for example and challenge for application.
- Empty space supports hierarchy rather than revealing missing content.

### 7. Visual hierarchy and accessibility

- Every slide has a semantic `h1` or `h2`.
- Text has strong contrast and remains readable at 16:9.
- Information is not encoded by color alone.
- Lists, labels and diagrams are not clipped or crowded.
- Generated raster slide images are absent.

### 8. Mermaid quality

- At least one useful Mermaid diagram is present.
- The diagram is focused and readable.
- It is followed by an `osp-caption` interpretation explaining what to observe and one relevant limit.
- A decorative or unexplained diagram fails review.

### 9. Link consistency

- The final slide may link to the complete lesson, primary practice and assessment.
- Learner-facing content never links to HTML, CSS, JavaScript, metadata or review evidence.
- The module and tasks use the direct PDF route under `https://github.com/OWNER/REPOSITORY/raw/HEAD/.../slides.pdf`.

## Durable review evidence

The review artifact records version 2, exact topic and content version, reviewer role, lesson hash, aggregate slide-source hash, outcomes reviewed, all required checks and findings.

Approve only when every check is `passed`, every outcome is reviewed and no blocking finding remains. A deck that technically renders but is visibly thin must receive a blocking finding under `narrative_arc`, `worked_example_quality`, `summary_quality` or `visual_variety`.

## PDF boundary

The PDF is deterministic delivery evidence after semantic review. It must contain embedded Open Study Path renderer provenance bound to the current source digest and rendered-browser snapshot digest. Missing provenance, a ReportLab substitute, stale metadata, page mismatch, overflow or Mermaid error blocks merge.
