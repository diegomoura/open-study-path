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
run in, not a separate driver repository). This is never copied automatically
by the GitHub template generator -- every new instance, including disposable
test repositories, needs it added by hand.

When creating the key in the Anthropic Console, scope it to a single
workspace. A key left scoped to "all workspaces" fails the very first
dispatch outright, before any diff or review happens, with `anthropic-
workspace-id is required when authenticating with an identity-linked API
key` -- this workflow only ever sends `x-api-key`, not a workspace-id
header, so a multi-workspace key has no way to tell it which workspace to
run in. If a dispatch fails with that exact error, edit the key in the
Console (its workspace scope is a property of the key itself, not
something this repository's workflow can pass in) and re-run.

Before running this against anything but a disposable test repository, set
a spend limit for that key in the Anthropic Console. Never put the key in a
committed file, an issue body, or a workflow log.

## Required repository setting: allow Actions to open pull requests

Every dispatched phase ends by having the workflow's own `GITHUB_TOKEN` open
a pull request. GitHub repositories created from a template do **not**
inherit this permission -- it defaults to off, and the first dispatch on a
fresh instance fails at the "Open pull request" step with `GitHub Actions is
not permitted to create or approve pull requests`.

Enable it once per instance, before the first dispatch: **Settings ->
Actions -> General -> Workflow permissions -> "Allow GitHub Actions to create
and approve pull requests"**. This is a repository security setting, not a
Secret -- it does not need to be kept confidential, but it is worth knowing
what it grants: the workflow's token can open pull requests, and -- since
Etapa 12 -- can also squash-merge one itself when the independent reviewer
approves and every required check succeeds (see "Auto-merge (Opcao C, Etapa
12)" in `docs/claude-agent-pilot.md`). If either condition is not met, the
pull request is left open for a human, exactly as before Etapa 12.

## Setup steps

1. Create a repository from `diegomoura/open-study-path` using the GitHub
   template (green **Use this template** button on the template repository's
   page, then **Create a new repository**). The `agent-pilot-*.yml` workflows
   are already part of the template; nothing extra to copy in.
   **Next:** you land on your new repository. Continue with step 2 before
   doing anything else -- a dispatch without the Secret and the permission
   below fails immediately.
2. Add `ANTHROPIC_API_KEY` as a repository Secret (see "Required repository
   Secret" above) and set its spend limit in the Anthropic Console.
   **Next:** step 3, in the same repository's Settings tab.
3. Enable "Allow GitHub Actions to create and approve pull requests" (see
   "Required repository setting" above). Skipping this is the most common
   first-dispatch failure on a new instance.
   **Next:** step 4 -- your first real dispatch.
4. Go to the **Actions** tab -> **Agent pilot** -> **Run workflow**. Choose
   `phase: bootstrap_instance` for this very first run regardless of what you
   plan to do afterward -- every other phase depends on files it creates.
   Give `target_repo` as this same repository's `OWNER/REPOSITORY`. Leave
   `extra_context` blank for this first run.
   **Next:** click the green **Run workflow** button. The run takes a
   minute or two; refresh the Actions tab to watch it.
5. When the run finishes, a pull request appears on the repository's **Pull
   requests** tab, with the author's diff and the independent reviewer's
   verdict (`state/reviews/agent-pilot-bootstrap_instance.yml` and a PR
   comment).
   **Next:** two possible outcomes --
   - **The PR is already merged** (its branch is gone, and `state/`,
     `study.config.yml`, and `.open-study-path/instance.yml` exist on your
     default branch): this is Etapa 12's auto-merge, and it only happens
     when the reviewer approved and every required check passed. Nothing
     left to do for this dispatch -- go to step 6.
   - **The PR is still open**: read the reviewer's findings in the PR
     description before merging it yourself. This means either the reviewer
     found something blocking, or a required check did not pass -- both are
     shown on the PR. Fix and re-dispatch, or merge by hand if you agree
     the finding does not actually block.
6. Optional, any time after your first `bootstrap_instance` dispatch: edit
   `.open-study-path/models.yml` (bootstrap creates it from
   `templates/agent-models.yml`) if you want to override the recommended
   Claude model tier for a specific agent role -- see
   `docs/agent-model-configuration.md`. Leave every override `null` to use
   the recommended tier for every agent.
   **Next:** repeat step 4 with your next phase (`configure_intake` is the
   usual second dispatch) whenever you are ready to continue the trilha --
   see "Current scope" below for what each phase does. `target_repo` and
   `extra_context` follow the same pattern as step 4; `extra_context` is
   optional free text passed straight to the author agent (a course name, a
   specific instruction, or -- for `evaluate` -- the learner's literal
   command, see `docs/claude-agent-pilot.md`).

`diagnostic` does not use the Run workflow button: `instructions/20-diagnostic.md`
requires a real multi-turn placement conversation, so **Agent pilot -
diagnostic** instead triggers on each comment posted to the session issue,
once per learner reply.

Nothing creates or labels that session issue automatically -- this is
deliberate, the same way nothing auto-creates the original study-request
issue. A human decides when a learner is ready to start their diagnostic and
makes that decision visible on GitHub:

1. Open the learner's `study-request` issue (or reuse whichever issue you
   want the diagnostic conversation to live in).
2. Add the `diagnostic:in-progress` label to it. The workflow's `issue_comment`
   trigger checks for exactly this label before it will respond to anything
   posted on the issue.
3. Post a comment starting the conversation (for example: "Vamos fazer meu
   diagnóstico."). **Next:** the workflow runs once per reply from here --
   watch the Actions tab for **Agent pilot - diagnostic** after each comment,
   yours or the learner's. The final turn removes `diagnostic:in-progress`
   automatically and opens a pull request the same way `Run workflow` phases
   do -- **`diagnostic` never auto-merges** (its own workflow has no
   auto-merge job, unlike every phase dispatched through `agent-pilot-
   setup.yml`), so read the reviewer's verdict and merge it yourself.

## A pull request opened by this workflow may need its CI started by hand

Every agent-pilot pull request is opened by the workflow's own `GITHUB_TOKEN`,
under the `github-actions[bot]` identity. This repository's own CI workflows
(`validate-template.yml` and the others under `.github/workflows/`)
deliberately skip their `pull_request`-triggered run for a PR opened by that
identity -- running it would just race Etapa 12's auto-merge job, which
already runs the same checks synchronously, inline, before deciding whether
to merge.

This matters only for a PR that auto-merge left open for you (the reviewer
found something blocking, a required check failed, or the phase -- like
`diagnostic` -- has no auto-merge job at all). Before merging one of those by
hand, get a real CI run against its exact head commit: **Actions -> Validate
Open Study Path -> Run workflow**, choosing the PR's branch as `ref`. A PR
that already auto-merged needs none of this -- its CI already ran as part of
the same dispatch, before the merge happened.

## Starting `evaluate`: how a real assessment submission works

`evaluate` also has no `Run workflow` entry point of its own for the
learner-facing half of the loop -- it dispatches through `agent-pilot-
setup.yml` (`phase: evaluate`) the same way `publish` and `generate_detailed`
do, but only once a real submission exists to grade:

1. The learner opens the assessment issue form for the specific topic
   (`.github/ISSUE_TEMPLATE/assessment-topic-NNN.yml`, linked from the
   lesson's own GitHub Issue) and submits it. This applies the
   `assessment`, `assessment:submitted`, and `topic:TOPIC-NNN` labels
   automatically -- the form's `labels:` key, not something you set by hand.
2. Dispatch `phase: evaluate` the normal way (step 4 above), with
   `target_repo` as usual. `extra_context` can carry the learner's own
   command if instructed to.
   **Next:** same as any other phase -- watch for the PR, read the
   reviewer's verdict, and either let auto-merge do its job or merge by hand
   if it was left open.

The evaluator finds the submission by that `topic:TOPIC-NNN` label, not by
searching the issue body for anything. Every assessment form's first block is
markdown-only instructional text containing a machine-readable marker for a
hand-authored or migrated issue outside the standard form -- but GitHub's own
documentation confirms a `type: markdown` block "is not submitted" with the
issue, so a real, form-submitted issue never actually carries that marker in
its body. If you are troubleshooting a submission `evaluate` isn't finding,
check the label first.

## Current scope

Every manifest phase now has a real, dispatchable path, but several carry
real restrictions -- read `docs/claude-agent-pilot.md` for the full detail
behind each one before relying on it:

| Phase | Restriction today |
|---|---|
| `bootstrap_instance`, `configure_intake` | `configure_intake` always resolves as `github_issue` intake; no interactive provider choice (nobody to ask in an unattended run) |
| `intake` | Only the `github_issue` provider path is wired; Jotform and manual YAML intake have no dispatched path yet |
| `publish` | Only the `task manager: GitHub Issues` backend; Trello/Todoist/Notion remain deferred |
| `generate_proposal`, `generate_detailed` | No slide generation -- study slides were removed from the pilot entirely, not just toggled off |
| `track`, `replan`, `evaluate` | No cross-repo restriction beyond the shared GitHub Issues scope above; `evaluate`'s materialization-on-mastery path reuses `generate_detailed`'s own restrictions |
| `diagnostic` | Its own event-triggered workflow, not `workflow_dispatch` -- see above |

None of these restrictions are enforced by hiding the option; each one fails
loudly (a tool call is rejected, or the author refuses) rather than silently
degrading. Jotform and manual YAML intake are documented contracts
(`docs/template-lifecycle.md`) waiting on a future stage to wire a dispatched
phase to them -- they are not deprecated, just not reachable yet.

## What this pilot deliberately does not do yet

- **No fork trigger.** `workflow_dispatch` and `issue_comment` both require
  repository access to invoke -- there is no automated response to an
  external contributor's fork or PR.

Auto-merge exists (see above), but only under the specific approved+CI-green
condition; see `docs/claude-agent-pilot.md`, "Auto-merge (Opcao C, Etapa
12)," for exactly what that requires and what happens when it does not
hold.

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
