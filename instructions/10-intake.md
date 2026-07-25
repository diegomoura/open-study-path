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

Normalize approved intake with `intake/field-mapping.yml` into `study.config.yml` and `state/intake-summary.json`. Set `configured: true` only after the required planning facts are populated and validated. Mark assumptions visibly. Missing optional answers must not block generation; derive conservative defaults only when necessary and record them as assumptions.

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
- no attachment, conflicting response or integration choice requires interpretation.

If any condition fails, leave the PR open and explain the specific review needed. A request to import intake authorizes creating the PR; automatic merge is authorized only by the marker policy.

## Completion

Stop before diagnostic or curriculum generation unless the owner explicitly requested another phase.

Follow `instructions/phase-completion.md`. By default, do not repeat every normalized field or changed file in chat. Report the result, link the PR, state whether it was merged, surface only material attention items, and guide the owner to the next phase with this command in pt-BR:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`