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

## Guided lifecycle

Read `instructions/manifest.yml` and its `completion_contract` before executing a lifecycle phase.

At the end of every phase, follow `instructions/phase-completion.md`:

- keep the response brief and action-oriented;
- link the primary artifact;
- mention only material assumptions or blockers;
- identify the next lifecycle phase;
- provide one exact command the owner can send to continue;
- state whether a pull request was merged or remains open for one specific decision;
- stop at the requested phase boundary.

Internal validation, review, correction and safe merge required by the current phase are part of that phase and must be completed before responding. Do not repeat every normalized field, diagnostic finding, topic or changed file in chat by default. Put detailed audit information in the pull request description and diff. Do not send a separate transition message before repository work.

## Instance setup workflow

When explicitly asked to set up a fork as an instance:

1. Resolve and verify the repository target using the rules above.
2. Confirm the repository is not the canonical template repository named in `.open-study-path/template.yml`.
3. Create `.open-study-path/instance.yml` with the source template, exact repository, setup timestamp and workflow defaults from `templates/instance.yml`.
4. Copy `study.config.example.yml` to `study.config.yml` without inventing learner answers.
5. Copy `templates/state/intake-summary.json` to `state/intake-summary.json`.
6. Copy `templates/state/progress.json` to `state/progress.json`.
7. Copy `templates/roadmap.md` to `study/roadmap.md`.
8. Create `study/topics/` only when the first topic is generated.
9. Configure the intake method using `instructions/05-configure-intake.md`.
10. Stop after the intake method is ready. Do not import answers or generate a curriculum unless explicitly requested.

If the owner explicitly asks to create only the instance files and postpone intake configuration, stop after step 8 and leave `intake.provider: unset`.

## GitHub Issue Form rules

- Confirm `.github/ISSUE_TEMPLATE/create-study-path.yml` exists before marking `github_issue` ready.
- Read the exact repository identity from `.open-study-path/instance.yml`.
- Build the direct URL as `https://github.com/OWNER/REPOSITORY/issues/new?template=create-study-path.yml`, replacing the placeholder with the instance repository.
- Always return that URL as a clickable link after setup.
- Explain that the Issue Form was inherited from the template.
- Ask the owner to submit the form and return with the explicit issue number.
- Never assume the newest issue is the approved intake.
- Do not create or submit an issue, import answers or generate a curriculum during provider setup unless explicitly requested.

## Automatic Jotform rules

- Never require the owner to duplicate a maintainer-owned form or manually copy its ID.
- Confirm Jotform access in ChatGPT before attempting creation.
- If Jotform is not connected, instruct the owner to authorize the app and stop; never request an API key.
- Before creating a form, verify whether the instance already has a valid `form_id` or an exact matching form in the owner's account.
- Create the form from the versioned specification in `intake/jotform-form-spec.yml`.
- Save only the created form ID, URL and specification version in the instance.
- Do not create a submission or import answers during form setup.

## Intake pull-request policy

Read `workflow.intake_merge_policy` from `.open-study-path/instance.yml`.

- `manual`: open the intake PR and wait for the owner to review and merge it.
- `auto_after_ci`: merge after required checks pass and the diff contains only files allowed by the intake phase.
- `auto_when_unambiguous`: merge only after required checks pass, the diff is phase-limited, all required facts are present, no material assumptions exist, and no attachment or conflicting response requires interpretation.

The default for new instances is `auto_when_unambiguous`. If the marker is missing this setting, use `manual` rather than guessing.

Never auto-merge curriculum generation, destructive changes or external-resource creation under the intake policy.

## Proportional diagnostic rules

Read `instructions/20-diagnostic.md` and `workflow.diagnostic_merge_policy` before starting.

- Treat the diagnostic as placement, not teaching or an exhaustive exam.
- Use intake and reliable prior evidence before asking questions.
- Ask one short question at a time without praising, restating or interpreting every answer.
- For `none` or `beginner`, target 3–5 questions and never exceed 7 without an explicit comprehensive-assessment request.
- For `intermediate` or `advanced`, target 4–7 questions and never exceed 10 without an explicit comprehensive-assessment request.
- Stop early as soon as a responsible starting depth is supported by conceptual and applied evidence.
- At the hard limit, choose a conservative depth and record limited evidence instead of continuing indefinitely.
- Create `state/diagnostic-summary.json` from the reusable template and validate it against `schemas/diagnostic-summary.schema.json`.
- Do not persist the raw transcript or conversational filler.

The diagnostic PR may change only `.open-study-path/instance.yml` and `state/diagnostic-summary.json`.

