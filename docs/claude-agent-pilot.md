# Agent pilot: real API calls for one setup phase

Stage 2 of the multi-agent work proposal (see the proposal document shared
outside this repository, section 7, step 2). Stage 1
(`docs/agent-model-configuration.md`) was pure model-selection logic with no
API calls. This is the first workflow that actually sends a request to the
Anthropic API and acts on what comes back.

## Scope

Two manifest phases only, chosen because their allowed diff is small and
mechanical (`instructions/02-setup-execution.md`, "Allowed setup diff"):

- `bootstrap_instance`
- `configure_intake`

Nothing else in `instructions/manifest.yml` is wired to a real agent call
yet. Extending to `intake`, `diagnostic`, `publish`, and eventually `generate`
is later work (proposal, section 7, steps 4-6) and should follow the same
pattern once this pilot's cost/quality numbers are measured.

`configure_intake` in this pilot always resolves as if the owner already
selected the `github_issue` provider. The instruction file
(`instructions/05-configure-intake.md`) lets the owner choose interactively
among three providers; an unattended GitHub Actions run has no one to ask, so
the author prompt does not present a choice. If your instance needs Jotform
or manual YAML intake, run that phase manually (ChatGPT Project or a Claude
chat) until a later stage adds a `workflow_dispatch` input for provider
selection.

## Files

- `scripts/agent_runtime.py` -- the harness. Two tool sets: authors get
  `read_file` / `list_dir` / `write_file` / `finish_phase`; reviewers get
  `read_file` / `list_dir` / `submit_review`. Every `write_file` call is
  checked against a hard-coded allowlist mirroring
  `instructions/02-setup-execution.md` *before* touching disk -- the model
  cannot write outside it no matter what it asks for. This is a deliberate
  extra guardrail beyond the CI validators: those catch a bad diff after the
  fact, this stops one from being written at all.
- `scripts/build_agent_prompt.py` -- assembles the system/user prompt from
  the real instruction files (`AGENTS.md`, `instructions/00-bootstrap.md` or
  `instructions/05-configure-intake.md`, `instructions/02-setup-execution.md`,
  `instructions/phase-completion.md` for the author;
  `instructions/04-review-generated-artifacts.md` and
  `docs/review-framework.md` for the reviewer). It reads these files at
  workflow run time rather than duplicating their text, so the automated path
  can't silently drift from the manual (ChatGPT Project) path.
- `.github/workflows/agent-pilot-setup.yml` -- `workflow_dispatch` only. Two
  sequential jobs, `author` then `reviewer`, each its own `run_agent()` call
  with its own fresh message history. The reviewer job never receives the
  author job's transcript or reasoning -- only the diff (`git diff
  base...HEAD`) and the author's one-line self-reported summary, which the
  reviewer prompt explicitly labels untrusted and to be verified
  independently, per `docs/review-framework.md`.

## What this pilot deliberately does not do yet

- **No auto-merge.** The workflow opens a pull request and records the
  reviewer's verdict in `state/reviews/agent-pilot-<phase>.yml` and in the PR
  body, but a human merges it. `instructions/03-await-ci-and-merge.md`'s
  automatic-merge policies are not invoked from this workflow. Wiring that up
  is a follow-up once the pilot's review quality has been checked against a
  few real runs (proposal, section 7, step 3).
- **No fork trigger.** `workflow_dispatch` requires repository write access
  to invoke, which is the cheapest way to keep `ANTHROPIC_API_KEY` away from
  untrusted input for this first pilot. Issue- or label-triggered runs are
  future work once the manual pilot is validated.
- **No cost/usage capture yet.** `agent_runtime.py` does not currently log
  the `usage` field from the API response. Add that before step 3 of the
  proposal ("medir o piloto") needs real numbers.

## Required repository secret

`ANTHROPIC_API_KEY` -- add it under **Settings -> Secrets and variables ->
Actions** on the repository that will run this workflow. Set a spend limit
for it in the Anthropic Console (proposal, section 6) before running this
against anything but a disposable test repository. Never put the key in a
committed file, an issue, or a workflow log.

## Running it

1. Confirm the secret above is set.
2. Actions tab -> "Agent pilot - setup phase" -> Run workflow.
3. Choose `phase` (`bootstrap_instance` or `configure_intake`) and give
   `target_repo` as `OWNER/REPOSITORY` for the instance you're bootstrapping
   or configuring. `extra_context` is optional free text passed straight to
   the author agent (e.g. a course name if you already know it).
4. The workflow opens a pull request with the author's diff and the
   independent review. Read `state/reviews/agent-pilot-<phase>.yml` for the
   reviewer's checks and any blocking findings before merging.

## Testing

`scripts/test_agent_runtime.py` covers the harness offline -- allowlist
enforcement, the tool-use loop, the budget cap, and the reviewer's
`approved` + non-empty `blocking_findings` rejection -- using a scripted fake
transport so no `ANTHROPIC_API_KEY` or network access is needed to run:

```
python scripts/test_agent_runtime.py
```

There is currently no automated end-to-end test that calls the real API;
that would cost real tokens on every CI run. Validate real-API behavior by
running the workflow against a disposable test repository first.
