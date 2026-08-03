#!/usr/bin/env python3
"""Validate the task-backend projection contract, journals and published state."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_STATES = {
    "planned",
    "ready",
    "ready_primary",
    "ready_parallel",
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
VISIBLE_LISTS = (
    "Planejado",
    "Disponível em paralelo",
    "Próxima aula",
    "Em estudo",
    "Em avaliação",
    "Revisão necessária",
    "Concluído",
)
VISIBLE_LIST_ORDER = " → ".join(VISIBLE_LISTS)
SUCCESS_STATUSES = {"success", "completed", "succeeded"}
PRIMARY_STATES = {
    "Próxima aula",
    "ready_primary",
    "ready-primary",
    "study:ready-primary",
}
KNOWN_LESSON_TYPES = {
    "trello": {"card"},
    "todoist": {"task"},
    "github_issues": {"issue"},
}
KNOWN_CONTAINER_TYPES = {
    "trello": {"board"},
    "todoist": {"project"},
    "github_issues": {"repository", "project"},
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


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, dict) else {}


def text(value: Any) -> str:
    return str(value or "").strip()


def validate_contract() -> list[str]:
    errors: list[str] = []
    instruction = ROOT / "instructions/41-task-backend-projection.md"
    manifest = ROOT / "instructions/manifest.yml"
    schema = ROOT / "schemas/publication-operation.schema.json"

    for path in (instruction, manifest, schema):
        if not path.exists():
            errors.append(f"missing contract artifact: {display_path(path)}")

    if instruction.exists():
        body = instruction.read_text(encoding="utf-8")
        for state in {
            "planned",
            "ready",
            "in_progress",
            "in_assessment",
            "review_required",
            "completed",
        }:
            if f"`{state}`" not in body:
                errors.append(
                    f"projection contract does not declare canonical state {state}"
                )
        for provider in ("trello", "todoist", "github_issues"):
            if f"`{provider}`" not in body:
                errors.append(
                    f"projection contract does not declare provider {provider}"
                )
        for fragment in (
            "content_generation.lookahead_topics",
            "📌 Leia antes de começar",
            VISIBLE_LIST_ORDER,
            "Learner-visible metadata boundary",
            "HTML comments such as `<!-- ... -->`",
            "the text `open-study-path` used as a machine marker",
            "state/integrations.json",
            "read every managed task back",
            "visible_internal_marker_count",
            "lesson_card_count",
            "managed_card_count",
        ):
            if fragment not in body:
                errors.append(
                    f"projection contract is missing required protection: {fragment}"
                )

    if manifest.exists():
        body = manifest.read_text(encoding="utf-8")
        reference = (
            "internal_task_projection: instructions/41-task-backend-projection.md"
        )
        if body.count(reference) < 2:
            errors.append(
                "publication and evaluation must reference task projection contract"
            )
        if "state/operations/" not in body:
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
                errors.append(
                    f"operation schema missing required fields: {sorted(missing)}"
                )
    return errors


def validate_operation(path: Path) -> list[str]:
    label = display_path(path)
    try:
        data = load_json(path)
    except ValueError as exc:
        return [str(exc)]
    if not isinstance(data, dict):
        return [f"{label} must contain one JSON object"]

    errors: list[str] = []
    operation_id = data.get("operation_id")
    if not isinstance(operation_id, str) or not OPERATION_ID.fullmatch(operation_id):
        errors.append(f"{label} has invalid operation_id")
    if data.get("provider") not in SUPPORTED_PROVIDERS:
        errors.append(f"{label} has unsupported provider {data.get('provider')!r}")
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
        not isinstance(topic, str) or not TOPIC_ID.fullmatch(topic)
        for topic in topics
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


def expected_types(provider: str, table: Mapping[str, set[str]], fallback: set[str]) -> set[str]:
    return table.get(provider, fallback)


def validate_projection_state(root: Path = ROOT) -> list[str]:
    state_path = root / "state/integrations.json"
    marker = root / ".open-study-path/instance.yml"
    if not marker.is_file() or not state_path.is_file():
        return []

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in state/integrations.json: {exc}"]
    if not isinstance(data, dict):
        return ["state/integrations.json must contain one JSON object"]

    selected = mapping(data.get("selected_capabilities"))
    task = mapping(selected.get("task_manager"))
    sync = mapping(data.get("sync"))
    task_status = text(task.get("status")).lower()
    resolution_status = text(task.get("resolution_status")).lower()
    sync_status = text(sync.get("status")).lower()
    if not task or not (
        task_status in SUCCESS_STATUSES
        or resolution_status == "resolved"
        or sync_status in SUCCESS_STATUSES
    ):
        return []

    errors: list[str] = []
    provider = text(task.get("provider")).lower()
    projection = mapping(data.get("projection"))
    resources_value = data.get("resources")
    if provider not in SUPPORTED_PROVIDERS:
        errors.append(
            f"published task_manager has unsupported provider: {provider or '<missing>'}"
        )
    if not projection:
        return errors + ["successful task publication requires projection metadata"]
    if projection.get("provider") != provider:
        errors.append("projection.provider must match selected task_manager provider")
    if not isinstance(resources_value, list):
        return errors + ["successful task publication requires a resources list"]
    resources = [item for item in resources_value if isinstance(item, dict)]

    topic_count = projection.get("topic_count")
    if not isinstance(topic_count, int) or isinstance(topic_count, bool) or topic_count < 1:
        errors.append("projection.topic_count must be a positive integer")
        topic_count = None

    container_types = expected_types(
        provider,
        KNOWN_CONTAINER_TYPES,
        {"board", "project", "repository"},
    )
    containers = [
        item
        for item in resources
        if item.get("capability") == "task_manager"
        and item.get("provider") == provider
        and item.get("type") in container_types
    ]
    if len(containers) != 1:
        errors.append(
            "published projection must register exactly one task board, project or repository"
        )
    else:
        container = containers[0]
        if not text(container.get("id")) or not text(container.get("url")):
            errors.append("published task container requires id and url")
        if projection.get("board_id") and container.get("id") != projection.get("board_id"):
            errors.append(
                "projection.board_id does not match the registered task container"
            )
        if projection.get("board_url") and container.get("url") != projection.get("board_url"):
            errors.append(
                "projection.board_url does not match the registered task container"
            )

    lessons = [
        item
        for item in resources
        if item.get("capability") == "task_manager"
        and item.get("provider") == provider
        and item.get("topic_id")
    ]
    if topic_count is not None and len(lessons) != topic_count:
        errors.append(
            f"projection.topic_count is {topic_count}, but {len(lessons)} lesson resources are registered"
        )

    lesson_types = expected_types(
        provider,
        KNOWN_LESSON_TYPES,
        {"card", "task", "issue", "page"},
    )
    topics: set[str] = set()
    resource_ids: set[str] = set()
    lesson_numbers: set[int] = set()
    primary_count = 0
    for lesson in lessons:
        topic_id = lesson.get("topic_id")
        resource_id = text(lesson.get("id"))
        lesson_number = lesson.get("visible_lesson_number")
        state = text(lesson.get("canonical_state"))
        prerequisites = lesson.get("direct_prerequisite_ids")
        content_version = lesson.get("content_version")

        if lesson.get("type") not in lesson_types:
            errors.append(
                f"registered lesson resource {topic_id} has invalid type for {provider}: {lesson.get('type')!r}"
            )
        if not isinstance(topic_id, str) or not TOPIC_ID.fullmatch(topic_id):
            errors.append(
                f"registered lesson resource has invalid topic_id: {topic_id!r}"
            )
        elif topic_id in topics:
            errors.append(f"duplicate lesson resource topic_id: {topic_id}")
        else:
            topics.add(topic_id)
        if not resource_id:
            errors.append(f"registered lesson resource {topic_id} is missing id")
        elif resource_id in resource_ids:
            errors.append(f"duplicate lesson resource id: {resource_id}")
        else:
            resource_ids.add(resource_id)
        if not isinstance(lesson_number, int) or isinstance(lesson_number, bool) or lesson_number < 1:
            errors.append(
                f"registered lesson resource {topic_id} has invalid visible_lesson_number"
            )
        elif lesson_number in lesson_numbers:
            errors.append(f"duplicate visible lesson number: {lesson_number}")
        else:
            lesson_numbers.add(lesson_number)
        if not state:
            errors.append(
                f"registered lesson resource {topic_id} is missing canonical_state"
            )
        if state in PRIMARY_STATES:
            primary_count += 1
        if not isinstance(content_version, int) or isinstance(content_version, bool) or content_version < 0:
            errors.append(
                f"registered lesson resource {topic_id} has invalid content_version"
            )
        if not isinstance(prerequisites, list) or any(
            not isinstance(item, str) or not TOPIC_ID.fullmatch(item)
            for item in prerequisites
        ):
            errors.append(
                f"registered lesson resource {topic_id} has invalid direct_prerequisite_ids"
            )
        elif len(prerequisites) != len(set(prerequisites)):
            errors.append(
                f"registered lesson resource {topic_id} has duplicate prerequisites"
            )
        if provider == "trello" and not text(lesson.get("url")):
            errors.append(f"registered Trello lesson card {topic_id} is missing url")

    if primary_count != 1:
        errors.append(
            f"published projection must contain exactly one primary next lesson, got {primary_count}"
        )

    orientations = [
        item
        for item in resources
        if item.get("capability") == "task_manager"
        and item.get("provider") == provider
        and item.get("type") == "orientation"
    ]
    if len(orientations) != 1:
        errors.append("published projection must register exactly one orientation resource")
    else:
        orientation = orientations[0]
        if not text(orientation.get("id")) or not text(orientation.get("url")):
            errors.append("registered orientation resource requires id and url")

    readback = mapping(projection.get("readback"))
    if not readback:
        errors.append("successful task projection requires readback evidence")
    else:
        if readback.get("lesson_card_count") != topic_count:
            errors.append(
                "projection.readback.lesson_card_count must match topic_count"
            )
        expected_managed = topic_count + 1 if isinstance(topic_count, int) else None
        if (
            expected_managed is not None
            and readback.get("managed_card_count") != expected_managed
        ):
            errors.append(
                "projection.readback.managed_card_count must include lessons and orientation"
            )
        if readback.get("visible_internal_marker_count") != 0:
            errors.append(
                "projection readback found learner-visible internal metadata"
            )
        if not text(readback.get("verified_at")):
            errors.append("projection.readback.verified_at is required")

    if provider == "trello":
        if projection.get("list_order") != list(VISIBLE_LISTS):
            errors.append(
                "Trello projection.list_order must match the canonical visual order"
            )
        lists = [
            item
            for item in resources
            if item.get("capability") == "task_manager"
            and item.get("provider") == "trello"
            and item.get("type") == "list"
        ]
        names = [item.get("name") for item in lists]
        if len(names) != len(VISIBLE_LISTS) or set(names) != set(VISIBLE_LISTS):
            errors.append(
                "Trello projection must register all seven managed lists exactly once"
            )
        for item in lists:
            if not text(item.get("id")):
                errors.append(
                    f"registered Trello list {item.get('name')!r} is missing id"
                )
        if orientations and orientations[0].get("canonical_state") != "Planejado":
            errors.append("orientation card must remain in Planejado")
        for lesson in lessons:
            if lesson.get("canonical_state") not in VISIBLE_LISTS:
                errors.append(
                    f"registered Trello lesson {lesson.get('topic_id')} has invalid canonical_state"
                )

    resolution = mapping(data.get("resolution"))
    if resolution.get("status") != "resolved":
        errors.append("successful projection requires resolution.status resolved")
    if sync_status not in SUCCESS_STATUSES:
        errors.append("successful projection requires sync.status success")
    if not text(sync.get("last_success_at")):
        errors.append("successful projection requires sync.last_success_at")

    reminders = mapping(selected.get("reminders"))
    if text(reminders.get("status")).lower() in SUCCESS_STATUSES:
        reminder_provider = text(reminders.get("provider")).lower()
        reminder_resources = [
            item
            for item in resources
            if item.get("capability") == "reminders"
            and item.get("provider") == reminder_provider
        ]
        if not reminder_resources:
            errors.append(
                "successful reminders capability requires a registered reminder resource"
            )
        for reminder in reminder_resources:
            if not text(reminder.get("id")) or not text(
                reminder.get("target_url")
            ):
                errors.append(
                    "registered reminder resource requires id and target_url"
                )
    return errors


def main() -> int:
    errors = validate_contract()
    errors.extend(validate_projection_state())
    operations_dir = ROOT / "state/operations"
    if operations_dir.exists():
        for path in sorted(operations_dir.glob("*.json")):
            errors.extend(validate_operation(path))

    if errors:
        for error in errors:
            fail(error)
        return 1

    print("Task projection contract, journals and published state are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
