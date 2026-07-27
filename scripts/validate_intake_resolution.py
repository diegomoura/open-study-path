#!/usr/bin/env python3
"""Validate deterministic intake discovery and guided diagnostic chaining."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTINUE_COMMAND = (
    "Enviei o formulário. Localize e importe a única submissão válida. "
    "Conclua e valide esta etapa; depois, inicie o diagnóstico proporcional "
    "com perguntas curtas, uma por vez."
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def text(path: str) -> str:
    file_path = ROOT / path
    if not file_path.is_file():
        fail(f"missing intake-resolution contract: {path}")
    return file_path.read_text(encoding="utf-8")


def require(path: str, terms: list[str]) -> None:
    content = text(path)
    for term in terms:
        if term not in content:
            fail(f"{path} is missing deterministic-intake term: {term}")


def load_yaml(path: str) -> Any:
    return yaml.safe_load(text(path))


def main() -> None:
    require(
        "instructions/05-configure-intake.md",
        [
            "https://github.com/OWNER/REPOSITORY/issues/new?template=create-study-path.yml",
            "direct clickable link",
            CONTINUE_COMMAND,
            "Do not require the owner to copy an issue number",
            "explicit issue number remains accepted",
        ],
    )
    require(
        "instructions/10-intake.md",
        [
            "study-request",
            "[Study Path]:",
            "expected field headings",
            "exactly one valid candidate",
            "When none remain",
            "more than one remains",
            "never select an arbitrary newest repository issue",
            "state/intake-summary.json.source_reference",
            "intake:imported",
            "immediately invoke `instructions/20-diagnostic.md`",
        ],
    )
    require(
        "instructions/phase-completion.md",
        [
            "Always return the direct clickable intake URL",
            CONTINUE_COMMAND,
            "Do not ask the owner to copy an issue number",
            "If zero valid submissions are found",
            "more than one valid submission remains",
        ],
    )
    require(
        "templates/chatgpt-project-instructions.md",
        [
            "chain intake import into diagnostic only after",
            "resolve exactly one valid `study-request` issue",
            "return the direct form link when none exists",
        ],
    )

    manifest = load_yaml("instructions/manifest.yml")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict)
    }
    intake = phases.get("intake", {})
    if intake.get("allow_explicit_chain_to") != "diagnostic":
        fail("intake phase must allow an explicit validated chain to diagnostic")
    if intake.get("stop_after_phase") is not True:
        fail("intake must still stop by default when chaining was not requested")

    print("Deterministic intake resolution and validated diagnostic chaining passed.")


if __name__ == "__main__":
    main()
