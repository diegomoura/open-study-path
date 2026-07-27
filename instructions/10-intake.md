# Import intake

Run this phase only in instance mode and only after `instructions/05-configure-intake.md` has completed with `intake.setup_status: ready`.

Use the provider configured in the instance's `study.config.yml`. Never use a form ID, issue or submission belonging to the canonical template.

The owner command `Enviei o formulário. Localize e importe a única submissão válida.` explicitly approves the single submission that remains after deterministic provider-specific filtering. It does not authorize choosing an arbitrary newest submission.

## Jotform

- Fetch the configured `intake.form_id` and confirm it is accessible.
- Search that form for submissions that contain all required planning facts and are not already recorded in `state/intake-summary.json.source_reference`.
- Treat the explicitly supplied submission ID as a valid direct selection when the owner provides one.
- When exactly one valid unimported submission remains, import it automatically.
- When none remain, return the configured clickable form URL and ask the owner to submit it before retrying.
- When more than one remains, list concise candidate identifiers and submission times and ask the owner to select one. Do not combine submissions or choose the latest silently.
- Treat file uploads as optional.
- Read attached files only when their contents materially affect the plan.
- Do not commit raw submissions or uploaded files.

## GitHub Issue Form

Search only the instance repository. A candidate intake issue should satisfy all available deterministic signals:

- it is an issue, not a pull request;
- it has the `study-request` label;
- its title starts with `[Study Path]:`;
- its body contains the expected field headings from `.github/ISSUE_TEMPLATE/create-study-path.yml`;
- it is not already identified by `state/intake-summary.json.source_reference`;
- it does not have the `intake:imported` label.

Use an explicit issue number immediately when the owner supplies one, after verifying the same form signals.

When the owner reports that the form was submitted without a number:

1. search for all candidate issues using the signals above;
2. import automatically when exactly one valid candidate remains;
3. when none remain, return the direct Issue Form link from the exact instance repository and explain that no valid submission was found yet;
4. when more than one remains, list the candidate issue numbers, titles and creation times and ask the owner to choose one;
5. never select an arbitrary newest repository issue.

After a successful import, set `state/intake-summary.json.source: github_issue`, persist the exact issue reference in `source_reference`, ensure the `intake:imported` label exists and apply it to the imported issue. Keep `study-request` for auditability. Treat attachments as optional and do not copy them into the repository by default.

## Manual YAML

- Read the learner-approved values already entered in `study.config.yml`.
- Do not reinterpret placeholder defaults as confirmed learner facts.

## Required and optional facts

Required planning facts are the subject, detailed objective, current level, preferred language and weekly availability. Desired outcome, motivation, deadline, preferred days or periods, accessibility needs, notes, text references, URLs and attachments are optional.

Integration preferences are also optional for curriculum generation, but normalize them when provided:

- desired experience: `minimal`, `guided_recommendations` or `enriched`;
- free-tier-only policy;
- account-connection policy;
- services already used;
- capability categories the learner would consider connecting;
- preferred task backend, scheduler, reminder and email provider;
- services or data handling the learner wants to avoid.

Normalize approved intake with `intake/field-mapping.yml` into `study.config.yml` and `state/intake-summary.json`. Set `configured: true` only after the required planning facts are populated and validated. Mark assumptions visibly. Missing optional answers must not block generation; derive conservative defaults only when necessary and record them as assumptions.

Do not recommend, connect, probe or create external tools during intake. Preserve `auto` provider choices. The actual contextual recommendation is created only after diagnostic evidence and the curriculum structure are available, following `templates/integrations-plan.md`.

GitHub remains the source of truth regardless of the selected external providers. Normalize the following invariant fields without requiring the learner to repeat them:

- `integrations.source_of_truth.provider: github`;
- formative practice and habit results do not affect mastery;
- analytics projection direction is `github_to_airtable`;
- Mermaid is the canonical visual provider;
- task management has one authoritative backend.

Update `.open-study-path/instance.yml` with `status.intake_imported: true`.

## Pull request and merge

Create a pull request containing only:

- `study.config.yml`;
- `state/intake-summary.json`;
- `.open-study-path/instance.yml`.

Read `workflow.intake_merge_policy` from `.open-study-path/instance.yml` and apply the rules in `instructions/phase-completion.md`.

For `auto_when_unambiguous`, auto-merge only when:

- all required facts are present;
- configuration validation and CI pass;
- the diff contains only the three files above;
- `state/intake-summary.json` contains no material assumptions;
- no attachment or conflicting response requires interpretation.

An `auto` integration preference is not ambiguity: it explicitly delegates contextual recommendation until after diagnostic. A direct provider choice is also not ambiguous when it is valid and does not conflict with `avoid`, `no_external_accounts` or free-tier requirements.

If any condition fails, leave the PR open and explain the specific review needed. A request to import intake authorizes creating the PR; automatic merge is authorized only by the marker policy.

## Completion and optional diagnostic chaining

Do not begin the diagnostic until intake normalization, validation, PR review and required merge have completed successfully.

When the owner's command explicitly says to begin the diagnostic after completing this stage, and the intake PR is merged with `status.intake_imported: true`, immediately invoke `instructions/20-diagnostic.md` in the same conversation. State the proportional question budget and ask the first short diagnostic question. Do not generate the curriculum.

If no unique valid submission exists, the intake PR cannot be completed, or owner review is required, stop before diagnostic and surface the exact blocking action.

When the owner requested intake import only, follow `instructions/phase-completion.md` and guide them with:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`

By default, do not repeat every normalized field or changed file in chat. Report the resolved source, link the PR, state whether it was merged and surface only material attention items.