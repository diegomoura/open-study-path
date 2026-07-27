# Evaluate a completed topic

Evaluate a materialized topic from an explicit topic ID. The assessment issue number is optional when the correct submission can be resolved deterministically.

The standard command is:

`Finalizei o TOPIC-000. Avalie minhas respostas.`

The explicit fallback remains supported:

`Finalizei o TOPIC-000. Avalie a issue #<número>.`

## Resolve the assessment issue

When an issue number is provided, read it and validate that it matches the requested topic.

When no issue number is provided, search the instance repository for candidate issues that satisfy all of these conditions:

1. label `assessment`;
2. label `assessment:submitted`;
3. title beginning with `[Avaliação] TOPIC-000`;
4. body containing `open-study-path:assessment topic_id=TOPIC-000`;
5. not already recorded as an evaluated attempt under `state/assessments/TOPIC-000/`;
6. not labeled `assessment:graded`;
7. created after the last recorded attempt when an earlier attempt exists.

Use the issue author as an additional filter when the learner identity is known from the active authenticated context. Do not persist unnecessary identity data solely for this lookup.

- Exactly one valid candidate: evaluate it automatically.
- No candidate: state that no submitted assessment was found and provide the direct topic form link.
- More than one candidate: show only the candidate issue numbers and links and ask which one should be evaluated.

Never choose an arbitrary newest repository issue.

## Required inputs

Before scoring:

1. read the approved topic contract;
2. confirm `content_status: materialized`;
3. read the complete module;
4. read the scoring rubric;
5. read the full resolved assessment issue;
6. read existing topic attempts when present.

If answers are incomplete, the issue belongs to another topic or deterministic resolution is ambiguous, do not grade.

## Response-by-response grading

Grade every response independently against the matching rubric item. For each question, provide:

- points earned and maximum points;
- what the response demonstrated correctly;
- the exact gap, misconception or missing reasoning;
- one actionable improvement suggestion.

Calculate a total score from 0 to 100. A topic is mastered only when:

- the score meets or exceeds `passing_score`;
- no critical misconception remains;
- required deliverable or evidence is present and usable.

Checklist completion, time spent, task state or a multiple-choice quiz score is not sufficient mastery evidence by itself.

## Persist and label the result

Post the detailed evaluation as a comment on the assessment issue. Create the next versioned result under:

`state/assessments/TOPIC-000/attempt-001.json`

Record topic ID, issue number and URL, attempt, timestamp, per-question score and feedback, total, mastery, critical misconceptions, recovery actions and evaluator method.

Update `state/progress.json` through a pull request. After evaluation:

- remove `assessment:submitted` from the issue;
- add `assessment:graded` when mastered;
- add `assessment:recovery-required` when recovery is required.

## When the topic is mastered

1. complete or move the configured task card to `Concluído`;
2. unlock eligible dependent topics;
3. automatically execute `instructions/57-materialize-next-content.md` to restore the configured content window;
4. update newly materialized task cards and calendar descriptions after connector probes;
5. return the next ready materialized topic with module, task and form links.

The learner must not send a separate command to generate the next topic.

## Recovery and focused reassessment

When the topic is not mastered:

1. identify only failed rubric dimensions and critical misconceptions;
2. create a focused GitHub recovery issue with targeted study tasks and a reassessment covering only weak areas;
3. create or update `RECOVERY-TOPIC-000-A<attempt>` in the configured task backend;
4. link the recovery issue, original assessment, module and topic task;
5. keep the topic out of `Concluído`;
6. require a new evidence attempt.

The standard recovery command is:

`Finalizei a recuperação do TOPIC-000. Avalie minhas respostas.`

Resolve the recovery issue deterministically using its topic, attempt marker and unresolved recovery status. Request an issue number only when more than one valid recovery submission remains.

Do not repeat mastered questions unless necessary to confirm correction of a critical misconception.

## Optional formative quizzes

Ace Quiz Maker or chat-generated quizzes may supplement practice. They never replace the durable GitHub assessment, rubric, evidence and response-by-response evaluation.

## Completion response

Report the score, mastery decision, resolved assessment issue and either the focused recovery path or the next ready materialized topic. Include any automatic materialization PR as an artifact, but do not require another command before study continues.
