#!/usr/bin/env python3
"""Assemble the system/user prompt files consumed by scripts/agent_runtime.py.

Deliberately reads the real instruction files instead of duplicating their
text: `instructions/*.md` are the contract each phase already runs under, and
the point of stage 2 is that an API call reads the same contract a human
running the ChatGPT Project used to read (proposal, section 2 -- "o que não
muda"). Keeping this a thin assembler instead of a second copy of the prose
means the contract can't silently drift between the manual and automated path.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PHASE_INSTRUCTION_FILES = {
    "bootstrap_instance": ["instructions/00-bootstrap.md"],
    "configure_intake": ["instructions/05-configure-intake.md"],
    "intake": ["instructions/10-intake.md"],
    "publish": ["instructions/40-publish-tasks.md"],
    "generate_proposal": ["instructions/28-propose-path.md"],
    "generate_detailed": ["instructions/30-generate-path.md"],
}

# Files every author/reviewer prompt gets regardless of phase.
AUTHOR_CORE_SHARED_FILES = [
    "AGENTS.md",
    "instructions/phase-completion.md",
]

REVIEWER_CORE_SHARED_FILES = [
    "AGENTS.md",
    "instructions/04-review-generated-artifacts.md",
    "docs/review-framework.md",
    "templates/review.yml",
]

# Files beyond the core shared set, specific to one phase. Etapa 4 (proposal,
# section 7, step 4) is what first needed this split: instructions/
# 02-setup-execution.md defines the "Allowed setup diff" for the two setup
# phases specifically -- it is not the right contract to hand an `intake`
# author, which has its own domain-output list (see agent_runtime.py's
# INTAKE_ALLOWED_EXACT_PATHS) and its own completion-recovery contract.
PHASE_EXTRA_AUTHOR_FILES: dict[str, list[str]] = {
    "bootstrap_instance": ["instructions/02-setup-execution.md"],
    "configure_intake": ["instructions/02-setup-execution.md"],
    "intake": ["instructions/11-intake-completion-recovery.md", "intake/field-mapping.yml"],
    "publish": [
        "instructions/41-task-backend-projection.md",
        "instructions/42-integration-preflight.md",
        "docs/learner-facing-language.md",
        "docs/study-slides.md",
    ],
    "generate_proposal": [
        "instructions/35-review-curriculum.md",
        "docs/learner-facing-language.md",
        "docs/beginner-first-pedagogy.md",
    ],
    "generate_detailed": [
        "instructions/36-review-course-content.md",
        "docs/learner-facing-language.md",
        "docs/beginner-first-pedagogy.md",
        "docs/content-quality-and-sources.md",
        "docs/mermaid-visual-learning.md",
        "docs/integration-capabilities.md",
    ],
}

PHASE_EXTRA_REVIEWER_FILES: dict[str, list[str]] = {
    "intake": ["instructions/11-intake-completion-recovery.md", "intake/field-mapping.yml"],
    "publish": [
        "instructions/41-task-backend-projection.md",
        "instructions/42-integration-preflight.md",
    ],
    "generate_proposal": [
        "instructions/35-review-curriculum.md",
        "docs/beginner-first-pedagogy.md",
    ],
    "generate_detailed": [
        "instructions/35-review-curriculum.md",
        "instructions/36-review-course-content.md",
        "docs/beginner-first-pedagogy.md",
        "docs/content-quality-and-sources.md",
    ],
}

# `review_profile` selects which required-check set instructions/
# 04-review-generated-artifacts.md applies (docs/review-framework.md,
# "Review profiles" table). Every phase before Etapa 4 used "setup"; intake
# uses its own profile with different required checks (request_fidelity,
# preference_preservation, ambiguity_resolution, data_minimization,
# next_phase_consistency -- instructions/11-intake-completion-recovery.md).
# `publish` uses the framework's `publication` profile name (not `publish` --
# docs/review-framework.md's table already used that name before this
# pilot existed). `generate_proposal` and `generate_detailed` both use
# `curriculum` -- the same profile manifest.yml assigns to the whole
# `generate` phase; two of its seven checks (content_review_complete,
# assessment_alignment) are about materialized content, which only exists
# once `generate_detailed` runs -- trivially satisfied ("nothing in scope")
# for `generate_proposal`, genuinely evaluated for `generate_detailed`.
PHASE_REVIEW_PROFILE: dict[str, str] = {
    "bootstrap_instance": "setup",
    "configure_intake": "setup",
    "intake": "intake",
    "publish": "publication",
    "generate_proposal": "curriculum",
    "generate_detailed": "curriculum",
}

AUTHOR_HARNESS_NOTE = """\
## Runtime harness note (not part of the phase contract above)

