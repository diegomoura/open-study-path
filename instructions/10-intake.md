# Import intake

Run this phase only in instance mode and only after `instructions/05-configure-intake.md` has completed with `intake.setup_status: ready`.

Use the provider configured in the instance's `study.config.yml`. Never use a form ID, issue or submission belonging to the canonical template.

## Jotform

- Fetch the configured `intake.form_id` and confirm it is accessible.
- Use the submission explicitly identified by the owner or the latest submission only when the owner asks for the latest one.
- Do not silently combine multiple submissions.
- Treat file uploads as optional.
- Read attached files only when their contents materially affect the plan.
- Do not commit raw submissions or uploaded files.

## GitHub Issue Form

- Use an issue explicitly selected by the owner.
- Confirm it was created from `.github/ISSUE_TEMPLATE/create-study-path.yml` or contains the expected field headings.
- Do not assume the newest repository issue is an intake request.
- Treat issue attachments as optional and do not copy them into the repository by default.

## Manual YAML

- Read the learner-approved values already entered in `study.config.yml`.
- Do not reinterpret placeholder defaults as confirmed learner facts.

## Required and optional facts

Required planning facts are the subject, detailed objective, current level, preferred language and weekly availability. Desired outcome, motivation, deadline, preferred days or periods, accessibility needs, notes, text references, URLs and attachments are optional.

Integration preferences are also optional for curriculum generation, but normalize them when provided:

- desired experience: `minimal`, `guided_recommendations` or `enriched`;
- free-tier-only policy;
- account-connection policy;
- services already used;
- capability categories the learner would consider connecting;
- preferred task backend, scheduler, reminder and email provider;
- services or data handling the learner wants to avoid.

Normalize approved intake with `intake/field-mapping.yml` into `study.config.yml` and `state/intake-summary.json`. Set `configured: true` only after the required planning facts are populated and validated. Mark assumptions visibly. Missing optional answers must not block generation; derive conservative defaults only when necessary and record them as assumptions.

Do not recommend, connect, probe or create external tools during intake. Preserve `auto` provider choices. The actual contextual recommendation is created only after diagnostic evidence and the curriculum structure are available, following `templates/integrations-plan.md`.

GitHub remains the source of truth regardless of the selected external providers. Normalize the following invariant fields without requiring the learner to repeat them:

- `integrations.source_of_truth.provider: github`;
- formative practice and habit results do not affect mastery;
- analytics projection direction is `github_to_airtable`;
- Mermaid is the canonical visual provider;
- task management has one authoritative backend.

Update `.open-study-path/instance.yml` with `status.intake_imported: true`.

## Pull request and merge

Create a pull request containing only:

- `study.config.yml`;
- `state/intake-summary.json`;
- `.open-study-path/instance.yml`.

Read `workflow.intake_merge_policy` from `.open-study-path/instance.yml` and apply the rules in `instructions/phase-completion.md`.

For `auto_when_unambiguous`, auto-merge only when:

- all required facts are present;
- configuration validation and CI pass;
- the diff contains only the three files above;
- `state/intake-summary.json` contains no material assumptions;
- no attachment or conflicting response requires interpretation.

An `auto` integration preference is not ambiguity: it explicitly delegates contextual recommendation until after diagnostic. A direct provider choice is also not ambiguous when it is valid and does not conflict with `avoid`, `no_external_accounts` or free-tier requirements.

If any condition fails, leave the PR open and explain the specific review needed. A request to import intake authorizes creating the PR; automatic merge is authorized only by the marker policy.

## Completion

Stop before diagnostic or curriculum generation unless the owner explicitly requested another phase.

Follow `instructions/phase-completion.md`. By default, do not repeat every normalized field or changed file in chat. Report the result, link the PR, state whether it was merged, surface only material attention items, and guide the owner to the next phase with this command in pt-BR:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`
