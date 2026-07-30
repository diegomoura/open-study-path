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

Search only the instance repository. Apply the algorithm in `scripts/intake_resolution.py`; do not replace it with similarity or newest-issue heuristics.

### Current version 3 submissions

A current candidate must satisfy all of these identity and state checks:

- it is an issue, not a pull request;
- its body contains exactly one supported marker: `<!-- open-study-path:intake form_id=create-study-path version=3 -->`;
- its body contains the expected field headings from `.github/ISSUE_TEMPLATE/create-study-path.yml`;
- its issue title contains a non-empty course name;
- it is not already identified by `state/intake-summary.json.source_reference`;
- it does not have the `intake:imported` label.

Treat the trimmed issue title as the synthetic field `issue_title` and map it to `path.name` through `intake/field-mapping.yml`. Preserve the learner's title as the course name. Do not add `[Nova trilha]`, another prefix or a generic suffix. Do not rewrite the issue title during import.

For a uniquely resolved current candidate, the `study-request` label is a repairable consistency signal. Add it when missing only after unique selection.

### Compatible marked version 2 submissions

Continue accepting exactly one supported older marker:

`<!-- open-study-path:intake form_id=create-study-path version=2 -->`

For version 2, use the non-empty `path_name` answer as `path.name`. When that optional answer is empty, remove the known `[Nova trilha]` or `[Study Path]:` prefix from the issue title and use the non-empty remainder. If neither source yields a course name, stop and ask the owner to provide one; do not invent it.

The version 2 title and discovery label remain compatibility signals. Add a missing `study-request` label after unique selection, but do not rewrite the issue title or the learner's answers.

If any `open-study-path:intake` marker is present but its form ID, version, count or syntax is unsupported, reject that issue. Do not reinterpret it as an unmarked legacy submission.

### Legacy unmarked submissions

An issue without an intake marker is a valid legacy candidate only when every legacy identity signal is present together:

- label `study-request`;
- legacy `[Nova trilha]` or `[Study Path]:` title prefix;
- expected form field headings;
- no prior source reference;
- no `intake:imported` label.

Matching headings alone, a unique recent issue, similar answers or an edited title are never sufficient legacy identity. Do not silently weaken the filter because only one issue looks plausible.

An explicit issue number narrows the search but does not bypass current, compatible or legacy identity checks.

### Selection and import

When the form was reported as submitted:

1. classify all candidates using the current-marker, compatible-marker and legacy rules above;
2. import automatically when exactly one valid candidate remains;
3. when none remain, return the direct form link and explain that no verifiable submission was found yet;
4. when more than one remains, list candidate number, title and creation time and ask the owner to choose;
5. never select an arbitrary newest repository issue.

After import, persist the exact source reference, apply `intake:imported` and retain `study-request` for auditability. Treat attachments as optional and do not copy them into the repository by default.

## Manual YAML

Read only learner-approved values in `study.config.yml`. Do not interpret placeholders as confirmed facts.

## Planning facts

Required facts are course name, subject, detailed objective, current level, preferred language and weekly availability. Other schedule, motivation, accessibility, reference and integration answers are optional.

Normalize approved answers through the provider-specific mappings in `intake/field-mapping.yml` into `study.config.yml` and `state/intake-summary.json`. Missing optional answers must not block the course. Record only necessary conservative assumptions.

Do not recommend, connect or probe external tools during intake. Keep delegated provider choices as `auto` until diagnostic and curriculum context exist.

Internal invariants such as GitHub authority, formative-practice limits, Mermaid canonical status, one primary task backend and `github_to_airtable` analytics are normalized without requiring the learner to repeat them. Do not surface those terms in the success response.

Update `.open-study-path/instance.yml` with completed intake status.

## Pull request and merge

Create a PR limited to the instance marker, `study.config.yml`, `state/intake-summary.json` and one intake review artifact under `state/reviews/`. Apply `workflow.intake_merge_policy`.

After authoring, run `instructions/04-review-generated-artifacts.md` with the `intake` profile. The reviewer must compare the selected source with every normalized learner fact, integration preference, assumption and consent decision. Auto-merge only when facts, validation, privacy, scope, assumptions and generated diff coverage are unambiguous.

Technical review belongs in GitHub. In chat, do not report changed files, CI or merge details after success unless requested or needed to explain a blocker.

## Diagnostic continuation

Do not begin diagnostic until import, independent intake review, validation and required merge complete.

When the command authorizes continuing, immediately run `instructions/20-diagnostic.md`, state the small question range and ask the first question.

When import only was requested, use:

`Vamos fazer meu diagnóstico.`

Continue accepting:

`Inicie o diagnóstico proporcional desta trilha. Faça perguntas curtas, uma por vez. Não gere a trilha ainda.`

If no unique candidate exists or a real decision is required, stop and surface only the action that resolves it.

<!-- Compatibility markers: expected field headings; exactly one valid candidate; When none remain; more than one remains; state/intake-summary.json.source_reference; intake:imported; immediately invoke `instructions/20-diagnostic.md`; auto_when_unambiguous; repairable consistency signals; unsupported. -->
