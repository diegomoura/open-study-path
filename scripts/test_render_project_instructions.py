#!/usr/bin/env python3
"""Regression tests for automatic ChatGPT Project Instructions rendering."""

from __future__ import annotations

from pathlib import Path

from render_project_instructions import PLACEHOLDER, render_instructions

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates/chatgpt-project-instructions.md"


def main() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    first_repository = "example/generative-ai-study"
    renamed_repository = "example/genai-study-renamed"

    rendered = render_instructions(source, first_repository)
    if PLACEHOLDER in rendered:
        raise SystemExit("repository placeholder remained after rendering")
    if f"- Instance: `{first_repository}`" not in rendered:
        raise SystemExit("rendered instructions missed the instance identity")
    if "The repository identifier is already filled in." not in rendered:
        raise SystemExit("rendered instructions still ask for manual replacement")

    if render_instructions(rendered, first_repository) != rendered:
        raise SystemExit("rendering is not idempotent")

    renamed = render_instructions(rendered, renamed_repository)
    if first_repository in renamed or renamed_repository not in renamed:
        raise SystemExit("repository rename was not propagated")

    print("Automatic Project Instructions rendering passed.")


if __name__ == "__main__":
    main()
