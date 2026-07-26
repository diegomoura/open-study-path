# Agent Operating Contract

Read this file before changing this repository or any repository derived from it.

## Determine the repository mode first

### Template mode

The repository is in template mode when `.open-study-path/template.yml` exists and `.open-study-path/instance.yml` does not.

In template mode, the agent may improve documentation, schemas, instructions and reusable templates. It must not import learner data, create instance state, generate a learner curriculum or create learner-specific external resources.

When asked to initialize a learning path in template mode, explain that the user must first fork or create a repository from the template. Never turn the original template repository into an instance.

### Instance mode

The repository is in instance mode only when `.open-study-path/instance.yml` exists. Instance setup must happen in a fork or derived repository and is separate from intake import and curriculum generation.

## Resolve the repository target

A ChatGPT Project should manage one Open Study Path instance.

Before the instance marker exists, resolve the target repository from:

1. the exact `OWNER/REPOSITORY` value in the ChatGPT Project Instructions; or
2. an exact repository identifier supplied by the owner.

The Project name and description are labels only. Before writing, confirm the repository is accessible, is not the canonical template and matches the explicit identifier.

During bootstrap, write the exact repository to `.open-study-path/instance.yml`. Afterwards its `repository` field is the persistent source of truth. Stop writes if it conflicts with Project Instructions or the current request.

## Guided lifecycle

Read `instructions/manifest.yml` and `instructions/phase-completion.md` before executing a lifecycle phase.

At the end of every phase:

- keep the response brief and action-oriented;
- link primary artifacts;
- mention only material assumptions or blockers;
- identify the next phase;
- provide one exact command;
- state the PR review and merge status;
- stop at the requested phase boundary.

Internal validation, review, correction and safe merge required by the phase are part of the phase and must finish before responding.

## Instance setup workflow

When explicitly asked to set up a fork as an instance:

1. verify repository identity and mode;
2. create `.open-study-path/instance.yml` with workflow defaults;
3. copy `study.config.example.yml` to `study.config.yml` without inventing answers;
4. create initial intake, progress and roadmap artifacts from templates;
5. configure the intake method;
6. stop after intake setup unless another operation was explicitly requested.

## GitHub Issue Form rules

- Confirm `.github/ISSUE_TEMPLATE/create-study-path.yml` exists before marking GitHub intake ready.
- Build direct URLs from the exact instance repository.
- Ask for an explicit issue number and never assume the newest issue.
- Do not import answers or generate curriculum during provider setup.

## Automatic Jotform rules

- Never request API keys.
- Confirm Jotform access before creation.
- Reuse a valid matching form when possible.
- Create forms from the versioned specification and store only safe identifiers.

## Intake pull-request policy

Read `workflow.intake_merge_policy`.

- `manual`: leave open for the specific owner action.
- `auto_after_ci`: merge after checks and phase-limited diff.
- `auto_when_unambiguous`: merge only when evidence, scope, privacy and consistency checks pass without human interpretation.

## Proportional diagnostic rules

Read `instructions/20-diagnostic.md` and `workflow.diagnostic_merge_policy`.

- Treat diagnosis as placement, not teaching.
- Use intake evidence before asking.
- Ask one short question per turn without praising or restating every answer.
- For `none` or `beginner`, target 3–5 and hard-limit 7 questions unless comprehensive assessment is explicitly requested.
- For `intermediate` or `advanced`, target 4–7 and hard-limit 10.
- Stop as soon as conceptual and applied evidence support a responsible starting depth.
- Persist only the structured diagnostic summary, never the raw transcript.

## Complete curriculum generation, review and merge

Generation is one user-facing phase containing structure, full teaching content, assessments, review, correction, validation and safe merge.

Read `instructions/30-generate-path.md`, `instructions/35-review-curriculum.md` and `workflow.curriculum_merge_policy`.

Generate:

- `study/roadmap.md`;
- concise contracts in `study/topics/`;
- complete lessons in `study/modules/`;
- scoring rubrics in `study/assessments/`;
- one assessment Issue Form per topic.

A topic file is not the lesson. Every module must teach the content with explanations, worked examples, misconceptions, guided practice, independent practice, active recall and exact assessment instructions. Reject vague checklist-only modules.

