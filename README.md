# Open Study Path

Open-source, AI-assisted system for creating, managing and adapting personalized learning paths.

This repository is designed to be forked. Learners provide their goals, current context, available time and preferences through Jotform, GitHub Issue Forms or YAML. An AI agent then generates a topic-based curriculum, tasks, assessments and progress state.

## Start here

1. Fork this repository.
2. Fill in the onboarding form: https://form.jotform.com/262053811445048
3. Connect GitHub and, optionally, Jotform and Trello to ChatGPT.
4. Ask: `Initialize my study path using my latest form submission.`
5. Review the generated pull request before merging.

The GitHub Issue Form under `.github/ISSUE_TEMPLATE/` and direct editing of `study.config.yml` are fallback intake methods.

## Core principles

- GitHub is the source of truth.
- Topics are the primary learning unit; weeks are only scheduling views.
- Jotform is the default onboarding experience.
- GitHub Issues, Trello and Markdown are interchangeable task backends.
- Completion requires evidence of learning, not only activity completion.
- Raw form submissions and unnecessary personal data must not be committed.
- Generated changes should be reviewed through pull requests.

## Repository map

- `AGENTS.md`: operating contract for AI agents.
- `study.config.yml`: normalized learner, goal and integration settings.
- `instructions/manifest.yml`: ordered execution phases.
- `instructions/`: intake, diagnostic, generation, publishing, tracking and replanning rules.
- `schemas/`: machine-readable validation contracts.
- `templates/`: reusable topic structure.
- `study/`: generated roadmap and learning topics.
- `state/`: normalized intake, progress and external identifiers.

## First test case

The first validation will migrate and compare the curriculum from `diegomoura/ia-study`, a 16-week AI application engineering curriculum, into this generic topic-based structure.

## Privacy

Do not commit raw form submissions, access tokens, API keys, webhook secrets, email addresses or unnecessary personal data. Persist only the normalized fields required to generate and adapt the learning path.
