#!/usr/bin/env python3
"""Validate reusable review contracts and instance PR review coverage."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any

import yaml

from review_framework import REVIEW_PROFILES, validate_current_pr

ROOT = Path(__file__).resolve().parents[1]
REVIEW_INSTRUCTION = "instructions/04-review-generated-artifacts.md"
REVIEW_DOC = "docs/review-framework.md"
REVIEW_TEMPLATE = "templates/review.yml"

LIFECYCLE_PHASE_PROFILES = {
    "bootstrap_instance": "setup",
    "configure_intake": "setup",
    "intake": "intake",
    "diagnostic": "diagnostic",
    "generate": "curriculum",
    "publish": "publication",
    "evaluate": "assessment",
    "track": "progress",
    "replan": "replan",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"missing review-framework file: {path}")
    return target.read_text(encoding="utf-8")


def load_yaml(path: str) -> Any:
    return yaml.safe_load(read(path))


def validate_reusable_contract() -> None:
    for path in [REVIEW_INSTRUCTION, REVIEW_DOC, REVIEW_TEMPLATE]:
        read(path)

    instance_template = load_yaml("templates/instance.yml")
    if not isinstance(instance_template, dict):
        fail("templates/instance.yml must be an object")
    framework = instance_template.get("review_framework")
    if not isinstance(framework, dict):
        fail("new instances must define review_framework")
    if framework.get("contract_version") != 1:
        fail("review_framework.contract_version must be 1")
    if framework.get("enabled") is not True:
        fail("new instances must enable the review framework")
    if framework.get("independent_pass") is not True:
        fail("new instances must require an independent review pass")
    if framework.get("require_generated_diff_coverage") is not True:
        fail("new instances must require generated diff coverage")
    required_profiles = framework.get("required_profiles")
    if not isinstance(required_profiles, list) or set(required_profiles) != set(REVIEW_PROFILES):
        fail("review_framework.required_profiles must list every supported profile")

    manifest = load_yaml("instructions/manifest.yml")
    phases = {phase.get("id"): phase for phase in manifest.get("phases", []) if isinstance(phase, dict)}
    for phase_id, profile in LIFECYCLE_PHASE_PROFILES.items():
        phase = phases.get(phase_id)
        if not phase:
            fail(f"lifecycle manifest is missing phase: {phase_id}")
        if phase.get("phase_review") != REVIEW_INSTRUCTION:
            fail(f"{phase_id} must reference the shared phase review instruction")
        if phase.get("review_profile") != profile:
            fail(f"{phase_id} must use review_profile: {profile}")
        if phase.get("review_outputs") != ["state/reviews/"]:
            fail(f"{phase_id} must declare state/reviews/ as dedicated review output")
        outputs = phase.get("outputs", [])
        if "state/reviews/" in outputs:
            fail(f"{phase_id} must keep review evidence separate from phase outputs")

    review_template = load_yaml(REVIEW_TEMPLATE)
    if not isinstance(review_template, dict):
        fail("templates/review.yml must be an object")
    for key in [
        "contract_version",
        "operation_id",
        "phase",
        "reviewer_role",
        "independent_pass",
        "status",
        "reviewed_at",
        "artifacts",
        "checks",
        "blocking_findings",
        "non_blocking_findings",
    ]:
        if key not in review_template:
            fail(f"templates/review.yml is missing key: {key}")

    workflow = read(".github/workflows/validate-template.yml")
    for term in [
        "fetch-depth: 0",
        "REVIEW_BASE_SHA:",
        "python scripts/test_review_framework.py",
        "python scripts/validate_review_framework.py",
    ]:
        if term not in workflow:
            fail(f"validation workflow is missing review-framework term: {term}")

    agents = read("AGENTS.md")
    for term in [
        REVIEW_DOC,
        REVIEW_INSTRUCTION,
        "Every generated artifact changed by an instance operation",
        "state/reviews/",
    ]:
        if term not in agents:
            fail(f"AGENTS.md is missing review-framework term: {term}")

    completion = read("instructions/phase-completion.md")
    for term in [REVIEW_INSTRUCTION, "approved review artifact", "generated diff coverage"]:
        if term not in completion:
            fail(f"phase completion is missing review-framework term: {term}")


def validate_instance_diff() -> None:
    marker = ROOT / ".open-study-path/instance.yml"
    if not marker.is_file():
        return

    document = yaml.safe_load(marker.read_text(encoding="utf-8"))
    framework = document.get("review_framework", {}) if isinstance(document, dict) else {}
    if not isinstance(framework, dict) or framework.get("enabled") is not True:
        return

    result = validate_current_pr(ROOT, os.getenv("REVIEW_BASE_SHA") or None)
    if result.errors:
        for error in result.errors:
            print(f"REVIEW ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)


def main() -> None:
    validate_reusable_contract()
    validate_instance_diff()
    print("Independent generated-artifact review framework passed.")


if __name__ == "__main__":
    main()
