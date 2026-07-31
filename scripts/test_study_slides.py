#!/usr/bin/env python3
"""Regression tests for the study-slide source, review and PDF contract."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys

import yaml
from pypdf import PdfWriter

sys.path.insert(0, str(Path(__file__).parent))
from study_slides import (  # noqa: E402
    PDF_PRODUCER,
    RENDERER_ID,
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


def canonical_css() -> str:
    return """/* open-study-path:study-slides-theme version=2 */
.osp-slide{width:1280px;height:720px}.osp-grid{}.osp-compare{}.osp-diagram{}.osp-case{}.osp-steps{}.osp-challenge{}.osp-checklist{}.osp-prompt-grid{}.osp-summary-layout{}
"""


def canonical_js() -> str:
    return """/* open-study-path:study-slides-runtime version=2 */
import mermaid from \"/node_modules/mermaid/dist/mermaid.esm.min.mjs\";
window.__OPEN_STUDY_PATH_SLIDES_READY__=true;
"""


def valid_html(repository: str) -> str:
    specs = [
        ("title", "LO-1", "", "osp-title-layout", "Introdução clara para a aula e para o resultado que será desenvolvido."),
        ("map", "LO-1", "", "osp-grid", "Mapa da aula com definição, mecanismo e aplicação em uma sequência compreensível."),
        ("concept", "LO-1 LO-2", "Conteúdo essencial", "osp-compare", "Contraste entre os objetos centrais e suas responsabilidades no sistema."),
        ("diagram", "LO-1 LO-2", "Mapa visual", "osp-diagram", "Fluxo principal explicado com uma interpretação curta e um limite importante."),
        ("example", "LO-1 LO-2", "Exemplos trabalhados", "osp-case", "Exemplo completo que conecta situação, decisão, consequência e evidência verificável."),
        ("example", "LO-2", "Exemplos trabalhados", "osp-steps", "Segundo exemplo que mostra transferência do conceito para uma situação diferente."),
        ("misconception", "LO-2", "Erros comuns e como corrigir", "osp-compare", "Erro provável comparado com um critério melhor para orientar a decisão."),
        ("application", "LO-1 LO-2", "Prática guiada", "osp-challenge osp-checklist", "Desafio curto para classificar componentes, justificar a decisão e indicar evidência."),
        ("recap", "LO-1 LO-2", "Confira sem consultar", "osp-prompt-grid", "Perguntas de recuperação ativa para explicar o conceito sem consultar a aula."),
        ("summary", "LO-1 LO-2", "", "osp-summary-layout", "Síntese dos aprendizados e links atuais para aula, prática e avaliação."),
    ]
    sections = []
    for index, (role, outcomes, section, layout, text) in enumerate(specs, start=1):
        section_attr = f' data-lesson-section="{section}"' if section else ""
        mermaid = '<div class="osp-diagram mermaid">flowchart LR; A-->B</div><p class="osp-caption">Observe o fluxo e o limite.</p>' if role == "diagram" else ""
        sections.append(
            f'<section class="osp-slide" data-slide-role="{role}" data-outcome-ids="{outcomes}"{section_attr}>'
            f'<h2>Slide {index}</h2><div class="{layout}"><p>{text}</p>{mermaid}</div></section>'
        )
    return f"""<!doctype html>
<html lang="pt-BR"><head>
<meta name="open-study-path:topic-id" content="TOPIC-001">
<meta name="open-study-path:content-version" content="2">
<meta name="open-study-path:slide-theme" content="canonical-v2">
<link rel="stylesheet" href="slides.css">
</head><body><main>{''.join(sections)}</main>
<a href="https://github.com/{repository}/blob/HEAD/study/modules/TOPIC-001.md">Aula</a>
<script type="module" src="slides.js"></script></body></html>
"""


def fake_pdf(pages: int, source_digest: str, snapshot_digest: str, *, reportlab: bool = False) -> bytes:
    stream = BytesIO()
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=1280, height=720)
    producer = "ReportLab Generated PDF document" if reportlab else PDF_PRODUCER
    writer.add_metadata({
        "/Producer": producer,
        "/Creator": producer,
        "/Title": "TOPIC-001 study slides",
        "/Subject": (
            f"open-study-path-renderer:{RENDERER_ID};"
            f"source:{source_digest};snapshot:{snapshot_digest}"
        ),
        "/Keywords": "x" * 25000,
    })
    writer.write(stream)
    return stream.getvalue()


def build_valid_tree(root: Path, *, reportlab: bool = False) -> tuple[dict, str]:
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
    template_dir = root / "templates/study-slides"
    write(template_dir / "slides.css", canonical_css())
    write(template_dir / "slides.js", canonical_js())

    topic_dir = root / "study/slides/TOPIC-001"
    write(topic_dir / "index.html", valid_html(repository))
    write(topic_dir / "slides.css", canonical_css())
    write(topic_dir / "slides.js", canonical_js())
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
    snapshot_digest = "a" * 64
    pdf = fake_pdf(10, source_digest, snapshot_digest, reportlab=reportlab)
    write(topic_dir / "slides.pdf", pdf)
    meta = {
        "contract_version": 2,
        "topic_id": "TOPIC-001",
        "content_version": 2,
        "generated_at": "2026-07-30T12:00:00Z",
        "renderer": {"id": RENDERER_ID, "playwright": "test", "mermaid": "test", "pdf_lib": "test"},
        "slide_count": 10,
        "mermaid_count": 1,
        "outcome_ids": ["LO-1", "LO-2"],
        "source_sha256": source_hashes,
        "source_digest": source_digest,
        "rendered_snapshot_sha256": snapshot_digest,
        "pdf": {
            "pages": 10,
            "bytes": len(pdf),
            "sha256": file_sha256(topic_dir / "slides.pdf"),
            "producer": PDF_PRODUCER,
            "source_digest": source_digest,
            "rendered_snapshot_sha256": snapshot_digest,
        },
        "diagnostics": {"console_errors": [], "overflow_slides": [], "external_requests": []},
    }
    write(topic_dir / "slides.meta.json", json.dumps(meta))
    review = {
        "version": 2,
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
        "checks": {name: "passed" for name in [
            "lesson_fidelity", "outcome_coverage", "narrative_arc", "worked_example_quality",
            "summary_quality", "visual_variety", "visual_hierarchy", "mermaid_quality",
            "accessibility", "link_consistency",
        ]},
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
        assert any("canonical-v2 template unchanged" in error for error in errors)
        assert any("source hashes are stale" in error for error in errors)
        assert any("review source hash is stale" in error for error in errors)


def test_thin_deck_is_rejected() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, repository = build_valid_tree(root)
        html = root / "study/slides/TOPIC-001/index.html"
        content = valid_html(repository)
        content = content.replace('data-slide-role="application"', 'data-slide-role="concept"')
        html.write_text(content, encoding="utf-8")
        errors = validate_materialized_topic(root, repository, topic)
        assert any("missing required narrative role: application" in error for error in errors)


def test_reportlab_pdf_is_rejected_even_with_matching_sidecar() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, repository = build_valid_tree(root, reportlab=True)
        errors = validate_materialized_topic(root, repository, topic)
        assert any("not produced by the HTML slide renderer" in error for error in errors)


def main() -> None:
    tests = [
        test_valid_topic,
        test_stale_source_is_rejected,
        test_thin_deck_is_rejected,
        test_reportlab_pdf_is_rejected_even_with_matching_sidecar,
    ]
    for test in tests:
        test()
    print(f"Study-slide regression tests passed ({len(tests)} cases).")


if __name__ == "__main__":
    main()
