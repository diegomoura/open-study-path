#!/usr/bin/env python3
"""Build deterministic offline ZIP packages from semantic study-slide sources."""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from study_slides import (
    PACKAGE_BUILDER_ID,
    PACKAGE_ENTRYPOINT,
    PACKAGE_MARKER,
    SOURCE_FILENAMES,
    aggregate_source_sha256,
    file_sha256,
    parse_slide_html,
)

ROOT = Path(__file__).resolve().parents[1]


def bundle_javascript(js_path: Path) -> tuple[str, str]:
    executable = ROOT / "node_modules" / ".bin" / ("esbuild.cmd" if sys.platform == "win32" else "esbuild")
    if not executable.is_file():
        raise RuntimeError("esbuild is missing; install the pinned study-slide package dependencies first")
    result = subprocess.run(
        [str(executable), str(js_path), "--bundle", "--format=iife", "--platform=browser", "--minify", "--log-level=error"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "esbuild failed")
    version = subprocess.run([str(executable), "--version"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    return result.stdout.strip(), version


def package_html(index_path: Path, css_path: Path, js_bundle: str) -> str:
    html = index_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    stylesheet = '<link rel="stylesheet" href="slides.css">'
    script = '<script type="module" src="slides.js"></script>'
    if stylesheet not in html or script not in html:
        raise RuntimeError(f"{index_path} must use canonical local asset tags")
    html = html.replace(stylesheet, f"<style>\n{css}\n</style>", 1)
    html = html.replace(script, f"<script>\n{js_bundle}\n</script>", 1)
    return html.replace("<!doctype html>", f"<!doctype html>\n<!-- {PACKAGE_MARKER} -->", 1)


def deterministic_zip(html: str) -> bytes:
    output = io.BytesIO()
    info = ZipInfo(PACKAGE_ENTRYPOINT, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        archive.writestr(info, html.encode("utf-8"), compress_type=ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def build_deck(topic_dir: Path) -> tuple[bytes, bytes]:
    source_paths = [topic_dir / name for name in SOURCE_FILENAMES]
    for path in source_paths:
        if not path.is_file():
            raise RuntimeError(f"missing slide source: {path}")
    parser = parse_slide_html(source_paths[0])
    js_bundle, esbuild_version = bundle_javascript(source_paths[2])
    html = package_html(source_paths[0], source_paths[1], js_bundle)
    html_bytes = html.encode("utf-8")
    archive_bytes = deterministic_zip(html)
    meta = {
        "contract_version": 2,
        "topic_id": parser.topic_id,
        "content_version": parser.content_version,
        "entrypoint": PACKAGE_ENTRYPOINT,
        "builder": {
            "id": PACKAGE_BUILDER_ID,
            "esbuild": esbuild_version,
            "mermaid": "11.16.0",
        },
        "source_sha256": {path.relative_to(ROOT).as_posix(): file_sha256(path) for path in source_paths},
        "source_digest": aggregate_source_sha256(source_paths, ROOT),
        "html": {"bytes": len(html_bytes), "sha256": sha256(html_bytes).hexdigest()},
        "package": {"bytes": len(archive_bytes), "sha256": sha256(archive_bytes).hexdigest(), "files": [PACKAGE_ENTRYPOINT]},
    }
    meta_bytes = (json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return archive_bytes, meta_bytes


def process(topic_dir: Path, check: bool) -> list[str]:
    archive, meta = build_deck(topic_dir)
    zip_path = topic_dir / "slides.zip"
    meta_path = topic_dir / "slides.meta.json"
    errors: list[str] = []
    if check:
        if not zip_path.is_file() or zip_path.read_bytes() != archive:
            errors.append(f"{topic_dir.name}: slides.zip is missing or stale")
        if not meta_path.is_file() or meta_path.read_bytes() != meta:
            errors.append(f"{topic_dir.name}: slides.meta.json is missing or stale")
    else:
        zip_path.write_bytes(archive)
        meta_path.write_bytes(meta)
        print(f"Packaged {topic_dir.name}: {zip_path.relative_to(ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify committed ZIP packages without rewriting them")
    parser.add_argument("topics", nargs="*", help="optional topic IDs such as TOPIC-001")
    args = parser.parse_args()
    slides_root = ROOT / "study" / "slides"
    if not slides_root.is_dir():
        print("No materialized study-slide sources found.")
        return 0
    selected = set(args.topics)
    topic_dirs = [path.parent for path in sorted(slides_root.glob("TOPIC-*/index.html")) if not selected or path.parent.name in selected]
    if not topic_dirs:
        print("No materialized study-slide sources found.")
        return 0
    errors: list[str] = []
    for topic_dir in topic_dirs:
        try:
            errors.extend(process(topic_dir, args.check))
        except Exception as exc:
            errors.append(f"{topic_dir.name}: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.check:
        print(f"Study-slide ZIP packages are current ({len(topic_dirs)} topic(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
