# Configure intake

Run this phase only in an Open Study Path instance. It prepares the selected intake method but does not import responses or generate a curriculum.

## Provider selection

When no provider is configured, let the owner choose:

1. `github_issue` — recommended because the form already exists in the repository;
2. `jotform` — create a form in the connected account;
3. `manual_yaml` — edit `study.config.yml` directly.

Do not silently select Jotform or create external resources without the owner's choice.

## GitHub Issue Form

1. Confirm `.github/ISSUE_TEMPLATE/create-study-path.yml` exists.
2. Read the exact repository identity from `.open-study-path/instance.yml`.
3. Configure the GitHub Issue Form as ready with deterministic submission lookup.
4. Build the direct URL:

   `https://github.com/OWNER/REPOSITORY/issues/new?template=create-study-path.yml`

5. Return it as a direct clickable link with a human label such as **Preencher meu formulário**.
6. Ensure labels `study-request` and `intake:imported` can be used.
7. Stop after setup and use the natural command:

   `Preenchi o formulário. Pode continuar.`

Do not create or submit an issue, import answers, run the diagnostic or generate curriculum during setup. Do not require an issue number.

### Compatibility

Continue accepting these older forms:

- `Enviei o formulário. Localize e importe a única submissão válida.`
- `Enviei o formulário. Localize e importe a única submissão válida. Conclua e valide esta etapa; depois, inicie o diagnóstico proporcional com perguntas curtas, uma por vez.`
- an explicit issue number when supplied or when multiple valid candidates require disambiguation.

Older `intake.submission_strategy: explicit_issue` means deterministic lookup with an optional number, not a burden to copy it every time.

## Jotform

Confirm the app is connected before reading or creating a form. Never request or store an API key.

Reuse an existing exact form for this instance when verified. Otherwise create it from `intake/jotform-form-spec.yml` in the owner's selected workspace. Do not create a test submission.

Persist only safe metadata: provider, setup status, form ID and URL, specification ID/version, creation mode, attachment policy and `persist_raw_submission: false`.

Return the form link and:

`Preenchi o formulário. Pode continuar.`

Stop before reading submissions.

## Manual YAML

Set the manual provider and return the configuration path. Required facts are subject, objective, current level, preferred language and weekly hours. Do not invent them.

Use:

`Preenchi minha configuração. Pode continuar.`

Continue accepting the older technical YAML command as an alias.

## Instance marker

Update setup and intake-provider status in `.open-study-path/instance.yml`. Setup complete means only that the instance and intake method are ready.

Complete with `instructions/phase-completion.md`. Return the selected form or configuration path and make the next human action unmistakable.

<!-- Compatibility markers: direct clickable link; explicit_issue; explicit issue number remains accepted; Do not require the owner to copy an issue number. -->
