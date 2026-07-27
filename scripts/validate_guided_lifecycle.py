#!/usr/bin/env python3
"""Validate guided rolling-course lifecycle contracts."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTANCE_MARKER = ROOT / ".open-study-path/instance.yml"
ALLOWED_CURRICULUM_POLICIES = {"manual", "agent_review_then_merge"}
ALLOWED_CONTENT_STRATEGIES = {"adaptive_rolling_window", "full_upfront"}
DEPRECATED_PUBLICATION_SUFFIX = "Não altere o conteúdo pedagógico aprovado"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_yaml(path: str) -> Any:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require_terms(path: str, terms: list[str]) -> None:
    if not (ROOT / path).is_file():
        fail(f"missing lifecycle file: {path}")
    text = load_text(path)
    for term in terms:
        if term not in text:
            fail(f"{path} is missing required term: {term}")


def validate_instance_contract(document: dict[str, Any], path: str, *, defaults: bool) -> None:
    workflow = document.get("workflow")
    if not isinstance(workflow, dict):
        fail(f"{path} must define workflow")
    if "curriculum_review_policy" in workflow:
        fail(f"{path} uses deprecated curriculum_review_policy")
    policy = workflow.get("curriculum_merge_policy")
    if policy not in ALLOWED_CURRICULUM_POLICIES:
        fail(f"invalid curriculum_merge_policy in {path}: {policy}")
    if defaults and policy != "agent_review_then_merge":
        fail("new instances must default curriculum_merge_policy to agent_review_then_merge")

    generation = document.get("content_generation")
    if not isinstance(generation, dict):
        fail(f"{path} must define content_generation")
    if generation.get("strategy") not in ALLOWED_CONTENT_STRATEGIES:
        fail(f"invalid content generation strategy in {path}")
    if not isinstance(generation.get("lookahead_topics"), int) or generation["lookahead_topics"] < 1:
        fail(f"{path} must define positive lookahead_topics")
    if generation.get("adapt_future_modules_from_assessments") is not True:
        fail(f"{path} must enable assessment-informed adaptation")
    granularity = generation.get("granularity")
    if not isinstance(granularity, dict):
        fail(f"{path} must define granularity")
    expected = {
        "activity_minutes_min": 10,
        "activity_minutes_max": 25,
        "activities_per_topic_min": 3,
        "activities_per_topic_max": 7,
        "topic_minutes_target_min": 45,
        "topic_minutes_target_max": 90,
        "split_topic_above_minutes": 120,
    }
    if defaults:
        for key, value in expected.items():
            if granularity.get(key) != value:
                fail(f"default {key} must be {value}")


def main() -> None:
    manifest = load_yaml("instructions/manifest.yml")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict) and phase.get("id")
    }
    if "review_curriculum" in phases or "materialize_content" in phases:
        fail("review and materialization must remain internal")

    generate = phases.get("generate", {})
    expected_generate_outputs = [
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
        fail("generate must reference internal review")
    if generate.get("outputs") != expected_generate_outputs:
        fail("generate output contract changed unexpectedly")

    publish = phases.get("publish", {})
    if publish.get("depends_on") != ["generate"] or publish.get("next_phase") != "evaluate":
        fail("publish must depend on generate and route to evaluate")
    if publish.get("internal_preflight") != "instructions/42-integration-preflight.md":
        fail("publish must reference integration preflight")

    evaluate = phases.get("evaluate", {})
    if evaluate.get("instruction") != "instructions/55-evaluate-topic.md":
        fail("evaluate must reference topic evaluation")
    if evaluate.get("internal_materialization") != "instructions/57-materialize-next-content.md":
        fail("evaluate must run rolling materialization internally")
    required_evaluate_outputs = {
        "state/assessments/", "state/progress.json", "study/roadmap.md", "study/topics/",
        "study/modules/", "study/assessments/", ".github/ISSUE_TEMPLATE/assessment-topic-*.yml",
    }
    if set(evaluate.get("outputs", [])) != required_evaluate_outputs:
        fail("evaluate outputs must include progress and rolling content artifacts")

    validate_instance_contract(load_yaml("templates/instance.yml"), "templates/instance.yml", defaults=True)
    if INSTANCE_MARKER.is_file():
        validate_instance_contract(load_yaml(".open-study-path/instance.yml"), ".open-study-path/instance.yml", defaults=False)

    require_terms("instructions/30-generate-path.md", [
        "Generate a complete dependency-aware roadmap",
        "adaptive_rolling_window",
        "lookahead_topics",
        "three to seven execution actions",
        "10–25 minutes",
        "content_status: planned",
        "Finalizei o TOPIC-000. Avalie minhas respostas.",
        "Never assume that an arbitrary newest repository issue",
    ])
    require_terms("instructions/35-review-curriculum.md", [
        "`planned` or `materialized`",
        "three to seven focused activities",
        "deterministic topic marker",
        "rolling-window size",
        "Revisão do PR: aprovada pelo agente e pelo CI",
    ])
    require_terms("instructions/40-publish-tasks.md", [
        "### Materialized topic",
        "### Planned topic",
        "Do not add nonexistent module",
        "assessment:submitted",
        "Finalizei o TOPIC-000. Avalie minhas respostas.",
    ])
    require_terms("instructions/55-evaluate-topic.md", [
        "issue number is optional",
        "Exactly one valid candidate",
        "More than one candidate",
        "Never choose an arbitrary newest repository issue",
        "instructions/57-materialize-next-content.md",
        "The learner must not send a separate command",
    ])
    require_terms("instructions/57-materialize-next-content.md", [
        "not a separate user-facing phase",
        "restore `lookahead_topics`",
        "verified assessment results",
        "must not silently rewrite",
        "Do not ask the owner for a separate generation",
    ])
    require_terms("instructions/phase-completion.md", [
        "initial rolling window",
        "Do not require the learner to copy the issue number",
        "automatically materialize",
        "Finalizei a recuperação do TOPIC-000. Avalie minhas respostas.",
    ])
    require_terms("templates/topic.md", [
        "content_status: planned",
        "content_version: 0",
        "between three and seven small",
        "Finalizei o TOPIC-000. Avalie minhas respostas.",
    ])
    require_terms("templates/module.md", [
        "## Plano de execução",
        "três a sete ações",
        "entre 10 e 25 minutos",
        "Finalizei o TOPIC-000. Avalie minhas respostas.",
    ])
    require_terms("templates/topic-assessment-issue-form.yml", [
        "assessment:submitted",
        "open-study-path:assessment topic_id=TOPIC-000",
        "Avalie minhas respostas",
    ])
    require_terms("templates/chatgpt-project-instructions.md", [
        "content_generation",
        "planned topics",
        "Do not require an issue number by default",
        "instructions/57-materialize-next-content.md",
    ])
    require_terms("AGENTS.md", [
        "adaptive content generation",
        "Deterministic assessment resolution",
        "Automatic next-content materialization",
        "Never select an arbitrary newest issue",
    ])

    for path in [
        "instructions/40-publish-tasks.md",
        "instructions/42-integration-preflight.md",
        "instructions/phase-completion.md",
        "templates/chatgpt-project-instructions.md",
        "AGENTS.md",
    ]:
        if DEPRECATED_PUBLICATION_SUFFIX in load_text(path):
            fail(f"{path} still requires owner to restate curriculum immutability")

    print("Guided rolling generation, publication, deterministic evaluation and materialization contracts passed.")


if __name__ == "__main__":
    main()
