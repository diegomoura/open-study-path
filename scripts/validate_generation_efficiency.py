#!/usr/bin/env python3
"""Validate the bounded, local-first curriculum generation contract."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXECUTION_CONTRACT = "instructions/32-generation-execution.md"


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
    require(
        EXECUTION_CONTRACT,
        [
            "Assemble the complete allowed phase diff before opening the pull request",
            "Every intermediate and final commit",
            "GitHub Actions is the final confirmation",
            "Do not add instrumentation commits",
            "`.github/workflows/`",
            "scripts/validate_curriculum_safe.py",
            "Terminal condition",
            "do not perform further research",
            "Do not attach or list them as primary learner artifacts",
        ],
    )
    require(
        "AGENTS.md",
        [
            EXECUTION_CONTRACT,
            "CI is confirmation, not the primary linter",
            "even temporarily",
            "current unchanged head",
            "## Publication and integrations",
            "## Deterministic assessment resolution",
            "## Automatic next-content materialization",
            "## Source of truth",
            "## Safety",
            "Finalizei o TOPIC-000. Avalie minhas respostas.",
            "instructions/57-materialize-next-content.md",
        ],
    )
    require(
        "templates/chatgpt-project-instructions.md",
        [
            EXECUTION_CONTRACT,
            "complete allowed diff before opening the PR",
            "Do not attach internal diagnostic ZIPs",
        ],
    )
    require(
        "instructions/phase-completion.md",
        [
            "Internal logs and diagnostic ZIP files",
            "current PR head is unchanged",
            "finish immediately",
        ],
    )

    manifest = load_yaml("instructions/manifest.yml")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict)
    }
    generate = phases.get("generate", {})
    if generate.get("execution_contract") != EXECUTION_CONTRACT:
        fail("generate phase must reference the efficient execution contract")

    workflow = text(".github/workflows/validate-template.yml")
    for command in [
        "python scripts/validate_generation_efficiency.py",
        "python scripts/test_curriculum_placeholder_detection.py",
        "python scripts/validate_curriculum_safe.py",
    ]:
        if command not in workflow:
            fail(f"validation workflow is missing: {command}")
    if "python scripts/validate_curriculum.py" in workflow:
        fail("workflow must use structural placeholder detection through the safe validator")

    print("Efficient curriculum generation and complete agent lifecycle contracts passed.")


if __name__ == "__main__":
    main()
