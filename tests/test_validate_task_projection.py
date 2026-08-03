import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "validate_task_projection.py"
)
SPEC = importlib.util.spec_from_file_location(
    "validate_task_projection", MODULE_PATH
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class TaskProjectionValidationTests(unittest.TestCase):
    def test_contract_artifacts_are_consistent(self):
        self.assertEqual([], validator.validate_contract())

    def write_json(self, value: dict) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "operation.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_valid_operation(self):
        operation = {
            "operation_id": "publication-v1",
            "operation_type": "publication",
            "provider": "trello",
            "mode": "active_window",
            "status": "in_progress",
            "topics": ["TOPIC-001", "TOPIC-002"],
            "attempt": 1,
            "external_read_count": 1,
            "external_write_count": 2,
            "started_at": "2026-07-31T14:00:00-03:00",
            "updated_at": "2026-07-31T14:05:00-03:00",
        }
        self.assertEqual(
            [], validator.validate_operation(self.write_json(operation))
        )

    def test_success_requires_completed_at(self):
        operation = {
            "operation_id": "publication-v1",
            "operation_type": "publication",
            "provider": "todoist",
            "mode": "active_window",
            "status": "success",
            "topics": ["TOPIC-001"],
            "attempt": 1,
            "external_read_count": 0,
            "external_write_count": 1,
            "started_at": "2026-07-31T14:00:00-03:00",
            "updated_at": "2026-07-31T14:05:00-03:00",
        }
        errors = validator.validate_operation(self.write_json(operation))
        self.assertTrue(
            any("requires completed_at" in error for error in errors)
        )

    def test_duplicate_topics_are_rejected(self):
        operation = {
            "operation_id": "reconcile-v1",
            "operation_type": "reconciliation",
            "provider": "github_issues",
            "mode": "active_window",
            "status": "partial",
            "topics": ["TOPIC-001", "TOPIC-001"],
            "attempt": 2,
            "external_read_count": 3,
            "external_write_count": 0,
            "started_at": "2026-07-31T14:00:00-03:00",
            "updated_at": "2026-07-31T14:05:00-03:00",
        }
        errors = validator.validate_operation(self.write_json(operation))
        self.assertTrue(
            any("duplicate topics" in error for error in errors)
        )

    def trello_state(self):
        lists = [
            {
                "capability": "task_manager",
                "provider": "trello",
                "type": "list",
                "id": f"list-{index}",
                "name": name,
            }
            for index, name in enumerate(validator.VISIBLE_LISTS, 1)
        ]
        return {
            "selected_capabilities": {
                "task_manager": {
                    "provider": "trello",
                    "status": "success",
                    "resolution_status": "resolved",
                },
                "reminders": {
                    "provider": "todoist",
                    "status": "success",
                    "resolution_status": "resolved",
                },
            },
            "projection": {
                "provider": "trello",
                "board_id": "board-1",
                "board_url": "https://trello.example/board-1",
                "topic_count": 2,
                "list_order": list(validator.VISIBLE_LISTS),
                "readback": {
                    "lesson_card_count": 2,
                    "managed_card_count": 3,
                    "visible_internal_marker_count": 0,
                    "verified_at": "2026-08-03T18:47:30Z",
                },
            },
            "resources": [
                {
                    "capability": "task_manager",
                    "provider": "trello",
                    "type": "board",
                    "id": "board-1",
                    "url": "https://trello.example/board-1",
                },
                *lists,
                {
                    "capability": "task_manager",
                    "provider": "trello",
                    "type": "orientation",
                    "id": "orientation-1",
                    "url": "https://trello.example/orientation",
                    "canonical_state": "Planejado",
                },
                {
                    "capability": "task_manager",
                    "provider": "trello",
                    "type": "card",
                    "id": "card-1",
                    "url": "https://trello.example/card-1",
                    "topic_id": "TOPIC-001",
                    "visible_lesson_number": 1,
                    "direct_prerequisite_ids": [],
                    "content_version": 1,
                    "canonical_state": "Próxima aula",
                },
                {
                    "capability": "task_manager",
                    "provider": "trello",
                    "type": "card",
                    "id": "card-2",
                    "url": "https://trello.example/card-2",
                    "topic_id": "TOPIC-002",
                    "visible_lesson_number": 2,
                    "direct_prerequisite_ids": ["TOPIC-001"],
                    "content_version": 0,
                    "canonical_state": "Planejado",
                },
                {
                    "capability": "reminders",
                    "provider": "todoist",
                    "type": "task",
                    "id": "reminder-1",
                    "target_url": "https://trello.example/board-1",
                },
            ],
            "resolution": {"status": "resolved"},
            "sync": {
                "status": "success",
                "last_success_at": "2026-08-03T18:47:30Z",
            },
        }

    def todoist_state(self):
        return {
            "selected_capabilities": {
                "task_manager": {
                    "provider": "todoist",
                    "status": "success",
                    "resolution_status": "resolved",
                }
            },
            "projection": {
                "provider": "todoist",
                "topic_count": 1,
                "readback": {
                    "lesson_card_count": 1,
                    "managed_card_count": 2,
                    "visible_internal_marker_count": 0,
                    "verified_at": "2026-08-03T18:47:30Z",
                },
            },
            "resources": [
                {
                    "capability": "task_manager",
                    "provider": "todoist",
                    "type": "project",
                    "id": "project-1",
                    "url": "https://todoist.example/project-1",
                },
                {
                    "capability": "task_manager",
                    "provider": "todoist",
                    "type": "orientation",
                    "id": "orientation-1",
                    "url": "https://todoist.example/orientation",
                    "canonical_state": "planned",
                },
                {
                    "capability": "task_manager",
                    "provider": "todoist",
                    "type": "task",
                    "id": "task-1",
                    "topic_id": "TOPIC-001",
                    "visible_lesson_number": 1,
                    "direct_prerequisite_ids": [],
                    "content_version": 1,
                    "canonical_state": "ready_primary",
                },
            ],
            "resolution": {"status": "resolved"},
            "sync": {
                "status": "success",
                "last_success_at": "2026-08-03T18:47:30Z",
            },
        }

    def write_instance(self, root: Path, state: dict):
        (root / ".open-study-path").mkdir(parents=True)
        (root / ".open-study-path" / "instance.yml").write_text(
            "kind: instance\n", encoding="utf-8"
        )
        (root / "state").mkdir()
        (root / "state" / "integrations.json").write_text(
            json.dumps(state), encoding="utf-8"
        )

    def validate_state(self, state: dict):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        self.write_instance(root, state)
        return validator.validate_projection_state(root)

    def test_valid_published_trello_state(self):
        self.assertEqual([], self.validate_state(self.trello_state()))

    def test_valid_published_todoist_state_is_not_trello_coupled(self):
        self.assertEqual([], self.validate_state(self.todoist_state()))

    def test_missing_orientation_and_lists_are_rejected(self):
        state = self.trello_state()
        state["resources"] = [
            item
            for item in state["resources"]
            if item.get("type") not in {"orientation", "list"}
        ]
        errors = self.validate_state(state)
        self.assertTrue(
            any("seven managed lists" in error for error in errors)
        )
        self.assertTrue(
            any("orientation resource" in error for error in errors)
        )

    def test_visible_marker_readback_blocks_success(self):
        state = self.trello_state()
        state["projection"]["readback"][
            "visible_internal_marker_count"
        ] = 1
        errors = self.validate_state(state)
        self.assertTrue(
            any(
                "learner-visible internal metadata" in error
                for error in errors
            )
        )

    def test_trello_card_url_is_required(self):
        state = self.trello_state()
        lesson = next(
            item for item in state["resources"] if item.get("topic_id")
        )
        lesson.pop("url")
        errors = self.validate_state(state)
        self.assertTrue(any("missing url" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
