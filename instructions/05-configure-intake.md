# Configure intake

Run this phase only in an Open Study Path instance. It prepares the selected intake method but does not import responses or generate a curriculum.

## Provider selection

If `study.config.yml` has `intake.provider: unset`, ask the instance owner to choose one provider:

1. `github_issue` — recommended zero-configuration option;
2. `jotform` — the agent creates a form in the owner's connected Jotform account;
3. `manual_yaml` — the owner edits `study.config.yml` directly.

Do not silently select Jotform, create external resources or fall back to another provider without the owner's choice. When no preference is given, recommend `github_issue` because it is already included in every fork.

## GitHub Issue Form

1. Confirm `.github/ISSUE_TEMPLATE/create-study-path.yml` exists in the instance.
2. Set:
   - `intake.provider: github_issue`;
   - `intake.setup_status: ready`;
   - `intake.issue_template: .github/ISSUE_TEMPLATE/create-study-path.yml`;
   - `intake.submission_strategy: explicit_issue`.
3. Do not create or submit an issue on behalf of the owner unless explicitly requested.

## Jotform

### Permission and availability

1. Confirm that the Jotform app is available to the current ChatGPT conversation.
2. If access is unavailable, tell the owner to connect or authorize Jotform in ChatGPT and stop this phase.
3. Never request, store or commit a Jotform API key or access token.

### Idempotent creation

1. If `intake.form_id` is already set, fetch that form and verify it is accessible. Do not create another form when the existing form is valid.
2. If no form ID is configured, search the owner's Jotform assets for the exact title derived from `intake/jotform-form-spec.yml`.
3. Reuse an accessible exact match only after confirming it belongs to this instance. Otherwise create a new form.
4. Read `intake/jotform-form-spec.yml` and convert the complete specification into the natural-language creation instruction required by the Jotform app.
5. Create the form in the owner's personal workspace unless the owner explicitly selected a team workspace.
6. Do not create a test submission.

### Persisted instance metadata

After creation or verified reuse, save only:

- `intake.provider: jotform`;
- `intake.setup_status: ready`;
- `intake.form_id`;
- `intake.form_url`;
- `intake.form_spec_id`;
- `intake.form_spec_version`;
- `intake.created_by: chatgpt_jotform_app` or `reused_existing`;
- `intake.submission_strategy: latest_approved`;
- `intake.attachments_optional: true`;
- `intake.persist_raw_submission: false`.

Display the form URL to the owner so it can be filled. Stop after configuration; do not read a submission until the owner explicitly asks to import one.

## Manual YAML

Set:

- `intake.provider: manual_yaml`;
- `intake.setup_status: ready`;
- `intake.submission_strategy: not_applicable`.

Explain that the required fields are subject, objective, current level, preferred language and weekly hours. Do not invent those values.

## Instance marker

Update `.open-study-path/instance.yml` with:

- `status.intake_configured: true`;
- `status.intake_provider`;
- `status.setup_complete: true`.

Setup completion means the instance and intake method are ready. It does not mean intake was imported or a curriculum was generated.