You are being run as an isolated author agent for exactly one phase of the
Open Study Path lifecycle, through a minimal tool harness -- not a full shell.
You have exactly these tools:

- read_file(path): read one text file, path relative to repo root.
- list_dir(path): list one directory, path relative to repo root.
- write_file(path, content): write one text file. Only paths inside this
  phase's allowed domain-output list are accepted; anything else is rejected
  by the harness before it touches disk, regardless of what you request. Do
  NOT write a review artifact under `state/reviews/` yourself: the
  instruction contract you were given describes a single-context flow where
  the same conversation authors and reviews, but in this harness a separate,
  independent reviewer agent does that -- with no access to this
  conversation. A self-written review here would be an unverified claim
  sitting next to the real one.
- finish_phase(summary, next_action): call this exactly once, when every
  required output file has been written. Nothing you do after finish_phase
  runs. `next_action` should be the concrete next command the repository
  owner should give, in the tone of instructions/phase-completion.md's
  learner-facing response, not internal PR/CI detail.

There is no git access, no shell, no general network access from inside this
harness (some phases get a narrow, separately-described exception below). A
separate GitHub Actions step commits whatever you write, opens the pull
request, and a *separate* reviewer agent call -- with none of this
conversation in its context -- checks your work before anything merges.
"""

AUTHOR_INTAKE_TOOL_NOTE = """\
## Intake tool addendum (Etapa 4)

You additionally have narrow, read-mostly access to GitHub Issues in this
same repository, scoped to the intake discovery label:

- list_intake_issues(): summaries of open, non-PR issues carrying the
  discovery label. No body -- use read_github_issue for that.
- read_github_issue(number): one issue's full rendered body, title, labels,
  author.
- resolve_intake_candidates(expected_headings, required_response_headings,
  consent_heading): classifies every candidate using the real
  scripts/intake_resolution.py algorithm running in the harness, not your own
  judgment. Read expected_headings/required_response_headings/consent_heading
  from the checked-in `.github/ISSUE_TEMPLATE/create-study-path.yml` via
  read_file first, then pass them here. Do not attempt to decide which issue
  is the right one yourself before calling this -- that is exactly the
  "similarity or newest-issue heuristic" instructions/10-intake.md forbids.
  Trust this tool's `state` field (`unique`, `none`, or `ambiguous`) and act
  on `accepted`/`rejected` exactly as instructions/10-intake.md's Selection
  and import section describes for each state:
  - `unique`: proceed with the normal import -- write the three domain-output
    files, then call label_github_issue on the accepted candidate.
  - `none` or `ambiguous`: do **not** write any domain-output file, including
    `state/intake-summary.json`. That file is governed by the same allowed
    domain-output list as the other two and holds the canonical intake
    summary schema when (and only when) an import actually happened -- it is
    not a scratchpad for reporting a classification result. Report the
    outcome only through `finish_phase`'s `summary`/`next_action` fields: for
    `none`, return the direct form link as instructions/10-intake.md
    describes; for `ambiguous`, list each candidate's number, title and
    creation time and ask the owner to choose. Do not call
    label_github_issue in either case.
- label_github_issue(number, label): the only label you may ever pass here is
  `intake:imported`. Call it once, on the accepted candidate's issue number,
  only after every domain-output file has already been written -- this is a
  real, immediate write to the live repository, independent of whether the
  pull request you're producing is later merged.
"""

REVIEWER_HARNESS_NOTE = """\
## Runtime harness note (not part of the review contract above)

