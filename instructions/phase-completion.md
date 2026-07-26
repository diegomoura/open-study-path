# Guided phase completion

Use this contract at the end of every lifecycle phase.

## Response goals

Keep the completion response brief and action-oriented. Do not repeat the full intake, diagnostic, diff or generated content unless the owner asks for details.

Do not send a separate transition message immediately before repository work. Complete the requested operation and send one final completion response.

The response must contain, in this order:

1. **Result** — one sentence stating what completed and whether it was validated.
2. **Artifact** — clickable links to the primary artifact or artifacts.
3. **Review status** — when a pull request was involved, state whether it was approved and merged or contains specific annotations requiring owner input.
4. **Attention** — include only material assumptions, ambiguities, validation failures or actions requiring review. Omit when empty.
5. **Next step** — name the next lifecycle phase.
6. **Continue command** — provide one exact, copyable command.

Always stop at the requested phase boundary. Internal validation, review, correction and safe merge required by the current phase are part of that phase and must be completed before responding.

## Pull-request state

When a phase creates a pull request, read the phase-specific merge policy from `.open-study-path/instance.yml`.

- `manual`: keep the PR open and explain the specific action required.
- `auto_after_ci`: self-review scope and merge only after all required checks pass.
- `auto_when_unambiguous`: merge only when checks, evidence, scope and privacy rules pass without a material interpretation decision.
- `workflow.curriculum_merge_policy: agent_review_then_merge`: create the curriculum PR as a draft, review and correct it internally, run checks, self-review the final diff, set approved status, rerun checks, mark ready and merge when no pedagogical decision remains unresolved.

Do not attempt to formally approve a PR authored by the same account. Contract verification plus successful checks are the automated review.

Use one of these review statuses:

- successful: `Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`
- owner decision required: `Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

Never ask the owner to review the entire PR when no unresolved decision exists.

## Phase guidance

### After intake setup

Tell the owner how to fill the selected provider and return the approved submission or issue reference.

### After intake import

Use:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`

### After diagnostic

Report only starting depth, artifact, merge state and material caveats. Use:

`Gere uma proposta de trilha com base no intake e no diagnóstico. Não publique tarefas ainda.`

### After curriculum generation

Generation includes complete modules, assessments, draft creation, internal review, corrections, validation and safe merge. Link the merged PR and the first module. Use:

`Publique as tarefas da trilha nas integrações configuradas.`

Do not instruct the owner to request another generic review or merge.

### When publication is blocked by integration access

Follow `instructions/42-integration-preflight.md`. When required connections fail:

- state that publication paused before external creation;
- name only unavailable providers;
- tell the owner to connect them in the current Project;
- provide exactly:

`Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.`

Re-run probes after the message and continue automatically when all pass.

### After task publication

Do not begin an improvised lesson in chat by default. Link:

- the first complete module;
- its task card or task artifact;
- its assessment Issue Form.

Use a handoff equivalent to:

`Ao concluir o TOPIC-000 e enviar o formulário, escreva: "Finalizei o TOPIC-000. Avalie a issue #<número>."`

The next phase is `evaluate` after the learner submits the explicit assessment issue.

### After topic evaluation

Report the total score, mastery decision, assessment issue and either:

- the next unlocked topic and its module/form; or
- the focused recovery issue and recovery task.

For a normal completed topic, the standard command is:

`Finalizei o TOPIC-000. Avalie a issue #<número>.`

For recovery:

`Finalizei a recuperação do TOPIC-000. Avalie a issue #<número>.`

## Concision rule

Do not list every field, finding, topic, question or changed file in chat by default. Detailed content belongs in the module, assessment issue, evaluation comment, PR and repository state.