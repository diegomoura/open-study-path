#!/usr/bin/env python3
"""One-time bootstrap for the canonical static SVG/PDF slide contract."""
from __future__ import annotations
import base64
from pathlib import Path
import json
import os
import subprocess
import urllib.request

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


def dispatch() -> None:
    data = json.dumps({"ref": os.environ["BOOTSTRAP_BRANCH"], "inputs": {"review_base_sha": os.environ["BOOTSTRAP_BASE_SHA"]}}).encode()
    request = urllib.request.Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/actions/workflows/validate-template.yml/dispatches",
        data=data, method="POST",
        headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 204:
            raise RuntimeError(f"workflow dispatch failed: {response.status}")


def main() -> None:
    (ROOT / "scripts/study_slides_legacy.py").write_bytes((ROOT / "scripts/study_slides.py").read_bytes())
    for relative in RESTORE:
        restore(relative)
    parts = sorted((ROOT / ".open-study-path/bootstrap-payload").glob("part-*.txt"))
    archive = ROOT / ".open-study-path-static-svg-payload.tar.gz"
    archive.write_bytes(base64.b64decode("".join(path.read_text() for path in parts)))
    run("tar", "-xzf", str(archive), "-C", str(ROOT))
    archive.unlink()
    for obsolete in (
        ROOT / "scripts/package_study_slides.py", ROOT / "templates/study-slides/slides.js",
        ROOT / "scripts/bootstrap_static_svg_contract.py", ROOT / ".open-study-path/bootstrap-payload",
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
    run("git", "config", "user.name", "open-study-path-bot")
    run("git", "config", "user.email", "open-study-path-bot@users.noreply.github.com")
    run("git", "reset", "--soft", os.environ["BOOTSTRAP_BASE_SHA"])
    run("git", "add", "-A")
    run("git", "commit", "-m", "Restaurar PDF com Mermaid estático em SVG")
    run("git", "push", "--force", "origin", f"HEAD:{os.environ['BOOTSTRAP_BRANCH']}")
    dispatch()
    print("Canonical static SVG/PDF contract committed and final validation dispatched.")


if __name__ == "__main__":
    main()
