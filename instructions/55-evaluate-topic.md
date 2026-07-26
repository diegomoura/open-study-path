# Evaluate a completed topic

Evaluate a topic only from an explicit topic ID and an explicit GitHub issue number. Never assume that the newest issue belongs to the learner or to the requested topic.

The standard command is:

`Finalizei o TOPIC-000. Avalie a issue #<número>.`

## Required inputs

Before scoring:

1. read the approved topic contract in `study/topics/TOPIC-000.md`;
2. read the complete lesson in `study/modules/TOPIC-000.md`;
3. read the rubric in `study/assessments/TOPIC-000.yml`;
4. read the full assessment issue and confirm that its title and questions match the topic;
5. read existing attempts for the topic under `state/assessments/TOPIC-000/` when present.

If the issue is missing answers, belongs to another topic or is ambiguous, do not grade it. Ask one specific question or request the correct issue number.

## Response-by-response grading

Grade every response independently against the matching rubric item. For each question, provide:

- points earned and maximum points;
- what the response demonstrated correctly;
- the exact gap, misconception or missing reasoning;
- one actionable improvement suggestion.

Calculate a total score from 0 to 100. A topic is mastered only when:

- the score meets or exceeds `passing_score`;
- no critical misconception listed in the rubric remains;
- the required deliverable or evidence is present and usable.

Do not treat checklist completion, time spent, a Trello card state or a multiple-choice quiz score as sufficient mastery evidence by itself.

## Persist the result

Post the detailed evaluation as a comment on the assessment issue. Create a versioned assessment result under:

`state/assessments/TOPIC-000/attempt-001.json`

Record at least:

- topic ID;
- issue number and URL;
- attempt number;
- evaluated timestamp;
- per-question scores and feedback summary;
- total score;
- mastery status;
- critical misconceptions;
- required recovery actions;
- evaluator method.

Update `state/progress.json` from the verified result. Use a pull request for repository-state changes and follow the configured safe merge policy for progress updates.

## When the topic is mastered

- comment on the issue with the final score and mastery decision;
- move the corresponding Trello card to `Concluído` when Trello is configured;
- move newly unblocked dependent topics to `Pronto para estudar`;
- identify the next available topic;
- return one exact command using the next topic's assessment flow.

## Recovery and focused reassessment

When the topic is not mastered:

1. identify only the failed rubric dimensions and critical misconceptions;
2. create a focused GitHub recovery issue with a short explanation, targeted study tasks and a new assessment containing only the weak areas;
3. create or update a Trello recovery card named `RECOVERY-TOPIC-000-A<attempt>` when Trello is configured;
4. link the recovery issue, original assessment issue, module and topic card;
5. keep the topic out of `Concluído`;
6. require a new evidence attempt.

The recovery issue should ask the learner to answer in one numbered comment. After completion, the standard command is:

`Finalizei a recuperação do TOPIC-000. Avalie a issue #<número>.`

Do not repeat already-mastered questions unless they are necessary to verify that a critical misconception was actually corrected.

## Optional formative quizzes

Ace Quiz Maker or a chat-generated multiple-choice quiz may be used as optional formative practice. It is not the source of truth for mastery, because the durable assessment, rubric, evidence and feedback history belong in GitHub.

## Completion response

Report the score, mastery decision, assessment issue, meaningful feedback and either the next unlocked topic or the focused recovery issue. Do not dump the entire JSON state into chat.