import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

import yaml


class RefreshReviewFingerprintsTest(unittest.TestCase):
    def test_refreshes_multiple_stale_entries_in_one_run(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "refresh_review_fingerprints.py"
        source = script.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "state" / "reviews").mkdir(parents=True)
            (root / "study").mkdir()
            (root / "study" / "a.md").write_text("A", encoding="utf-8")
            (root / "study" / "b.md").write_text("B", encoding="utf-8")
            (root / "scripts" / "refresh_review_fingerprints.py").write_text(source, encoding="utf-8")
            manifest = {
                "artifacts": [
                    {"path": "study/a.md", "change": "current", "sha256": "0" * 64},
                    {"path": "study/b.md", "change": "current", "sha256": "1" * 64},
                ]
            }
            review = root / "state" / "reviews" / "review.yml"
            review.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            result = subprocess.run([sys.executable, str(root / "scripts" / "refresh_review_fingerprints.py"), "--write"], cwd=root, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            updated = yaml.safe_load(review.read_text(encoding="utf-8"))
            self.assertEqual(updated["artifacts"][0]["sha256"], hashlib.sha256(b"A").hexdigest())
            self.assertEqual(updated["artifacts"][1]["sha256"], hashlib.sha256(b"B").hexdigest())


if __name__ == "__main__":
    unittest.main()
