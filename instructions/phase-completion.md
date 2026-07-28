# Guided phase completion

Use this contract at the end of every lifecycle phase. Read `docs/learner-facing-language.md` before composing the response.

## Internal completion

Finish validation, review, correction, safe merge and configured rolling-window materialization before responding. Pull requests, checks and repository state remain the technical audit trail.

Do not send a transition message immediately before repository work. Complete the operation and send one final response.

## Learner-facing response

A successful response should answer, in this order:

1. **What is ready** — one short sentence focused on the learner's outcome.
2. **Where to go** — the one or two links needed now.
3. **What to do next** — a concrete next action.
4. **Continue naturally** — one short, copyable sentence.
5. **Attention** — only when a real decision, missing connection or limitation changes the next action.

Do not foreground PR numbers, CI, commit hashes, branches, changed files, validator names, internal states or synchronization metadata after success. Provide technical details only when requested or when they explain a blocker that requires action.

## Technical review state

Operational review still occurs internally. Record review and merge status in the PR and repository history. Do not require a fixed PR-status sentence in the learner-facing response.

When a genuine unresolved decision exists, link the exact PR or comment and say plainly what decision is needed. Never ask the owner to review an entire PR merely because one exists.

## Natural commands

Present natural commands by default and accept older technical commands as aliases.

### After intake setup

Return the direct intake link and use:

`Preenchi o formulário. Pode continuar.`

Do not ask for an issue or submission number unless deterministic lookup finds more than one valid candidate.

### After intake import

When diagnostic chaining was authorized, start the bounded diagnostic and ask the first short question. Otherwise use:

`Vamos fazer meu diagnóstico.`

### After diagnostic

Use:

`Crie minha trilha de estudos.`

### After curriculum generation

State whether all lessons or only the first lessons are ready, using human language. Link the roadmap, the first ready lesson and useful local practice. Summarize only tools that help now.

When a useful optional app is not connected, use the platform Plugin Management capability to render a nonblocking install/connect suggestion under `instructions/42-integration-preflight.md`. Do not ask a separate text-only confirmation first. A suggestion requires an explicit user click and does not prove authorization.

Use:

`Organize minha trilha nas ferramentas que escolhemos.`

For Quizlet after connection, use:

`Conectei o Quizlet. Crie meus flashcards.`

The technical aliases remain accepted:

- `Publique as tarefas da trilha nas integrações configuradas.`
- `Conectei o Quizlet ao ChatGPT. Verifique novamente e publique os flashcards dos tópicos materializados.`

### When required publication is blocked

Name only the service that needs attention and explain its practical effect. Use a natural return command such as:

`Conectei o Trello. Pode continuar.`

Re-run access verification; a learner statement alone does not prove connection.

### After task and integration publication

Link the first ready lesson, its task and its assessment. Do not lead with a publication report or a list of providers.

Use the topic title in the command:

`Terminei <título da aula>. Avalie minhas respostas.`

Continue accepting `Finalizei o TOPIC-000. Avalie minhas respostas.` as a deterministic technical alias.

### After topic evaluation

Report:

- the score and a plain-language conclusion;
- the strongest evidence and the most important next improvement;
- the next ready lesson when mastered;
- the focused review when more work is needed.

When mastered, restore the configured lookahead automatically. Do not mention the automatic content PR unless requested or unless it failed.

Natural commands:

- `Terminei <título da aula>. Avalie minhas respostas.`
- `Terminei a revisão de <título da aula>.`

Technical aliases remain accepted:

- `Finalizei o TOPIC-000. Avalie minhas respostas.`
- `Finalizei a recuperação do TOPIC-000. Avalie minhas respostas.`

Only request an explicit issue number when multiple valid candidates remain.

## Optional connection suggestions

Use Plugin Management only for selected or recommended optional providers with immediate value in the ready content window. Do not suggest declined, forbidden, irrelevant or already connected providers. Show at most one suggestion per provider and at most three connection suggestions in one completion response. Continue with the repository-native alternative without waiting for a click.

## Concision and visibility

Detailed provider explanations, source mappings, scores, diffs, PR state and synchronization metadata belong in repository artifacts. Surface them in chat only when they change what the learner should do now.

Internal logs and diagnostic ZIP files are debugging aids. Do not attach or foreground them after success.

<!-- Compatibility markers for repository validation: Next step; Continue command; Concision rule; auto_when_unambiguous; Do not send a separate transition message. -->
