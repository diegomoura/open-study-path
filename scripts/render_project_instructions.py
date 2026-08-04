#!/usr/bin/env python3
"""Render ChatGPT Project Instructions for one repository instance."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PLACEHOLDER = "OWNER/REPOSITORY"
MARKER = re.compile(r"<!-- open-study-path:project-instructions repository=([^\s]+) -->")
COMPATIBILITY_MARKER = "<!-- open-study-path:template-placeholder OWNER/REPOSITORY -->"
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TEMPLATE_COPY_LINE = (
    "Copy the content below into the Project Instructions and replace "
    "`OWNER/REPOSITORY`."
)
RENDERED_COPY_LINE = (
    "Copy the content below into the Project Instructions. "
    "The repository identifier is already filled in."
)
PROJECTION_START = "<!-- open-study-path:canonical-task-projection:start -->"
PROJECTION_END = "<!-- open-study-path:canonical-task-projection:end -->"
PROJECTION_PATTERN = re.compile(
    re.escape(PROJECTION_START) + r".*?" + re.escape(PROJECTION_END),
    re.DOTALL,
)
PROJECTION_BLOCK = f"""{PROJECTION_START}
## Canonical external task projection

This block overrides older equivalent wording elsewhere in this file.

Use the provider-independent engine in `scripts/task_projection_engine.py` and the contract in `instructions/41-task-backend-projection.md`. Ordered backends use exactly:

`Planejado → Disponível em paralelo → Próxima aula → Em estudo → Em avaliação → Revisão necessária → Concluído`

Keep stable internal states. Exactly one unfinished eligible materialized lesson is **Próxima aula** when any is eligible; other eligible materialized lessons are **Disponível em paralelo**. The orientation resource stays in **Planejado** and is not a lesson.

Generate learner-visible title, description, checklist and managed comments separately from synchronization metadata. Never place HTML comments, `open-study-path` markers, topic IDs, content versions, prerequisite arrays, fingerprints, provider IDs or sync JSON in those fields.

Resolve every existing resource before the first write. Prefer durable external ID, then private stable key, then one unambiguous compatible title. Ambiguity blocks destructive writes. Preserve learner-created lists, tasks, comments, attachments and unknown content.

After writes, read the complete external state back and validate count, uniqueness, managed order, primary and parallel lessons, prerequisites, states, URLs, fingerprint and visible metadata. Persist `state/operations/<operation-id>.json`, `state/integrations.json` and the learner summary before declaring success.

Keep one convergent branch and pull request for the same `operation_id`. Historical reviews remain immutable; a later approved review supersedes current ownership without rewriting old fingerprints.

For GitHub Issues, keep one issue per materialized lesson and the compatible `study:ready` label. Migrate `study:ready-primary` and `study:ready-parallel` back to `study:ready` rather than introducing a silent schema break.
{PROJECTION_END}"""


def _insert_after_heading(content: str, lines: list[str]) -> str:
    first_heading_end = content.find("\n")
    if first_heading_end < 0:
        raise ValueError("project instructions need a Markdown heading")
    block = "\n" + "\n".join(lines) + "\n"
    return content[: first_heading_end + 1] + block + content[first_heading_end + 1 :]


def _inject_projection_contract(content: str) -> str:
    if PROJECTION_PATTERN.search(content):
        return PROJECTION_PATTERN.sub(PROJECTION_BLOCK, content, count=1)
    anchor = "\n## Completion response\n"
    if anchor in content:
        return content.replace(anchor, "\n" + PROJECTION_BLOCK + "\n" + anchor, 1)
    return content.rstrip() + "\n\n" + PROJECTION_BLOCK + "\n"


def render_instructions(content: str, repository: str) -> str:
    """Return instructions bound to repository, preserving idempotency and renames."""
    if not REPOSITORY.fullmatch(repository):
        raise ValueError(f"invalid repository identifier: {repository}")

    rendered = content.replace(TEMPLATE_COPY_LINE, RENDERED_COPY_LINE)
    marker = MARKER.search(rendered)
    previous = marker.group(1) if marker else PLACEHOLDER

    if previous == PLACEHOLDER:
        visible_source = rendered.replace(COMPATIBILITY_MARKER, "")
        if PLACEHOLDER not in visible_source:
            raise ValueError("project instructions have no repository placeholder or marker")
        rendered = visible_source.replace(PLACEHOLDER, repository)
    elif previous != repository:
        rendered = rendered.replace(previous, repository)

    marker_value = f"<!-- open-study-path:project-instructions repository={repository} -->"
    marker = MARKER.search(rendered)
    if marker:
        rendered = MARKER.sub(marker_value, rendered, count=1)
    else:
        rendered = _insert_after_heading(rendered, [marker_value])

    if COMPATIBILITY_MARKER not in rendered:
        rendered = _insert_after_heading(rendered, [COMPATIBILITY_MARKER])

    rendered = _inject_projection_contract(rendered)
    visible_rendered = rendered.replace(COMPATIBILITY_MARKER, "")
    if PLACEHOLDER in visible_rendered:
        raise ValueError("visible repository placeholder remains after rendering")
    if f"- Instance: `{repository}`" not in rendered:
        raise ValueError("rendered instructions do not contain the instance repository")
    if rendered.count(PROJECTION_START) != 1 or rendered.count(PROJECTION_END) != 1:
        raise ValueError("rendered instructions must contain one canonical projection block")
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument(
        "--path",
        default="templates/chatgpt-project-instructions.md",
        help="file to render in place",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    path = Path(args.path)
    original = path.read_text(encoding="utf-8")
    rendered = render_instructions(original, args.repository)
    if args.check:
        if rendered != original:
            raise SystemExit(f"{path} is not rendered for {args.repository}")
        print(f"Project Instructions are ready for {args.repository}.")
        return
    if rendered == original:
        print(f"Project Instructions already target {args.repository}.")
        return
    path.write_text(rendered, encoding="utf-8")
    print(f"Rendered {path} for {args.repository}.")


if __name__ == "__main__":
    main()
