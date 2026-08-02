# Generate and approve learning path

Generate a complete dependency-aware roadmap and concise contract for every topic. Materialize detailed teaching content according to the configured strategy. Generate a contextual integration plan, but do not publish external resources during this phase.

Read before generating:

- `docs/learner-facing-language.md`;
- `docs/beginner-first-pedagogy.md`;
- `docs/content-quality-and-sources.md`;
- `docs/mermaid-visual-learning.md`;
- `docs/integration-capabilities.md`;
- `docs/study-slides.md`;
- `instructions/35-review-curriculum.md`;
- `instructions/36-review-course-content.md`;
- `instructions/37-review-study-slides.md`;
- `instructions/38-complete-usable-generation.md`.

## Planning contract

Always create upfront:

- `study/roadmap.md` with the complete topic graph and estimated effort;
- one concise contract per topic under `study/topics/`;
- observable objectives, prerequisites, effort, deliverables, evidence, completion criteria and precise resources;
- one to seven stable learning outcome IDs per topic, with concepts that must be taught;
- `study/integrations.md` using the integrations-plan template.

Stable outcome IDs use `LO-1`, `LO-2` and so on inside each topic. They are internal traceability keys. The learner-facing objective remains natural prose and must describe the same promised results.

Translate `materialized` to “aula pronta” and `planned` to “aula futura” in learner-facing prose. Do not expose rolling-window or topological-order terminology unless technical details are requested.

## Dependency graph

Topic numbers provide stable identity and roadmap order. They do not establish prerequisites. Use only direct prerequisite IDs declared in each contract. In a branched graph, never infer numeric adjacency or say “todas as etapas anteriores” when the dependency list is narrower.

## Personalization and beginner progression

Use intake and diagnostic evidence to personalize motivation, examples, difficulty, prerequisite retrieval, formats, accessibility, practice balance, source selection and next-step language. Treat subject knowledge and transferable experience as separate dimensions.

When level is `none` or `beginner`, or diagnostic records missing vocabulary:

1. explain what the object is before how it works;
2. expand acronyms at first visible occurrence;
3. define prerequisites before using them in another definition;
4. distinguish neighboring concepts and common confusions;
5. explain why the concept exists and where it appears;
6. provide intuition through a bounded analogy or concrete example;
7. then introduce mechanisms, limits and implementation.

Every beginner module contains `## Começando do zero`, `### Vocabulário desta aula` and `## Intuição antes dos detalhes`.

## Topic and task granularity

A topic is an independently assessable capability. Use three to seven focused actions, normally 10–25 minutes each. Prefer 45–90 minutes per topic and split above 120 minutes when responsibly separable.

## Content-generation strategy

For `adaptive_rolling_window`:

1. generate the complete roadmap and every topic contract;
2. generate all detailed content only when the curriculum fits both full-upfront thresholds;
3. otherwise materialize only the first deterministic lookahead window;
4. choose it in topological order;
5. keep future contracts `content_status: planned` without broken module, slide, rubric or form links.

For every materialized topic, create:

- a complete module under `study/modules/`;
- semantic slide sources under `study/slides/TOPIC-000/`;
- a deterministic `slides.zip` containing exactly one self-contained `slides.html`;
- `slides.meta.json` with current source, HTML and package hashes;
- a 100-point rubric under `study/assessments/`;
- a GitHub Issue Form under `.github/ISSUE_TEMPLATE/`;
- positive content version and materialization date;
- a current independent review under `state/content-reviews/`;
- a current independent slide review under `state/slide-reviews/`.

Do not create flashcards, Markdown decks, TSV exports or Quizlet sets. Retrieval practice belongs inside the lesson and assessment.

The topic contract records `slides`, `slides_package` and `slides_review`. The module links only the ZIP through the stable authenticated GitHub raw route and tells the learner to extract it and open `slides.html`. Source HTML, CSS, JavaScript, metadata and review evidence remain internal.

## Outcome traceability

For every materialized topic:

1. preserve approved outcomes and required concepts;
2. place exactly one hidden `open-study-path:outcome` marker for each outcome beside content that genuinely teaches it;
3. add `outcome_ids` to every rubric question;
4. ensure every outcome is taught and assessed;
5. run course-content review as a separate pass;
6. create a current content-review artifact;
7. represent every outcome honestly in slides through `data-outcome-ids`;
8. run independent slide review before packaging.

