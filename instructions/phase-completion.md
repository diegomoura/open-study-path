# Guided phase completion

Use this contract at the end of every lifecycle phase.

## Response goals

Keep the completion response brief and action-oriented. Do not repeat the full intake, diagnostic, diff or generated content unless the owner asks for details.

Do not send a separate transition message immediately before repository work, such as “there is enough evidence; I will register it”. Complete the requested operation and send one final completion response.

The response must contain, in this order:

1. **Result** — one sentence stating what completed and whether it was validated.
2. **Artifact** — a clickable link to the pull request, form, issue, roadmap or other primary artifact when one exists.
3. **Attention** — include only material assumptions, ambiguities, validation failures or actions that require review. Omit this section when there is nothing material.
4. **Next step** — name the next lifecycle phase and state whether the repository is waiting for review, merge, answers or authorization.
5. **Continue command** — provide one exact, copyable command in the owner's preferred language.

Always stop at the requested phase boundary. Do not execute the next phase merely because it is recommended.

## Pull-request state

When a phase creates a pull request, read the phase-specific merge policy from `.open-study-path/instance.yml`.

- If the configured policy is `manual`, keep the pull request open and instruct the owner to review and merge it before continuing.
- If the policy is `auto_after_ci`, self-review the phase scope and merge only after all required checks pass and the diff contains only files allowed for the phase.
- If the policy is `auto_when_unambiguous`, self-review the phase scope and merge only when all required checks pass, the diff contains only allowed files, required evidence is present, no material assumption was introduced and no contradiction requires human interpretation.
- Never auto-merge destructive changes, credential changes, external-resource creation, curriculum generation or task publication unless a phase-specific instruction explicitly allows it.

Do not attempt to formally approve a pull request authored by the same account. Contract verification plus successful required checks are the automated review. State clearly whether the pull request remains open or was merged automatically.

## Phase guidance

### After intake setup

Tell the owner how to fill the selected provider and how to return the approved submission or issue reference.

### After intake import

The next phase is `diagnostic`. Use a command equivalent to:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`

### After diagnostic

The next phase is `generate`. The completion response should normally contain only:

- the recommended starting depth in the result sentence;
- the diagnostic pull-request link;
- whether it was merged automatically or remains open;
- a material caveat only when it changes what the owner should do;
- the exact generation command.

Do not list all confirmed competencies, knowledge gaps or misconceptions in chat by default. Those details belong in `state/diagnostic-summary.json` and the pull request.

Use a command equivalent to:

`Gere uma proposta de trilha com base no intake e no diagnóstico. Abra um pull request e não publique tarefas ainda.`

### After curriculum generation

The next phase is review and then `publish`. Tell the owner to review the roadmap and topics before publishing tasks.

### After task publication

The next phase is `track`. Explain how the owner should report or synchronize evidence of progress.

## Concision rule

By default, do not list every normalized field, diagnostic finding or changed file in the chat response. Those details belong in the pull request description and repository diff. Surface only the result, artifact, material attention items and next action.
