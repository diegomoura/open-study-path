#!/usr/bin/env python3
"""Validate marker-first intake discovery and natural learner commands."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from intake_resolution import CURRENT_MARKER

ROOT = Path(__file__).resolve().parents[1]
NATURAL_COMMAND = "Preenchi o formulário. Pode continuar."
LEGACY_PREFIX = "[Study Path]:"
CURRENT_PREFIX = "[Nova trilha]"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def text(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"missing intake-resolution contract: {path}")
    return target.read_text(encoding="utf-8")


def require(path: str, terms: list[str]) -> None:
    content = text(path)
    for term in terms:
        if term not in content:
            fail(f"{path} is missing deterministic-intake term: {term}")


def load_yaml(path: str) -> Any:
    return yaml.safe_load(text(path))


def main() -> None:
    require("instructions/05-configure-intake.md", [
        "https://github.com/OWNER/REPOSITORY/issues/new?template=create-study-path.yml",
        CURRENT_MARKER,
        "study-request",
        "intake:imported",
        "Do not require an issue number",
        "older forms",
    ])
    require("instructions/10-intake.md", [
        "scripts/intake_resolution.py",
        CURRENT_MARKER,
        CURRENT_PREFIX,
        LEGACY_PREFIX,
        "Matching headings alone",
        "repairable consistency signals",
        "unsupported",
        "exactly one valid candidate",
        "When none remain",
        "more than one remains",
        "never select an arbitrary newest repository issue",
        "state/intake-summary.json.source_reference",
        "intake:imported",
        "instructions/20-diagnostic.md",
    ])
    require("instructions/phase-completion.md", [
        "Return the direct intake link",
        NATURAL_COMMAND,
        "Do not ask for an issue or submission number",
        "multiple valid candidates",
    ])
    require("templates/chatgpt-project-instructions.md", [
        NATURAL_COMMAND,
        "Ask for an issue number only when multiple valid candidates remain",
        "Internal review, correction, CI, safe merge",
    ])
    require("AGENTS.md", [
        "current intake marker",
        "legacy submissions",
        "Matching headings alone",
    ])

    issue_form = load_yaml(".github/ISSUE_TEMPLATE/create-study-path.yml")
    if issue_form.get("title") != "[Nova trilha] ":
        fail("new intake form must use the human title prefix")
    markdown = "\n".join(
        str(block.get("attributes", {}).get("value", ""))
        for block in issue_form.get("body", [])
        if isinstance(block, dict) and block.get("type") == "markdown"
    )
    if markdown.count(CURRENT_MARKER) != 1:
        fail("intake Issue Form must contain exactly one current hidden marker")

    for path in [
        "scripts/intake_resolution.py",
        "scripts/test_intake_resolution.py",
        "scripts/ensure_repository_labels.py",
        "scripts/test_repository_labels.py",
    ]:
        if not (ROOT / path).is_file():
            fail(f"missing intake regression asset: {path}")

    workflow = text(".github/workflows/validate-template.yml")
    for command in [
        "python scripts/test_intake_resolution.py",
        "python scripts/test_repository_labels.py",
    ]:
        if command not in workflow:
            fail(f"validation workflow is missing: {command}")

    manifest = load_yaml("instructions/manifest.yml")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict)
    }
    intake = phases.get("intake", {})
    if intake.get("allow_explicit_chain_to") != "diagnostic":
        fail("intake phase must allow validated diagnostic chaining")
    if intake.get("stop_after_phase") is not True:
        fail("intake must stop by default when chaining was not requested")

    print("Marker-first deterministic intake resolution and diagnostic chaining passed.")


if __name__ == "__main__":
    main()
