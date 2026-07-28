#!/usr/bin/env python3
"""Validate lifecycle structure, human-facing language, visuals and sourced lessons."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTANCE = ROOT / ".open-study-path/instance.yml"
MERMAID = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
LINK = re.compile(r"https?://[^\s)>]+")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str | Path) -> str:
    target = ROOT / path if isinstance(path, str) else path
    if not target.is_file():
        fail(f"missing lifecycle file: {target.relative_to(ROOT)}")
    return target.read_text(encoding="utf-8")


def load_yaml(path: str) -> Any:
    return yaml.safe_load(read(path))


def require(path: str, terms: list[str]) -> None:
    content = read(path)
    for term in terms:
        if term not in content:
            fail(f"{path} is missing required term: {term}")


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    content = read(path)
    if not content.startswith("---\n"):
        fail(f"missing frontmatter: {path.relative_to(ROOT)}")
    try:
        _, raw, body = content.split("---", 2)
    except ValueError:
        fail(f"malformed frontmatter: {path.relative_to(ROOT)}")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        fail(f"frontmatter must be an object: {path.relative_to(ROOT)}")
    return data, body


def validate_manifest() -> None:
    manifest = load_yaml("instructions/manifest.yml")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict) and phase.get("id")
    }
    if "review_curriculum" in phases or "materialize_content" in phases:
        fail("review and materialization must remain internal")
    if phases.get("generate", {}).get("next_phase") != "publish":
        fail("generate must route to publish")
    if phases.get("publish", {}).get("next_phase") != "evaluate":
        fail("publish must route to evaluate")
    if phases.get("evaluate", {}).get("internal_materialization") != "instructions/57-materialize-next-content.md":
        fail("evaluation must retain automatic materialization")


def validate_instance_config() -> dict[str, Any]:
    config_path = ".open-study-path/instance.yml" if INSTANCE.is_file() else "templates/instance.yml"
    document = load_yaml(config_path)
    workflow = document.get("workflow", {})
    if workflow.get("curriculum_merge_policy") not in {"manual", "agent_review_then_merge"}:
        fail(f"invalid curriculum merge policy in {config_path}")
    generation = document.get("content_generation", {})
    if generation.get("strategy") not in {"adaptive_rolling_window", "full_upfront"}:
        fail(f"invalid content generation strategy in {config_path}")
    visual = generation.get("visual_learning", {})
    if visual.get("mermaid_enabled") is not True:
        fail(f"{config_path} must enable Mermaid")
    if not isinstance(visual.get("minimum_diagrams_per_materialized_module"), int):
        fail(f"{config_path} must define a diagram minimum")
    return document


def validate_contract_terms() -> None:
    require("docs/learner-facing-language.md", [
        "Quatro perguntas da resposta principal",
        "Preenchi o formulário. Pode continuar.",
        "Terminei <título da aula>. Avalie minhas respostas.",
    ])
    require("docs/content-quality-and-sources.md", [
        "Como este conteúdo foi construído",
        "Fontes e caminhos para aprofundar",
        "no mínimo três fontes",
        "timestamp",
    ])
    require("instructions/phase-completion.md", [
        "Do not foreground PR numbers",
        "Organize minha trilha nas ferramentas que escolhemos.",
        "Conectei o Quizlet. Crie meus flashcards.",
    ])
    require("instructions/30-generate-path.md", [
        "Source and provenance contract",
        "Other ways to learn",
        "three to seven curated sources",
        "Terminei <título da aula>. Avalie minhas respostas.",
    ])
    require("instructions/35-review-curriculum.md", [
        "Source and content review",
        "learner-facing prose",
        "Trello card text uses human titles",
    ])
    require("instructions/40-publish-tasks.md", [
        "Human card titles",
        "Sua sessão de estudo",
        "Esta aula será preparada automaticamente",
    ])
    require("templates/module.md", [
        "## Como este conteúdo foi construído",
        "## Fontes e caminhos para aprofundar",
        "## Outras formas de aprender",
        "flashcards_study: null",
    ])
    require("templates/topic.md", [
        "## O que você vai aprender",
        "## Por que isso importa para você",
        "## Para concluir esta etapa",
    ])
    require("templates/integrations-plan.md", [
        "# Ferramentas que podem ajudar nesta trilha",
        "<details>",
        "Conectei o Quizlet. Crie meus flashcards.",
    ])
    require("templates/chatgpt-project-instructions.md", [
        "Experience for the person",
        "Do not lead successful responses",
        "Fontes e caminhos para aprofundar",
    ])
    require("README.md", [
        "Configure este repositório como uma nova trilha de estudos",
        "Conteúdo com fontes",
        "Linguagem voltada para quem estuda",
    ])
    require("AGENTS.md", [
        "Do not lead with PR, CI",
        "docs/content-quality-and-sources.md",
        "Human task titles",
    ])


def validate_generated(document: dict[str, Any]) -> None:
    topics_dir = ROOT / "study/topics"
    if not topics_dir.is_dir():
        return

    topics = sorted(topics_dir.glob("TOPIC-*.md"))
    if not topics:
        return

    roadmap = ROOT / "study/roadmap.md"
    if not roadmap.is_file() or not MERMAID.findall(read(roadmap)):
        fail("generated roadmap must contain a Mermaid dependency diagram")

    minimum = document["content_generation"]["visual_learning"]["minimum_diagrams_per_materialized_module"]
    for topic_path in topics:
        metadata, _ = parse_frontmatter(topic_path)
        if metadata.get("content_status") != "materialized":
            continue
        topic_id = metadata.get("id")
        module_value = metadata.get("module")
        if not isinstance(module_value, str):
            fail(f"materialized topic {topic_id} must define a module")
        module_path = ROOT / module_value
        module_meta, body = parse_frontmatter(module_path)
        diagrams = MERMAID.findall(body)
        if len(diagrams) < minimum:
            fail(f"module {topic_id} has fewer Mermaid diagrams than configured")
        for section in [
            "## Mapa visual",
            "## Outras formas de aprender",
            "## Como este conteúdo foi construído",
            "## Fontes e caminhos para aprofundar",
        ]:
            if section not in body:
                fail(f"module {topic_id} is missing section: {section}")
        source_section = body.split("## Fontes e caminhos para aprofundar", 1)[1]
        links = LINK.findall(source_section)
        if len(set(links)) < 3:
            fail(f"module {topic_id} needs at least three verified source links")
        if "Como foi usada" not in source_section and "Como foi usado" not in source_section:
            fail(f"module {topic_id} must explain how sources were used")
        if module_meta.get("visual_diagrams", 0) < minimum:
            fail(f"module {topic_id} must declare configured visual_diagrams")


def main() -> None:
    validate_manifest()
    document = validate_instance_config()
    validate_contract_terms()
    validate_generated(document)
    print("Guided lifecycle, human-facing language, visuals and source-rich lessons passed.")


if __name__ == "__main__":
    main()
