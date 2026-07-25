# Open Study Path

Open-source, AI-assisted template for creating, managing and adapting personalized learning paths.

> **This repository is the template, not a learning-path instance.** Do not generate a curriculum, learner configuration, progress state, Trello board or study tasks in this repository.

## How it works

Open Study Path has two explicit modes:

1. **Template mode** — the original reusable repository. It contains instructions, schemas and file templates only.
2. **Instance mode** — a fork or repository created from this template. Only an instance may contain a learner's configuration, generated roadmap, topics, progress and integration identifiers.

The marker `.open-study-path/template.yml` keeps this repository in template mode. An AI agent must not generate learner data while that marker is active and `.open-study-path/instance.yml` is absent.

## Start a new learning path

1. Fork this repository or create a repository from it.
2. Connect the new repository to ChatGPT.
3. Ask: `Set up this fork as an Open Study Path instance. Do not generate the curriculum yet.`
4. Choose an intake method:
   - create or duplicate a Jotform using `intake/jotform-form-spec.md`;
   - open the GitHub Issue Form in your own copy;
   - fill `study.config.yml` manually after instance setup.
5. Fill the selected intake method.
6. Ask the agent to import the latest approved intake and propose the curriculum in a pull request.

The reference Jotform used while developing the template is documented for maintainers, but each user should use a form in their own Jotform account and configure its ID in their own instance.

## What instance setup creates

Instance setup copies or creates the following files only inside the fork or derived repository:

- `.open-study-path/instance.yml`;
- `study.config.yml`, based on `study.config.example.yml`;
- `state/intake-summary.json`, based on `templates/state/intake-summary.json`;
- `state/progress.json`, based on `templates/state/progress.json`;
- `study/roadmap.md`, based on `templates/roadmap.md`;
- generated topic files under `study/topics/`.

Setup and curriculum generation are separate operations. Creating an instance must not automatically create a learning path.

## Core principles

- GitHub is the source of truth for each instance.
- Topics are the primary learning unit; weeks are scheduling projections only.
- Jotform, GitHub Issue Forms and YAML are interchangeable intake methods.
- GitHub Issues, Trello and Markdown are interchangeable task backends.
- Completion requires evidence of learning, not only activity completion.
- Raw form submissions and unnecessary personal data must not be committed.
- Generated changes should be reviewed through pull requests.

## Repository map

- `.open-study-path/template.yml`: template-mode guard.
- `AGENTS.md`: operating contract for AI agents.
- `study.config.example.yml`: configuration model copied during instance setup.
- `instructions/manifest.yml`: lifecycle and phase ordering.
- `instructions/`: setup, intake, diagnostic, generation, publishing, tracking and replanning rules.
- `schemas/`: machine-readable validation contracts.
- `templates/`: files used to initialize instance state and generated content.
- `intake/`: specifications for supported intake methods.

The template intentionally does not contain `study.config.yml`, `state/` or `study/` instance artifacts.

## Privacy

Do not commit raw form submissions, uploaded reference files, access tokens, API keys, webhook secrets, email addresses or unnecessary personal data. Persist only normalized information required to generate and adapt the learning path. Attachments are optional and should be read only when needed, then represented by safe metadata or summaries rather than copied into the repository by default.