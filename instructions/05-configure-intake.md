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
2. Read the exact repository identity from `.open-study-path/instance.yml` and confirm it matches the active repository.
3. Set:
   - `intake.provider: github_issue`;
   - `intake.setup_status: ready`;
   - `intake.issue_template: .github/ISSUE_TEMPLATE/create-study-path.yml`;
   - `intake.submission_strategy: explicit_issue`.
4. Build the direct Issue Form URL from the exact repository identity:

   `https://github.com/OWNER/REPOSITORY/issues/new?template=create-study-path.yml`

   Replace `OWNER/REPOSITORY` with the instance repository. Never return the placeholder URL.
5. Display the URL as a clickable link. Prefer the label `Preencher o Issue Form de REPOSITORY`, replacing `REPOSITORY` with the repository name.
6. Explain that the Issue Form was inherited from the repository template and was not dynamically created during setup.
7. Tell the owner to submit the form and return with the created issue number, using a command equivalent to: `Importe a issue #4 como intake aprovado. Não gere a trilha ainda.`
8. Stop after presenting the link and next command. Do not create or submit an issue, import answers or generate a curriculum unless explicitly requested.

The completion response for `github_issue` must always contain the direct clickable link and the instruction to return with an explicit issue number.

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

Display the form URL and provide an exact command to import the approved or latest submission. Stop after configuration; do not read a submission until the owner explicitly asks to import one.

## Manual YAML

Set:

- `intake.provider: manual_yaml`;
- `intake.setup_status: ready`;
- `intake.submission_strategy: not_applicable`.

Explain that the required fields are subject, objective, current level, preferred language and weekly hours. Do not invent those values. Provide an exact command for the owner to use after saving the approved values.

## Instance marker

Update `.open-study-path/instance.yml` with:

- `status.intake_configured: true`;
- `status.intake_provider`;
- `status.setup_complete: true`.

Setup completion means the instance and intake method are ready. It does not mean intake was imported or a curriculum was generated.

Complete this phase using `instructions/phase-completion.md`. Keep the response concise, link the selected provider, and make the next required owner action unmistakable.