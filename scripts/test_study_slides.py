#!/usr/bin/env python3
"""Regression tests for semantic slides and deterministic offline ZIP delivery."""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import json
import sys

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from study_slides import (  # noqa: E402
    PACKAGE_BUILDER_ID,
    PACKAGE_ENTRYPOINT,
    PACKAGE_MARKER,
    REQUIRED_REVIEW_CHECKS,
    aggregate_source_sha256,
    expected_package_url,
    file_sha256,
    validate_materialized_topic,
)


def write(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content) if isinstance(content, bytes) else path.write_text(content, encoding="utf-8")


def canonical_css() -> str:
    return """/* open-study-path:study-slides-theme version=2 */
.osp-slide{width:1280px;height:720px}.osp-grid{}.osp-compare{}.osp-diagram{}.osp-case{}.osp-steps{}.osp-challenge{}.osp-checklist{}.osp-prompt-grid{}.osp-summary-layout{}
"""


def canonical_js() -> str:
    return """/* open-study-path:study-slides-runtime version=3 */
import mermaid from "mermaid";
window.__OPEN_STUDY_PATH_SLIDES_READY__=Boolean(mermaid);
"""


def valid_html(repository: str, *, packaged: bool = False) -> str:
    specs = [
        ("title", "LO-1", "", "osp-title-layout", "Introdução clara para o resultado desenvolvido."),
        ("map", "LO-1", "", "osp-grid", "Mapa da aula com definição, mecanismo e aplicação."),
        ("concept", "LO-1 LO-2", "Conteúdo essencial", "osp-compare", "Contraste entre os objetos centrais."),
        ("diagram", "LO-1 LO-2", "Mapa visual", "osp-diagram", "Fluxo principal com interpretação e limite."),
        ("example", "LO-1 LO-2", "Exemplos trabalhados", "osp-case", "Exemplo com situação, decisão e verificação."),
        ("example", "LO-2", "Exemplos trabalhados", "osp-steps", "Segundo exemplo que demonstra transferência."),
        ("misconception", "LO-2", "Erros comuns e como corrigir", "osp-compare", "Erro provável comparado com critério melhor."),
        ("application", "LO-1 LO-2", "Prática guiada", "osp-challenge osp-checklist", "Desafio para justificar uma decisão."),
        ("recap", "LO-1 LO-2", "Confira sem consultar", "osp-prompt-grid", "Perguntas de recuperação ativa."),
        ("summary", "LO-1 LO-2", "", "osp-summary-layout", "Síntese e links atuais."),
    ]
    sections = []
    for index, (role, outcomes, section, layout, text) in enumerate(specs, start=1):
        section_attr = f' data-lesson-section="{section}"' if section else ""
        mermaid = '<div class="osp-diagram mermaid">flowchart LR; A-->B</div><p class="osp-caption">Observe o fluxo e seu limite.</p>' if role == "diagram" else ""
        sections.append(
            f'<section class="osp-slide" data-slide-role="{role}" data-outcome-ids="{outcomes}"{section_attr}>'
            f'<h2>Slide {index}</h2><div class="{layout}"><p>{text}</p>{mermaid}</div></section>'
        )
    asset_head = "<style>.osp-slide{display:block}</style>" if packaged else '<link rel="stylesheet" href="slides.css">'
    asset_tail = "<script>window.ready=true;</script>" if packaged else '<script type="module" src="slides.js"></script>'
    marker = f"<!-- {PACKAGE_MARKER} -->" if packaged else ""
    return f"""<!doctype html>{marker}
<html lang="pt-BR"><head>
<meta name="open-study-path:topic-id" content="TOPIC-001">
<meta name="open-study-path:content-version" content="2">
<meta name="open-study-path:slide-theme" content="canonical-v2">{asset_head}
</head><body><main>{''.join(sections)}</main>
<a href="https://github.com/{repository}/blob/HEAD/study/modules/TOPIC-001.md">Aula</a>
{asset_tail}</body></html>
"""


