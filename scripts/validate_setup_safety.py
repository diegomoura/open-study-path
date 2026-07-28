#!/usr/bin/env python3
"""Validate first-chat setup discovery, scope and template-marker preservation."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SETUP_EXECUTION = "instructions/02-setup-execution.md"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def text(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"missing setup-safety file: {path}")
    return target.read_text(encoding="utf-8")


def require(path: str, terms: list[str]) -> None:
    content = text(path)
    for term in terms:
        if term not in content:
            fail(f"{path} is missing setup-safety term: {term}")


def run_validator(repo: Path, check: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/validate_template.py", check],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def materialize_minimal_instance(repo: Path) -> None:
    instance = (repo / "templates/instance.yml").read_text(encoding="utf-8")
    instance = instance.replace("OWNER/REPOSITORY", "example/setup-regression")
    (repo / ".open-study-path/instance.yml").write_text(instance, encoding="utf-8")

    shutil.copy2(repo / "study.config.example.yml", repo / "study.config.yml")

    state_dir = repo / "state"
    state_dir.mkdir(exist_ok=True)
    shutil.copy2(repo / "templates/state/intake-summary.json", state_dir / "intake-summary.json")
    shutil.copy2(repo / "templates/state/progress.json", state_dir / "progress.json")

    integrations = (repo / "templates/integrations-state.json").read_text(encoding="utf-8")
    integrations = integrations.replace("OWNER/REPOSITORY", "example/setup-regression")
    (state_dir / "integrations.json").write_text(integrations, encoding="utf-8")

    study_dir = repo / "study"
    study_dir.mkdir(exist_ok=True)
    shutil.copy2(repo / "templates/roadmap.md", study_dir / "roadmap.md")


def validate_contracts() -> None:
    require(SETUP_EXECUTION, [
        "Repository metadata",
        ".open-study-path/template.yml",
        "Do not reconstruct the repository",
        "Allowed setup diff",
        "failing, pending, cancelled, missing or unreadable required check",
        "Do not claim that the instance is configured",
    ])
    require("AGENTS.md", [
        SETUP_EXECUTION,
        "Repository metadata",
        "retains `.open-study-path/template.yml`",
        "CI is red or unknown",
    ])
    require("templates/chatgpt-project-instructions.md", [
        SETUP_EXECUTION,
        "Repository size",
        "keeps `.open-study-path/template.yml`",
        "CI is red or unknown",
    ])
    require("instructions/00-bootstrap.md", [
        SETUP_EXECUTION,
        "sentinel files",
        "Keep `.open-study-path/template.yml`",
        "merge gate",
    ])
    require("instructions/05-configure-intake.md", [
        SETUP_EXECUTION,
        "Do not infer absence from repository size",
        "Do not edit, recreate or replace it",
        "failing, pending, cancelled, missing or unreadable",
    ])
    require("instructions/phase-completion.md", [
        "current unchanged pull-request head",
        "cannot be verified",
        "Do not merge and do not send a successful phase response",
    ])
    require("docs/validation-modes.md", [
        "repository metadata",
        "must remain present",
        "takes precedence",
    ])

    manifest = yaml.safe_load(text("instructions/manifest.yml"))
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict)
    }
    for phase_id in ["bootstrap_instance", "configure_intake"]:
        if phases.get(phase_id, {}).get("execution_contract") != SETUP_EXECUTION:
            fail(f"{phase_id} must reference {SETUP_EXECUTION}")

    workflow = text(".github/workflows/validate-template.yml")
    if "python scripts/validate_setup_safety.py" not in workflow:
        fail("validation workflow must run setup-safety regression")


def validate_instance_regression() -> None:
    with tempfile.TemporaryDirectory(prefix="open-study-path-setup-") as temporary:
        repo = Path(temporary) / "repo"
        shutil.copytree(
            ROOT,
            repo,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        materialize_minimal_instance(repo)

        template_marker = repo / ".open-study-path/template.yml"
        instance_marker = repo / ".open-study-path/instance.yml"
        if not template_marker.is_file() or not instance_marker.is_file():
            fail("a configured instance must retain both repository markers")

        valid = run_validator(repo, "all")
        if valid.returncode != 0:
            details = (valid.stdout + valid.stderr).strip()
            fail(f"safe template-to-instance setup did not validate: {details}")

        template_marker.unlink()
        destructive = run_validator(repo, "yaml")
        combined = destructive.stdout + destructive.stderr
        if destructive.returncode == 0:
            fail("validator accepted an instance that deleted the template marker")
        if "missing required YAML file: .open-study-path/template.yml" not in combined:
            fail("template-marker deletion failed for an unexpected reason")


def main() -> None:
    validate_contracts()
    validate_instance_regression()
    print("Safe repository discovery, setup scope and marker preservation passed.")


if __name__ == "__main__":
    main()
