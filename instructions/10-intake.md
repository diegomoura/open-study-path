# Import intake

Run this phase only in instance mode after intake setup is ready. Use only the configured form or approved manual configuration belonging to the instance.

The natural command `Preenchi o formulário. Pode continuar.` approves importing the single valid unimported submission found by deterministic filtering. It never authorizes choosing an arbitrary newest submission.

## Jotform

- Fetch the configured form and confirm access.
- Find submissions containing all required planning facts and not already recorded in `state/intake-summary.json.source_reference`.
- Use an explicitly supplied submission ID when verified.
- Import automatically when exactly one valid candidate remains.
- When none remain, return the form link.
- When several remain, list only the concise information needed for the owner to choose.
- Do not combine submissions, select the newest silently or persist raw submissions and uploads.

## GitHub Issue Form

Search only the instance repository. Apply the algorithm in `scripts/intake_resolution.py`; do not replace it with similarity or newest-issue heuristics.

A valid candidate must satisfy all of these identity and state checks:

- it is an issue, not a pull request;
- its body contains exactly one supported marker: `<!-- open-study-path:intake form_id=create-study-path version=4 -->`;
- its body contains the expected field headings from `.github/ISSUE_TEMPLATE/create-study-path.yml`;
- its issue title contains a non-empty course name;
- it is not already identified by `state/intake-summary.json.source_reference`;
- it does not have the `intake:imported` label.

Treat the trimmed issue title as the synthetic field `issue_title` and map it to `path.name` through `intake/field-mapping.yml`. Preserve the learner's title as the course name. Do not add a prefix or generic suffix. Do not rewrite the issue title during import.

For a uniquely resolved candidate, the `study-request` label is a repairable consistency signal. Add it when missing only after unique selection.

Only the current marked form is supported. Reject a missing, duplicated, malformed, differently versioned or differently identified marker. Matching headings alone, a unique recent issue or similar answers never establish identity. An explicit issue number narrows the search but does not bypass current marker, heading, title or import-state checks.

### Selection and import

When the form was reported as submitted:

1. classify candidates using the current marker and state rules above;
2. import automatically when exactly one valid candidate remains;
3. When none remain, return the direct form link and explain that no verifiable submission was found yet;
4. when more than one remains, list candidate number, title and creation time and ask the owner to choose;
5. never select an arbitrary newest repository issue.

After import, persist the exact source reference, apply `intake:imported` and retain `study-request` for auditability. Treat attachments as optional and do not copy them into the repository by default.

## Manual YAML

Read only learner-approved values in `study.config.yml`. Do not interpret placeholders as confirmed facts.

## Planning facts

Required facts are course name, complete learning request, concise subject, current level and preferred language. Objective details, desired outcome, motivation, time constraints, accessibility, references, learning preferences and integration answers are optional.

Preserve the complete answer to “O que você quer aprender?” in `path.learning_request`. Derive `path.subject` as a short factual topic label of at most 120 characters. Do not replace the original answer with the summary and do not add scope that the learner did not request.

Normalize approved answers through the provider-specific mappings in `intake/field-mapping.yml` into `study.config.yml` and `state/intake-summary.json`. Normalize language to `pt-BR` or `en`. Missing optional answers must not block the course. Record only necessary conservative assumptions.

A value in `path.time_constraints` is planning context, not permission to remove mastery-required content or claim that an unrealistic course fits the available time. Preserve the complete dependency-aware course, identify a sensible priority order when useful and explain feasibility honestly. Create a dated or weekly projection only after an explicit request and the minimum scheduling details are known.

Do not recommend, connect or probe external tools during intake. Keep delegated provider choices as `auto` until diagnostic and curriculum context exist. An empty learning-format selection delegates the choice to the course generator. The theory/practice balance defaults to `balanced`.

When the learner chooses not to connect other accounts, normalize `integration_preferences.account_connections: no_external_accounts`. Do not later suggest, probe or write to providers that require another account; use GitHub Issues or the repository-native Markdown fallback. Otherwise use `ask_per_provider`, preserving explicit tool constraints in `integration_preferences.notes`.

Internal invariants such as GitHub authority, formative-practice limits, Mermaid canonical status, Trello preference with GitHub Issues and then Markdown as task fallbacks, one primary task backend and `github_to_airtable` analytics are normalized without requiring the learner to repeat them. Do not surface those terms in the success response.

Update `.open-study-path/instance.yml` with completed intake status.

## Pull request and merge

Create a PR limited to the instance marker, `study.config.yml`, `state/intake-summary.json` and one intake review artifact under `state/reviews/`. Apply `workflow.intake_merge_policy`.

After authoring, run `instructions/04-review-generated-artifacts.md` with the `intake` profile. The reviewer must compare the selected source with every normalized learner fact, integration preference, assumption and consent decision. It must also verify that `path.learning_request` preserves the original answer, `path.subject` is only a concise label and time constraints were not converted into silent scope loss. Auto-merge only when facts, validation, privacy, scope, assumptions and generated diff coverage are unambiguous.

Technical review belongs in GitHub. In chat, do not report changed files, CI or merge details after success unless requested or needed to explain a blocker.

## Diagnostic continuation

Do not begin diagnostic until import, independent intake review, validation and required merge complete.

When the command authorizes continuing, immediately run `instructions/20-diagnostic.md`, state the small question range and ask the first question.

When import only was requested, use:

`Vamos fazer meu diagnóstico.`

If no unique candidate exists or a real decision is required, stop and surface only the action that resolves it.

<!-- Contract markers: expected field headings; exactly one valid candidate; When none remain; more than one remains; state/intake-summary.json.source_reference; intake:imported; immediately invoke `instructions/20-diagnostic.md`; auto_when_unambiguous; repairable consistency signals; unsupported. -->
