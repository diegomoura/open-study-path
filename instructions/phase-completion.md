# Guided phase completion

Use this contract at the end of every lifecycle phase.

## Response goals

Keep the completion response brief and action-oriented. Do not repeat the full intake, diagnostic, diff or generated content unless the owner asks for details.

Do not send a separate transition message immediately before repository work, such as “there is enough evidence; I will register it”. Complete the requested operation and send one final completion response.

The response must contain, in this order:

1. **Result** — one sentence stating what completed and whether it was validated.
2. **Artifact** — a clickable link to the pull request, form, issue, roadmap or other primary artifact when one exists.
3. **Attention** — include only material assumptions, ambiguities, validation failures or actions that require review. Omit this section when there is nothing material.
4. **Next step** — name the next lifecycle phase and state whether the repository is waiting for answers, authorization or an external action.
5. **Continue command** — provide one exact, copyable command in the owner's preferred language.

Always stop at the requested phase boundary. Internal validation, review, correction and safe merge required by the current phase are part of that phase and must be completed before responding.

## Pull-request state

When a phase creates a pull request, read the phase-specific merge policy from `.open-study-path/instance.yml`.

- If the configured policy is `manual`, keep the pull request open and explain the specific action still required.
- If the policy is `auto_after_ci`, self-review the phase scope and merge only after all required checks pass and the diff contains only files allowed for the phase.
- If the policy is `auto_when_unambiguous`, self-review the phase scope and merge only when all required checks pass, the diff contains only allowed files, required evidence is present, no material assumption was introduced and no contradiction requires human interpretation.
- If `workflow.curriculum_merge_policy` is `agent_review_then_merge`, create the curriculum PR as a draft, review and correct it internally, run required checks, self-review the final diff, set the approved status, rerun checks, mark the PR ready and merge before completing generation when no pedagogical decision remains unresolved.
- Never auto-merge destructive changes, credential changes, external-resource creation or task publication unless a phase-specific instruction explicitly allows it.

Do not attempt to formally approve a pull request authored by the same account. Contract verification plus successful required checks are the automated review. State clearly whether the pull request was merged or remains open because of one specific unresolved decision.

## Phase guidance

### After intake setup

Tell the owner how to fill the selected provider and how to return the approved submission or issue reference.

### After intake import

The next phase is `diagnostic`. Use a command equivalent to:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`

### After diagnostic

The next phase is `generate`. Report only the recommended starting depth, artifact, merge state, material caveats and the exact generation command:

`Gere uma proposta de trilha com base no intake e no diagnóstico. Não publique tarefas ainda.`

Do not list all confirmed competencies, knowledge gaps or misconceptions in chat by default.

### After curriculum generation

Generation includes draft creation, internal review, corrections, validation and safe merge. When successful, the next phase is `publish`. Link the merged curriculum PR and provide:

`Publique as tarefas da trilha nas integrações configuradas. Não altere o conteúdo pedagógico aprovado.`

Do not instruct the owner to request another review, correct files or merge the pull request. When a material pedagogical decision remains unresolved, leave the PR open and ask only one concise question that resolves that decision.

### When publication is blocked by integration access

Connection verification is part of the publication phase. Follow `instructions/42-integration-preflight.md` before any external write.

When one or more required connections fail their read-only probes:

- state that publication was paused before creating external resources;
- name only the unavailable providers;
- omit the artifact section because nothing was published;
- tell the owner to connect or authorize those apps in the current ChatGPT Project;
- provide exactly one dynamic return command:

`Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação das tarefas sem alterar o currículo.`

Do not claim the integrations are configured merely because the owner sent that sentence. Re-run the probes. When all probes pass, continue the pending publication automatically without another confirmation or an intermediate connection-success response.

### After task publication

The next phase is `track`. Explain how the owner should report or synchronize evidence of progress.

## Concision rule

By default, do not list every normalized field, diagnostic finding, topic or changed file in the chat response. Those details belong in the pull request description and repository diff. Surface only the result, artifact, material attention items and next action.
