#!/usr/bin/env python3
"""Validate the reusable Open Study Path template contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

YAML_FILES = [
    ".open-study-path/template.yml",
    ".github/ISSUE_TEMPLATE/create-study-path.yml",
    "instructions/manifest.yml",
    "intake/jotform-form-spec.yml",
    "intake/field-mapping.yml",
    "study.config.example.yml",
    "templates/instance.yml",
]

FORBIDDEN_TEMPLATE_ARTIFACTS = [
    ".open-study-path/instance.yml",
    "study.config.yml",
    "state/intake-summary.json",
    "state/progress.json",
    "study/roadmap.md",
]

REQUIRED_INTAKE_KEYS = {
    "subject",
    "objective",
    "current_level",
    "preferred_language",
    "weekly_hours",
    "task_manager",
    "consent",
}


def load_yaml(path: str) -> Any:
    with (ROOT / path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    for path in YAML_FILES:
        if not (ROOT / path).is_file():
            fail(f"missing required file: {path}")
        load_yaml(path)

    for path in FORBIDDEN_TEMPLATE_ARTIFACTS:
        if (ROOT / path).exists():
            fail(f"instance artifact must not exist in canonical template: {path}")

    marker = load_yaml(".open-study-path/template.yml")
    if marker.get("generation_allowed") is not False:
        fail("template marker must set generation_allowed: false")

    spec = load_yaml("intake/jotform-form-spec.yml")
    mapping = load_yaml("intake/field-mapping.yml")
    example = load_yaml("study.config.example.yml")
    issue_form = load_yaml(".github/ISSUE_TEMPLATE/create-study-path.yml")

    fields = spec.get("fields", [])
    field_keys = [field.get("key") for field in fields]
    if len(field_keys) != len(set(field_keys)):
        fail("jotform specification contains duplicate field keys")

    missing_required = REQUIRED_INTAKE_KEYS.difference(field_keys)
    if missing_required:
        fail(f"jotform specification is missing required keys: {sorted(missing_required)}")

    if spec.get("privacy", {}).get("attachments_optional") is not True:
        fail("jotform specification must keep attachments optional")
    if spec.get("privacy", {}).get("persist_raw_submission") is not False:
        fail("jotform specification must prohibit raw-submission persistence")

    if mapping.get("spec_id") != spec.get("id"):
        fail("field mapping spec_id does not match jotform specification id")

    intake = example.get("intake", {})
    if intake.get("form_spec_id") != spec.get("id"):
        fail("configuration example form_spec_id does not match specification")
    if intake.get("form_spec_version") != spec.get("version"):
        fail("configuration example form_spec_version does not match specification")
    if intake.get("attachments_optional") is not True:
        fail("configuration example must keep attachments optional")
    if intake.get("persist_raw_submission") is not False:
        fail("configuration example must prohibit raw-submission persistence")

    issue_ids = {
        block.get("id")
        for block in issue_form.get("body", [])
        if isinstance(block, dict) and block.get("id")
    }
    missing_issue_fields = REQUIRED_INTAKE_KEYS.difference(issue_ids)
    if missing_issue_fields:
        fail(f"GitHub Issue Form is missing required fields: {sorted(missing_issue_fields)}")

    with (ROOT / "schemas/study-config.schema.json").open("r", encoding="utf-8") as handle:
        schema = json.load(handle)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))
    if errors:
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f"SCHEMA ERROR at {location}: {error.message}", file=sys.stderr)
        raise SystemExit(1)

    print("Open Study Path template validation passed.")


if __name__ == "__main__":
    main()