You are the independent reviewer for one already-completed author run. You do
not have and must not assume any of the author's reasoning -- only the diff
it produced and read access to the repository, exactly as
docs/review-framework.md requires ("the reviewer reconstructs evidence from
approved inputs, repository outputs ... it does not trust the authoring
pass's success claim").

Tools:

- read_file(path): read one text file, path relative to repo root.
- list_dir(path): list one directory, path relative to repo root.
- compute_sha256(path): compute the real sha256 of a file's exact current
  bytes. Always call this for every `artifacts[].sha256` value you put in the
  review document -- never write a hex string from memory or estimation. A
  fingerprint that isn't the real hash defeats the entire point of binding
  approval to exact bytes.
- submit_review(review_yaml, status, blocking_findings): call this exactly
  once. `review_yaml` must be a complete document matching the shape of
  templates/review.yml (contract_version, operation_id, phase, reviewer_role,
  independent_pass: true, status, artifacts with sha256 fingerprints, checks
  for every item in the phase's review profile, blocking_findings,
  non_blocking_findings). status='approved' is rejected by the harness unless
  blocking_findings is empty.

There is no git access, no shell, no general network access from inside this
harness (some phases get a narrow, separately-described exception below). The
workflow step after you records exactly the review you submit; it does not
edit it.
"""

REVIEWER_INTAKE_TOOL_NOTE = """\
## Intake tool addendum (Etapa 4)

You additionally have read-only access to GitHub Issues in this same
repository:

- list_intake_issues(): summaries of open, non-PR issues carrying the intake
  discovery label.
- read_github_issue(number): one issue's full rendered body, title, labels,
  author.

Use these to independently re-fetch the source issue the author claims to
have imported and compare it -- title, rendered field values, consent
checkbox, author, `intake:imported` label -- against what was normalized into
`study.config.yml` and `state/intake-summary.json`. You do not have
label_github_issue: you are checking whether the label was applied correctly,
not applying it yourself.
"""

AUTHOR_PUBLISH_TOOL_NOTE = """\
## Publish tool addendum (Etapa 4)

Restricted to the `github_issues` task-manager backend only in this pilot --
Trello, Todoist and any other provider are out of scope here (see
docs/claude-agent-pilot.md's Scope section). Do not attempt to resolve,
probe or write to any other task-manager provider, and do not activate
reminders, calendars or email -- this pilot only covers the required
task-manager capability.

You have exactly one tool for the actual publication:

- run_publish_projection(topics, operation_id, course_name): runs the real
  scripts/task_projection_engine.py projection, matching, external writes
  and read-back validation against GitHub Issues -- never build or validate
  the projection yourself. Read the approved roadmap and topic contracts via
  read_file first, then construct `topics` as a list of objects matching
  TopicProjection's fields (topic_id, lesson_number, title,
  direct_prerequisite_ids, content_version, canonical_state, materialized,
  slides_url, lesson_url, practice_url, assessment_url). For every topic
  already published in an earlier run, read its known `external_id` from
  `state/integrations.json` first and pass it back in -- this is what lets
  the engine update the same issue instead of creating a duplicate.

The tool's response has a `status` field:

- `status: "success"`: write `state/integrations.json` (the returned
  `integration_state`, as JSON), `study/integrations.md` (the returned
  `learner_summary`, verbatim -- it is already validated, human-readable
  Markdown, do not rewrite it), and `state/operations/<operation_id>.json`
  (the returned `journal`, as JSON). Then call finish_phase with the
  completion response instructions/40-publish-tasks.md describes.
- `status: "error"`: do **not** write `state/integrations.json` or
  `study/integrations.md` -- the harness refuses those writes at the code
  level in this state regardless of what you attempt. If the response
  includes a `journal`, write only that to
  `state/operations/<operation_id>.json` (this is the resumable technical
  journal instructions/41-task-backend-projection.md requires even on a
  blocked or partial outcome). Report the blocked/partial/failed outcome
  through finish_phase using instructions/40-publish-tasks.md's guidance for
  that case -- do not claim success.
"""

REVIEWER_PUBLISH_TOOL_NOTE = """\
## Publish tool addendum (Etapa 4)

You have the same read-only GitHub Issues access as the intake reviewer
(list_intake_issues, read_github_issue) -- use it to independently re-fetch
the issues the author's `state/integrations.json` claims to have created or
updated, and compare title, labels and rendered description against what
instructions/40-publish-tasks.md and instructions/41-task-backend-
projection.md require (numbered title format, exactly one `Próxima aula`,
correct `study:*` label, no internal metadata leaked into visible fields).
You do not have run_publish_projection: you are checking the result, not
reproducing or re-running the publication.
"""

AUTHOR_PROPOSAL_NOTE = """\
## Proposal scope addendum (Etapa 5)

This run covers only the `proposal` suboperation of the `generate` phase
(instructions/28-propose-path.md) -- the roadmap architecture, nothing
materialized yet. instructions/28-propose-path.md already says this
explicitly, but it bears repeating given how much of the parent
instructions/30-generate-path.md's surrounding content (materialized
modules, slides, assessments, rubrics) is reachable from the same
instructions/ directory: do not create `study/topics/`, `study/modules/`,
`study/slides/`, `study/assessments/`, `.github/ISSUE_TEMPLATE/assessment-
topic-*.yml`, or any other materialization artifact in this run. The only
files you may write are `study/roadmap.md` and `.open-study-path/
instance.yml` -- write_file rejects anything else regardless of what you
attempt, matching the same allowed-domain-output enforcement every other
phase in this harness already has.

