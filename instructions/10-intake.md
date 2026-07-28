# Import intake

Run this phase only in instance mode after intake setup is ready. Use only the configured form or approved manual configuration belonging to the instance.

The natural command `Preenchi o formulário. Pode continuar.` approves importing the single valid unimported submission found by deterministic filtering. It never authorizes choosing an arbitrary newest submission.

Continue accepting older technical intake commands as aliases.

## Jotform

- Fetch the configured form and confirm access.
- Find submissions containing all required planning facts and not already recorded in `state/intake-summary.json.source_reference`.
- Use an explicitly supplied submission ID when verified.
- Import automatically when exactly one valid candidate remains.
- When none remain, return the form link.
- When several remain, list only the concise information needed for the owner to choose.
- Do not combine submissions, select the newest silently or persist raw submissions and uploads.

## GitHub Issue Form

Search only the instance repository. A valid candidate should satisfy all available signals:

- it is an issue, not a pull request;
- it has the `study-request` label;
- its title starts with the current `[Nova trilha]` prefix or the legacy `[Study Path]:` prefix;
- its body contains the expected field headings from `.github/ISSUE_TEMPLATE/create-study-path.yml`;
- it is not already in `state/intake-summary.json.source_reference`;
- it does not have the `intake:imported` label.

Use an explicit issue number immediately when provided, after verifying the form signals.

When the form was reported as submitted:

1. search all candidates using the signals above;
2. import automatically when exactly one valid candidate remains;
3. when none remain, return the direct form link and explain that no valid submission was found yet;
4. when more than one remains, list candidate number, title and creation time and ask the owner to choose;
5. never select an arbitrary newest repository issue.

After import, persist the exact source reference, apply `intake:imported` and retain `study-request` for auditability. Treat attachments as optional and do not copy them into the repository by default.

## Manual YAML

Read only learner-approved values in `study.config.yml`. Do not interpret placeholders as confirmed facts.

## Planning facts

Required facts are subject, detailed objective, current level, preferred language and weekly availability. Other schedule, motivation, accessibility, reference and integration answers are optional.

Normalize approved answers through `intake/field-mapping.yml` into `study.config.yml` and `state/intake-summary.json`. Missing optional answers must not block the course. Record only necessary conservative assumptions.

Do not recommend, connect or probe external tools during intake. Keep delegated provider choices as `auto` until diagnostic and curriculum context exist.

Internal invariants such as GitHub authority, formative-practice limits, Mermaid canonical status, one primary task backend and `github_to_airtable` analytics are normalized without requiring the learner to repeat them. Do not surface those terms in the success response.

Update `.open-study-path/instance.yml` with completed intake status.

## Pull request and merge

Create a PR limited to the instance marker, `study.config.yml` and `state/intake-summary.json`. Apply `workflow.intake_merge_policy`. Auto-merge only when facts, validation, privacy, scope and assumptions are unambiguous.

Technical review belongs in GitHub. In chat, do not report changed files, CI or merge details after success unless requested or needed to explain a blocker.

## Diagnostic continuation

Do not begin diagnostic until import, validation and required merge complete.

When the command authorizes continuing, immediately run `instructions/20-diagnostic.md`, state the small question range and ask the first question.

When import only was requested, use:

`Vamos fazer meu diagnóstico.`

Continue accepting:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`

If no unique candidate exists or a real decision is required, stop and surface only the action that resolves it.

<!-- Compatibility markers: expected field headings; exactly one valid candidate; When none remain; more than one remains; state/intake-summary.json.source_reference; intake:imported; immediately invoke `instructions/20-diagnostic.md`. -->
