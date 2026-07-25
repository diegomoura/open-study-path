# Import intake

Run this phase only in instance mode and only after `instructions/05-configure-intake.md` has completed with `intake.setup_status: ready`.

Use the provider configured in the instance's `study.config.yml`. Never use a form ID, issue or submission belonging to the canonical template.

## Jotform

- Fetch the configured `intake.form_id` and confirm it is accessible.
- Use the submission explicitly identified by the owner or the latest submission when the owner asks for the latest one.
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

Update `.open-study-path/instance.yml` with `status.intake_imported: true`. Stop before curriculum generation unless the owner explicitly requested both operations.
