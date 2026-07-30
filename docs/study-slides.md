# Study slides and PDF delivery

Open Study Path creates a concise visual presentation for every materialized topic. The presentation is derived from the reviewed lesson and is delivered to the learner only as a PDF. HTML, CSS and JavaScript are build sources kept in the repository for reproducible rendering; they are not learner-facing navigation targets.

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

## Authoring boundary

Slides are created only after the complete lesson, practice and assessment have passed the course-content review. They summarize that approved content; they do not perform new research, introduce unsupported claims or become a second lesson.

Every approved learning outcome must appear in at least one slide through `data-outcome-ids`. The deck should preserve the lesson's conceptual sequence while reducing prose. Prefer six to eighteen focused slides, one main idea per slide and no more than 120 words on a slide.

Use diagrams when they clarify structure, sequence, state, architecture, components, dependencies or decisions. Mermaid source remains text in the HTML and is rendered as SVG before PDF creation. Split a crowded diagram into focused slides instead of shrinking it until it becomes unreadable.

Generated raster illustrations are outside the initial contract. Do not create an image of the complete slide. Inline SVG icons and Mermaid-rendered SVG are allowed.

## Visual system

The default presentation uses:

- a 16:9 page;
- a dark background;
- high-contrast text;
- large typography;
- restrained accent colors;
- semantic headings and lists;
- keyboard navigation for build inspection;
- print rules that place exactly one slide on each PDF page.

The source uses system fonts only. Rendering must not depend on a CDN, remote font, public repository, GitHub Pages, RawGitHack or any external slide service.

## Independent slide review

After slide authoring, run `instructions/37-review-study-slides.md` as a separate reviewer role. The review compares the deck with the approved topic contract and lesson, verifies outcome coverage, summary fidelity, Mermaid usefulness, visual hierarchy, accessibility and learner links, then records evidence under `state/slide-reviews/`.

The slide reviewer reviews the HTML source and rendered browser state. PDF validation is deterministic rather than editorial: it confirms that rendering completed, page count matches slide count, the file is a valid non-empty PDF, metadata matches the current sources and no overflow or Mermaid error was observed.

## Rendering

Use `scripts/render_study_slides.mjs` with pinned Playwright and Mermaid versions. The renderer:

1. serves the repository on a local-only HTTP server;
2. blocks external network requests;
3. waits for fonts and Mermaid;
4. checks browser console errors and slide overflow;
5. prints one 16:9 page per slide with backgrounds enabled;
6. creates a tagged PDF;
7. writes source hashes and render diagnostics to `slides.meta.json`.

Normal generation writes the PDF into the topic directory. `--check` renders to an internal diagnostic directory and verifies that the committed PDF and metadata are current. When a runtime cannot render locally, the inherited GitHub Actions job creates the same internal artifact; the agent adds the resulting PDF and metadata to the existing draft pull request before final review. The learner never performs this step.

## Direct PDF link

Use an authenticated GitHub raw route that follows the repository's default branch without publishing the repository:

```text
https://github.com/OWNER/REPOSITORY/raw/HEAD/study/slides/TOPIC-000/slides.pdf
```

This URL remains on `github.com`, preserves private-repository access control and opens the PDF response directly when the viewer has repository access. Never store a temporary signed `raw.githubusercontent.com` URL, token or query credential.

## Versioning and idempotency

Slides use the topic's exact `content_version`. Changing the lesson or slide sources invalidates `slides.meta.json`, the PDF and the slide review. Re-running the renderer without source changes must not require a new pedagogical review, but a changed lesson or deck requires a new independent slide review and a newly rendered PDF in the same curriculum or materialization pull request.
