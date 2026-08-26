# Set up the agent pilot for an Open Study Path instance

Every `instructions/manifest.yml` phase runs as an isolated Claude API call
dispatched through GitHub Actions -- author and reviewer never share
context, and the workflow does the dispatching instead of a human copying
prompts into a chat conversation. This is the only onboarding path this
repository supports (Etapa 8 removed the earlier manual chat flow entirely).

Read `docs/claude-agent-pilot.md` for the full design rationale and current
validation status of every phase. This document is only the setup path:
what to add, where, and how to run it.

## Why this needs a Secret

The repository itself calls the Anthropic API directly from a GitHub
Actions workflow, so it needs its own credential: an `ANTHROPIC_API_KEY`
stored as a repository Secret. The workflow already lives in the repository
(it ships with the template) and reads `AGENTS.md` / `instructions/*.md`
directly at run time -- there is nothing to copy or paste anywhere. Setup
is the Secret plus one workflow run.

## Required repository Secret

`ANTHROPIC_API_KEY` -- add it under **Settings -> Secrets and variables ->
Actions** on the instance repository (the same repository the workflow will
run in, not a separate driver repository).

Before running this against anything but a disposable test repository, set
a spend limit for that key in the Anthropic Console. Never put the key in a
committed file, an issue body, or a workflow log.

## Setup steps

1. Create a repository from `diegomoura/open-study-path` using the GitHub
   template. The `agent-pilot-*.yml` workflows are already part of the
   template; nothing extra to copy in.
2. Add `ANTHROPIC_API_KEY` as a repository Secret (above) and set its spend
   limit in the Anthropic Console. GitHub does not copy repository Secrets
   when generating from a template -- this has to be done on every new
   instance repository, even though the workflow file itself is already
   there.
3. Under **Settings -> Actions -> General -> Workflow permissions**, enable
   **"Allow GitHub Actions to create and approve pull requests."** This is
   also not copied from the template repository and defaults to off on a
   freshly generated repository. Without it, the reviewer job's "Open pull
   request" step fails outright (`GitHub Actions is not permitted to create
   or approve pull requests`) after the author and reviewer have both
   already run -- i.e. after the API cost is already spent, so it is worth
   confirming this setting before the first dispatch rather than after.
4. `bootstrap_instance` copies `templates/agent-models.yml` to
   `.open-study-path/models.yml` automatically the first time it runs, so
   every agent role starts at the recommended tier and the override file is
   already there to edit. No manual step needed unless you want to change a
   tier before the first dispatch even runs -- in that case copy and edit
   the template yourself; `instructions/00-bootstrap.md` never overwrites an
   existing `.open-study-path/models.yml`. See `docs/agent-model-configuration.md`.
5. Go to the **Actions** tab -> **Agent pilot** -> **Run workflow**.
6. Choose `phase` from the dropdown (see "Current scope" for what each phase
   actually does today), and give `target_repo` as this same repository's
   `OWNER/REPOSITORY`. `extra_context` is optional free text passed straight
   to the author agent (a course name, a specific instruction, or -- for
   `evaluate` -- the learner's literal command, see `docs/claude-agent-pilot.md`).
7. The workflow opens a pull request with the author's diff and the
   independent reviewer's verdict (`state/reviews/agent-pilot-<phase>.yml`
   and a PR comment). Read the reviewer's findings before merging -- this
   pilot does not auto-merge; a human makes the final call on every run.
8. `Validate Open Study Path` (`.github/workflows/validate-template.yml`) is
   the CI check that actually matters before merging any of this pilot's
   pull requests, but it will not appear on the PR by itself: GitHub does
   not trigger `pull_request`-event workflows for a pull request opened by
   the default `GITHUB_TOKEN` inside another workflow run (a built-in loop
   guard). Trigger it by hand -- **Actions tab -> Validate Open Study Path
   -> Run workflow**, choosing the pilot's branch as `ref` -- and wait for it
   to go green before merging. Don't merge on the strength of the reviewer
   agent's verdict alone; that verdict and CI are independent checks.

`diagnostic` does not use the Run workflow button: `instructions/20-diagnostic.md`
requires a real multi-turn placement conversation, so **Agent pilot -
diagnostic** instead triggers once per learner reply, on each comment posted
to the session issue. Start it by opening that issue; no separate dispatch
step.

## Current scope

Every manifest phase now has a real, dispatchable path, but several carry
real restrictions -- read `docs/claude-agent-pilot.md` for the full detail
behind each one before relying on it:

| Phase | Restriction today |
|---|---|
| `bootstrap_instance`, `configure_intake` | `configure_intake` always resolves as `github_issue` intake; no interactive provider choice (nobody to ask in an unattended run) |
| `intake` | Only the `github_issue` provider path is wired; Jotform and manual YAML intake have no dispatched path yet |
| `publish` | Only the `task manager: GitHub Issues` backend; Trello/Todoist/Notion remain deferred |
| `generate_proposal`, `generate_detailed` | `generate_detailed` has slide generation disabled by default (`AGENT_PILOT_ENABLE_SLIDES`) |
| `track`, `replan`, `evaluate` | No cross-repo restriction beyond the shared GitHub Issues scope above; `evaluate`'s materialization-on-mastery path reuses `generate_detailed`'s own restrictions |
| `diagnostic` | Its own event-triggered workflow, not `workflow_dispatch` -- see above |

None of these restrictions are enforced by hiding the option; each one fails
loudly (a tool call is rejected, or the author refuses) rather than silently
degrading. Jotform and manual YAML intake are documented contracts
(`docs/template-lifecycle.md`) waiting on a future stage to wire a dispatched
phase to them -- they are not deprecated, just not reachable yet.

## What this pilot deliberately does not do yet

- **No auto-merge.** Every run opens a pull request; a human merges it.
- **No fork trigger.** `workflow_dispatch` and `issue_comment` both require
  repository access to invoke -- there is no automated response to an
  external contributor's fork or PR.

See `docs/claude-agent-pilot.md`, "What this pilot deliberately does not do
yet," for the reasoning behind both.

## Cost visibility

Every run's combined author + reviewer token usage and estimated cost is
appended to `state/agent-pilot-usage.jsonl` in the instance repository and
shown in the pull request body. Treat the estimate as planning-only; check
the Anthropic Console for real billed usage. See `docs/claude-agent-pilot.md`,
"Token usage and cost estimates," for real sample numbers per phase.

## Updating an existing instance after a contract change

There is no separate copied-instructions file to go stale: the workflow
reads `AGENTS.md` and `instructions/*.md` directly from the instance
repository's own checkout on every run. Pulling in an upstream template
update (a normal git merge or cherry-pick from `diegomoura/open-study-path`)
is enough to bring the next dispatch up to date; there is no second
synchronization step.
