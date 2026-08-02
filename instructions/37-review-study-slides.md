# Independent study-slide review

Run this review after the complete lesson, practice and assessment pass `instructions/36-review-course-content.md` and after semantic slide HTML has been authored. It is separate from lesson authorship and package generation.

## Role

Act as the **study-slides reviewer**. Re-read the approved topic contract, reviewed lesson and final visual deck. Do not approve because files or outcome IDs merely exist.

The reviewer answers:

> Does this presentation transform the reviewed lesson into a coherent visual explanation that remains useful when opened offline?

## Review sequence

1. Confirm the current lesson version has an approved course-content review.
2. Confirm `slides.css` and `slides.js` match the canonical templates.
3. Inspect every slide in the browser at 16:9.
4. Trace concept, diagram, example, misconception and application slides to real lesson sections.
5. Verify every outcome is genuinely represented.
6. Correct all blocking findings in the source HTML.
7. Record evidence in `state/slide-reviews/TOPIC-000.yml` using review version 3.
8. Package `slides.zip`, then run deterministic package and contract validation.

## Required dimensions

- `lesson_fidelity`: no unsupported facts, sources or recommendations;
- `outcome_coverage`: every outcome is represented by relevant slides;
- `narrative_arc`: useful result, early map, concept, diagram, example, misconception, application and synthesis;
- `worked_example_quality`: at least one complete situation-to-verification example;
- `summary_quality`: concise but explanatory, not slogans;
- `visual_variety`: at least five canonical composition patterns;
- `visual_hierarchy`: readable at 16:9 with strong structure;
- `mermaid_quality`: focused diagram, interpretation and limit;
- `accessibility`: semantic headings, contrast and no color-only meaning;
- `link_consistency`: ZIP is the only learner-facing slide artifact;
- `offline_delivery`: packaged HTML opens without runtime network assets.

## Learner-facing boundary

The module and tasks link only to:

```text
https://github.com/OWNER/REPOSITORY/raw/HEAD/study/slides/TOPIC-000/slides.zip
```

They tell the learner to extract the ZIP and open `slides.html`. Never link `index.html`, `slides.css`, `slides.js`, `slides.meta.json` or review evidence.

## Durable review evidence

Approve only when every check is `passed`, every outcome is reviewed and no blocking finding remains. A technically valid but visually thin or offline-broken deck must not be approved.
