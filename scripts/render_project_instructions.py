#!/usr/bin/env python3
"""Render ChatGPT Project Instructions for one repository instance."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PLACEHOLDER = "OWNER/REPOSITORY"
MARKER = re.compile(
    r"<!-- open-study-path:project-instructions repository=([^\s]+) -->"
)
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def render_instructions(content: str, repository: str) -> str:
    """Return instructions bound to repository, preserving idempotency and renames."""
    if not REPOSITORY.fullmatch(repository):
        raise ValueError(f"invalid repository identifier: {repository}")

    marker = MARKER.search(content)
    if marker is None:
        raise ValueError("missing project-instructions repository marker")

    previous = marker.group(1)
    if previous == PLACEHOLDER:
        rendered = content.replace(PLACEHOLDER, repository)
    elif previous == repository:
        rendered = content
    else:
        rendered = content.replace(previous, repository)

    rendered = MARKER.sub(
        f"<!-- open-study-path:project-instructions repository={repository} -->",
        rendered,
        count=1,
    )

    if PLACEHOLDER in rendered:
        raise ValueError("repository placeholder remains after rendering")
    if f"- Instance: `{repository}`" not in rendered:
        raise ValueError("rendered instructions do not contain the instance repository")
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument(
        "--path",
        default="templates/chatgpt-project-instructions.md",
        help="file to render in place",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the file is already rendered without writing",
    )
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
