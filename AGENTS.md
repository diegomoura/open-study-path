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

## Resolve the repository target

A ChatGPT Project should manage one Open Study Path instance.

Before the instance marker exists, resolve the target repository from one of these explicit sources:

1. the exact `OWNER/REPOSITORY` value in the ChatGPT Project Instructions;
2. an exact repository identifier supplied by the owner in the current message.

The ChatGPT Project name and description are human-facing labels only. Do not infer the repository target from them when an exact identifier is absent.

Before writing files:

1. confirm the repository is accessible through the connected GitHub account;
2. confirm it is not the canonical template repository;
3. confirm the repository being modified matches the explicit `OWNER/REPOSITORY` identifier.

During bootstrap, write the exact repository identifier to `.open-study-path/instance.yml`.

After `.open-study-path/instance.yml` exists, its `repository` field is the persistent repository source of truth. If it conflicts with the ChatGPT Project Instructions or the current request, stop all write operations and ask the owner to resolve the mismatch.

Do not manage multiple unrelated Open Study Path instances from the same ChatGPT Project unless the repository explicitly implements a multi-instance extension.

## Instance setup workflow

When explicitly asked to set up a fork as an instance:

1. Resolve and verify the repository target using the rules above.
2. Confirm the repository is not the canonical template repository named in `.open-study-path/template.yml`.
3. Create `.open-study-path/instance.yml` with the source template, exact repository and setup timestamp.
4. Copy `study.config.example.yml` to `study.config.yml` without inventing learner answers.
5. Copy `templates/state/intake-summary.json` to `state/intake-summary.json`.
6. Copy `templates/state/progress.json` to `state/progress.json`.
7. Copy `templates/roadmap.md` to `study/roadmap.md`.
8. Create `study/topics/` only when the first topic is generated.
9. Configure the intake method using `instructions/05-configure-intake.md`:
   - GitHub Issue Form is the zero-configuration default;
   - Jotform is created automatically in the owner's connected Jotform account from `intake/jotform-form-spec.yml`;
   - manual YAML remains available.
10. Stop after the intake method is ready. Do not import answers or generate a curriculum unless explicitly requested.

If the owner explicitly asks to create only the instance files and postpone intake configuration, stop after step 8 and leave `intake.provider: unset`.

## Automatic Jotform rules

- Never require the owner to duplicate a maintainer-owned form or manually copy its ID.
- Confirm Jotform access in ChatGPT before attempting creation.
- If Jotform is not connected, instruct the owner to authorize the app and stop; never request an API key.
- Before creating a form, verify whether the instance already has a valid `form_id` or an exact matching form in the owner's account.
- Create the form from the versioned specification in `intake/jotform-form-spec.yml`.
- Save only the created form ID, URL and specification version in the instance.
- Do not create a submission or import answers during form setup.

## Instance source of truth

1. `.open-study-path/instance.yml` identifies the repository instance.
2. `study.config.yml` contains normalized learner and integration preferences.
3. `instructions/manifest.yml` defines the execution phases.
4. `state/progress.json` contains machine-readable progress.
5. `study/topics/` contains generated learning units.
6. Raw Jotform submissions and uploaded files must never be committed by default.

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