def deterministic_zip(html: str) -> bytes:
    output = BytesIO()
    info = ZipInfo(PACKAGE_ENTRYPOINT, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        archive.writestr(info, html.encode("utf-8"), compress_type=ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def build_valid_tree(root: Path) -> tuple[dict, str]:
    repository = "example/private-study"
    topic = {
        "id": "TOPIC-001",
        "content_status": "materialized",
        "content_version": 2,
        "module": "study/modules/TOPIC-001.md",
        "slides": "study/slides/TOPIC-001/index.html",
        "slides_package": "study/slides/TOPIC-001/slides.zip",
        "slides_review": "state/slide-reviews/TOPIC-001.yml",
        "learning_outcomes": [
            {"id": "LO-1", "statement": "One", "required_concepts": ["A"]},
            {"id": "LO-2", "statement": "Two", "required_concepts": ["B"]},
        ],
    }
    template_dir = root / "templates/study-slides"
    write(template_dir / "slides.css", canonical_css())
    write(template_dir / "slides.js", canonical_js())
    topic_dir = root / "study/slides/TOPIC-001"
    write(topic_dir / "index.html", valid_html(repository))
    write(topic_dir / "slides.css", canonical_css())
    write(topic_dir / "slides.js", canonical_js())
    lesson = root / "study/modules/TOPIC-001.md"
    package_url = expected_package_url(repository, topic["slides_package"])
    write(lesson, f"# Aula\n\n<!-- open-study-path:slides-link:start -->\n## Slides da aula\n\n[Baixar slides (ZIP)]({package_url})\n\nExtraia o arquivo e abra `{PACKAGE_ENTRYPOINT}` no navegador.\n<!-- open-study-path:slides-link:end -->\n")
    source_paths = [topic_dir / name for name in ["index.html", "slides.css", "slides.js"]]
    packaged_html = valid_html(repository, packaged=True)
    package = deterministic_zip(packaged_html)
    write(topic_dir / "slides.zip", package)
    meta = {
        "contract_version": 2,
        "topic_id": "TOPIC-001",
        "content_version": 2,
        "entrypoint": PACKAGE_ENTRYPOINT,
        "builder": {"id": PACKAGE_BUILDER_ID, "esbuild": "test", "mermaid": "test"},
        "source_sha256": {p.relative_to(root).as_posix(): file_sha256(p) for p in source_paths},
        "source_digest": aggregate_source_sha256(source_paths, root),
        "html": {"bytes": len(packaged_html.encode()), "sha256": sha256(packaged_html.encode()).hexdigest()},
        "package": {"bytes": len(package), "sha256": sha256(package).hexdigest(), "files": [PACKAGE_ENTRYPOINT]},
    }
    write(topic_dir / "slides.meta.json", json.dumps(meta))
    review = {
        "version": 3,
        "topic_id": "TOPIC-001",
        "content_version": 2,
        "reviewed_at": "2026-08-02T12:00:00Z",
        "reviewer_role": "study_slides_reviewer",
        "review_mode": "independent_pass",
        "status": "approved",
        "source_lesson": "study/modules/TOPIC-001.md",
        "source_lesson_sha256": file_sha256(lesson),
        "slides_source": "study/slides/TOPIC-001/index.html",
        "slides_source_sha256": aggregate_source_sha256(source_paths, root),
        "checks": {name: "passed" for name in REQUIRED_REVIEW_CHECKS},
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


def test_external_runtime_asset_is_rejected() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, repository = build_valid_tree(root)
        package = valid_html(repository, packaged=True).replace("<style>", '<script src="https://cdn.example/x.js"></script><style>')
        write(root / topic["slides_package"], deterministic_zip(package))
        errors = validate_materialized_topic(root, repository, topic)
        assert any("external runtime assets" in error for error in errors)


def test_stale_package_is_rejected() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, repository = build_valid_tree(root)
        path = root / topic["slides_package"]
        path.write_bytes(path.read_bytes() + b"x")
        errors = validate_materialized_topic(root, repository, topic)
        assert any("package hash is stale" in error for error in errors)


def test_pdf_link_is_rejected() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, repository = build_valid_tree(root)
        lesson = root / topic["module"]
        lesson.write_text(lesson.read_text(encoding="utf-8") + "\nslides.pdf\n", encoding="utf-8")
        errors = validate_materialized_topic(root, repository, topic)
        assert any("still exposes a PDF" in error for error in errors)


def main() -> None:
    tests = [test_valid_topic, test_external_runtime_asset_is_rejected, test_stale_package_is_rejected, test_pdf_link_is_rejected]
    for test in tests:
        test()
    print(f"Study-slide regression tests passed ({len(tests)} cases).")


if __name__ == "__main__":
    main()
