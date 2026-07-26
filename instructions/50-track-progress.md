# Track progress

Synchronize activity state from the selected task backend, but mark a topic as mastered only from a verified evaluation produced by `instructions/55-evaluate-topic.md`.

Record timestamps, evidence links, assessment issue references, attempt numbers, scores, mastery decisions and recovery state in `state/progress.json`.

Activity completion is not equivalent to learning. A checked Trello item, elapsed study time, calendar attendance or formative quiz score may show engagement, but it cannot independently mark a topic as mastered.

When an assessment issue exists but has not been evaluated, keep the topic in `Em avaliação` or the equivalent state and provide:

`Finalizei o TOPIC-000. Avalie a issue #<número>.`

When evidence is insufficient or a critical misconception remains, use the focused recovery workflow from `instructions/55-evaluate-topic.md`. Do not unlock dependent topics until mastery rules pass.

Complete each tracking operation using `instructions/phase-completion.md`. Report only meaningful progress changes, verified evidence, the next available topic or recovery action, and one exact command. Do not dump the entire progress state into chat unless requested.