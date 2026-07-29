#!/usr/bin/env python3
"""Validate bounded practice-link synchronization and current external projections."""

from __future__ import annotations

import sys
from pathlib import Path

from sync_practice_links import END_MARKER, START_MARKER, sync_repository

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(path: str, terms: list[str]) -> None:
    target = ROOT / path
    if not target.is_file():
        fail(f"missing practice-link contract file: {path}")
    content = target.read_text(encoding="utf-8")
    for term in terms:
        if term not in content:
            fail(f"{path} is missing practice-link contract term: {term}")


def main() -> None:
    require(
        "templates/module.md",
        [
            START_MARKER,
            END_MARKER,
            "scripts/sync_practice_links.py",
            "Praticar no Quizlet",
            "Estudar os flashcards no GitHub",
            "Baixar ou importar o TSV",
        ],
    )
    require(
        "instructions/40-publish-tasks.md",
        [
            "Synchronize lesson practice links",
            "python scripts/sync_practice_links.py",
            "python scripts/sync_practice_links.py --check",
            "must remain byte-for-byte unchanged",
            "does not match the topic",
        ],
    )

    try:
        changed = sync_repository(ROOT, check=True)
    except Exception as exc:  # validation boundary reports a concise repository error
        fail(str(exc))

    if changed:
        for path in changed:
            print(
                f"ERROR: practice links are out of sync: {path.relative_to(ROOT)}",
                file=sys.stderr,
            )
        raise SystemExit(1)

    print("Practice links match approved local decks and current integration state.")


if __name__ == "__main__":
    main()
