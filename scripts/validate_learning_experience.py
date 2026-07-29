#!/usr/bin/env python3
"""Validate learner-facing language, progressive lessons, flashcards and sources."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

from beginner_pedagogy import validate_module_pedagogy

ROOT = Path(__file__).resolve().parents[1]
INSTANCE = ROOT / ".open-study-path/instance.yml"
TOPICS = ROOT / "study/topics"
MODULES = ROOT / "study/modules"
ISSUE_FORMS = ROOT / ".github/ISSUE_TEMPLATE"
LINK = re.compile(r"https?://[^\s)>]+")


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


def require_terms(path: str, terms: list[str]) -> None:
    content = text(path)
    for term in terms:
        if term not in content:
            fail(f"{path} is missing learner-experience term: {term}")


def forbid_terms(path: str, terms: list[str]) -> None:
    content = text(path)
    for term in terms:
        if term in content:
            fail(f"{path} retains obsolete learner-experience term: {term}")


def validate_contracts() -> None:
    module_template = text("templates/module.md")
    if module_template.startswith("---\n"):
        fail("lesson template must not expose YAML frontmatter")
    require_terms("templates/module.md", [
        "Não adicione frontmatter YAML a este arquivo",
        "## Começando do zero",
        "### Vocabulário desta aula",
        "## Intuição antes dos detalhes",
        "**Analogia:**",
        "**Onde a analogia deixa de funcionar:**",
        "**Exemplo concreto:**",
        "flashcards_study: study/flashcards/TOPIC-000.md",
        "<details>",
        "issues/new?template=assessment-topic-000.yml",
        "## Como este conteúdo foi construído",
        "## Fontes e caminhos para aprofundar",
        "cartão mostra somente um recurso principal de prática",
        "Terminei <título da aula>. Avalie minhas respostas.",
    ])
    require_terms("templates/topic.md", [
        "flashcards_study: null",
        "## O que você vai aprender",
        "## Por que isso importa para você",
        "não é uma página de navegação principal",
        "aula publicada não recebe frontmatter YAML",
        "Não apresente a rubrica YAML como link normal",
        "Esta aula será preparada automaticamente",
    ])
    require_terms("instructions/phase-completion.md", [
        "Do not foreground PR numbers",
        "Preenchi o formulário. Pode continuar.",
        "Organize minha trilha nas ferramentas que escolhemos.",
    ])
    require_terms("instructions/30-generate-path.md", [
        "docs/beginner-first-pedagogy.md",
        "experience in an adjacent domain",
        "first learner-visible occurrence",
        "analogy with an explicit limit",
    ])
    require_terms("instructions/35-review-curriculum.md", [
        "declared subject level",
        "title acronym",
        "realistic teaching scenario",
    ])
    require_terms("instructions/40-publish-tasks.md", [
        "One primary resource per capability",
        "one current practice link",
        "Do not link internal topic contracts",
        "show only **Praticar no Quizlet**",
        "The future card must stand on its own",
        "Sua sessão de estudo",
    ])
    forbid_terms("instructions/40-publish-tasks.md", [
        "**Pratique:** <Markdown>, <Quizlet quando real>, <TSV para importação>",
        "while preserving local links",
        "Link only the topic overview or contract",
    ])
    require_terms("docs/learner-facing-language.md", [
        "Uma interface não é um inventário",
        "um único recurso principal",
        "contratos internos em `study/topics/`",
        "Terminei <título da aula>. Avalie minhas respostas.",
    ])
    require_terms("docs/beginner-first-pedagogy.md", [
        "Nível é multidimensional",
        "Progressão conceitual",
        "Analogias com limites explícitos",
        "cenário realista criado para ensino",
        "Nunca interprete uma lista de assuntos desejados como conhecimento prévio",
    ])
    require_terms("templates/chatgpt-project-instructions.md", [
        "not an inventory of repository artifacts",
        "one primary practice link available now",
        "Do not link `study/topics/` contracts",
    ])
    require_terms("AGENTS.md", [
        "A task backend is not a repository inventory",
        "Do not link topic contracts, rubric YAML, state files or synchronization records",
        "Read `docs/beginner-first-pedagogy.md`",
    ])
    require_terms("docs/content-quality-and-sources.md", [
        "no mínimo três fontes",
        "Antes de citar",
        "Vídeos",
        "Cursos e plataformas",
        "Analogia não é evidência",
        "cenário realista",
    ])

    if not (ROOT / "templates/flashcards.md").is_file():
        fail("missing templates/flashcards.md")

    issue = load_yaml("templates/topic-assessment-issue-form.yml")
    if issue.get("title") != "[Avaliação] TOPIC-000 — Replace me":
        fail("assessment form must prefill the complete title")
    issue_text = text("templates/topic-assessment-issue-form.yml")
    for forbidden in [
        "O título já vem preenchido",
        "Você não precisa copiar o número da issue",
    ]:
        if forbidden in issue_text:
            fail(f"assessment form exposes internal mechanics: {forbidden}")

    intake = load_yaml(".github/ISSUE_TEMPLATE/create-study-path.yml")
    if intake.get("name") != "Criar meu curso":
        fail("intake form must use learner-facing course language")
    if intake.get("title") not in (None, ""):
        fail("intake issue title must be entered by the learner as the course name")


def validate_generated_modules() -> None:
    if not INSTANCE.is_file() or not MODULES.is_dir():
        return

    instance = load_yaml(INSTANCE)
    repository = instance.get("repository") if isinstance(instance, dict) else None
    if not isinstance(repository, str) or "/" not in repository:
        fail("instance repository identity is required")

    for module_path in sorted(MODULES.glob("TOPIC-*.md")):
        body = text(module_path)
        if body.startswith("---\n"):
            fail(f"module exposes operational YAML frontmatter: {module_path.relative_to(ROOT)}")

        topic_id = module_path.stem
        topic_path = TOPICS / f"{topic_id}.md"
        metadata, _ = parse_frontmatter(topic_path)
        title = metadata.get("title")
        if metadata.get("id") != topic_id or not isinstance(title, str):
            fail(f"topic contract identity is incomplete for {topic_id}")
        if not re.search(rf"^#\s+(?:\d+\.\s+|{re.escape(topic_id)}\s+[—-]\s+)?{re.escape(title)}\s*$", body, re.MULTILINE):
            fail(f"module {topic_id} must begin with its learner-facing title")

        difficulty = str(metadata.get("difficulty", ""))
        for error in validate_module_pedagogy(title, body, difficulty):
            fail(f"module {topic_id} {error}")

        suffix = topic_id.split("-")[-1].lower()
        form_name = f"assessment-topic-{suffix}.yml"
        direct_url = f"https://github.com/{repository}/issues/new?template={form_name}"
        if direct_url not in body:
            fail(f"module {topic_id} must contain its direct assessment URL")
        if f"formulário `{form_name}`" in body:
            fail(f"module {topic_id} exposes only an internal form filename")

        form_path = ISSUE_FORMS / form_name
        form = load_yaml(form_path)
        if form.get("title") != f"[Avaliação] {topic_id} — {title}":
            fail(f"assessment form {topic_id} must prefill the complete title")

        for section in [
            "## Outras formas de aprender",
            "## Como este conteúdo foi construído",
            "## Fontes e caminhos para aprofundar",
        ]:
            if section not in body:
                fail(f"module {topic_id} is missing: {section}")

        source_section = body.split("## Fontes e caminhos para aprofundar", 1)[1]
        if len(set(LINK.findall(source_section))) < 3:
            fail(f"module {topic_id} needs at least three source links")
        if "Como foi usada" not in source_section and "Como foi usado" not in source_section:
            fail(f"module {topic_id} must explain source use")

        tsv_value = metadata.get("flashcards")
        study_value = metadata.get("flashcards_study")
        if tsv_value is None and study_value is None:
            continue
        if not isinstance(tsv_value, str) or not isinstance(study_value, str):
            fail(f"topic contract {topic_id} must declare both flashcard formats")
        tsv = text(ROOT / tsv_value)
        study = text(ROOT / study_value)
        if not tsv.startswith("Front\tBack\tTags\n") or len(tsv.splitlines()) < 5:
            fail(f"flashcard TSV for {topic_id} is incomplete")
        if study.count("<details>") < 4 or study.count("<summary>") < 4:
            fail(f"Markdown flashcards for {topic_id} need expandable cards")
        if Path(study_value).name not in body or Path(tsv_value).name not in body:
            fail(f"module {topic_id} must link both flashcard formats")
        if re.search(r"Quizlet[^\n]*https?://", body, re.IGNORECASE):
            state_path = ROOT / "state/integrations.json"
            state_text = text(state_path) if state_path.is_file() else ""
            if topic_id not in state_text:
                fail(f"module {topic_id} claims an external set without integration state")


def main() -> None:
    validate_contracts()
    validate_generated_modules()
    print("Progressive learner language, metadata-free lessons, sources, assessments and flashcards passed.")


if __name__ == "__main__":
    main()