Each assessment must have five substantial prompts and a 100-point rubric with passing score, critical misconceptions and recovery rules.

Create the curriculum PR as a draft. Keep the diff limited to the instance marker, roadmap, topics, modules, assessments and assessment Issue Forms. Correct every resolvable issue. For `agent_review_then_merge`, rerun checks after approval state, mark ready and merge when no pedagogical decision remains.

Do not formally approve a PR authored by the same account. Contract verification, final diff review and successful CI are the operational review.

Use one chat status:

- `Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`
- `Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

Do not ask for a generic second review command or whole-PR review when no unresolved decision exists.

## Integration preflight and task publication

Task publication is one user-facing phase. Connection verification is an internal prerequisite.

- Read `instructions/40-publish-tasks.md` and `instructions/42-integration-preflight.md`.
- Treat roadmap, topics, modules, assessments and assessment Issue Forms as immutable approved inputs. The owner never needs to repeat this invariant.
- Derive required connections only from enabled providers.
- Verify authorization with one harmless read-only operation per required connector.
- Complete all probes before external writes.
- If any probe fails, create no external resources and do not partially publish unless partial publication was explicitly requested.
- Provide: `Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.`
- Re-run probes rather than trusting the statement; continue automatically when all pass.
- Reuse exact matching resources and identifiers to prevent duplicates.

Trello is an execution index, not the content repository. Every topic card must link the full module, topic contract and assessment form and use granular checklist items.

After publication, do not begin an improvised lesson in chat by default. Link the first module, task and assessment form and say:

`Ao concluir o TOPIC-000 e enviar o formulário, escreva: "Finalizei o TOPIC-000. Avalie a issue #<número>."`

## Evidence-based topic evaluation and recovery

Read `instructions/55-evaluate-topic.md`.

- Require an explicit topic ID and explicit assessment issue number.
- Read the topic, complete module, rubric and full issue.
- Grade every response independently with points, correct evidence, gap and actionable improvement.
- Calculate a score from 0 to 100.
- Mark mastery only when the passing score, evidence requirement and critical-misconception rule all pass.
- Comment the detailed evaluation on the issue.
- Store a versioned attempt under `state/assessments/TOPIC-000/` and update `state/progress.json`.
- When mastered, complete the Trello card and unlock dependent topics.
- When not mastered, create a focused recovery GitHub issue and Trello recovery card, then require a new targeted assessment.

The standard commands are:

- `Finalizei o TOPIC-000. Avalie a issue #<número>.`
- `Finalizei a recuperação do TOPIC-000. Avalie a issue #<número>.`

Ace Quiz Maker or chat multiple-choice quizzes may supplement practice, but never replace the durable GitHub issue, rubric, evidence and response-by-response evaluation.

## Instance source of truth

1. `.open-study-path/instance.yml` identifies repository and workflow policy.
2. `study.config.yml` contains normalized preferences and integrations.
3. `instructions/manifest.yml` defines phases.
4. `state/diagnostic-summary.json` contains placement evidence.
5. `study/roadmap.md` and `study/topics/` define structure and contracts.
6. `study/modules/` contains complete teaching content.
7. `study/assessments/` and assessment Issue Forms define evaluation.
8. `state/assessments/` contains attempt results.
9. `state/progress.json` contains verified progress.
10. Raw submissions, diagnostic transcripts and uploaded files are not committed by default.

## Curriculum workflow in instance mode

1. validate repository and intake configuration;
2. import an explicitly approved intake;
3. run bounded diagnosis;
4. generate topic graph, complete modules, rubrics and assessment forms;
5. automatically review, correct, validate and safely merge;
6. run integration preflight and publish execution links;
7. collect answers through explicit assessment issues;
8. evaluate response by response and update verified progress;
9. create focused recovery and reassessment when needed;
10. replan dates without changing dependencies unless evidence or goals change.

## Safety and privacy

- Never commit secrets, credentials or unnecessary personal data.
- Prefer safe references and summaries over original uploaded files.
- Use pull requests for structural and material changes.
- Ask before destructive operations.

## Commands

- `import issue #<number> as approved intake`
- `start the proportional diagnostic`
- `generate curriculum proposal`
- `publish tasks`
- `Finalizei o TOPIC-000. Avalie a issue #<número>.`
- `sync progress`
- `replan study path`
- `generate retrospective`