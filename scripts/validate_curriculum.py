#!/usr/bin/env python3
"""Validate curriculum lifecycle contracts and generated topic files."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTANCE_MARKER = ROOT / ".open-study-path/instance.yml"
TOPICS_DIR = ROOT / "study/topics"
ROADMAP = ROOT / "study/roadmap.md"
ALLOWED_REVIEW_POLICIES = {"manual", "agent_review_then_merge"}
REQUIRED_HEADINGS = [
    "## Objective",
    "## Why this matters",
    "## Prerequisites",
    "## Learning activities",
    "## Deliverable",
    "## Evidence",
    "## Mastery criteria",
    "## Resources",
    "## Prompt to start a study chat",
]
VAGUE_REQUIRED_RESOURCE = re.compile(
    r"(?:a selecionar|passagem curta|uma introdução|trecho e tradução a revisar|"
    r"edição ou tradução a revisar|com edição a revisar)",
    re.IGNORECASE,
)
CANONICAL_LOCATOR = re.compile(r"(?:§|\b\d+\b|\b[IVXLCDM]+\.)")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def parse_topic(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"topic is missing YAML frontmatter: {path.relative_to(ROOT)}")
    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        fail(f"topic frontmatter is malformed: {path.relative_to(ROOT)}")
    document = yaml.safe_load(frontmatter)
    if not isinstance(document, dict):
        fail(f"topic frontmatter must be an object: {path.relative_to(ROOT)}")
    return document, body


def required_resource_lines(body: str, path: Path) -> list[str]:
    match = re.search(
        r"### Required\s*(.*?)(?:\n### Optional|\n## Prompt to start a study chat|\Z)",
        body,
        re.DOTALL,
    )
    if not match:
        fail(f"topic is missing a Required resources subsection: {path.relative_to(ROOT)}")
    lines = [line.strip()[2:].strip() for line in match.group(1).splitlines() if line.strip().startswith("- ")]
    if not lines:
        fail(f"topic must contain at least one required resource: {path.relative_to(ROOT)}")
    return lines


def check_lifecycle_contract() -> None:
    manifest = load_yaml(ROOT / "instructions/manifest.yml")
    phases = {phase.get("id"): phase for phase in manifest.get("phases", []) if isinstance(phase, dict)}
    generate = phases.get("generate", {})
    review = phases.get("review_curriculum", {})
    if generate.get("next_phase") != "review_curriculum":
        fail("generation must route to review_curriculum")
    if review.get("instruction") != "instructions/35-review-curriculum.md":
        fail("review_curriculum must reference instructions/35-review-curriculum.md")
    if review.get("next_phase") != "publish":
        fail("review_curriculum must route to publish")
    if review.get("merge_policy_path") != "workflow.curriculum_review_policy":
        fail("review_curriculum must reference workflow.curriculum_review_policy")

    template = load_yaml(ROOT / "templates/instance.yml")
    policy = template.get("workflow", {}).get("curriculum_review_policy")
    if policy != "agent_review_then_merge":
        fail("new instances must default curriculum review to agent_review_then_merge")

    for required in [
        ROOT / "instructions/30-generate-path.md",
        ROOT / "instructions/35-review-curriculum.md",
    ]:
        if not required.is_file():
            fail(f"missing curriculum instruction: {required.relative_to(ROOT)}")

    if INSTANCE_MARKER.is_file():
        marker = load_yaml(INSTANCE_MARKER)
        instance_policy = marker.get("workflow", {}).get("curriculum_review_policy")
        if instance_policy not in ALLOWED_REVIEW_POLICIES:
            fail(f"invalid curriculum_review_policy: {instance_policy}")


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
        metadata, body = parse_topic(path)
        for key in ["id", "title", "status", "difficulty", "estimated_hours", "prerequisites"]:
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
        for heading in REQUIRED_HEADINGS:
            if heading not in body:
                fail(f"topic {topic_id} is missing heading: {heading}")
        for resource in required_resource_lines(body, path):
            if VAGUE_REQUIRED_RESOURCE.search(resource) and not CANONICAL_LOCATOR.search(resource):
                fail(f"required resource is vague in {topic_id}: {resource}")
            if not CANONICAL_LOCATOR.search(resource):
                fail(f"required resource needs a canonical locator in {topic_id}: {resource}")
        if topic_id not in roadmap:
            fail(f"roadmap does not reference topic {topic_id}")
        topics[topic_id] = path
        prerequisites[topic_id] = topic_prerequisites

    for topic_id, required_ids in prerequisites.items():
        for required_id in required_ids:
            if required_id not in topics:
                fail(f"topic {topic_id} references missing prerequisite {required_id}")
            if required_id == topic_id:
                fail(f"topic {topic_id} cannot depend on itself")

    detect_cycle(prerequisites)
    print(f"Curriculum contract passed for {len(topics)} topics.")


def main() -> None:
    check_lifecycle_contract()
    check_topics()
    print("Curriculum validation passed.")


if __name__ == "__main__":
    main()
