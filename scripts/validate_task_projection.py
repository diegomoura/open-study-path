#!/usr/bin/env python3
"""Validate the progressive task-backend projection contract.

The validator is intentionally dependency-free so template and instance CI can run it
before optional rendering dependencies are installed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_STATES = {
    "planned",
    "ready",
    "in_progress",
    "in_assessment",
    "review_required",
    "completed",
}
SUPPORTED_PROVIDERS = {
    "trello",
    "todoist",
    "github_issues",
    "clickup",
    "notion",
    "markdown",
}
OPERATION_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,127}$")
TOPIC_ID = re.compile(r"^TOPIC-[0-9]{3,}$")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {display_path(path)}")
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON in {display_path(path)}: {exc.msg} at line {exc.lineno}"
        ) from exc


def validate_contract() -> list[str]:
    errors: list[str] = []
    instruction = ROOT / "instructions/41-task-backend-projection.md"
    manifest = ROOT / "instructions/manifest.yml"
    schema = ROOT / "schemas/publication-operation.schema.json"

    for path in (instruction, manifest, schema):
        if not path.exists():
            errors.append(f"missing contract artifact: {display_path(path)}")

    if instruction.exists():
        text = instruction.read_text(encoding="utf-8")
        for state in CANONICAL_STATES:
            if f"`{state}`" not in text:
                errors.append(f"projection contract does not declare canonical state {state}")
        for provider in ("trello", "todoist", "github_issues"):
            if f"`{provider}`" not in text:
                errors.append(f"projection contract does not declare provider {provider}")
        if "content_generation.lookahead_topics" not in text:
            errors.append("projection contract must use content_generation.lookahead_topics")
        if "📌 Leia antes de começar" not in text:
            errors.append("projection contract must define the orientation resource")

    if manifest.exists():
        text = manifest.read_text(encoding="utf-8")
        reference = "internal_task_projection: instructions/41-task-backend-projection.md"
        if text.count(reference) < 2:
            errors.append("publication and evaluation must reference task projection contract")
        if "state/operations/" not in text:
            errors.append("manifest must declare state/operations outputs")

    if schema.exists():
        try:
            data = load_json(schema)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            required = set(data.get("required", []))
            expected = {
                "operation_id",
                "operation_type",
                "provider",
                "mode",
                "status",
                "topics",
                "attempt",
                "external_read_count",
                "external_write_count",
                "started_at",
                "updated_at",
            }
            missing = expected - required
            if missing:
                errors.append(f"operation schema missing required fields: {sorted(missing)}")

    return errors


def validate_operation(path: Path) -> list[str]:
    errors: list[str] = []
    label = display_path(path)
    try:
        data = load_json(path)
    except ValueError as exc:
        return [str(exc)]

    if not isinstance(data, dict):
        return [f"{label} must contain one JSON object"]

    operation_id = data.get("operation_id")
    if not isinstance(operation_id, str) or not OPERATION_ID.fullmatch(operation_id):
        errors.append(f"{label} has invalid operation_id")

    provider = data.get("provider")
    if provider not in SUPPORTED_PROVIDERS:
        errors.append(f"{label} has unsupported provider {provider!r}")

    if data.get("mode") not in {"active_window", "full_curriculum"}:
        errors.append(f"{label} has invalid mode")

    if data.get("status") not in {
        "not_started",
        "in_progress",
        "partial",
        "blocked",
        "failed",
        "success",
    }:
        errors.append(f"{label} has invalid status")

    topics = data.get("topics")
    if not isinstance(topics, list) or any(
        not isinstance(topic, str) or not TOPIC_ID.fullmatch(topic) for topic in topics
    ):
        errors.append(f"{label} has invalid topics")
    elif len(topics) != len(set(topics)):
        errors.append(f"{label} contains duplicate topics")

    for field in ("attempt", "external_read_count", "external_write_count"):
        value = data.get(field)
        minimum = 1 if field == "attempt" else 0
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            errors.append(f"{label} has invalid {field}")

    if data.get("status") == "success" and not data.get("completed_at"):
        errors.append(f"{label} success operation requires completed_at")

    return errors


def main() -> int:
    errors = validate_contract()
    operations_dir = ROOT / "state/operations"
    if operations_dir.exists():
        for path in sorted(operations_dir.glob("*.json")):
            errors.extend(validate_operation(path))

    if errors:
        for error in errors:
            fail(error)
        return 1

    print("Task projection contract is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
