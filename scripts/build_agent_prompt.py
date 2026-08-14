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
}

AUTHOR_SHARED_FILES = [
    "AGENTS.md",
    "instructions/02-setup-execution.md",
    "instructions/phase-completion.md",
]

REVIEWER_SHARED_FILES = [
    "AGENTS.md",
    "instructions/04-review-generated-artifacts.md",
    "docs/review-framework.md",
    "templates/review.yml",
]

AUTHOR_HARNESS_NOTE = """\
## Runtime harness note (not part of the phase contract above)

You are being run as an isolated author agent for exactly one phase of the
Open Study Path lifecycle, through a minimal tool harness -- not a full shell.
You have exactly these tools:

- read_file(path): read one text file, path relative to repo root.
- list_dir(path): list one directory, path relative to repo root.
- write_file(path, content): write one text file. Only paths inside this
  phase's "Allowed setup diff" (see instructions/02-setup-execution.md) are
  accepted; anything else is rejected by the harness before it touches disk,
  regardless of what you request.
- finish_phase(summary, next_action): call this exactly once, when every
  required output file has been written. Nothing you do after finish_phase
  runs. `next_action` should be the concrete next command the repository
  owner should give, in the tone of instructions/phase-completion.md's
  learner-facing response, not internal PR/CI detail.

There is no git access, no shell, no network from inside this harness. A
separate GitHub Actions step commits whatever you write, opens the pull
request, and a *separate* reviewer agent call -- with none of this
conversation in its context -- checks your work before anything merges.
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
- submit_review(review_yaml, status, blocking_findings): call this exactly
  once. `review_yaml` must be a complete document matching the shape of
  templates/review.yml (contract_version, operation_id, phase, reviewer_role,
  independent_pass: true, status, artifacts with sha256 fingerprints, checks
  for every item in the phase's review profile, blocking_findings,
  non_blocking_findings). status='approved' is rejected by the harness unless
  blocking_findings is empty.

There is no git access, no shell, no network from inside this harness. The
workflow step after you records exactly the review you submit; it does not
edit it.
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
    sections = [_read(path) for path in AUTHOR_SHARED_FILES]
    sections.extend(_read(path) for path in PHASE_INSTRUCTION_FILES[phase])
    sections.append(AUTHOR_HARNESS_NOTE)
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
    sections = [_read(path) for path in REVIEWER_SHARED_FILES]
    sections.append(REVIEWER_HARNESS_NOTE)
    system_prompt = "\n\n---\n\n".join(sections)

    diff = _diff_against(base_sha)
    user_prompt = (
        f"Target repository: {target_repo}\n"
        f"Phase under review: {phase}\n"
        f"Review profile: setup\n\n"
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
