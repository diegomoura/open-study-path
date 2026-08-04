from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_task_projection.py"
SPEC = importlib.util.spec_from_file_location("validate_task_projection", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidateTaskProjectionTests(unittest.TestCase):
    def test_contract_is_complete(self):
        self.assertEqual([], validator.validate_contract())

    def write_json(self, value):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "operation.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def operation(self):
        return {
            "operation_id": "publication-v1",
            "operation_type": "publication",
            "provider": "trello",
            "mode": "full_curriculum",
            "status": "success",
            "topics": ["TOPIC-001"],
            "attempt": 1,
            "checkpoints": [{"name": "readback_validated", "at": "2026-08-03T20:00:00Z"}],
            "external_read_count": 1,
            "external_write_count": 3,
            "commit_budget": 1,
            "warnings": [],
            "errors": [],
            "started_at": "2026-08-03T19:00:00Z",
            "updated_at": "2026-08-03T20:00:00Z",
            "completed_at": "2026-08-03T20:00:00Z"
        }

    def test_valid_operation(self):
        self.assertEqual([], validator.validate_operation(self.write_json(self.operation())))

    def test_success_requires_readback(self):
        value = self.operation()
        value["external_read_count"] = 0
        errors = validator.validate_operation(self.write_json(value))
        self.assertTrue(any("final read-back" in error for error in errors))

    def test_duplicate_topics_are_rejected(self):
        value = self.operation()
        value["topics"] = ["TOPIC-001", "TOPIC-001"]
        errors = validator.validate_operation(self.write_json(value))
        self.assertTrue(any("duplicate topics" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
