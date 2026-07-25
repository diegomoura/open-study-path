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
2. Create a dedicated ChatGPT Project for the new learning path.
3. Connect GitHub to ChatGPT and authorize the new repository.
4. Copy `templates/chatgpt-project-instructions.md` into the ChatGPT Project Instructions.
5. Replace `OWNER/REPOSITORY` with the exact repository identifier.
6. Open the first chat and ask:

   `Use the repository defined in this project's instructions. Set it up as an Open Study Path instance and ask me which intake provider to use. Do not import a submission or generate the curriculum yet.`

7. Choose an intake method when prompted:
   - **GitHub Issue Form** — zero configuration and available immediately in the fork;
   - **Jotform** — ChatGPT creates a new form in your connected Jotform account;
   - **Manual YAML** — edit `study.config.yml` directly.
8. Fill the selected intake method.
9. Ask the agent to import the approved intake.
10. Follow the exact next-step command returned by the agent for diagnostic, curriculum generation, publication and tracking.

Instance setup prepares the repository and the intake method. It does not import answers or generate the curriculum.

See `docs/chatgpt-project-setup.md` for the complete ChatGPT Project workflow.

## Guided lifecycle

The process is designed to be guided rather than requiring the owner to remember the lifecycle.

Every phase must end with:

- one brief result;
- a link to the primary artifact when one exists;
- material assumptions or blockers only;
- the current pull-request state;
- the next lifecycle phase;
- one exact command to continue.

Detailed normalized fields, diagnostic findings and file lists belong in the pull request, not in the default chat response. The shared response contract is `instructions/phase-completion.md` and is referenced by `instructions/manifest.yml`.

The standard lifecycle is:

`setup → intake import → diagnostic → curriculum proposal → task publication → progress tracking → replanning`

## Safe phase merge policies

New instances store operational policy in `.open-study-path/instance.yml`:

```yaml
workflow:
  guided: true
  intake_merge_policy: auto_when_unambiguous
  diagnostic_merge_policy: auto_when_unambiguous
```

Available policies:

- `manual` — always wait for owner review and merge;
- `auto_after_ci` — self-review and merge a phase-limited PR after required checks pass;
- `auto_when_unambiguous` — self-review and merge only after checks pass and no material assumption or contradiction requires review.

The defaults authorize safe automation only for narrowly scoped intake and diagnostic PRs. They do not authorize automatic curriculum generation, external integration creation, destructive changes or task publication.

## Bounded proportional diagnostic

The diagnostic is a placement step, not a comprehensive exam or a teaching session.

For learners declared as `none` or `beginner`, the normal target is 3–5 questions with a hard maximum of 7. Intermediate or advanced diagnostics normally use 4–7 questions with a hard maximum of 10. The agent must stop earlier when conceptual and applied evidence already support a responsible starting depth.

The hard maximum may be exceeded only when the owner explicitly requests a comprehensive assessment. The exception and total question count are recorded in `state/diagnostic-summary.json`. If uncertainty remains at the hard limit, the agent records limited evidence and chooses a conservative starting depth instead of continuing indefinitely.

Diagnostic results are validated against `schemas/diagnostic-summary.schema.json`. Raw dialogue is not committed.

## Repository identity

The ChatGPT Project name and description are optional labels for human organization. They may include the repository name, but they are not the repository source of truth.

Before the first setup, the exact `OWNER/REPOSITORY` identifier must be stored in the ChatGPT Project Instructions or provided explicitly in the first message.

During setup, the agent records the exact identifier in `.open-study-path/instance.yml`. After that marker exists, it becomes the persistent repository source of truth. A mismatch between the instance marker and the ChatGPT Project Instructions must stop write operations until the owner resolves it.

Use one ChatGPT Project per Open Study Path instance to avoid mixing conversations, files and integrations between learning paths.

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

After selecting `github_issue`, the agent must present a clickable direct link built from the exact instance repository:

`https://github.com/OWNER/REPOSITORY/issues/new?template=create-study-path.yml`

The response must explain that the form was inherited from the template, ask the owner to submit it and tell them to return with the created issue number. The agent must use an issue explicitly selected by the instance owner; it must not assume that the repository's newest issue is the intake response.

Integration questions name their provider explicitly. For example, selecting email summaries means Gmail because both the GitHub Issue Form and Jotform ask specifically about Gmail.

## What instance setup creates

Instance setup copies or creates the following files only inside the fork or derived repository:

- `.open-study-path/instance.yml`;
- `study.config.yml`, based on `study.config.example.yml`;
- `state/intake-summary.json`, based on `templates/state/intake-summary.json`;
- `state/progress.json`, based on `templates/state/progress.json`;
- `study/roadmap.md`, based on `templates/roadmap.md`.

`state/diagnostic-summary.json` is created only when the diagnostic completes. Topic files under `study/topics/` are created only after an approved intake, diagnostic and curriculum proposal.

## Core principles

- GitHub is the source of truth for each instance.
- Topics are the primary learning unit; weeks are scheduling projections only.
- GitHub Issue Forms, automatically created Jotforms and YAML are interchangeable intake methods.
- GitHub Issues, Trello and Markdown are interchangeable task backends.
- Completion requires evidence of learning, not only activity completion.
- Raw form submissions, diagnostic transcripts and unnecessary personal data must not be committed.
- Generated changes should be reviewed through pull requests unless a narrowly scoped merge policy explicitly permits safe automation.

## Repository map

- `.open-study-path/template.yml`: template-mode guard.
- `AGENTS.md`: operating contract for AI agents.
- `study.config.example.yml`: configuration model copied during instance setup.
- `instructions/manifest.yml`: lifecycle and phase ordering.
- `instructions/phase-completion.md`: guided response and next-step contract.
- `instructions/05-configure-intake.md`: automatic provider setup.
- `instructions/10-intake.md`: intake normalization and safe merge policy.
- `instructions/20-diagnostic.md`: bounded placement assessment and diagnostic merge policy.
- `intake/jotform-form-spec.yml`: executable form definition.
- `intake/field-mapping.yml`: provider-independent normalization contract.
- `.github/ISSUE_TEMPLATE/create-study-path.yml`: zero-config GitHub intake.
- `templates/state/diagnostic-summary.json`: reusable diagnostic artifact template.
- `schemas/diagnostic-summary.schema.json`: diagnostic artifact validation contract.
- `templates/chatgpt-project-instructions.md`: copyable ChatGPT Project Instructions.
- `docs/chatgpt-project-setup.md`: ChatGPT Project onboarding and identity rules.
- `schemas/`: machine-readable validation contracts.
- `templates/`: files used to initialize instance state and generated content.

The template intentionally does not contain `study.config.yml`, `state/` or `study/` instance artifacts.

## Privacy

Do not commit raw form submissions, diagnostic transcripts, uploaded reference files, access tokens, API keys, webhook secrets, email addresses or unnecessary personal data. Persist only normalized information required to generate and adapt the learning path. Attachments are optional and should be read only when needed, then represented by safe metadata or summaries rather than copied into the repository by default.
