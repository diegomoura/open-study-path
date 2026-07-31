#!/usr/bin/env python3
"""Validate bounded generation while keeping technical work out of learner responses."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXECUTION_CONTRACT = "instructions/32-generation-execution.md"
TERMINAL_RESOLVER = "scripts/generation_terminal_state.py"
TERMINAL_TESTS = "scripts/test_generation_terminal_state.py"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def text(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"missing generation-efficiency file: {path}")
    return target.read_text(encoding="utf-8")


def require(path: str, terms: list[str]) -> None:
    content = text(path)
    for term in terms:
        if term not in content:
            fail(f"{path} is missing generation-efficiency term: {term}")


def load_yaml(path: str) -> Any:
    return yaml.safe_load(text(path))


def main() -> None:
    require(EXECUTION_CONTRACT, [
        "Connector-first execution",
        "Do not attempt `gh`, `git clone`, `curl`",
        "Do not use fixed `sleep` loops",
        "Assemble the complete allowed phase diff before opening the pull request",
        "Every intermediate and final commit",
        "GitHub Actions is the final confirmation",
        "A failed locator, fingerprint, schema, path, placeholder, render, integration-plan or review-coverage check is internal correction work",
        "Batch every failure of the same deterministic class",
        "Do not add instrumentation commits",
        "`.github/workflows/`",
        "scripts/validate_curriculum_safe.py",
        TERMINAL_RESOLVER,
        "Final current-head read-back",
        "Never say that the trail is generated while the pull request is open or draft",
        "Terminal condition",
        "do not perform further research",
        "Do not attach or list them as primary learner artifacts",
    ])
    require("AGENTS.md", [
        EXECUTION_CONTRACT,
        "Complete them before responding",
        "Do not lead with PR, CI",
        "instructions/57-materialize-next-content.md",
        "Natural commands presented to the learner",
        "## Safety",
    ])
    require("templates/chatgpt-project-instructions.md", [
        "Internal review, correction, CI, safe merge",
        "Do not lead successful responses",
        "Never store credentials",
        EXECUTION_CONTRACT,
    ])
    require("instructions/phase-completion.md", [
        "Finish validation, review, correction, safe merge",
        "Do not foreground PR numbers",
        "Internal logs and diagnostic ZIP files",
    ])
    require("docs/learner-facing-language.md", [
        "O que não deve aparecer por padrão após sucesso",
        "hash de commit ou merge",
    ])

    for path in [TERMINAL_RESOLVER, TERMINAL_TESTS]:
        text(path)

    manifest = load_yaml("instructions/manifest.yml")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict)
    }
    if phases.get("generate", {}).get("execution_contract") != EXECUTION_CONTRACT:
        fail("generate phase must reference the efficient execution contract")

    workflow = text(".github/workflows/validate-template.yml")
    for command in [
        "python scripts/test_generation_terminal_state.py",
        "python scripts/validate_generation_efficiency.py",
        "python scripts/validate_learning_experience.py",
        "python scripts/test_curriculum_placeholder_detection.py",
        "python scripts/validate_curriculum_safe.py",
    ]:
        if command not in workflow:
            fail(f"validation workflow is missing: {command}")
    if "python scripts/validate_curriculum.py" in workflow:
        fail("workflow must use structural placeholder detection through the safe validator")

    print("Efficient generation and stable completion contracts passed.")


if __name__ == "__main__":
    main()
