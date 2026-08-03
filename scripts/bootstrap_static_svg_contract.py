#!/usr/bin/env python3
"""One-time bootstrap for the canonical static SVG/PDF slide contract."""
from __future__ import annotations
import base64
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OLD_PDF_COMMIT = "65cd2bdb71709ac812fa516f6c3eefa1e4fb0980"
RESTORE = (
    "AGENTS.md", "README.md", ".github/workflows/validate-usable-generation.yml",
    "instructions/30-generate-path.md", "instructions/36-review-course-content.md",
    "instructions/38-complete-usable-generation.md", "instructions/40-publish-tasks.md",
    "instructions/57-materialize-next-content.md", "templates/chatgpt-project-instructions.md",
    "templates/module.md", "templates/topic.md",
)


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def restore(relative: str) -> None:
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["git", "show", f"{OLD_PDF_COMMIT}:{relative}"], cwd=ROOT, check=True, stdout=subprocess.PIPE)
    target.write_bytes(result.stdout)


def main() -> None:
    (ROOT / "scripts/study_slides_legacy.py").write_bytes((ROOT / "scripts/study_slides.py").read_bytes())
    for relative in RESTORE:
        restore(relative)
    payload_dir = ROOT / ".open-study-path/exact-payload"
    parts = [
        payload_dir / "part-000.txt",
        payload_dir / "part-001.txt",
        payload_dir / "part-002-003.txt",
        payload_dir / "part-004-005.txt",
        payload_dir / "part-006.txt",
        payload_dir / "part-007.txt",
        payload_dir / "part-008-009.txt",
        payload_dir / "part-010-011.txt",
    ]
    archive = ROOT / ".open-study-path-static-svg-payload.tar.gz"
    archive.write_bytes(base64.b64decode("".join(path.read_text() for path in parts), validate=True))
    import hashlib
    expected_archive_sha256 = "9b7d6f2be6d8bc044c23c0226d2c077a0d28b6c3eed89d63433bee578800e0a7"
    actual_archive_sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual_archive_sha256 != expected_archive_sha256:
        raise RuntimeError(f"payload checksum mismatch: {actual_archive_sha256}")
    run("tar", "-xzf", str(archive), "-C", str(ROOT))
    archive.unlink()
    for obsolete in (
        ROOT / "scripts/package_study_slides.py", ROOT / "templates/study-slides/slides.js",
        ROOT / "scripts/bootstrap_static_svg_contract.py", ROOT / ".open-study-path/bootstrap-payload",
        ROOT / ".open-study-path/exact-payload",
    ):
        if obsolete.is_dir():
            import shutil; shutil.rmtree(obsolete)
        elif obsolete.exists():
            obsolete.unlink()
    run("python", "scripts/update_static_svg_slide_contract_text.py")
    run("python", "-m", "py_compile", "scripts/study_slides.py", "scripts/study_slides_legacy.py", "scripts/validate_study_slides.py", "scripts/test_study_slides.py", "scripts/validate_generation_efficiency.py")
    run("python", "scripts/test_study_slides.py")
    run("node", "--check", "scripts/render_study_slides.mjs")
    run("node", "--check", "scripts/test_study_slide_renderer.mjs")
    import shutil
    for cache in ROOT.rglob("__pycache__"):
        shutil.rmtree(cache)
    for pyc in ROOT.rglob("*.pyc"):
        pyc.unlink()
    output = Path("/tmp/open-study-path-final-tree.tar.gz")
    subprocess.run(
        ["tar", "--exclude=.git", "--exclude=.open-study-path-final-tree.tar.gz", "-czf", str(output), "-C", str(ROOT), "."],
        check=True,
    )
    print(f"Canonical static SVG/PDF tree exported to {output}.")


if __name__ == "__main__":
    main()
