#!/usr/bin/env python3
"""Validate curriculum lifecycle contracts, modules and assessments."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTANCE_MARKER = ROOT / ".open-study-path/instance.yml"
TOPICS_DIR = ROOT / "study/topics"
MODULES_DIR = ROOT / "study/modules"
ASSESSMENTS_DIR = ROOT / "study/assessments"
ISSUE_FORMS_DIR = ROOT / ".github/ISSUE_TEMPLATE"
ROADMAP = ROOT / "study/roadmap.md"
ALLOWED_CURRICULUM_POLICIES = {"manual", "agent_review_then_merge"}
TOPIC_HEADINGS = [
    "## Objective",
    "## Why this matters",
    "## Prerequisites",
    "## Learning activities",
    "## Complete module",
    "## Assessment",
    "## Deliverable",
    "## Evidence",
    "## Mastery criteria",
    "## Resources",
]
MODULE_HEADINGS = [
    "## Como usar este módulo",
    "## Objetivos de aprendizagem",
    "## Verificação de pré-requisitos",
    "## Conteúdo essencial",
    "## Exemplos trabalhados",
    "## Erros comuns e como corrigi-los",
    "## Prática guiada",
    "## Prática independente",
    "## Síntese por recuperação ativa",
    "## Entregável e evidência",
    "## Avaliação do tópico",
    "## Referências",
]
VAGUE_REQUIRED_RESOURCE = re.compile(
    r"(?:a selecionar|passagem curta|uma introdução|trecho e tradução a revisar|"
    r"edição ou tradução a revisar|com edição a revisar)",
    re.IGNORECASE,
)
CANONICAL_LOCATOR = re.compile(r"(?:§|\b\d+\b|\b[IVXLCDM]+\.)")
PLACEHOLDER_CONTENT = re.compile(
    r"(?:replace me|substitua por|estude o conceito|study the core concept|"
    r"descreva o|inclua exercícios|apresente ao menos)",
    re.IGNORECASE,
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"missing YAML frontmatter: {path.relative_to(ROOT)}")
    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        fail(f"malformed frontmatter: {path.relative_to(ROOT)}")
    document = yaml.safe_load(frontmatter)
    if not isinstance(document, dict):
        fail(f"frontmatter must be an object: {path.relative_to(ROOT)}")
    return document, body


def required_resource_lines(body: str, path: Path) -> list[str]:
    match = re.search(
        r"### Required\s*(.*?)(?:\n### Optional|\n## Prompt to start a study chat|\Z)",
        body,
        re.DOTALL,
    )
    if not match:
        fail(f"missing Required resources subsection: {path.relative_to(ROOT)}")
    lines = [line.strip()[2:].strip() for line in match.group(1).splitlines() if line.strip().startswith("- ")]
    if not lines:
        fail(f"must contain at least one required resource: {path.relative_to(ROOT)}")
    return lines


def check_lifecycle_contract() -> None:
    manifest = load_yaml(ROOT / "instructions/manifest.yml")
    phases = {phase.get("id"): phase for phase in manifest.get("phases", []) if isinstance(phase, dict)}
    if "review_curriculum" in phases:
        fail("curriculum review must be internal to generation")

    generate = phases.get("generate", {})
    if generate.get("next_phase") != "publish":
        fail("generation must route to publish")
    if generate.get("internal_review") != "instructions/35-review-curriculum.md":
        fail("generation must reference the internal review checklist")
    if generate.get("merge_policy_path") != "workflow.curriculum_merge_policy":
        fail("generation must reference workflow.curriculum_merge_policy")
    if generate.get("outputs") != [
        ".open-study-path/instance.yml",
        "study/roadmap.md",
        "study/topics/",
        "study/modules/",
        "study/assessments/",
        ".github/ISSUE_TEMPLATE/assessment-topic-*.yml",
    ]:
        fail("generation outputs must include topics, complete modules, rubrics and assessment forms")

    publish = phases.get("publish", {})
    if publish.get("depends_on") != ["generate"] or publish.get("next_phase") != "evaluate":
        fail("publish must depend on generation and route to evaluate")
    evaluate = phases.get("evaluate", {})
    if evaluate.get("instruction") != "instructions/55-evaluate-topic.md":
        fail("evaluate phase must reference instructions/55-evaluate-topic.md")

    template = load_yaml(ROOT / "templates/instance.yml")
    workflow = template.get("workflow", {})
    if workflow.get("curriculum_merge_policy") != "agent_review_then_merge":
        fail("new instances must default curriculum merge to agent_review_then_merge")

    for required in [
        "instructions/30-generate-path.md",
        "instructions/35-review-curriculum.md",
        "instructions/55-evaluate-topic.md",
        "templates/module.md",
        "templates/assessment-rubric.yml",
        "templates/topic-assessment-issue-form.yml",
    ]:
        if not (ROOT / required).is_file():
            fail(f"missing curriculum file: {required}")

    if INSTANCE_MARKER.is_file():
        marker = load_yaml(INSTANCE_MARKER)
        policy = marker.get("workflow", {}).get("curriculum_merge_policy")
        if policy not in ALLOWED_CURRICULUM_POLICIES:
            fail(f"invalid curriculum_merge_policy: {policy}")


def detect_cycle(prerequisites: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(topic_id: str) -> None:
        if topic_id in visited:
            return
        if topic_id in visiting:
            fail(f"curriculum dependency cycle detected at {topic_id}")
        visiting.add(topic_id)
        for prerequisite in prerequisites[topic_id]:
            visit(prerequisite)
        visiting.remove(topic_id)
        visited.add(topic_id)

    for topic_id in prerequisites:
        visit(topic_id)


def check_module(topic_id: str, path: Path) -> None:
    metadata, body = parse_frontmatter(path)
    if metadata.get("topic_id") != topic_id:
        fail(f"module topic_id mismatch for {topic_id}")
    for heading in MODULE_HEADINGS:
        if heading not in body:
            fail(f"module {topic_id} is missing heading: {heading}")
    words = re.findall(r"\b\w+\b", body, flags=re.UNICODE)
    if len(words) < 500:
        fail(f"module {topic_id} is too short to be complete: {len(words)} words")
    if PLACEHOLDER_CONTENT.search(body):
        fail(f"module {topic_id} contains template placeholder content")
    if body.count("### Exemplo") + body.count("**Exemplo") < 2:
        fail(f"module {topic_id} must contain at least two worked examples")
    if f"Finalizei o {topic_id}. Avalie a issue #<número>." not in body:
        fail(f"module {topic_id} is missing the explicit assessment completion command")


def check_rubric(topic_id: str, path: Path) -> None:
    rubric = load_yaml(path)
    if not isinstance(rubric, dict) or rubric.get("topic_id") != topic_id:
        fail(f"invalid rubric topic_id for {topic_id}")
    passing = rubric.get("passing_score")
    if not isinstance(passing, int) or not 1 <= passing <= 100:
        fail(f"invalid passing_score for {topic_id}")
    questions = rubric.get("questions")
    if not isinstance(questions, list) or len(questions) != 5:
        fail(f"rubric {topic_id} must define exactly five questions")
    ids = [item.get("id") for item in questions if isinstance(item, dict)]
    if ids != ["q1", "q2", "q3", "q4", "q5"]:
        fail(f"rubric {topic_id} question ids must be q1..q5")
    points = [item.get("max_points") for item in questions]
    if not all(isinstance(point, int) and point > 0 for point in points) or sum(points) != 100:
        fail(f"rubric {topic_id} must total 100 points")
    for item in questions:
        for key in ["evaluates", "full_credit", "partial_credit", "no_credit"]:
            if not isinstance(item.get(key), str) or not item[key].strip():
                fail(f"rubric {topic_id} question {item.get('id')} is missing {key}")


def check_issue_form(topic_id: str, path: Path) -> None:
    form = load_yaml(path)
    if not isinstance(form, dict):
        fail(f"invalid assessment Issue Form for {topic_id}")
    if topic_id not in str(form.get("name", "")) or topic_id not in str(form.get("title", "")):
        fail(f"assessment Issue Form does not identify {topic_id}")
    body = form.get("body")
    if not isinstance(body, list):
        fail(f"assessment Issue Form body must be a list for {topic_id}")
    ids = [entry.get("id") for entry in body if isinstance(entry, dict)]
    for question_id in ["q1", "q2", "q3", "q4", "q5", "confirmation"]:
        if question_id not in ids:
            fail(f"assessment Issue Form {topic_id} is missing {question_id}")


def check_topics() -> None:
    topic_paths = sorted(TOPICS_DIR.glob("*.md")) if TOPICS_DIR.is_dir() else []
    if not topic_paths:
        print("No generated curriculum topics to validate.")
        return
    if not ROADMAP.is_file():
        fail("generated topics require study/roadmap.md")

    topics: dict[str, Path] = {}
    prerequisites: dict[str, list[str]] = {}
    roadmap = ROADMAP.read_text(encoding="utf-8")

    for path in topic_paths:
        metadata, body = parse_frontmatter(path)
        for key in [
            "id", "title", "status", "difficulty", "estimated_hours", "prerequisites",
            "module", "assessment", "assessment_form",
        ]:
            if key not in metadata:
                fail(f"topic is missing frontmatter key {key}: {path.relative_to(ROOT)}")
        topic_id = metadata["id"]
        if not isinstance(topic_id, str) or not topic_id:
            fail(f"topic id must be a non-empty string: {path.relative_to(ROOT)}")
        if topic_id in topics:
            fail(f"duplicate topic id: {topic_id}")
        hours = metadata["estimated_hours"]
        if not isinstance(hours, (int, float)) or hours <= 0:
            fail(f"estimated_hours must be positive for {topic_id}")
        topic_prerequisites = metadata["prerequisites"]
        if not isinstance(topic_prerequisites, list) or not all(isinstance(item, str) for item in topic_prerequisites):
            fail(f"prerequisites must be a string array for {topic_id}")
        for heading in TOPIC_HEADINGS:
            if heading not in body:
                fail(f"topic {topic_id} is missing heading: {heading}")
        for resource in required_resource_lines(body, path):
            if VAGUE_REQUIRED_RESOURCE.search(resource) and not CANONICAL_LOCATOR.search(resource):
                fail(f"required resource is vague in {topic_id}: {resource}")
            if not CANONICAL_LOCATOR.search(resource):
                fail(f"required resource needs a canonical locator in {topic_id}: {resource}")
        if topic_id not in roadmap:
            fail(f"roadmap does not reference topic {topic_id}")

        expected_module = f"study/modules/{topic_id}.md"
        expected_rubric = f"study/assessments/{topic_id}.yml"
        suffix = topic_id.split("-")[-1].lower()
        expected_form = f".github/ISSUE_TEMPLATE/assessment-topic-{suffix}.yml"
        if metadata["module"] != expected_module or metadata["assessment"] != expected_rubric or metadata["assessment_form"] != expected_form:
            fail(f"topic {topic_id} artifact paths are inconsistent")
        module_path = ROOT / expected_module
        rubric_path = ROOT / expected_rubric
        form_path = ROOT / expected_form
        for artifact in [module_path, rubric_path, form_path]:
            if not artifact.is_file():
                fail(f"missing artifact for {topic_id}: {artifact.relative_to(ROOT)}")
        check_module(topic_id, module_path)
        check_rubric(topic_id, rubric_path)
        check_issue_form(topic_id, form_path)

        topics[topic_id] = path
        prerequisites[topic_id] = topic_prerequisites

    for topic_id, required_ids in prerequisites.items():
        for required_id in required_ids:
            if required_id not in topics:
                fail(f"topic {topic_id} references missing prerequisite {required_id}")
            if required_id == topic_id:
                fail(f"topic {topic_id} cannot depend on itself")

    detect_cycle(prerequisites)
    print(f"Complete curriculum contract passed for {len(topics)} topics.")


def main() -> None:
    check_lifecycle_contract()
    check_topics()
    print("Curriculum validation passed.")


if __name__ == "__main__":
    main()