Identifiers do not prove coverage. Reviewers verify explanations, examples, practice, assessment and visual summary.

## Complete-content contract

Every ready lesson is self-contained for the configured time and level and includes:

1. personal orientation and clear outcome;
2. granular study session;
3. first-principles onboarding when required;
4. prerequisite retrieval based on direct prerequisites;
5. actual explanatory content;
6. definitions, relationships, limits and nuance;
7. bounded analogy or concrete example;
8. at least one explained Mermaid model;
9. at least two worked examples;
10. common errors and corrections;
11. guided and independent practice;
12. active recall inside the lesson;
13. direct assessment action;
14. provenance and verified sources;
15. Other ways to learn when useful;
16. one direct **Slides da aula** ZIP link plus the `slides.html` opening instruction.

Reject modules that merely instruct the learner to read, study, watch, reflect or discuss without teaching the content.

## Source and provenance contract

Inspect every source before including it. Use three to seven curated sources by default, including a primary or official source when available and a reliable explanatory source. Record precise locators and explain how each source was used. Distinguish sourced claims from agent-created diagrams, analogies, examples and exercises. The slide deck inherits reviewed claims and does not perform a second research pass.

## Visual learning with Mermaid

The roadmap shows the actual dependency graph. Every materialized module contains the configured number of explained Mermaid diagrams. Every slide deck contains at least one focused Mermaid diagram with a short interpretation and a relevant limit.

## Study-slide authoring and packaging

Slides are derived only after lesson, practice and assessment pass course-content review.

- Use `templates/study-slides/` and create 8–18 focused 16:9 slides.
- Keep one principal conceptual move per slide and no more than 120 words.
- Use semantic headings, high contrast, concise examples and focused diagrams.
- Do not generate raster illustrations or complete-slide images.
- Do not use CDNs, remote fonts, GitHub Pages or external slide services.
- Keep `slides.css` and `slides.js` identical to canonical templates.

After authoring:

1. run `instructions/37-review-study-slides.md` and correct findings;
2. run `python scripts/package_study_slides.py`;
3. run `python scripts/package_study_slides.py --check`;
4. run `python scripts/validate_study_slides.py`.

The packager bundles local JavaScript and Mermaid, inlines CSS and JavaScript and writes a deterministic ZIP containing exactly `slides.html`. The packaged document must open through `file://` without a server or runtime network assets.

Do not install Playwright or Chromium. Do not render or commit PDF files. PDF failure must not be part of curriculum completion because PDF is no longer an active artifact.

## Contextual integration recommendation

Recommend only capabilities supported by concrete current course signals. Explain them in learner language in `study/integrations.md`; keep technical classifications in state. Optional providers never block repository-native content.

## Assessments

Each assessment contains five substantial prompts covering understanding, analysis, transfer, misconception correction and evidence. Every rubric question declares one or more valid `outcome_ids`, and all approved outcomes are assessed.

The lesson may teach:

`Terminei <título da aula>. Avalie minhas respostas.`

Continue accepting `Finalizei o TOPIC-000. Avalie minhas respostas.` as an alias.

## Roadmap and contracts language

Emphasize what the learner will be able to do, why it matters, what is ready, what will be prepared next, how to know the stage is complete and where supporting sources are. Do not foreground generation thresholds, topological order, PR status or CI in learner-facing sections.

## Pull request and automatic review

Open one draft PR containing only allowed curriculum artifacts. Run curriculum review, course-content review for every materialized topic, slide review, ZIP packaging and the shared phase review. The lesson, slide sources, ZIP, metadata and reviews belong to the same content version and PR. Merge only when required checks pass and no material decision or blocking finding remains.

## Completion

Create no external tasks, events, reminders, email messages or workspaces during generation. Complete using `instructions/phase-completion.md` and resolve the next action through `scripts/lifecycle_next_action.py`.

When generation succeeds and publication is pending, guide naturally to:

`Organize minha trilha nas ferramentas que escolhemos.`

Do not present `Terminei <título da aula>. Avalie minhas respostas.` as the next command before publication succeeds.
