#!/usr/bin/env python3
"""Validate guided lifecycle, review, publication and evaluation contracts."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTANCE_MARKER = ROOT / ".open-study-path/instance.yml"
ALLOWED_CURRICULUM_POLICIES = {"manual", "agent_review_then_merge"}
DEPRECATED_PUBLICATION_SUFFIX = "Não altere o conteúdo pedagógico aprovado"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_yaml(path: str) -> Any:
    with (ROOT / path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require_terms(path: str, terms: list[str]) -> None:
    if not (ROOT / path).is_file():
        fail(f"missing guided lifecycle file: {path}")
    text = load_text(path)
    for term in terms:
        if term not in text:
            fail(f"{path} is missing required term: {term}")


def validate_workflow(document: dict[str, Any], path: str, *, default_required: bool) -> None:
    workflow = document.get("workflow")
    if not isinstance(workflow, dict):
        fail(f"{path} must define workflow")
    if "curriculum_review_policy" in workflow:
        fail(f"{path} uses deprecated workflow.curriculum_review_policy")
    policy = workflow.get("curriculum_merge_policy")
    if policy not in ALLOWED_CURRICULUM_POLICIES:
        fail(f"invalid curriculum_merge_policy in {path}: {policy}")
    if default_required and policy != "agent_review_then_merge":
        fail("new instances must default curriculum_merge_policy to agent_review_then_merge")


def main() -> None:
    manifest = load_yaml("instructions/manifest.yml")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict) and phase.get("id")
    }

    if "review_curriculum" in phases:
        fail("review_curriculum must remain internal to generation")

    generate = phases.get("generate", {})
    expected_outputs = [
        ".open-study-path/instance.yml",
        "study/roadmap.md",
        "study/topics/",
        "study/modules/",
        "study/assessments/",
        ".github/ISSUE_TEMPLATE/assessment-topic-*.yml",
    ]
    if generate.get("next_phase") != "publish":
        fail("generate must route to publish")
    if generate.get("internal_review") != "instructions/35-review-curriculum.md":
        fail("generate must reference internal curriculum review")
    if generate.get("outputs") != expected_outputs:
        fail("generate must output topics, complete modules, rubrics and assessment forms")

    publish = phases.get("publish", {})
    if publish.get("depends_on") != ["generate"] or publish.get("next_phase") != "evaluate":
        fail("publish must depend on generate and route to evaluate")
    if publish.get("internal_preflight") != "instructions/42-integration-preflight.md":
        fail("publish must reference integration preflight")

    evaluate = phases.get("evaluate", {})
    if evaluate.get("instruction") != "instructions/55-evaluate-topic.md":
        fail("evaluate phase must reference topic evaluation instruction")
    if evaluate.get("outputs") != ["state/assessments/", "state/progress.json"]:
        fail("evaluate outputs must include assessment history and progress")

    validate_workflow(load_yaml("templates/instance.yml"), "templates/instance.yml", default_required=True)
    if INSTANCE_MARKER.is_file():
        validate_workflow(load_yaml(".open-study-path/instance.yml"), ".open-study-path/instance.yml", default_required=False)

    require_terms("instructions/30-generate-path.md", [
        "study/modules/",
        "study/assessments/",
        "Complete-content contract",
        "five substantial prompts",
        "Revisão do PR: aprovada pelo agente e pelo CI",
        "anotações adicionadas ao PR",
        "Finalizei o TOPIC-000. Avalie a issue #<número>.",
    ])
    require_terms("instructions/35-review-curriculum.md", [
        "every module teaches the content",
        "rubric totaling 100 points",
        "anotações adicionadas ao PR",
        "aprovada pelo agente e pelo CI",
    ])
    require_terms("instructions/40-publish-tasks.md", [
        "study/modules/",
        "study/assessments/",
        "direct link to the complete module",
        "direct link to the assessment Issue Form",
        "Do not start an improvised lesson in chat by default",
    ])
    require_terms("instructions/55-evaluate-topic.md", [
        "explicit GitHub issue number",
        "Grade every response independently",
        "total score from 0 to 100",
        "focused GitHub recovery issue",
        "Finalizei a recuperação do TOPIC-000",
        "Ace Quiz Maker",
    ])
    require_terms("instructions/phase-completion.md", [
        "Revisão do PR: aprovada pelo agente e pelo CI",
        "anotações adicionadas ao PR",
        "Do not begin an improvised lesson in chat by default",
        "Finalizei o TOPIC-000. Avalie a issue #<número>.",
    ])
    require_terms("templates/topic.md", [
        "module: study/modules/TOPIC-000.md",
        "assessment: study/assessments/TOPIC-000.yml",
        "Submit the GitHub assessment form",
    ])
    for path in [
        "templates/module.md",
        "templates/assessment-rubric.yml",
        "templates/topic-assessment-issue-form.yml",
    ]:
        if not (ROOT / path).is_file():
            fail(f"missing course artifact template: {path}")

    for path in [
        "instructions/40-publish-tasks.md",
        "instructions/42-integration-preflight.md",
        "instructions/phase-completion.md",
        "templates/chatgpt-project-instructions.md",
        "AGENTS.md",
    ]:
        if DEPRECATED_PUBLICATION_SUFFIX in load_text(path):
            fail(f"{path} still requires the owner to restate curriculum immutability")

    print("Guided full-course generation, publication and evaluation contracts passed.")


if __name__ == "__main__":
    main()
