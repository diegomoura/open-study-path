#!/usr/bin/env python3
"""Regression tests for the study-slide source, review and PDF contract."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json

import yaml

from study_slides import (
    aggregate_source_sha256,
    expected_pdf_url,
    file_sha256,
    validate_materialized_topic,
)


def write(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def fake_pdf(pages: int) -> bytes:
    body = [b"%PDF-1.7\n"]
    for index in range(1, pages + 1):
        body.append(f"{index} 0 obj << /Type /Page /Parent 99 0 R >> endobj\n".encode())
    body.append(b"% padding\n" + b"x" * 1400 + b"\n%%EOF\n")
    return b"".join(body)


def valid_html(repository: str) -> str:
    sections = []
    outcomes = ["LO-1", "LO-1", "LO-2", "LO-2", "LO-1 LO-2", "LO-2"]
    for index, mapped in enumerate(outcomes, start=1):
        diagram = '<div class="mermaid">flowchart LR; A-->B</div>' if index == 2 else ""
        sections.append(
            f'<section class="osp-slide" data-outcome-ids="{mapped}"><h2>Slide {index}</h2>'
            f'<p>Resumo claro do conteúdo aprovado.</p>{diagram}</section>'
        )
    return f"""<!doctype html>
<html lang="pt-BR"><head>
<meta name="open-study-path:topic-id" content="TOPIC-001">
<meta name="open-study-path:content-version" content="2">
<link rel="stylesheet" href="slides.css">
</head><body><main>{''.join(sections)}</main>
<a href="https://github.com/{repository}/blob/HEAD/study/modules/TOPIC-001.md">Aula</a>
<script type="module" src="slides.js"></script></body></html>
"""


def build_valid_tree(root: Path) -> tuple[dict, str]:
    repository = "example/private-study"
    topic = {
        "id": "TOPIC-001",
        "content_status": "materialized",
        "content_version": 2,
        "module": "study/modules/TOPIC-001.md",
        "slides": "study/slides/TOPIC-001/index.html",
        "slides_pdf": "study/slides/TOPIC-001/slides.pdf",
        "slides_review": "state/slide-reviews/TOPIC-001.yml",
        "learning_outcomes": [
            {"id": "LO-1", "statement": "One", "required_concepts": ["A"]},
            {"id": "LO-2", "statement": "Two", "required_concepts": ["B"]},
        ],
    }
    topic_dir = root / "study/slides/TOPIC-001"
    write(topic_dir / "index.html", valid_html(repository))
    write(topic_dir / "slides.css", ".osp-slide{width:100%;height:100%;}")
    write(topic_dir / "slides.js", "window.__OPEN_STUDY_PATH_SLIDES_READY__=true;")
    pdf = fake_pdf(6)
    write(topic_dir / "slides.pdf", pdf)
    lesson = root / "study/modules/TOPIC-001.md"
    pdf_url = expected_pdf_url(repository, topic["slides_pdf"])
    write(
        lesson,
        "# Aula\n\n<!-- open-study-path:slides-link:start -->\n"
        f"## Slides da aula\n\n[Ver os slides desta aula em PDF]({pdf_url})\n"
        "<!-- open-study-path:slides-link:end -->\n",
    )
    source_paths = [topic_dir / name for name in ["index.html", "slides.css", "slides.js"]]
    source_hashes = {
        path.relative_to(root).as_posix(): file_sha256(path)
        for path in [*source_paths, lesson]
    }
    source_digest = aggregate_source_sha256([*source_paths, lesson], root)
    meta = {
        "contract_version": 1,
        "topic_id": "TOPIC-001",
        "content_version": 2,
        "generated_at": "2026-07-30T12:00:00Z",
        "renderer": {"playwright": "test", "mermaid": "test"},
        "slide_count": 6,
        "mermaid_count": 1,
        "outcome_ids": ["LO-1", "LO-2"],
        "source_sha256": source_hashes,
        "source_digest": source_digest,
        "pdf": {"pages": 6, "bytes": len(pdf), "sha256": file_sha256(topic_dir / "slides.pdf")},
        "diagnostics": {"console_errors": [], "overflow_slides": [], "external_requests": []},
    }
    write(topic_dir / "slides.meta.json", json.dumps(meta))
    review = {
        "version": 1,
        "topic_id": "TOPIC-001",
        "content_version": 2,
        "reviewed_at": "2026-07-30T12:00:00Z",
        "reviewer_role": "study_slides_reviewer",
        "review_mode": "independent_pass",
        "status": "approved",
        "source_lesson": "study/modules/TOPIC-001.md",
        "source_lesson_sha256": file_sha256(lesson),
        "slides_source": "study/slides/TOPIC-001/index.html",
        "slides_source_sha256": aggregate_source_sha256(source_paths, root),
        "checks": {
            "lesson_fidelity": "passed",
            "outcome_coverage": "passed",
            "summary_quality": "passed",
            "visual_hierarchy": "passed",
            "mermaid_quality": "passed",
            "accessibility": "passed",
            "link_consistency": "passed",
        },
        "outcomes_reviewed": ["LO-1", "LO-2"],
        "blocking_findings": [],
        "non_blocking_findings": [],
    }
    write(root / "state/slide-reviews/TOPIC-001.yml", yaml.safe_dump(review, sort_keys=False))
    return topic, repository


def test_valid_topic() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, repository = build_valid_tree(root)
        assert validate_materialized_topic(root, repository, topic) == []


def test_stale_source_is_rejected() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, repository = build_valid_tree(root)
        css = root / "study/slides/TOPIC-001/slides.css"
        css.write_text(css.read_text(encoding="utf-8") + "\n.changed{}", encoding="utf-8")
        errors = validate_materialized_topic(root, repository, topic)
        assert any("source hashes are stale" in error for error in errors)
        assert any("review source hash is stale" in error for error in errors)


def test_images_and_external_runtime_are_rejected() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, repository = build_valid_tree(root)
        html = root / "study/slides/TOPIC-001/index.html"
        content = html.read_text(encoding="utf-8")
        content = content.replace('href="slides.css"', 'href="https://example.com/slides.css"')
        content = content.replace("</main>", '<img src="slide.png" alt=""><\/main>').replace("<\/main>", "</main>")
        html.write_text(content, encoding="utf-8")
        errors = validate_materialized_topic(root, repository, topic)
        assert any("external runtime URLs" in error for error in errors)
        assert any("must not contain generated raster images" in error for error in errors)


def main() -> None:
    tests = [test_valid_topic, test_stale_source_is_rejected, test_images_and_external_runtime_are_rejected]
    for test in tests:
        test()
    print(f"Study-slide regression tests passed ({len(tests)} cases).")


if __name__ == "__main__":
    main()
