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
}

PHASE_EXTRA_REVIEWER_FILES: dict[str, list[str]] = {
    "intake": ["instructions/11-intake-completion-recovery.md", "intake/field-mapping.yml"],
}

# `review_profile` selects which required-check set instructions/
# 04-review-generated-artifacts.md applies (docs/review-framework.md,
# "Review profiles" table). Every phase before Etapa 4 used "setup"; intake
# uses its own profile with different required checks (request_fidelity,
# preference_preservation, ambiguity_resolution, data_minimization,
# next_phase_consistency -- instructions/11-intake-completion-recovery.md).
PHASE_REVIEW_PROFILE: dict[str, str] = {
    "bootstrap_instance": "setup",
    "configure_intake": "setup",
    "intake": "intake",
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
  and import section describes for each state.
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
