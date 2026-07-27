# Guided phase completion

Use this contract at the end of every lifecycle phase.

## Response goals

Keep the completion response brief and action-oriented. Do not repeat full intake, diagnostic, curriculum, integration plan or state unless requested.

Do not send a separate transition message immediately before repository work. Complete the active operation and send one final completion response.

The response must contain, in this order:

1. **Result** — what completed and whether it was validated.
2. **Artifact** — primary links.
3. **Review status** — PR approved/merged or annotated for one concrete decision.
4. **Attention** — only material assumptions, required-provider failures, optional fallbacks or required actions.
5. **Next step** — the next lifecycle action.
6. **Continue command** — one exact copyable command.

Internal validation, review, correction, safe merge and automatic rolling-window materialization required by the active operation must finish before responding.

## Pull-request state

Follow the configured phase-specific policy. `auto_when_unambiguous` permits merge only when checks, evidence, scope, privacy and consistency rules pass without a material interpretation decision. For `workflow.curriculum_merge_policy: agent_review_then_merge`, review, correct, validate, mark ready and merge when no pedagogical or integration-policy decision remains.

Use one review status:

- `Revisão do PR: aprovada pelo agente e pelo CI; PR #<número> mesclado.`
- `Revisão do PR: anotações adicionadas ao PR #<número>. Avalie somente os pontos marcados e responda no PR.`

Never ask for whole-PR review when no unresolved decision exists.

## Phase guidance

### After intake setup

Always return the direct clickable intake URL when the selected provider has a form. For manual YAML, return the exact configuration path instead.

For GitHub Issue Form or Jotform, use this continuation command:

`Enviei o formulário. Localize e importe a única submissão válida. Conclua e valide esta etapa; depois, inicie o diagnóstico proporcional com perguntas curtas, uma por vez.`

Do not ask the owner to copy an issue number or submission ID by default.

### After intake import

Do not claim that providers were recommended or connected. Intake records preferences only.

If the owner explicitly authorized diagnostic chaining, begin `instructions/20-diagnostic.md` only after the intake source is resolved, the state validates and the intake PR is merged. State the proportional question budget and ask the first short question.

If diagnostic chaining was not requested, use:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`

If zero valid submissions are found, return the same direct intake link. If more than one valid submission remains, list only the candidates needed for disambiguation and request a choice.

### After diagnostic

`Gere uma proposta de trilha com base no intake e no diagnóstico. Não publique tarefas ainda.`

### After curriculum generation

State whether the configured strategy generated all modules or an initial rolling window. Link:

- the roadmap;
- `study/integrations.md`;
- the first materialized module;
- local flashcards when generated.

Summarize only the selected or recommended capability providers, not every known plugin. Make clear that no external resource was created during generation.

Use:

`Publique as tarefas da trilha nas integrações configuradas.`

### When required publication is blocked

Name only unavailable required providers and use:

`Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.`

Re-run probes and continue automatically when they pass. Do not include unavailable optional providers in the blocked list because they use fallbacks.

### After task and integration publication

Do not begin an improvised lesson in chat by default. Link the first complete module, authoritative task and assessment form.

Briefly list optional providers that used fallbacks, such as local flashcards instead of Quizlet or Mermaid-only instead of an external visual workspace. Do not frame optional fallback as a failure of the course.

Link the integration plan when the learner needs to understand why a provider was selected.

Use:

`Ao concluir o TOPIC-000 e enviar o formulário, escreva: "Finalizei o TOPIC-000. Avalie minhas respostas."`

Do not require the learner to copy the issue number by default.

### After topic evaluation

Report the resolved assessment issue, score and mastery. GitHub is the only source allowed to establish mastery.

When mastered, automatically materialize enough eligible planned topics to restore the configured lookahead window. Link the automatic materialization PR when one was needed and give the next ready module without asking for a generation command.

When recovery is required, link the focused recovery issue and authoritative task. Optional reminders, habits, schedules or flashcards may support recovery but are not evidence of mastery.

Report deferred optional synchronization only when it changes what the learner can use immediately.

Normal command:

`Finalizei o TOPIC-000. Avalie minhas respostas.`

Recovery command:

`Finalizei a recuperação do TOPIC-000. Avalie minhas respostas.`

Only request an explicit issue number when deterministic lookup finds more than one valid candidate.

## Concision rule

Detailed questions, provider explanations, scores, state and diffs belong in issues, pull requests and repository artifacts. Surface only meaningful results and next actions in chat.