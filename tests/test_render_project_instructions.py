from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "render_project_instructions.py"
SPEC = importlib.util.spec_from_file_location("render_project_instructions", MODULE_PATH)
assert SPEC and SPEC.loader
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


class RenderProjectInstructionsTests(unittest.TestCase):
    def source(self):
        return """# Project\n\nCopy the content below into the Project Instructions and replace `OWNER/REPOSITORY`.\n\n- Instance: `OWNER/REPOSITORY`\n\n## Tasks\n\nOld wording.\n\n## Completion response\n\nDone.\n"""

    def test_new_instance_includes_canonical_projection_contract(self):
        rendered = renderer.render_instructions(self.source(), "owner/course")
        self.assertIn("Planejado → Disponível em paralelo → Próxima aula", rendered)
        self.assertIn("one issue per materialized lesson", rendered)
        self.assertIn("study:ready", rendered)
        self.assertEqual(1, rendered.count(renderer.PROJECTION_START))

    def test_render_is_idempotent(self):
        first = renderer.render_instructions(self.source(), "owner/course")
        second = renderer.render_instructions(first, "owner/course")
        self.assertEqual(first, second)

    def test_repository_rename_keeps_projection_block_once(self):
        first = renderer.render_instructions(self.source(), "owner/course")
        second = renderer.render_instructions(first, "owner/renamed")
        self.assertIn("- Instance: `owner/renamed`", second)
        self.assertEqual(1, second.count(renderer.PROJECTION_START))


if __name__ == "__main__":
    unittest.main()
