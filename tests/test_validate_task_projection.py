import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_task_projection.py"
SPEC = importlib.util.spec_from_file_location("validate_task_projection", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class TaskProjectionValidationTests(unittest.TestCase):
    def test_contract_artifacts_are_consistent(self):
        self.assertEqual([], validator.validate_contract())

    def test_valid_operation(self):
        operation = {
            "operation_id": "publication-v1",
            "operation_type": "publication",
            "provider": "trello",
            "mode": "active_window",
            "status": "in_progress",
            "current_batch": "batch-001",
            "topics": ["TOPIC-001", "TOPIC-002"],
            "attempt": 1,
            "external_read_count": 1,
            "external_write_count": 2,
            "last_checkpoint": "trello.card.TOPIC-002",
            "last_error": None,
            "branch": "agent/publication-v1",
            "pull_request": None,
            "started_at": "2026-07-31T14:00:00-03:00",
            "updated_at": "2026-07-31T14:05:00-03:00",
            "completed_at": None,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "operation.json"
            path.write_text(json.dumps(operation), encoding="utf-8")
            self.assertEqual([], validator.validate_operation(path))

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
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "operation.json"
            path.write_text(json.dumps(operation), encoding="utf-8")
            errors = validator.validate_operation(path)
            self.assertTrue(any("requires completed_at" in error for error in errors))

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
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "operation.json"
            path.write_text(json.dumps(operation), encoding="utf-8")
            errors = validator.validate_operation(path)
            self.assertTrue(any("duplicate topics" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
