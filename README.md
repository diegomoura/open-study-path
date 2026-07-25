# Open Study Path

Open-source, AI-assisted template for creating, managing and adapting personalized learning paths.

> **This repository is the template, not a learning-path instance.** Do not generate a curriculum, learner configuration, progress state, Jotform, Trello board or study tasks in this repository.

## How it works

Open Study Path has two explicit modes:

1. **Template mode** — the original reusable repository. It contains instructions, schemas and file templates only.
2. **Instance mode** — a fork or repository created from this template. Only an instance may contain a learner's configuration, generated roadmap, topics, progress and integration identifiers.

The marker `.open-study-path/template.yml` keeps this repository in template mode. An AI agent must not generate learner data while that marker is active and `.open-study-path/instance.yml` is absent.

## Start a new learning path

1. Fork this repository or create a repository from it.
2. Connect the new repository to ChatGPT.
3. Ask: `Set up this fork as an Open Study Path instance.`
4. Choose an intake method when prompted:
   - **GitHub Issue Form** — zero configuration and available immediately in the fork;
   - **Jotform** — ChatGPT creates a new form in your connected Jotform account;
   - **Manual YAML** — edit `study.config.yml` directly.
5. Fill the selected intake method.
6. Ask the agent to import the approved intake and propose the curriculum in a pull request.

Instance setup prepares the repository and the intake method. It does not import answers or generate the curriculum.

## Automatic Jotform setup

The template does not contain a maintainer-owned form ID. Instead, it contains an executable, versioned specification in `intake/jotform-form-spec.yml`.

When the instance owner selects Jotform, the agent must:

1. confirm that the Jotform app is connected to ChatGPT;
2. ask the owner to authorize it when access is unavailable;
3. verify that the instance does not already have a valid form;
4. create a form in the owner's Jotform account from the specification;
5. save only the form ID, URL and specification version in `study.config.yml`;
6. present the form URL and stop before importing a submission.

No API key or token is stored in the repository. Re-running setup must not create duplicate forms when the configured form is still valid.

## GitHub Issue Form fallback

`.github/ISSUE_TEMPLATE/create-study-path.yml` is copied with every fork or repository created from the template. It is the recommended zero-configuration intake method and requires no external account.

The agent must use an issue explicitly selected by the instance owner; it must not assume that the repository's newest issue is the intake response.

## What instance setup creates

Instance setup copies or creates the following files only inside the fork or derived repository:

- `.open-study-path/instance.yml`;
- `study.config.yml`, based on `study.config.example.yml`;
- `state/intake-summary.json`, based on `templates/state/intake-summary.json`;
- `state/progress.json`, based on `templates/state/progress.json`;
- `study/roadmap.md`, based on `templates/roadmap.md`.

Topic files under `study/topics/` are created only after an approved intake and curriculum proposal.

## Core principles

- GitHub is the source of truth for each instance.
- Topics are the primary learning unit; weeks are scheduling projections only.
- GitHub Issue Forms, automatically created Jotforms and YAML are interchangeable intake methods.
- GitHub Issues, Trello and Markdown are interchangeable task backends.
- Completion requires evidence of learning, not only activity completion.
- Raw form submissions and unnecessary personal data must not be committed.
- Generated changes should be reviewed through pull requests.

## Repository map

- `.open-study-path/template.yml`: template-mode guard.
- `AGENTS.md`: operating contract for AI agents.
- `study.config.example.yml`: configuration model copied during instance setup.
- `instructions/manifest.yml`: lifecycle and phase ordering.
- `instructions/05-configure-intake.md`: automatic provider setup.
- `intake/jotform-form-spec.yml`: executable form definition.
- `intake/field-mapping.yml`: provider-independent normalization contract.
- `.github/ISSUE_TEMPLATE/create-study-path.yml`: zero-config GitHub intake.
- `schemas/`: machine-readable validation contracts.
- `templates/`: files used to initialize instance state and generated content.

The template intentionally does not contain `study.config.yml`, `state/` or `study/` instance artifacts.

## Privacy

Do not commit raw form submissions, uploaded reference files, access tokens, API keys, webhook secrets, email addresses or unnecessary personal data. Persist only normalized information required to generate and adapt the learning path. Attachments are optional and should be read only when needed, then represented by safe metadata or summaries rather than copied into the repository by default.
