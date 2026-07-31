# Study slides and PDF delivery

Open Study Path creates a concise visual presentation for every materialized topic. The deck is derived from the reviewed lesson, uses the canonical visual system and is delivered to the learner as a PDF. HTML, CSS and JavaScript remain internal reproducible build sources.

## Artifact contract

Each materialized topic uses:

```text
study/slides/TOPIC-000/
  index.html
  slides.css
  slides.js
  slides.pdf
  slides.meta.json
state/slide-reviews/TOPIC-000.yml
```

The topic contract records `slides`, `slides_pdf` and `slides_review`. Planned topics do not expose slide paths as usable resources and must not contain a generated deck.

The module contains one visible **Slides da aula** link to the PDF. Task projections show resources in this order:

1. slides;
2. complete lesson;
3. one primary practice resource;
4. assessment.

Neither the module nor an external task links to `index.html`, `slides.css`, `slides.js`, metadata or review evidence.

## Pedagogical quality bar

Slides are not a six-page checklist or a collection of headings. They must turn the reviewed lesson into a useful visual narrative.

A normal 45–90 minute topic uses **8 to 18 slides**. The deck must contain these narrative roles through `data-slide-role`:

- `title`: useful outcome and orientation;
- `map`: visible route through the lesson;
- `concept`: definition, contrast or model;
- `diagram`: one focused Mermaid model with an explanatory caption;
- `example`: at least one worked example derived from the lesson;
- `misconception`: a plausible error contrasted with a better criterion;
- `application`: a short learner decision, prompt or guided challenge;
- `recap`: active retrieval when it adds value;
- `summary`: concise takeaways and current learner links.

The required minimum roles are title, map, diagram, example, misconception, application and summary. A deck may have several concept or example slides. The first slide is `title`, the last is `summary`, and examples appear before the learner application.

Slides with roles `concept`, `diagram`, `example`, `misconception`, `application` or `recap` use `data-lesson-section` to identify the exact reviewed lesson section they summarize. This is traceability, not visible technical copy.

## Visual system

All generated topics use the current canonical assets from `templates/study-slides/slides.css` and `slides.js` unchanged. Topic-specific authorship belongs in semantic HTML, not in a newly invented reduced stylesheet.

The canonical system provides multiple composition patterns, including:

- title plus outcome panel;
- three-part maps and concept cards;
- comparisons;
- Mermaid diagrams with captions;
- worked cases;
- step sequences;
- misconception corrections;
- learner challenges and checklists;
- active-retrieval prompts;
- closing resources.

A deck must use at least five distinct canonical layout types. Avoid repeating the same card grid across the whole presentation. One main idea per slide remains the rule, but visual economy must not remove the explanatory example, qualification or application that makes the slide useful.

Use system fonts only. Generated raster illustrations and complete-slide images remain outside the current contract. Mermaid-rendered SVG and inline semantic SVG are allowed.

## Authoring boundary

Slides are created only after the complete lesson, practice and assessment pass course-content review. They summarize approved content and do not perform new research or introduce unsupported claims.

Every approved learning outcome must appear in one or more `data-outcome-ids`. The corresponding slide must genuinely teach or represent the outcome. An identifier on unrelated content is invalid.

Keep each slide below 120 words. Non-title slides must still carry explanatory value; a heading plus a slogan is not enough. Use diagrams when they clarify structure, sequence, state, architecture, dependencies or decisions. Every Mermaid slide includes a short interpretation that tells the learner what to observe and what the diagram does not prove.

## Independent slide review

After slide authoring, run `instructions/37-review-study-slides.md` as a separate reviewer role. The review compares the deck with the approved topic contract and lesson and verifies:

- lesson fidelity;
- outcome coverage;
- complete narrative arc;
- worked-example quality;
- summary quality;
- visual variety;
- visual hierarchy;
- Mermaid usefulness;
- accessibility;
- link consistency.

The reviewer inspects the final browser-rendered deck, not only the source or metadata. A mechanically complete but visibly empty deck cannot be approved.

## Rendering and PDF provenance

Use `scripts/render_study_slides.mjs` with pinned Playwright, Mermaid and pdf-lib versions. The renderer:

1. serves the repository on a local-only HTTP server;
2. blocks external network requests;
3. waits for fonts and Mermaid;
4. checks console errors and slide overflow;
5. snapshots the fully rendered HTML state;
6. renders each slide in isolation as one 16:9 PDF page;
7. merges pages with pdf-lib;
8. embeds the renderer identity, current source digest and rendered-snapshot digest into the PDF metadata;
9. writes matching provenance to `slides.meta.json`.

The committed PDF must be the PDF produced by the current HTML renderer. A sidecar JSON that merely describes another PDF is invalid. Validation rejects missing renderer provenance, stale source or rendered-state digests, ReportLab substitutes, page-count drift, missing backgrounds, overflow, Mermaid errors and unexpectedly small PDFs.

`--check` performs a fresh Chromium render and verifies that the committed PDF metadata is bound to the exact current source and rendered browser state.

## Direct PDF link

Use an authenticated GitHub raw route that follows the repository's default branch:

```text
https://github.com/OWNER/REPOSITORY/raw/HEAD/study/slides/TOPIC-000/slides.pdf
```

Never store a temporary signed raw URL, token or query credential. Do not use GitHub Pages, external slide services or manual browser printing.

## Versioning and idempotency

Slides use the topic's exact `content_version`. Changing the lesson or slide sources invalidates `slides.meta.json`, the PDF and the slide review. A changed deck requires a new independent slide review and a newly rendered PDF in the same curriculum or materialization pull request.
