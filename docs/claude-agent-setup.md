# Set up the automated agent pilot for an Open Study Path instance

This is the Secret-based, GitHub Actions counterpart to
`docs/chatgpt-project-setup.md`. Where the ChatGPT/Claude chat flow is one
person driving one long conversation through every phase, this flow runs
each `instructions/manifest.yml` phase as an isolated Claude API call --
author and reviewer never share context, and a GitHub Actions workflow does
the dispatching instead of a human copying prompts.

Read `docs/claude-agent-pilot.md` for the full design rationale and current
validation status of every phase. This document is only the setup path: what
to add, where, and how to run it.

## Status: pilot, not the default

Both onboarding paths work today. This one is still a pilot with real,
documented scope limits (see "Current scope" below) -- it is an alternative
for an owner who wants to try real automated dispatches, not yet a
replacement for `docs/chatgpt-project-setup.md`. Nothing here turns off or
changes the manual chat flow.

## Why this needs a Secret instead of a chat connection

The ChatGPT Project flow authenticates through a person's ChatGPT account
connected to GitHub. This flow instead has the *repository itself* call the
Anthropic API directly from a GitHub Actions workflow, so it needs its own
credential: an `ANTHROPIC_API_KEY` stored as a repository Secret.

There is no equivalent of "copy the prepared instructions into a Project" --
the workflow already lives in the repository (it ships with the template)
and reads `AGENTS.md` / `instructions/*.md` directly at run time, the same
files the manual flow reads. Setup is the Secret plus one workflow run.

## Required repository Secret

`ANTHROPIC_API_KEY` -- add it under **Settings -> Secrets and variables ->
Actions** on the instance repository (the same repository the workflow will
run in, not a separate driver repository).

Before running this against anything but a disposable test repository, set
a spend limit for that key in the Anthropic Console. Never put the key in a
committed file, an issue body, or a workflow log.

## Setup steps

1. Create a repository from `diegomoura/open-study-path` using the GitHub
   template, the same as the manual flow's step 1. The `agent-pilot-*.yml`
   workflows are already part of the template; nothing extra to copy in.
2. Add `ANTHROPIC_API_KEY` as a repository Secret (above) and set its spend
   limit in the Anthropic Console.
3. Optional: if you want to override the recommended Claude model tier per
   agent role, copy `templates/agent-models.yml` to
   `.open-study-path/models.yml` and edit it. This step is not automated by
   `bootstrap_instance` yet -- skip it to use the recommended tier for every
   agent (see `docs/agent-model-configuration.md`).
4. Go to the **Actions** tab -> **Agent pilot** -> **Run workflow**.
5. Choose `phase` from the dropdown (see "Current scope" for what each phase
   actually does today), and give `target_repo` as this same repository's
   `OWNER/REPOSITORY`. `extra_context` is optional free text passed straight
   to the author agent (a course name, a specific instruction, or -- for
   `evaluate` -- the learner's literal command, see `docs/claude-agent-pilot.md`).
6. The workflow opens a pull request with the author's diff and the
   independent reviewer's verdict (`state/reviews/agent-pilot-<phase>.yml`
   and a PR comment). Read the reviewer's findings before merging -- this
   pilot does not auto-merge; a human makes the final call on every run.

`diagnostic` does not use the Run workflow button: instructions/20-diagnostic.md
requires a real multi-turn placement conversation, so **Agent pilot -
diagnostic** instead triggers once per learner reply, on each comment posted
to the session issue. Start it by opening that issue the same way the
manual flow does; no separate dispatch step.

## Current scope

Every manifest phase now has a real, dispatchable path, but several carry
real restrictions -- read `docs/claude-agent-pilot.md` for the full detail
behind each one before relying on it:

| Phase | Restriction today |
|---|---|
| `bootstrap_instance`, `configure_intake` | `configure_intake` always resolves as `github_issue` intake; no interactive provider choice (nobody to ask in an unattended run) |
| `intake` | Only the `github_issue` provider path is wired; Jotform and manual YAML intake still need the manual chat flow |
| `publish` | Only the `task manager: GitHub Issues` backend; Trello/Todoist/Notion remain deferred |
| `generate_proposal`, `generate_detailed` | `generate_detailed` has slide generation disabled by default (`AGENT_PILOT_ENABLE_SLIDES`) |
| `track`, `replan`, `evaluate` | No cross-repo restriction beyond the shared GitHub Issues scope above; `evaluate`'s materialization-on-mastery path reuses `generate_detailed`'s own restrictions |
| `diagnostic` | Its own event-triggered workflow, not `workflow_dispatch` -- see above |

None of these restrictions are enforced by hiding the option; each one fails
loudly (a tool call is rejected, or the author refuses) rather than silently
degrading, matching the same pattern already used for the manual flow's own
guardrails.

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

Unlike the ChatGPT Project flow, there is no separate copied-instructions
file to go stale here -- the workflow reads `AGENTS.md` and
`instructions/*.md` directly from the instance repository's own checkout on
every run. Pulling in an upstream template update (a normal git merge or
cherry-pick from `diegomoura/open-study-path`) is enough to bring the next
dispatch up to date; there is no second synchronization step.

## Running both flows on the same repository

An instance is not required to pick one flow permanently. A repository
owner can run a phase through this pilot one day and continue the same
instance through a manual ChatGPT/Claude chat the next -- both read the same
`instructions/*.md` contracts and the same repository state
(`.open-study-path/instance.yml`, `state/*.json`, `study.config.yml`), so
neither flow's output is foreign to the other.
