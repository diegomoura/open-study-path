#!/usr/bin/env python3
"""Regression tests for automatic ChatGPT Project Instructions rendering."""

from __future__ import annotations

from pathlib import Path

import yaml

from render_project_instructions import (
    COMPATIBILITY_MARKER,
    PLACEHOLDER,
    render_instructions,
)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates/chatgpt-project-instructions.md"
WORKFLOW = ROOT / ".github/workflows/render-project-instructions.yml"
MARKER = ROOT / ".open-study-path/template.yml"
INSTANCE = ROOT / ".open-study-path/instance.yml"


def main() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    first_repository = "example/generative-ai-study"
    renamed_repository = "example/genai-study-renamed"

    rendered = render_instructions(source, first_repository)
    visible = rendered.replace(COMPATIBILITY_MARKER, "")
    if PLACEHOLDER in visible:
        raise SystemExit("visible repository placeholder remained after rendering")
    if COMPATIBILITY_MARKER not in rendered:
        raise SystemExit("hidden compatibility marker was not preserved")
    if f"- Instance: `{first_repository}`" not in rendered:
        raise SystemExit("rendered instructions missed the instance identity")
    if "The repository identifier is already filled in." not in rendered:
        raise SystemExit("rendered instructions still ask for manual replacement")

    if render_instructions(rendered, first_repository) != rendered:
        raise SystemExit("rendering is not idempotent")

    renamed = render_instructions(rendered, renamed_repository)
    if first_repository in renamed or renamed_repository not in renamed:
        raise SystemExit("repository rename was not propagated")

    if not WORKFLOW.is_file():
        raise SystemExit("automatic Project Instructions workflow is missing")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for term in [
        "github.repository != 'diegomoura/open-study-path'",
        "github.event.repository.default_branch",
        "contents: write",
        "scripts/render_project_instructions.py",
        'git commit -m "chore: prepare ChatGPT project instructions"',
    ]:
        if term not in workflow:
            raise SystemExit(f"renderer workflow is missing: {term}")

    marker = yaml.safe_load(MARKER.read_text(encoding="utf-8"))
    setup = marker.get("instance_setup", {})
    if setup.get("chatgpt_project_instructions_renderer") != "scripts/render_project_instructions.py":
        raise SystemExit("template marker does not register the renderer")
    if setup.get("chatgpt_project_instructions_workflow") != ".github/workflows/render-project-instructions.yml":
        raise SystemExit("template marker does not register the renderer workflow")

    if INSTANCE.is_file():
        instance = yaml.safe_load(INSTANCE.read_text(encoding="utf-8"))
        repository = instance.get("repository") if isinstance(instance, dict) else None
        if not isinstance(repository, str) or "/" not in repository:
            raise SystemExit("instance marker has no valid repository identity")
        if render_instructions(source, repository) != source:
            raise SystemExit(
                "ChatGPT Project Instructions do not match the instance repository"
            )

    print("Automatic Project Instructions rendering passed.")


if __name__ == "__main__":
    main()
