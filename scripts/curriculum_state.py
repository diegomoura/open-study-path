#!/usr/bin/env python3
"""Validate curriculum proposal and generation state boundaries."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

PLACEHOLDER_TERMS = (
    "Replace the example below",
    "First capability",
    "TOPIC-000",
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_repository(root: Path) -> tuple[str, ...]:
    errors: list[str] = []
    manifest_path = root / "instructions" / "manifest.yml"
    proposal_instruction = root / "instructions" / "28-propose-path.md"

    if not manifest_path.is_file():
        return ("missing instructions/manifest.yml",)
    manifest = _mapping(load_yaml(manifest_path))
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict) and phase.get("id")
    }
    propose = _mapping(phases.get("propose"))
    generate = _mapping(phases.get("generate"))
    diagnostic = _mapping(phases.get("diagnostic"))

    if diagnostic.get("next_phase") != "propose":
        errors.append("diagnostic must route to propose")
    if propose.get("instruction") != "instructions/28-propose-path.md":
        errors.append("propose phase must reference instructions/28-propose-path.md")
    if propose.get("review_profile") != "curriculum":
        errors.append("propose phase must use the curriculum review profile")
    if propose.get("merge_policy_path") != "workflow.curriculum_merge_policy":
        errors.append("propose phase must use workflow.curriculum_merge_policy")
    if propose.get("next_phase") != "generate":
        errors.append("propose phase must route to generate")
    if generate.get("depends_on") != ["propose"]:
        errors.append("generate phase must depend on propose")

    if not proposal_instruction.is_file():
        errors.append("missing instructions/28-propose-path.md")
    else:
        text = proposal_instruction.read_text(encoding="utf-8")
        for term in [
            "Abra um pull request",
            "does not create an implicit learner-approval gate",
            "Não publique tarefas ainda",
            "curriculum_approved: true",
            "agent_review_then_merge",
            "Crie minha trilha de estudos.",
        ]:
            if term not in text:
                errors.append(f"proposal instruction is missing contract term: {term}")

    instance_path = root / ".open-study-path" / "instance.yml"
    if not instance_path.is_file():
        return tuple(errors)

    instance = _mapping(load_yaml(instance_path))
    status = _mapping(instance.get("status"))
    proposed = status.get("curriculum_proposed") is True
    approved = status.get("curriculum_approved") is True
    generated = status.get("curriculum_generated") is True

    if proposed != approved:
        errors.append(
            "curriculum proposal state must be atomic: curriculum_proposed and "
            "curriculum_approved must become true together after review"
        )
    if generated and not (proposed and approved):
        errors.append("curriculum_generated requires an approved proposal")

    roadmap = root / "study" / "roadmap.md"
    if proposed:
        if not roadmap.is_file():
            errors.append("approved curriculum proposal requires study/roadmap.md")
        else:
            body = roadmap.read_text(encoding="utf-8")
            if any(term in body for term in PLACEHOLDER_TERMS):
                errors.append("approved curriculum proposal contains roadmap placeholder content")
            if "TOPIC-001" not in body:
                errors.append("approved curriculum proposal must contain the real topic graph")

    topic_paths = sorted((root / "study" / "topics").glob("TOPIC-*.md"))
    if topic_paths and not generated:
        errors.append(
            "topic contracts exist while curriculum_generated is false; complete the "
            "generation operation and set the final state atomically"
        )
    if generated:
        if not topic_paths:
            errors.append("curriculum_generated requires topic contracts")
        if not (root / "study" / "integrations.md").is_file():
            errors.append("curriculum_generated requires study/integrations.md")

    return tuple(errors)
