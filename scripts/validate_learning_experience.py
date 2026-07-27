#!/usr/bin/env python3
"""Validate learner-facing flashcards, assessments and optional app offers."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTANCE = ROOT / ".open-study-path/instance.yml"
MODULES = ROOT / "study/modules"
ISSUE_FORMS = ROOT / ".github/ISSUE_TEMPLATE"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def text(path: str | Path) -> str:
    target = ROOT / path if isinstance(path, str) else path
    if not target.is_file():
        fail(f"missing learner-experience file: {target.relative_to(ROOT)}")
    return target.read_text(encoding="utf-8")


def load_yaml(path: str | Path) -> Any:
    return yaml.safe_load(text(path))


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    content = text(path)
    if not content.startswith("---\n"):
        fail(f"missing frontmatter: {path.relative_to(ROOT)}")
    try:
        _, raw, body = content.split("---", 2)
    except ValueError:
        fail(f"malformed frontmatter: {path.relative_to(ROOT)}")
    metadata = yaml.safe_load(raw)
    if not isinstance(metadata, dict):
        fail(f"frontmatter must be an object: {path.relative_to(ROOT)}")
    return metadata, body


def require_terms(path: str, terms: list[str], message: str) -> None:
    content = text(path)
    for term in terms:
        if term not in content:
            fail(f"{path} is missing {message}: {term}")


def require_contracts() -> None:
    require_terms(
        "templates/module.md",
        [
            "flashcards_study: null",
            "<details>",
            "issues/new?template=assessment-topic-000.yml",
            "Não apresente somente o nome interno",
        ],
        "learner-experience term",
    )

    if not (ROOT / "templates/flashcards.md").is_file():
        fail("missing templates/flashcards.md")

    issue_template = load_yaml("templates/topic-assessment-issue-form.yml")
    if issue_template.get("title") != "[Avaliação] TOPIC-000 — Replace me":
        fail("assessment Issue Form template must prefill the complete topic title")

    require_terms(
        "instructions/30-generate-path.md",
        [
            "Durable and usable flashcards",
            "study/flashcards/TOPIC-000.md",
            "direct clickable URL",
            "title is a useful signal, not the sole authority",
        ],
        "generation learner-experience term",
    )

    require_terms(
        "instructions/55-evaluate-topic.md",
        [
            "preferred consistency signal",
            "normalize its title",
            "Never reject or penalize",
        ],
        "editable-title handling",
    )

    require_terms(
        "instructions/phase-completion.md",
        [
            "platform Plugin Management capability",
            "nonblocking install/connect suggestion",
            "at most three connection suggestions",
            "Conectei o Quizlet ao ChatGPT. Verifique novamente e publique os flashcards dos tópicos materializados.",
        ],
        "post-generation connection-offer contract",
    )

    require_terms(
        "instructions/42-integration-preflight.md",
        [
            "## Optional app discovery and connection offer",
            "do not ask a separate text-only confirmation",
            "Never create a test flashcard set",
            "connection_offer_status",
            "displayed offer is not consent for an external write",
        ],
        "optional connection preflight term",
    )

    require_terms(
        "instructions/40-publish-tasks.md",
        [
            "nonblocking Quizlet connection suggestion",
            "first intended topic-set creation is the access check",
            "versioned replacement",
            "mark the prior resource record as superseded",
        ],
        "Quizlet publication term",
    )

    require_terms(
        "docs/integration-capabilities.md",
        [
            "## Optional connection offer",
            "explicit user click",
            "no more than three suggestions",
            "never create a disposable test resource",
        ],
        "connection-offer documentation term",
    )

    require_terms(
        "templates/integrations-plan.md",
        [
            "## Oferta contextual de conexão",
            "**Oferta de conexão:**",
            "Conectei o Quizlet ao ChatGPT. Verifique novamente e publique os flashcards dos tópicos materializados.",
            "substituição versionada",
        ],
        "integration-plan connection-offer term",
    )


def validate_generated_modules() -> None:
    if not INSTANCE.is_file() or not MODULES.is_dir():
        return

    instance = load_yaml(INSTANCE)
    repository = instance.get("repository") if isinstance(instance, dict) else None
    if not isinstance(repository, str) or "/" not in repository:
        fail("instance repository identity is required for direct assessment links")

    for module_path in sorted(MODULES.glob("TOPIC-*.md")):
        metadata, body = parse_frontmatter(module_path)
        topic_id = metadata.get("topic_id")
        title = metadata.get("title")
        if not isinstance(topic_id, str) or not isinstance(title, str):
            fail(f"module identity is incomplete: {module_path.relative_to(ROOT)}")

        suffix = topic_id.split("-")[-1].lower()
        form_name = f"assessment-topic-{suffix}.yml"
        direct_url = f"https://github.com/{repository}/issues/new?template={form_name}"
        if direct_url not in body:
            fail(f"module {topic_id} must contain its direct assessment Issue Form URL")
        if f"formulário `{form_name}`" in body:
            fail(f"module {topic_id} must not present only the internal form filename")

        form_path = ISSUE_FORMS / form_name
        form = load_yaml(form_path)
        expected_title = f"[Avaliação] {topic_id} — {title}"
        if form.get("title") != expected_title:
            fail(f"assessment Issue Form {topic_id} must prefill the complete title")

        tsv_value = metadata.get("flashcards")
        study_value = metadata.get("flashcards_study")
        if tsv_value is None and study_value is None:
            continue
        if not isinstance(tsv_value, str) or not isinstance(study_value, str):
            fail(f"module {topic_id} must declare both flashcards and flashcards_study")

        tsv_path = ROOT / tsv_value
        study_path = ROOT / study_value
        tsv = text(tsv_path)
        study = text(study_path)
        if not tsv.startswith("Front\tBack\tTags\n"):
            fail(f"flashcard TSV for {topic_id} must use Front/Back/Tags headers")
        if len(tsv.splitlines()) < 5:
            fail(f"flashcard TSV for {topic_id} needs at least four cards")
        if study.count("<details>") < 4 or study.count("<summary>") < 4:
            fail(f"Markdown flashcards for {topic_id} need at least four expandable cards")
        if Path(study_value).name not in body or Path(tsv_value).name not in body:
            fail(f"module {topic_id} must link both Markdown and TSV flashcards")
        if re.search(r"Quizlet[^\n]*https?://", body, re.IGNORECASE):
            state_path = ROOT / "state/integrations.json"
            state_text = text(state_path) if state_path.is_file() else ""
            if topic_id not in state_text:
                fail(f"module {topic_id} claims an external flashcard URL without integration state")


def main() -> None:
    require_contracts()
    validate_generated_modules()
    print(
        "Learner-facing flashcards, assessment links, editable titles and optional app offers passed."
    )


if __name__ == "__main__":
    main()
