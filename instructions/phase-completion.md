# Guided phase completion

Use this contract at the end of every lifecycle phase. Read `docs/learner-facing-language.md` before composing the response.

## Internal completion

Finish validation, review, correction, safe merge and configured rolling-window materialization before responding. Pull requests, checks and repository state remain the technical audit trail.

Read `instructions/04-review-generated-artifacts.md` and run the phase profile declared in `instructions/manifest.yml`. A successful phase requires an approved review artifact under `state/reviews/` and generated diff coverage for every instance artifact changed by the operation. Specialized reviews remain additional requirements.

Missing review, partial coverage, stale artifact fingerprints, a skipped required check or any blocking finding blocks merge and blocks a successful response. Do not treat CI structure checks as a substitute for the independent semantic review pass.

Verify every required check for the current unchanged pull-request head. If any required check is failing, pending, cancelled, missing or cannot be verified, the phase is blocked. Do not merge and do not send a successful phase response. Never treat a correct-looking diff, an earlier green commit or a future default-branch run as validation of the current head.

Do not send a transition message immediately before repository work. Complete the operation and send one final response.

## Learner-facing response

A successful response should answer, in this order:

1. **What is ready** — one short sentence focused on the learner's outcome.
2. **Where to go** — the one or two links needed now.
3. **What to do next** — a concrete next action.
4. **Continue naturally** — one short, copyable sentence.
5. **Attention** — only when a real decision, missing connection or limitation changes the next action.

Do not foreground PR numbers, CI, commit hashes, branches, changed files, validator names, internal states or synchronization metadata after success. Provide technical details only when requested or when they explain a blocker that requires action.

## Resolve the next action from persisted state

Before composing the final response, read `.open-study-path/instance.yml` and `state/integrations.json` and apply `scripts/lifecycle_next_action.py`. Persisted lifecycle state, not the wording of a previously suggested command, determines the next operation.

An agent-authored phrase such as `sem publicar tarefas ainda` deliberately defers publication for one operation; it is not a learner decision to skip publication permanently. The agent owns that deferral and must surface the deferred publication as the next action after detailed curriculum generation.

The normal routing invariant is:

- diagnostic complete and curriculum proposal not approved → proposal suboperation inside `generate`;
- curriculum proposal approved but detailed curriculum not generated → detailed generation inside `generate`;
- curriculum generated and publication not completed → `publish`;
- publication completed successfully → `evaluate`.

The proposal and detailed generation share the lifecycle phase `generate`, but they have different persisted states and different commands. Never repeat the proposal command after `curriculum_proposed` and `curriculum_approved` are true. Never skip directly from an approved proposal to publication while `curriculum_generated` is false.

Publication is complete only when `state/integrations.json.sync.status` is `success`, `succeeded` or `completed` and `last_success_at` is present. Missing, `not_started`, pending, partial, blocked or failed publication state cannot enable evaluation.

When publication is pending, do not present an assessment submission or evaluation command as the next action. Lesson and local-practice links may be shown as previews, but the single copyable continuation must remain the publication command. When publication is blocked by a required provider, use the provider-specific return command instead of pretending publication completed.

## Technical review state

Operational review still occurs internally. Record review and merge status in the PR and repository history. Do not require a fixed PR-status sentence in the learner-facing response.

When a genuine unresolved decision exists, link the exact PR or comment and say plainly what decision is needed. Never ask the owner to review an entire PR merely because one exists.

A command containing `Abra um pull request` identifies the audit mechanism, not a request to leave the pull request open. Under `agent_review_then_merge`, review, correct, validate, mark ready and merge automatically unless the learner explicitly says `não faça merge`, `deixe o PR aberto` or `espere minha revisão`, or a concrete material decision remains unresolved.

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

`Gere uma proposta de trilha com base no intake e no diagnóstico. Abra um pull request e não publique tarefas ainda.`

This command creates, independently reviews, validates and merges the roadmap proposal. `Não publique tarefas ainda` restricts only the later publication operation. It does not request human PR review or block merge.

### After approved curriculum proposal

State that the roadmap architecture is approved and that detailed lessons and external tasks have not been created yet. Link the roadmap when useful.

Use:

`Crie minha trilha de estudos.`

This command creates every topic contract, the contextual integration plan and the configured initial window of complete lessons, slides, assessments and local practice. It still does not publish external tasks.

### After curriculum generation

State whether all lessons or only the first lessons are ready, using human language. Link the roadmap, the first ready lesson and useful local practice as previews. Summarize only tools that help now.

If the agent previously suggested generating `sem publicar tarefas ainda`, state plainly that organization in the selected tools remains pending because it was intentionally deferred. Do not make the learner infer or remember that deferred operation.

When a useful optional app is not connected, use the platform Plugin Management capability to render a nonblocking install/connect suggestion under `instructions/42-integration-preflight.md`. Do not ask a separate text-only confirmation first. A suggestion requires an explicit user click and does not prove authorization.

Use this as the only normal copyable continuation:

`Organize minha trilha nas ferramentas que escolhemos.`

Do not include `Terminei <título da aula>. Avalie minhas respostas.` in the generation-completion response while publication is pending.

The technical publication alias remains accepted:

`Publique as tarefas da trilha nas integrações configuradas.`

### When required publication is blocked

Name only the service that needs attention and explain its practical effect. Use a natural return command such as:

`Conectei o Trello. Pode continuar.`

Re-run access verification; a learner statement alone does not prove connection.

### After task and integration publication

Link the first ready lesson, its task and its assessment. Do not lead with a publication report or a list of providers.

Use the topic title in the command:

`Terminei <título da aula>. Avalie minhas respostas.`

For Quizlet after connection, use:

`Conectei o Quizlet. Crie meus flashcards.`

Continue accepting these technical aliases:

- `Finalizei o TOPIC-000. Avalie minhas respostas.`
- `Conectei o Quizlet ao ChatGPT. Verifique novamente e publique os flashcards dos tópicos materializados.`

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
