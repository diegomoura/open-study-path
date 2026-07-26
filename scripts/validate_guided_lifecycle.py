#!/usr/bin/env python3
"""Validate the guided lifecycle and automatic phase contracts."""

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
        fail("review_curriculum must not be a separate user-facing phase")

    generate = phases.get("generate", {})
    if generate.get("next_phase") != "publish":
        fail("generate must guide directly to publish after internal review and merge")
    if generate.get("internal_review") != "instructions/35-review-curriculum.md":
        fail("generate must reference the internal curriculum review checklist")
    if generate.get("merge_policy_path") != "workflow.curriculum_merge_policy":
        fail("generate must reference workflow.curriculum_merge_policy")
    if generate.get("outputs") != [
        ".open-study-path/instance.yml",
        "study/roadmap.md",
        "study/topics/",
    ]:
        fail("generate outputs must remain phase-limited")

    publish = phases.get("publish", {})
    if publish.get("depends_on") != ["generate"]:
        fail("publish must depend directly on completed generation")
    if publish.get("internal_preflight") != "instructions/42-integration-preflight.md":
        fail("publish must reference the internal integration preflight")

    validate_workflow(load_yaml("templates/instance.yml"), "templates/instance.yml", default_required=True)
    if INSTANCE_MARKER.is_file():
        validate_workflow(load_yaml(".open-study-path/instance.yml"), ".open-study-path/instance.yml", default_required=False)

    require_terms(
        "instructions/30-generate-path.md",
        [
            "automatically execute the internal checklist",
            "Do not ask the owner to request a separate review",
            "workflow.curriculum_merge_policy",
            "mark the draft pull request ready",
            "merge it when no pedagogical decision remains unresolved",
            "Publique as tarefas da trilha",
        ],
    )
    require_terms(
        "instructions/35-review-curriculum.md",
        [
            "Run this checklist automatically inside the generation phase",
            "Do not ask the owner to send a separate review command",
            "agent_review_then_merge",
            "Never ask the owner to perform the entire review or merge",
        ],
    )
    require_terms(
        "instructions/40-publish-tasks.md",
        [
            "Approved curriculum invariant",
            "immutable inputs during publication",
            "must not add, remove, rewrite or reinterpret pedagogical",
            "The owner does not need to restate this invariant",
            "`Publique as tarefas da trilha nas integrações configuradas.`",
            "Before any external write",
            "instructions/42-integration-preflight.md",
            "harmless read-only probe",
            "create no board, card, issue, event, email or integration-state write",
            "continue publication immediately",
            "do not ask for another confirmation",
        ],
    )
    require_terms(
        "instructions/42-integration-preflight.md",
        [
            "A provider name in `study.config.yml`, an installed app, or an available tool definition does not prove",
            "harmless read-only operation",
            "create no external resources",
            "do not partially publish",
            "Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.",
            "Run the read-only probes again",
            "do not send an intermediate",
            "Never request API keys, tokens or passwords",
            "immutability rule",
        ],
    )
    require_terms(
        "instructions/phase-completion.md",
        [
            "Internal validation, review, correction and safe merge",
            "Generation includes draft creation, internal review, corrections, validation and safe merge",
            "Do not instruct the owner to request another review",
            "`Publique as tarefas da trilha nas integrações configuradas.`",
            "immutability rule is internal to `publish`",
            "When publication is blocked by integration access",
            "Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.",
            "Re-run the probes",
            "continue the pending publication automatically",
        ],
    )
    require_terms(
        "templates/chatgpt-project-instructions.md",
        [
            "must not require a second owner command",
            "workflow.curriculum_merge_policy",
            "Never ask the owner to request a separate curriculum review",
            "immutable approved inputs",
            "Do not require the owner to repeat this rule",
            "instructions/42-integration-preflight.md",
            "harmless read-only connector operation",
            "create no external resources and do not partially publish",
            "Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.",
            "re-run every required probe",
            "without another confirmation",
        ],
    )
    require_terms(
        "AGENTS.md",
        [
            "Automatic curriculum generation, review and merge",
            "Do not ask the owner to send a separate review command",
            "Automatically review, correct, validate and safely merge",
            "Integration preflight and task publication",
            "Connection verification is an internal prerequisite",
            "one harmless read-only operation per required connector",
            "immutable approved inputs",
            "Conectei <providers> ao ChatGPT. Verifique novamente e continue a publicação.",
            "re-run the probes rather than trusting the statement",
        ],
    )

    checked_paths = [
        "instructions/40-publish-tasks.md",
        "instructions/42-integration-preflight.md",
        "instructions/phase-completion.md",
        "templates/chatgpt-project-instructions.md",
        "AGENTS.md",
    ]
    for path in checked_paths:
        if DEPRECATED_PUBLICATION_SUFFIX in load_text(path):
            fail(f"{path} still requires the owner to restate curriculum immutability")

    for path in [
        "instructions/manifest.yml",
        "instructions/phase-completion.md",
        "templates/chatgpt-project-instructions.md",
        "AGENTS.md",
    ]:
        if "review curriculum PR #<number>" in load_text(path):
            fail(f"{path} still exposes a separate review command")

    print("Guided lifecycle, automatic curriculum review, immutable publication and integration preflight contracts passed.")


if __name__ == "__main__":
    main()