Detailed content materialization (instructions/30-generate-path.md) is a
separate, not-yet-built harness phase -- do not attempt it here even if the
roadmap makes it tempting to keep going.
"""

REVIEWER_PROPOSAL_NOTE = """\
## Proposal scope addendum (Etapa 5)

You are reviewing only the `proposal` suboperation -- a roadmap architecture,
no materialized content. Two of the seven required `curriculum` profile
checks (`content_review_complete`, `assessment_alignment`) are about
materialized lessons and assessments that do not exist yet at this stage.
Record them as `passed` with a short note that there is no materialized
content in scope for this operation to fail those checks against -- do not
leave them `pending` (an incomplete review) and do not invent materialized-
content findings that don't apply.
"""

AUTHOR_DETAILED_NOTE = """\
## Detailed-generation scope addendum (Etapa 5b)

Slides are off for this pilot -- do not create `study/slides/`,
`state/slide-reviews/`, or run instructions/37-review-study-slides.md; do
not read docs/study-slides.md. write_file rejects any path under
`study/slides/` or `state/slide-reviews/` regardless of what you attempt, so
treat every instruction in instructions/30-generate-path.md that refers to
slides as not applicable to this run:

- Topic contracts (`study/topics/`) do not record `slides` or
  `slides_review` fields. `slides_pdf` also does not apply -- omit it too.
- The module's "Complete-content contract" (18 required elements) drops
  element 18 ("one direct Slides da aula PDF link") for this run -- there is
  no PDF. 17 elements apply.
