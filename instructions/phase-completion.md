# Guided phase completion

Use this contract at the end of every lifecycle phase.

## Response goals

Keep the completion response brief and action-oriented. Do not repeat the full intake, diagnostic, diff or generated content unless the owner asks for details.

The response must contain, in this order:

1. **Result** — one sentence stating what completed and whether it was validated.
2. **Artifact** — a clickable link to the pull request, form, issue, roadmap or other primary artifact when one exists.
3. **Attention** — include only material assumptions, ambiguities, validation failures or actions that require review. Omit this section when there is nothing material.
4. **Next step** — name the next lifecycle phase and state whether the repository is waiting for review, merge, answers or authorization.
5. **Continue command** — provide one exact, copyable command in the owner's preferred language.

Always stop at the requested phase boundary. Do not execute the next phase merely because it is recommended.

## Pull-request state

When a phase creates a pull request:

- If the configured merge policy is `manual`, keep the pull request open and instruct the owner to review and merge it before continuing.
- If the policy is `auto_after_ci`, merge only after all required checks pass and the diff contains only files allowed for the phase.
- If the policy is `auto_when_unambiguous`, merge only when all required checks pass, the diff contains only allowed files, required facts are present, no material assumption was introduced and no attachment or conflicting answer requires human interpretation.
- Never auto-merge destructive changes, credential changes, external-resource creation, curriculum generation or task publication unless a phase-specific instruction explicitly allows it.

State clearly whether the pull request remains open or was merged automatically.

## Phase guidance

### After intake setup

Tell the owner how to fill the selected provider and how to return the approved submission or issue reference.

### After intake import

The next phase is `diagnostic`. Use a command equivalent to:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`

### After diagnostic

The next phase is `generate`. Use a command equivalent to:

`Gere uma proposta de trilha com base no intake e no diagnóstico. Abra um pull request e não publique tarefas ainda.`

### After curriculum generation

The next phase is review and then `publish`. Tell the owner to review the roadmap and topics before publishing tasks.

### After task publication

The next phase is `track`. Explain how the owner should report or synchronize evidence of progress.

## Concision rule

By default, do not list every normalized field or every changed file in the chat response. Those details belong in the pull request description and repository diff. Surface only the result, artifact, material attention items and next action.