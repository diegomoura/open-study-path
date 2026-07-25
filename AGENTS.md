# Agent Operating Contract

Read this file first whenever asked to initialize, generate, synchronize or replan a study path.

## Source of truth

1. `study.config.yml` contains normalized learner and integration preferences.
2. `instructions/manifest.yml` defines the execution phases.
3. `state/progress.json` contains machine-readable progress.
4. `study/topics/` contains generated learning units.
5. Raw Jotform submissions must never be committed.

## Required workflow

1. Read `instructions/manifest.yml`.
2. Resolve the selected intake provider.
3. Normalize intake data into `study.config.yml`.
4. Validate configuration against `schemas/study-config.schema.json`.
5. Generate a dependency-aware topic graph.
6. Create Markdown files from `templates/topic.md`.
7. Publish tasks using the configured adapter.
8. Update `state/progress.json` only from verified evidence.
9. Replan dates without rewriting topic dependencies unless the learning goal changes.

## Safety and privacy

- Do not persist names, email addresses, phone numbers or raw submission payloads unless explicitly required and approved.
- Never commit API keys, tokens or webhook secrets.
- Prefer pull requests over direct writes to the default branch.
- Ask for review before destructive changes.

## Commands

- `initialize study path`
- `generate curriculum`
- `publish tasks`
- `sync progress`
- `evaluate topic <id>`
- `replan study path`
- `generate retrospective`