- Outcome traceability step 7 ("represent every outcome in slides through
  honest data-outcome-ids") and step 8 (slide review before PDF rendering)
  do not apply.
- The learner-facing completion response and any task/assessment copy must
  never promise, reference or link a slide deck or PDF that does not exist.

Everything else in instructions/30-generate-path.md applies in full:
dependency-aware topic contracts, beginner-first concept progression,
outcome traceability via hidden markers, the source and provenance
contract, the 100-point rubric, the GitHub Issue Form per materialized
topic, and running instructions/36-review-course-content.md as the
independent content-review pass. Only materialize the deterministic
lookahead window from `.open-study-path/instance.yml`'s
`content_generation` config (or all topics, if the roadmap is within both
`full_upfront_max_topics` and `full_upfront_max_hours`) -- do not
materialize every future topic regardless of that budget.

REQUIRED DELIVERABLE, not an optional later step: for every topic you
materialize in this run, you must also produce and commit a passing
`state/content-reviews/<TOPIC-ID>.yml` from running instructions/36-review-
course-content.md yourself, in this same operation. A real dispatch (Etapa
5b validation, docs/claude-agent-pilot-etapa5.md section 7) produced an
otherwise-strong materialized topic but never created this file, and the
isolated reviewer correctly blocked the whole operation for it
(`action_required`) even though everything else passed -- do not repeat
that gap. Acknowledging the omission in your summary is not a substitute
for doing it.
"""

REVIEWER_DETAILED_NOTE = """\
## Detailed-generation scope addendum (Etapa 5b)

Slides are off for this pilot run -- do not check for `study/slides/`,
`state/slide-reviews/`, or a "Slides da aula" PDF link in the module (the
18th element of the complete-content contract does not apply here; verify
the other 17). A topic contract without `slides`/`slides_pdf`/
`slides_review` fields is correct for this run, not a finding. If the
module, rubric or Issue Form references or promises a slide deck anywhere,
that IS a real finding -- nothing may promise an artifact that does not
exist in this run.

Otherwise, apply instructions/36-review-course-content.md in full to every
materialized topic: outcome traceability, source and provenance checks,
beginner-first progression where the learner's level warrants it, and
whether the lookahead-window scope (not the whole roadmap) was respected.
"""


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _diff_against(base_sha: str) -> str:
    result = subprocess.run(
        ["git", "diff", f"{base_sha}...HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def build_author_prompts(phase: str, target_repo: str, extra_context: str) -> tuple[str, str]:
    sections = [_read(path) for path in AUTHOR_CORE_SHARED_FILES]
    sections.extend(_read(path) for path in PHASE_EXTRA_AUTHOR_FILES.get(phase, []))
    sections.extend(_read(path) for path in PHASE_INSTRUCTION_FILES[phase])
    sections.append(AUTHOR_HARNESS_NOTE)
    if phase == "intake":
        sections.append(AUTHOR_INTAKE_TOOL_NOTE)
    elif phase == "publish":
        sections.append(AUTHOR_PUBLISH_TOOL_NOTE)
    elif phase == "generate_proposal":
        sections.append(AUTHOR_PROPOSAL_NOTE)
    elif phase == "generate_detailed":
        sections.append(AUTHOR_DETAILED_NOTE)
    system_prompt = "\n\n---\n\n".join(sections)

    user_prompt = (
        f"Target repository: {target_repo}\n"
        f"Phase: {phase}\n\n"
        f"{extra_context}\n\n"
        "Read whatever repository files you need through read_file/list_dir, then "
        "write only the files required by this phase's contract, then call finish_phase."
    )
    return system_prompt, user_prompt


def build_reviewer_prompts(phase: str, target_repo: str, base_sha: str, author_summary: str) -> tuple[str, str]:
    sections = [_read(path) for path in REVIEWER_CORE_SHARED_FILES]
    sections.extend(_read(path) for path in PHASE_EXTRA_REVIEWER_FILES.get(phase, []))
    sections.append(REVIEWER_HARNESS_NOTE)
    if phase == "intake":
        sections.append(REVIEWER_INTAKE_TOOL_NOTE)
    elif phase == "publish":
        sections.append(REVIEWER_PUBLISH_TOOL_NOTE)
    elif phase == "generate_proposal":
        sections.append(REVIEWER_PROPOSAL_NOTE)
    elif phase == "generate_detailed":
        sections.append(REVIEWER_DETAILED_NOTE)
    system_prompt = "\n\n---\n\n".join(sections)

    review_profile = PHASE_REVIEW_PROFILE.get(phase, "setup")
    diff = _diff_against(base_sha)
    user_prompt = (
        f"Target repository: {target_repo}\n"
        f"Phase under review: {phase}\n"
        f"Review profile: {review_profile}\n\n"
        f"Author's self-reported summary (untrusted, verify independently):\n{author_summary}\n\n"
        f"Diff produced by the author agent (base {base_sha} -> HEAD):\n"
        f"```diff\n{diff}\n```\n\n"
        "Reconstruct evidence for each required check from the diff and repository "
        "reads, then call submit_review exactly once."
    )
    return system_prompt, user_prompt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=["author", "reviewer"])
    parser.add_argument("--phase", required=True, choices=sorted(PHASE_INSTRUCTION_FILES))
    parser.add_argument("--target-repo", required=True)
    parser.add_argument("--out-system", required=True)
    parser.add_argument("--out-user", required=True)
    parser.add_argument("--extra-context", default="")
    parser.add_argument("--base-sha", default=None, help="required for role=reviewer")
    parser.add_argument("--author-summary-file", default=None, help="required for role=reviewer")
    args = parser.parse_args()

    if args.role == "author":
        system_prompt, user_prompt = build_author_prompts(args.phase, args.target_repo, args.extra_context)
    else:
        if not args.base_sha:
            raise SystemExit("--base-sha is required for role=reviewer")
        author_summary = ""
        if args.author_summary_file:
            author_summary = Path(args.author_summary_file).read_text(encoding="utf-8")
        system_prompt, user_prompt = build_reviewer_prompts(args.phase, args.target_repo, args.base_sha, author_summary)

    Path(args.out_system).write_text(system_prompt, encoding="utf-8")
    Path(args.out_user).write_text(user_prompt, encoding="utf-8")


if __name__ == "__main__":
    main()
