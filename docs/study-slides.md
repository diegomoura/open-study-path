# Study slides and offline ZIP delivery

Open Study Path creates a concise visual presentation for every materialized topic. The deck is derived from the reviewed lesson and delivered as a ZIP containing one self-contained HTML file. PDF generation, browser printing and Chromium rendering are not part of the active contract.

## Artifact contract

Each materialized topic uses:

```text
study/slides/TOPIC-000/
  index.html
  slides.css
  slides.js
  slides.zip
  slides.meta.json
state/slide-reviews/TOPIC-000.yml
```

The topic contract records `slides`, `slides_package` and `slides_review`. The source files remain internal. The learner receives `slides.zip`, extracts it and opens `slides.html` in a browser.

The module contains one visible **Slides da aula** link to the ZIP and one short instruction:

> Baixe o arquivo ZIP, extraia o conteúdo e abra `slides.html` no navegador.

Task projections show resources in this order: slides, complete lesson, optional separate practice and assessment. Do not link source HTML, CSS, JavaScript, metadata or review evidence.

## Pedagogical quality bar

A normal 45–90 minute topic uses 8–18 slides. Required narrative roles are `title`, `map`, `diagram`, `example`, `misconception`, `application` and `summary`. The first slide is `title`, the last is `summary`, and a worked example appears before learner application.

Slides with roles `concept`, `diagram`, `example`, `misconception`, `application` or `recap` identify the reviewed lesson section through `data-lesson-section`. Every approved outcome appears honestly through `data-outcome-ids`.

Use at least five canonical layout types. Keep one main idea per slide and no more than 120 words. Mermaid diagrams include a short interpretation and a relevant limit.

## Source and package boundary

Author semantic HTML in `index.html` and reuse the canonical `slides.css` and `slides.js` unchanged. The package builder:

1. bundles the local JavaScript and Mermaid runtime with esbuild;
2. inlines CSS and JavaScript into the final HTML;
3. adds no remote fonts, scripts, styles or media;
4. creates a deterministic ZIP containing exactly `slides.html`;
5. records source, HTML and ZIP hashes in `slides.meta.json`.

Run:

```bash
npm install --no-save --package-lock=false esbuild@0.25.8 mermaid@11.16.0
python scripts/package_study_slides.py
python scripts/package_study_slides.py --check
python scripts/validate_study_slides.py
```

`--check` rebuilds the expected bytes and rejects missing or stale packages. Re-running without source changes produces identical ZIP and metadata bytes.

## Offline and security contract

The ZIP contains exactly one file named `slides.html`. The packaged document must open through `file://` without a server and without network access for rendering. External hyperlinks may remain as optional navigation, but scripts, styles, images, fonts and media must not depend on remote URLs.

Reject encrypted archives, unsafe paths, variable ZIP timestamps, extra files, external runtime assets, stale hashes or a missing entrypoint.

## Independent review

Run `instructions/37-review-study-slides.md` after the lesson passes course-content review and before packaging. Review source fidelity, outcome coverage, narrative arc, examples, visual hierarchy, accessibility, Mermaid usefulness, learner links and offline delivery.

The review artifact uses version 3. A changed lesson or slide source invalidates the review, ZIP and metadata. Repair them in the same curriculum or materialization pull request.
