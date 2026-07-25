# Agent Operating Contract

Read this file before changing this repository or any repository derived from it.

## Determine the repository mode first

### Template mode

The repository is in template mode when `.open-study-path/template.yml` exists and `.open-study-path/instance.yml` does not.

In template mode, the agent may improve documentation, schemas, instructions and reusable templates. It must not:

- import a learner submission;
- create `study.config.yml`;
- create `state/` or `study/` instance artifacts;
- generate a curriculum;
- create a learner's Jotform, GitHub Issues, Trello cards or calendar events;
- store learner-specific integration identifiers.

When asked to initialize a learning path in template mode, explain that the user must first fork or create a repository from the template. Never turn the original template repository into an instance.

### Instance mode

The repository is in instance mode only when `.open-study-path/instance.yml` exists. Instance setup must happen in a fork or derived repository and is separate from intake import and curriculum generation.

## Instance setup workflow

When explicitly asked to set up a fork as an instance:

1. Confirm the repository is not the canonical template repository named in `.open-study-path/template.yml`.
2. Create `.open-study-path/instance.yml` with the source template, repository and setup timestamp.
3. Copy `study.config.example.yml` to `study.config.yml` without inventing learner answers.
4. Copy `templates/state/intake-summary.json` to `state/intake-summary.json`.
5. Copy `templates/state/progress.json` to `state/progress.json`.
6. Copy `templates/roadmap.md` to `study/roadmap.md`.
7. Create `study/topics/` only when the first topic is generated.
8. Configure the intake method using `instructions/05-configure-intake.md`:
   - GitHub Issue Form is the zero-configuration default;
   - Jotform is created automatically in the owner's connected Jotform account from `intake/jotform-form-spec.yml`;
   - manual YAML remains available.
9. Stop after the intake method is ready. Do not import answers or generate a curriculum unless explicitly requested.

If the owner explicitly asks to create only the instance files and postpone intake configuration, stop after step 7 and leave `intake.provider: unset`.

## Automatic Jotform rules

- Never require the owner to duplicate a maintainer-owned form or manually copy its ID.
- Confirm Jotform access in ChatGPT before attempting creation.
- If Jotform is not connected, instruct the owner to authorize the app and stop; never request an API key.
- Before creating a form, verify whether the instance already has a valid `form_id` or an exact matching form in the owner's account.
- Create the form from the versioned specification in `intake/jotform-form-spec.yml`.
- Save only the created form ID, URL and specification version in the instance.
- Do not create a submission or import answers during form setup.

## Instance source of truth

1. `study.config.yml` contains normalized learner and integration preferences.
2. `instructions/manifest.yml` defines the execution phases.
3. `state/progress.json` contains machine-readable progress.
4. `study/topics/` contains generated learning units.
5. Raw Jotform submissions and uploaded files must never be committed by default.

## Curriculum workflow in instance mode

1. Read `instructions/manifest.yml`.
2. Confirm the selected intake provider has `setup_status: ready`.
3. Read the explicitly selected or latest approved intake.
4. Normalize only required planning facts using `intake/field-mapping.yml` into `study.config.yml` and `state/intake-summary.json`.
5. Validate configuration against `schemas/study-config.schema.json`.
6. Run a proportional diagnostic or use reliable existing evidence.
7. Generate a dependency-aware topic graph.
8. Create Markdown files from `templates/topic.md`.
9. Publish tasks using the configured adapter only after approval.
10. Update `state/progress.json` only from verified evidence.
11. Replan dates without rewriting topic dependencies unless evidence or the goal changes.

## Optional intake fields and attachments

- Desired outcome, motivation, deadline, schedule preferences, accessibility needs, notes and attachments are optional.
- Missing optional fields must not block setup or generation.
- Attachments may include a job description, résumé, PDF, image, text file or syllabus.
- Do not download or persist an attachment unless its contents are needed.
- Store a summary or safe reference instead of the original file whenever possible.

## Safety and privacy

- Do not persist names, email addresses, phone numbers or raw submission payloads unless explicitly required and approved.
- Never commit API keys, tokens or webhook secrets.
- Prefer pull requests over direct writes to the default branch.
- Ask for review before destructive changes.

## Commands

Template or fork setup:

- `set up this fork as an Open Study Path instance`
- `set up this instance using Jotform`
- `set up this instance using the GitHub Issue Form`
- `validate this repository as a reusable template`

Instance operations:

- `import latest approved intake`
- `generate curriculum proposal`
- `publish tasks`
- `sync progress`
- `evaluate topic <id>`
- `replan study path`
- `generate retrospective`