For `workflow.diagnostic_merge_policy: auto_when_unambiguous`, self-review and merge after CI only when the summary validates, the budget is respected or has an allowed exception, the diff is phase-limited, the starting depth is supported and no unresolved contradiction needs owner review.

## Automatic curriculum generation, review and merge

Generation is one user-facing phase that includes proposal creation, internal review, correction, validation and safe merge.

- Read `instructions/30-generate-path.md`, `instructions/35-review-curriculum.md` and `workflow.curriculum_merge_policy` before starting.
- Create the curriculum PR as a draft and set `status.curriculum_proposed: true` with `status.curriculum_approved: false` while drafting.
- State when the proposal is only an introductory cycle.
- Use realistic effort for the configured weekly availability.
- Required resources must identify a specific work and canonical locator; edition, translation and URL may remain pending.
- Review the proposal automatically against intake, diagnostic and the topic contract.
- Correct every issue that can be resolved from existing evidence.
- Run all required checks, self-review the final diff and keep the diff limited to `.open-study-path/instance.yml`, `study/roadmap.md` and `study/topics/`.
- For `workflow.curriculum_merge_policy: agent_review_then_merge`, set `status.curriculum_approved: true`, rerun checks, mark the draft ready and merge when no pedagogical decision remains unresolved.
- Do not formally approve a PR authored by the same account.
- Do not ask the owner to send a separate review command, correct the branch or merge the PR merely because it exists.
- Leave the PR open only when scope, structure, effort or resources require a genuine owner decision; ask one concise, specific question.
- Do not publish tasks or create external integrations during generation.

## Integration preflight and task publication

Task publication is one user-facing phase. Connection verification is an internal prerequisite, not a separate confirmation phase.

- Read `instructions/40-publish-tasks.md` and `instructions/42-integration-preflight.md` before any external write.
- Derive required connections only from enabled providers in `study.config.yml`.
- Verify actual authorization through one harmless read-only operation per required connector. A configuration value, installed app or available tool definition is not sufficient proof of access.
- GitHub Issues require repository access; Trello requires a Trello read; enabled Google Calendar requires a Calendar read; enabled Gmail requires a Gmail read. Markdown, chat and disabled providers require no external probe.
- Complete all required probes before creating any board, card, issue, event, email or integration-state write.
- If any probe fails, create no external resources and do not partially publish through connected providers unless the owner explicitly requests partial publication.
- Name only the unavailable providers, tell the owner to connect or authorize them in the current ChatGPT Project and provide: `Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação das tarefas sem alterar o currículo.`
- Never request API keys, tokens, passwords or copied credentials.
- When the owner sends the standard return command, re-run the probes rather than trusting the statement. If every probe passes, continue the pending publication automatically under the original authorization, without another confirmation or an intermediate connection-success response.
- Before writes, reuse valid identifiers from `state/integrations.json` and exact matching provider resources to prevent duplicates.
- If publication fails after writes begin, report exactly which resources were created and which remain pending. Do not claim rollback unless it actually occurred.

## Instance source of truth

1. `.open-study-path/instance.yml` identifies the repository instance and workflow policy.
2. `study.config.yml` contains normalized learner and integration preferences.
3. `instructions/manifest.yml` defines the user-facing phases and internal review contracts.
4. `state/diagnostic-summary.json` contains bounded placement evidence after diagnosis.
5. `state/progress.json` contains machine-readable progress.
6. `study/roadmap.md` and `study/topics/` contain the proposed or approved curriculum.
7. Raw submissions, diagnostic transcripts and uploaded files must never be committed by default.

## Curriculum workflow in instance mode

1. Read `instructions/manifest.yml` and `instructions/phase-completion.md`.
2. Confirm the selected intake provider has `setup_status: ready`.
3. Read the explicitly selected or approved intake.
4. Normalize planning facts into `study.config.yml` and `state/intake-summary.json`.
5. Validate configuration against `schemas/study-config.schema.json`.
6. Run a bounded proportional diagnostic or use reliable existing evidence.
7. Generate a dependency-aware topic graph in a draft PR.
8. Automatically review, correct, validate and safely merge the curriculum PR using `instructions/35-review-curriculum.md`.
9. During publication, run the integration preflight and continue automatically when every required connection is available.
10. Publish tasks using the configured adapter only after curriculum approval.
11. Update `state/progress.json` only from verified evidence.
12. Replan dates without rewriting topic dependencies unless evidence or the goal changes.

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

- `import issue #<number> as approved intake`
- `start the proportional diagnostic`
- `generate curriculum proposal`
- `publish tasks`
- `sync progress`
- `evaluate topic <id>`
- `replan study path`
- `generate retrospective`
