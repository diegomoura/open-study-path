#!/usr/bin/env python3
"""Validate an Open Study Path repository in template or instance mode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INSTANCE_MARKER = ".open-study-path/instance.yml"
COMPLETION_CONTRACT = "instructions/phase-completion.md"
DIAGNOSTIC_TEMPLATE = "templates/state/diagnostic-summary.json"
DIAGNOSTIC_SCHEMA = "schemas/diagnostic-summary.schema.json"
DIAGNOSTIC_STATE = "state/diagnostic-summary.json"
MERGE_POLICIES = {"manual", "auto_after_ci", "auto_when_unambiguous"}
DIAGNOSTIC_EXCEPTIONS = {None, "owner_requested_comprehensive", "legacy_before_policy"}

REUSABLE_YAML_FILES = [
    ".open-study-path/template.yml",
    ".github/ISSUE_TEMPLATE/create-study-path.yml",
    "instructions/manifest.yml",
    "intake/jotform-form-spec.yml",
    "intake/field-mapping.yml",
    "study.config.example.yml",
    "templates/instance.yml",
]

REQUIRED_REUSABLE_FILES = [
    "README.md",
    "AGENTS.md",
    "docs/chatgpt-project-setup.md",
    "templates/chatgpt-project-instructions.md",
    "instructions/00-bootstrap.md",
    "instructions/05-configure-intake.md",
    "instructions/10-intake.md",
    "instructions/20-diagnostic.md",
    COMPLETION_CONTRACT,
    DIAGNOSTIC_TEMPLATE,
    DIAGNOSTIC_SCHEMA,
]

INSTANCE_ARTIFACTS = [
    INSTANCE_MARKER,
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


def load_json(path: str) -> Any:
    with (ROOT / path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def is_instance() -> bool:
    return (ROOT / INSTANCE_MARKER).is_file()


def check_yaml() -> None:
    paths = list(REUSABLE_YAML_FILES)
    if is_instance():
        paths.extend([INSTANCE_MARKER, "study.config.yml"])

    for path in paths:
        if not (ROOT / path).is_file():
            fail(f"missing required YAML file: {path}")
        load_yaml(path)

    print("YAML parsing passed.")


def validate_workflow_policy(document: dict[str, Any], *, required: bool) -> None:
    workflow = document.get("workflow")
    if workflow is None:
        if required:
            fail("instance marker template must define workflow defaults")
        return
    if not isinstance(workflow, dict):
        fail("instance marker workflow must be an object")
    if workflow.get("guided") is not True:
        fail("instance workflow must set guided: true")

    for key in ["intake_merge_policy", "diagnostic_merge_policy"]:
        policy = workflow.get(key)
        if policy not in MERGE_POLICIES:
            fail(f"invalid {key}: {policy}")


def validate_diagnostic_budget(document: dict[str, Any], path: str) -> None:
    budget = document.get("question_budget", {})
    target_min = budget.get("target_min")
    target_max = budget.get("target_max")
    hard_max = budget.get("hard_max")
    exception = budget.get("exception")
    count = document.get("question_count")

    if not all(isinstance(value, int) for value in [target_min, target_max, hard_max, count]):
        fail(f"diagnostic budget values must be integers in {path}")
    if not (1 <= target_min <= target_max <= hard_max <= 10):
        fail(f"invalid diagnostic question budget in {path}")
    if exception not in DIAGNOSTIC_EXCEPTIONS:
        fail(f"invalid diagnostic budget exception in {path}: {exception}")
    if count > hard_max and exception is None:
        fail(f"diagnostic question count exceeds hard maximum without exception in {path}")


def validate_json_document(path: str, validator: Draft202012Validator) -> dict[str, Any]:
    document = load_json(path)
    errors = list(validator.iter_errors(document))
    if errors:
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f"SCHEMA ERROR in {path} at {location}: {error.message}", file=sys.stderr)
        raise SystemExit(1)
    return document


def check_reusable_contract(marker: dict[str, Any]) -> None:
    for path in REQUIRED_REUSABLE_FILES:
        if not (ROOT / path).is_file():
            fail(f"missing required reusable file: {path}")

    if marker.get("generation_allowed") is not False:
        fail("template marker must set generation_allowed: false")

    setup = marker.get("instance_setup", {})
    expected_assets = {
        "chatgpt_project_instructions_template": "templates/chatgpt-project-instructions.md",
        "chatgpt_project_setup_guide": "docs/chatgpt-project-setup.md",
        "instance_marker": INSTANCE_MARKER,
        "configuration_template": "study.config.example.yml",
    }
    for key, expected in expected_assets.items():
        if setup.get(key) != expected:
            fail(f"template marker {key} must reference {expected}")

    manifest = load_yaml("instructions/manifest.yml")
    if manifest.get("completion_contract") != COMPLETION_CONTRACT:
        fail(f"lifecycle manifest must reference {COMPLETION_CONTRACT}")
    phases = {
        phase.get("id"): phase
        for phase in manifest.get("phases", [])
        if isinstance(phase, dict) and phase.get("id")
    }
    if phases.get("intake", {}).get("next_phase") != "diagnostic":
        fail("intake phase must guide to diagnostic")
    diagnostic_phase = phases.get("diagnostic", {})
    if diagnostic_phase.get("next_phase") != "generate":
        fail("diagnostic phase must guide to generation")
    if diagnostic_phase.get("merge_policy_path") != "workflow.diagnostic_merge_policy":
        fail("diagnostic phase must reference its merge policy")
    if diagnostic_phase.get("outputs") != [INSTANCE_MARKER, DIAGNOSTIC_STATE]:
        fail("diagnostic phase must restrict outputs to marker and diagnostic summary")

    instance_template = load_yaml("templates/instance.yml")
    validate_workflow_policy(instance_template, required=True)
    workflow = instance_template.get("workflow", {})
    if workflow.get("intake_merge_policy") != "auto_when_unambiguous":
        fail("new instances must default intake to auto_when_unambiguous")
    if workflow.get("diagnostic_merge_policy") != "auto_when_unambiguous":
        fail("new instances must default diagnostic to auto_when_unambiguous")

    project_instructions = load_text("templates/chatgpt-project-instructions.md")
    for term in [
        "OWNER/REPOSITORY",
        INSTANCE_MARKER,
        "diegomoura/open-study-path",
        "Keep the process guided",
        "exact command to continue",
    ]:
        if term not in project_instructions:
            fail(f"ChatGPT Project Instructions template is missing required term: {term}")

    project_setup = load_text("docs/chatgpt-project-setup.md")
    if "Project Instructions" not in project_setup:
        fail("ChatGPT Project setup guide must explain Project Instructions")
    if "OWNER/REPOSITORY" not in project_setup:
        fail("ChatGPT Project setup guide must include the repository placeholder")

    intake_setup = load_text("instructions/05-configure-intake.md")
    for term in [
        "https://github.com/OWNER/REPOSITORY/issues/new?template=create-study-path.yml",
        "explicit_issue",
        "clickable link",
        "issue number",
    ]:
        if term not in intake_setup:
            fail(f"GitHub Issue Form setup instructions are missing required term: {term}")

    intake_instruction = load_text("instructions/10-intake.md")
    for term in [
        "workflow.intake_merge_policy",
        "auto_when_unambiguous",
        "Inicie o diagnóstico proporcional desta trilha",
    ]:
        if term not in intake_instruction:
            fail(f"intake instructions are missing required guided-flow term: {term}")

    diagnostic_instruction = load_text("instructions/20-diagnostic.md")
    for term in [
        "target 3 to 5 questions",
        "hard maximum of 7 questions",
        "workflow.diagnostic_merge_policy",
        DIAGNOSTIC_TEMPLATE,
        DIAGNOSTIC_SCHEMA,
        "Do not send a separate transition message",
    ]:
        if term not in diagnostic_instruction:
            fail(f"diagnostic instructions are missing required bounded-flow term: {term}")

    completion = load_text(COMPLETION_CONTRACT)
    for term in [
        "Next step",
        "Continue command",
        "Concision rule",
        "auto_when_unambiguous",
        "Do not send a separate transition message",
    ]:
        if term not in completion:
            fail(f"phase completion contract is missing required term: {term}")


def check_template_mode(marker: dict[str, Any]) -> None:
    for path in INSTANCE_ARTIFACTS:
        if (ROOT / path).exists():
            fail(f"instance artifact must not exist before instance setup: {path}")
    print("Template-mode guard passed.")


def check_instance_mode(marker: dict[str, Any]) -> None:
    for path in INSTANCE_ARTIFACTS:
        if not (ROOT / path).exists():
            fail(f"required instance artifact is missing: {path}")

    instance = load_yaml(INSTANCE_MARKER)
    canonical_repository = marker.get("canonical_repository")
    repository = instance.get("repository")
    source_template = instance.get("source_template")

    if instance.get("kind") != "open-study-path-instance":
        fail("instance marker kind must be open-study-path-instance")
    if not isinstance(repository, str) or not repository.strip():
        fail("instance marker must contain a repository identifier")
    if repository == "OWNER/REPOSITORY":
        fail("instance marker repository placeholder must be replaced")
    if repository == canonical_repository:
        fail("canonical template repository cannot be configured as an instance")
    if source_template != canonical_repository:
        fail("instance source_template must match the canonical repository")

    validate_workflow_policy(instance, required=False)
    if instance.get("status", {}).get("diagnostic_complete") is True and not (ROOT / DIAGNOSTIC_STATE).is_file():
        fail("completed diagnostic requires state/diagnostic-summary.json")
    print(f"Instance-mode guard passed for {repository}.")


def check_guard() -> None:
    marker = load_yaml(".open-study-path/template.yml")
    check_reusable_contract(marker)
    if is_instance():
        check_instance_mode(marker)
    else:
        check_template_mode(marker)


def check_intake() -> None:
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

    email_field = next((field for field in fields if field.get("key") == "email_summaries"), None)
    if not email_field or "Gmail" not in str(email_field.get("label", "")):
        fail("Jotform email summaries field must name Gmail explicitly")

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

    issue_blocks = [block for block in issue_form.get("body", []) if isinstance(block, dict)]
    issue_ids = {block.get("id") for block in issue_blocks if block.get("id")}
    missing_issue_fields = REQUIRED_INTAKE_KEYS.difference(issue_ids)
    if missing_issue_fields:
        fail(f"GitHub Issue Form is missing required fields: {sorted(missing_issue_fields)}")

    issue_email = next((block for block in issue_blocks if block.get("id") == "email_summaries"), None)
    issue_email_label = (issue_email or {}).get("attributes", {}).get("label", "")
    if "Gmail" not in str(issue_email_label):
        fail("GitHub Issue Form email summaries field must name Gmail explicitly")

    print("Intake contract passed.")


def validate_config(path: str, validator: Draft202012Validator) -> None:
    config = load_yaml(path)
    errors = list(validator.iter_errors(config))
    if errors:
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f"SCHEMA ERROR in {path} at {location}: {error.message}", file=sys.stderr)
        raise SystemExit(1)


def check_schema() -> None:
    study_validator = Draft202012Validator(load_json("schemas/study-config.schema.json"), format_checker=FormatChecker())
    validate_config("study.config.example.yml", study_validator)
    if is_instance():
        validate_config("study.config.yml", study_validator)

    diagnostic_validator = Draft202012Validator(load_json(DIAGNOSTIC_SCHEMA), format_checker=FormatChecker())
    template_document = validate_json_document(DIAGNOSTIC_TEMPLATE, diagnostic_validator)
    validate_diagnostic_budget(template_document, DIAGNOSTIC_TEMPLATE)
    if (ROOT / DIAGNOSTIC_STATE).is_file():
        state_document = validate_json_document(DIAGNOSTIC_STATE, diagnostic_validator)
        validate_diagnostic_budget(state_document, DIAGNOSTIC_STATE)

    print("Configuration and diagnostic schemas passed.")


CHECKS = {
    "yaml": check_yaml,
    "guard": check_guard,
    "intake": check_intake,
    "schema": check_schema,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("check", choices=[*CHECKS, "all"])
    args = parser.parse_args()

    selected = CHECKS.values() if args.check == "all" else [CHECKS[args.check]]
    for check in selected:
        check()

    print("Open Study Path repository validation passed.")


if __name__ == "__main__":
    main()
