#!/usr/bin/env python3
"""Validate guided lifecycle, visual learning and capability integrations."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTANCE_MARKER = ROOT / ".open-study-path/instance.yml"
ALLOWED_CURRICULUM_POLICIES = {"manual", "agent_review_then_merge"}
ALLOWED_CONTENT_STRATEGIES = {"adaptive_rolling_window", "full_upfront"}
DEPRECATED_PUBLICATION_SUFFIX = "Não altere o conteúdo pedagógico aprovado"
MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
ALLOWED_MERMAID_TYPES = (
    "flowchart", "graph", "mindmap", "timeline", "statediagram-v2",
    "sequencediagram", "classdiagram", "erdiagram", "gantt", "journey", "pie",
)


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


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"missing YAML frontmatter: {path.relative_to(ROOT)}")
    try:
        _, raw, body = text.split("---", 2)
    except ValueError:
        fail(f"malformed YAML frontmatter: {path.relative_to(ROOT)}")
    metadata = yaml.safe_load(raw)
    if not isinstance(metadata, dict):
        fail(f"frontmatter must be an object: {path.relative_to(ROOT)}")
    return metadata, body


def mermaid_blocks(text: str) -> list[str]:
    return [block.strip() for block in MERMAID_BLOCK.findall(text) if block.strip()]


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

    visual = generation.get("visual_learning")
    if not isinstance(visual, dict):
        fail(f"{path} must define content_generation.visual_learning")
    if visual.get("mermaid_enabled") is not True:
        fail(f"{path} must enable Mermaid visual learning")
    if visual.get("roadmap_dependency_diagram_required") is not True:
        fail(f"{path} must require a Mermaid roadmap dependency diagram")
    minimum = visual.get("minimum_diagrams_per_materialized_module")
    if not isinstance(minimum, int) or minimum < 1:
        fail(f"{path} must require at least one Mermaid diagram per materialized module")
    if visual.get("diagrams_must_be_explained") is not True:
        fail(f"{path} must require explanatory prose around diagrams")
    if defaults and visual.get("prefer_multiple_diagrams_for_complex_topics") is not True:
        fail("new instances must prefer multiple focused diagrams for complex topics")


def validate_capability_config(document: dict[str, Any], path: str) -> None:
    preferences = document.get("integration_preferences")
    if not isinstance(preferences, dict):
        fail(f"{path} must define integration_preferences")
    if preferences.get("experience") not in {"minimal", "guided_recommendations", "enriched"}:
        fail(f"{path} has invalid integration experience")
    if preferences.get("account_connections") not in {
        "ask_per_provider", "connected_services_only", "no_external_accounts"
    }:
        fail(f"{path} has invalid account connection policy")
    if not isinstance(preferences.get("free_tier_only"), bool):
        fail(f"{path} must define free_tier_only")
    for key in ["already_uses", "willing_to_connect", "avoid"]:
        if not isinstance(preferences.get(key), list):
            fail(f"{path} integration_preferences.{key} must be an array")

    integrations = document.get("integrations")
    if not isinstance(integrations, dict):
        fail(f"{path} must define integrations")
    required = {
        "source_of_truth", "research", "formative_practice", "task_manager",
        "reminders", "calendar", "habit_tracking", "visual_workspace",
        "artifact_workspace", "analytics_projection", "course_discovery", "notifications",
    }
    if set(integrations) != required:
        fail(f"{path} integration capability set changed: {sorted(set(integrations) ^ required)}")

    truth = integrations["source_of_truth"]
    if truth.get("provider") != "github" or truth.get("required") is not True:
        fail("GitHub must remain the required source of truth")
    authority = set(truth.get("authority", []))
    if not {"curriculum", "content", "assessment", "mastery", "progress"}.issubset(authority):
        fail("GitHub source-of-truth authority is incomplete")

    if integrations["task_manager"].get("single_authoritative_backend") is not True:
        fail("task management must have one authoritative backend")
    if integrations["formative_practice"].get("affects_mastery") is not False:
        fail("formative practice must not affect mastery")
    if integrations["reminders"].get("affects_task_state") is not False:
        fail("auxiliary reminders must not affect authoritative task state")
    habits = integrations["habit_tracking"]
    if habits.get("affects_mastery") is not False:
        fail("habit tracking must not affect mastery")
    if not isinstance(habits.get("max_default_habits"), int) or not 1 <= habits["max_default_habits"] <= 3:
        fail("habit tracking must default to at most three habits")
    if integrations["visual_workspace"].get("canonical") != "mermaid":
        fail("Mermaid must remain the canonical visual provider")
    analytics = integrations["analytics_projection"]
    if analytics.get("direction") != "github_to_airtable" or analytics.get("affects_mastery") is not False:
        fail("Airtable must remain a non-authoritative GitHub projection")
    discovery = integrations["course_discovery"]
    if discovery.get("resource_only") is not True:
        fail("course discovery providers must remain resource-only")
    if discovery.get("require_free_alternative_for_paid_resources") is not True:
        fail("potentially paid course resources require a free alternative")


def validate_generated_artifacts(document: dict[str, Any]) -> None:
    topics_dir = ROOT / "study/topics"
    topic_paths = sorted(topics_dir.glob("*.md")) if topics_dir.is_dir() else []
    if not topic_paths:
        return

    integration_plan = ROOT / "study/integrations.md"
    if not integration_plan.is_file():
        fail("generated curriculum must contain study/integrations.md")
    integration_text = integration_plan.read_text(encoding="utf-8")
    for term in [
        "GitHub", "fonte de verdade", "Fallback", "Airtable", "github_to_airtable",
        "Todoist", "Mermaid", "domínio",
    ]:
        if term not in integration_text:
            fail(f"generated integration plan is missing: {term}")

    visual = document["content_generation"]["visual_learning"]
    minimum = visual["minimum_diagrams_per_materialized_module"]
    topic_ids: list[str] = []
    topics: list[tuple[dict[str, Any], Path]] = []
    for path in topic_paths:
        metadata, _ = parse_frontmatter(path)
        topic_id = metadata.get("id")
        if not isinstance(topic_id, str) or not topic_id:
            fail(f"topic is missing an id: {path.relative_to(ROOT)}")
        topic_ids.append(topic_id)
        topics.append((metadata, path))

    roadmap = ROOT / "study/roadmap.md"
    if not roadmap.is_file():
        fail("generated topics require study/roadmap.md")
    roadmap_blocks = mermaid_blocks(roadmap.read_text(encoding="utf-8"))
    if not roadmap_blocks:
        fail("generated roadmap must contain a Mermaid dependency diagram")
    if not any(all(topic_id in block for topic_id in topic_ids) for block in roadmap_blocks):
        fail("one roadmap Mermaid block must contain every generated topic id")

    for metadata, topic_path in topics:
        if metadata.get("content_status") != "materialized":
            continue
        topic_id = metadata["id"]
        module_value = metadata.get("module")
        if not isinstance(module_value, str) or not module_value:
            fail(f"materialized topic {topic_id} must define its module path")
        module_path = ROOT / module_value
        if not module_path.is_file():
            fail(f"materialized topic {topic_id} is missing module: {module_value}")
        module_metadata, module_body = parse_frontmatter(module_path)
        declared = module_metadata.get("visual_diagrams")
        if not isinstance(declared, int) or declared < minimum:
            fail(f"module {topic_id} must declare at least {minimum} visual_diagrams")
        blocks = mermaid_blocks(module_body)
        if len(blocks) < minimum or len(blocks) < declared:
            fail(f"module {topic_id} has fewer Mermaid blocks than declared or configured")
        if "## Mapa visual" not in module_body:
            fail(f"module {topic_id} is missing the Mapa visual section")
        if "## Prática formativa e revisão" not in module_body:
            fail(f"module {topic_id} is missing the formative-practice section")
        for block in blocks:
            first_line = next((line.strip().lower() for line in block.splitlines() if line.strip()), "")
            if not first_line.startswith(ALLOWED_MERMAID_TYPES):
                fail(f"module {topic_id} uses an unsupported Mermaid diagram type: {first_line}")
        visual_section = re.search(
            r"^## Mapa visual\s*$\n(.*?)(?=^##\s|\Z)",
            module_body,
            re.MULTILINE | re.DOTALL,
        )
        if not visual_section:
            fail(f"module {topic_id} is missing visual explanation")
        prose = MERMAID_BLOCK.sub(" ", visual_section.group(1))
        if len(re.findall(r"\b\w+\b", prose, flags=re.UNICODE)) < 30:
            fail(f"module {topic_id} must explain its Mermaid diagram with meaningful prose")

        flashcards = module_metadata.get("flashcards")
        if flashcards is not None:
            if not isinstance(flashcards, str) or not flashcards.startswith("study/flashcards/"):
                fail(f"module {topic_id} has invalid flashcards path")
            flashcard_path = ROOT / flashcards
            if not flashcard_path.is_file():
                fail(f"module {topic_id} references missing flashcards: {flashcards}")
            lines = flashcard_path.read_text(encoding="utf-8").splitlines()
            if not lines or lines[0] != "Front\tBack\tTags":
                fail(f"flashcards for {topic_id} must use Front/Back/Tags TSV headers")
            if len(lines) < 5:
                fail(f"flashcards for {topic_id} need at least four useful cards")


def main() -> None:
    manifest = load_yaml("instructions/manifest.yml")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict) and phase.get("id")
    }
    if "review_curriculum" in phases or "materialize_content" in phases:
        fail("review and materialization must remain internal")

    bootstrap = phases.get("bootstrap_instance", {})
    if "state/integrations.json" not in bootstrap.get("outputs", []):
        fail("bootstrap must create integration state")

    generate = phases.get("generate", {})
    expected_generate_outputs = [
        ".open-study-path/instance.yml",
        "study.config.yml",
        "study/roadmap.md",
        "study/integrations.md",
        "study/topics/",
        "study/modules/",
        "study/flashcards/",
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
    if set(publish.get("outputs", [])) != {"study.config.yml", "state/integrations.json"}:
        fail("publish must persist provider resolution and idempotency state")

    evaluate = phases.get("evaluate", {})
    if evaluate.get("instruction") != "instructions/55-evaluate-topic.md":
        fail("evaluate must reference topic evaluation")
    if evaluate.get("internal_materialization") != "instructions/57-materialize-next-content.md":
        fail("evaluate must run rolling materialization internally")
    required_evaluate_outputs = {
        "state/assessments/", "state/progress.json", "state/integrations.json",
        "study/roadmap.md", "study/integrations.md", "study/topics/", "study/modules/",
        "study/flashcards/", "study/assessments/",
        ".github/ISSUE_TEMPLATE/assessment-topic-*.yml",
    }
    if set(evaluate.get("outputs", [])) != required_evaluate_outputs:
        fail("evaluate outputs must include progress, integrations and rolling content artifacts")

    template_document = load_yaml("templates/instance.yml")
    validate_instance_contract(template_document, "templates/instance.yml", defaults=True)
    active_document = template_document
    if INSTANCE_MARKER.is_file():
        active_document = load_yaml(".open-study-path/instance.yml")
        validate_instance_contract(active_document, ".open-study-path/instance.yml", defaults=False)

    validate_capability_config(load_yaml("study.config.example.yml"), "study.config.example.yml")
    validate_generated_artifacts(active_document)

    require_terms("instructions/30-generate-path.md", [
        "Contextual integration recommendation", "Consensus", "Quizlet", "Reclaim",
        "Habitify", "Whimsical", "github_to_airtable", "Durable flashcard fallback",
        "Finalizei o TOPIC-000. Avalie minhas respostas.",
    ])
    require_terms("instructions/35-review-curriculum.md", [
        "study/integrations.md", "exactly one task backend", "Airtable",
        "github_to_airtable", "optional providers", "Revisão do PR: aprovada pelo agente e pelo CI",
    ])
    require_terms("instructions/40-publish-tasks.md", [
        "Authority model", "Authoritative task backend", "Auxiliary Todoist reminders",
        "Formative practice", "Airtable analytical projection", "state/integrations.json",
    ])
    require_terms("instructions/42-integration-preflight.md", [
        "required_for_selected_publication", "optional_probe", "Optional-provider fallback",
        "Free-tier policy", "Conectei <providers> ao ChatGPT",
    ])
    require_terms("instructions/55-evaluate-topic.md", [
        "GitHub is the only authority", "Todoist reminders", "Habitify streaks",
        "github_to_airtable", "Never choose an arbitrary newest repository issue",
    ])
    require_terms("instructions/57-materialize-next-content.md", [
        "Optional research during materialization", "durable TSV flashcard file",
        "Auxiliary Todoist reminders", "Airtable projection", "Do not ask the owner",
    ])
    require_terms("templates/module.md", [
        "flashcards: null", "## Mapa visual", "## Prática formativa e revisão",
        "study/flashcards/TOPIC-000.tsv", "Pontuação, sequência ou conclusão",
    ])
    require_terms("templates/integrations-plan.md", [
        "Cartões explicativos", "Apenas um backend de tarefas", "github_to_airtable",
        "Acesso e custo", "Preflight", "Idempotência",
    ])
    require_terms("templates/integrations-state.json", [
        '"source_of_truth"', '"selected_capabilities"', '"resources"', '"sync"',
    ])
    require_terms("docs/integration-capabilities.md", [
        "Capability-based integrations", "Quizlet", "Consensus", "Reclaim",
        "Habitify", "Whimsical", "Airtable", "Explanation card contract",
    ])
    require_terms("templates/chatgpt-project-instructions.md", [
        "capability-based", "GitHub remains the only source of truth", "Quizlet",
        "Consensus", "Reclaim", "Airtable", "instructions/57-materialize-next-content.md",
    ])
    require_terms("AGENTS.md", [
        "Capability-based integrations", "single authoritative task backend",
        "GitHub remains the only source of truth", "github_to_airtable",
    ])
    require_terms("README.md", [
        "## Capability-based integrations", "study/integrations.md",
        "state/integrations.json", "docs/integration-capabilities.md",
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

    print(
        "Guided rolling generation, Mermaid visual learning, capability integrations, "
        "deterministic evaluation and materialization contracts passed."
    )


if __name__ == "__main__":
    main()
