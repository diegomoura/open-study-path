#!/usr/bin/env python3
"""Validate semantic study-slide sources, review evidence and rendered PDFs."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from typing import Any, Mapping

import yaml
from pypdf import PdfReader

OUTCOME_ID = re.compile(r"^LO-[1-9][0-9]*$")
TOPIC_ID = re.compile(r"^TOPIC-[0-9]{3,}$")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
PDF_PAGE = re.compile(rb"/Type\s*/Page\b")
SLIDES_LINK_START = "<!-- open-study-path:slides-link:start -->"
SLIDES_LINK_END = "<!-- open-study-path:slides-link:end -->"
MIN_SLIDES = 8
MAX_SLIDES = 18
THEME_NAME = "canonical-v2"
RENDERER_ID = "open-study-path-html-v2"
PDF_PRODUCER = "Open Study Path HTML slide renderer v2"
CSS_MARKER = "open-study-path:study-slides-theme version=2"
JS_MARKER = "open-study-path:study-slides-runtime version=2"
REQUIRED_ROLES = (
    "title",
    "map",
    "diagram",
    "example",
    "misconception",
    "application",
    "summary",
)
TRACEABLE_ROLES = {"concept", "diagram", "example", "misconception", "application", "recap"}
LAYOUT_CLASSES = {
    "osp-title-layout",
    "osp-grid",
    "osp-compare",
    "osp-diagram",
    "osp-case",
    "osp-steps",
    "osp-challenge",
    "osp-checklist",
    "osp-prompt-grid",
    "osp-summary-layout",
}
REQUIRED_REVIEW_CHECKS = (
    "lesson_fidelity",
    "outcome_coverage",
    "narrative_arc",
    "worked_example_quality",
    "summary_quality",
    "visual_variety",
    "visual_hierarchy",
    "mermaid_quality",
    "accessibility",
    "link_consistency",
)
SOURCE_FILENAMES = ("index.html", "slides.css", "slides.js")


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing YAML frontmatter: {path}")
    try:
        _, raw, body = text.split("---", 2)
    except ValueError as exc:
        raise ValueError(f"malformed YAML frontmatter: {path}") from exc
    document = yaml.safe_load(raw)
    if not isinstance(document, dict):
        raise ValueError(f"frontmatter must be an object: {path}")
    return document, body


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def aggregate_source_sha256(paths: list[Path], root: Path) -> str:
    digest = sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_sha256(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def slides_enabled(instance: Mapping[str, Any]) -> bool:
    contract = _mapping(instance.get("study_slides"))
    return (
        contract.get("contract_version") == 1
        and contract.get("enabled") is True
        and contract.get("required_for_materialized_topics") is True
        and _text(contract.get("learner_format")) == "pdf"
        and _text(contract.get("html_visibility")) == "internal_only"
    )


class SlideHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.topic_id = ""
        self.content_version: int | None = None
        self.theme = ""
        self.slides: list[dict[str, Any]] = []
        self.mermaid_count = 0
        self.image_count = 0
        self.external_runtime_urls: list[str] = []
        self.stylesheet = ""
        self.script = ""
        self._slide_depth = 0
        self._current: dict[str, Any] | None = None
        self._heading_depth = 0

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {key: value or "" for key, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = self._attrs(attrs)
        classes = set(values.get("class", "").split())

        if tag == "meta":
            name = values.get("name")
            content = values.get("content", "")
            if name == "open-study-path:topic-id":
                self.topic_id = content
            elif name == "open-study-path:content-version":
                try:
                    self.content_version = int(content)
                except ValueError:
                    self.content_version = None
            elif name == "open-study-path:slide-theme":
                self.theme = content

        if tag == "link" and values.get("rel") == "stylesheet":
            self.stylesheet = values.get("href", "")
            if self.stylesheet.startswith(("http://", "https://", "//")):
                self.external_runtime_urls.append(self.stylesheet)

        if tag == "script" and values.get("src"):
            self.script = values["src"]
            if self.script.startswith(("http://", "https://", "//")):
                self.external_runtime_urls.append(self.script)

        if tag == "img":
            self.image_count += 1

        if tag == "section" and "osp-slide" in classes:
            outcomes = [value for value in values.get("data-outcome-ids", "").split() if value]
            self._current = {
                "outcomes": outcomes,
                "heading": "",
                "text": [],
                "role": values.get("data-slide-role", ""),
                "lesson_section": values.get("data-lesson-section", ""),
                "layouts": set(classes & LAYOUT_CLASSES),
                "has_mermaid": False,
                "has_caption": False,
            }
            self.slides.append(self._current)
            self._slide_depth = 1
            return

        if self._slide_depth and self._current is not None:
            self._slide_depth += 1
            self._current["layouts"].update(classes & LAYOUT_CLASSES)
            if "mermaid" in classes:
                self.mermaid_count += 1
                self._current["has_mermaid"] = True
            if "osp-caption" in classes:
                self._current["has_caption"] = True
            if tag in {"h1", "h2"}:
                self._heading_depth = 1
        elif "mermaid" in classes:
            self.mermaid_count += 1

    def handle_endtag(self, tag: str) -> None:
        if not self._slide_depth:
            return
        if self._heading_depth:
            self._heading_depth -= 1
        self._slide_depth -= 1
        if self._slide_depth == 0:
            self._current = None

    def handle_data(self, data: str) -> None:
        if not self._current:
            return
        text = " ".join(data.split())
        if not text:
            return
        self._current["text"].append(text)
        if self._heading_depth:
            self._current["heading"] = f"{self._current['heading']} {text}".strip()


def parse_slide_html(path: Path) -> SlideHTMLParser:
    parser = SlideHTMLParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def expected_pdf_url(repository: str, pdf_path: str) -> str:
    return f"https://github.com/{repository}/raw/HEAD/{pdf_path}"


def pdf_info(path: Path) -> tuple[int, int, str, bytes, list[str]]:
    errors: list[str] = []
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        errors.append(f"{path} does not start with a PDF header")
    if b"%%EOF" not in data[-4096:]:
        errors.append(f"{path} does not contain a final PDF marker")
    pages = len(PDF_PAGE.findall(data))
    if pages <= 0:
        errors.append(f"{path} does not contain any PDF pages")
    if len(data) < max(4096, pages * 2048):
        errors.append(f"{path} is unexpectedly small for {pages} rendered slides")
    return pages, len(data), sha256(data).hexdigest(), data, errors


def pdf_metadata(path: Path) -> tuple[dict[str, str], list[str]]:
    try:
        reader = PdfReader(str(path))
        metadata = reader.metadata or {}
        return {
            "producer": _text(metadata.get("/Producer")),
            "creator": _text(metadata.get("/Creator")),
            "title": _text(metadata.get("/Title")),
            "subject": _text(metadata.get("/Subject")),
        }, []
    except Exception as exc:
        return {}, [f"{path} PDF metadata cannot be read: {exc}"]


def _validate_assets(root: Path, topic_id: str, source_paths: list[Path]) -> list[str]:
    errors: list[str] = []
    template_dir = root / "templates" / "study-slides"
    css_template = template_dir / "slides.css"
    js_template = template_dir / "slides.js"
    css_path, js_path = source_paths[1], source_paths[2]
    if CSS_MARKER not in css_path.read_text(encoding="utf-8"):
        errors.append(f"{topic_id} slide CSS is missing the canonical-v2 theme marker")
    if JS_MARKER not in js_path.read_text(encoding="utf-8"):
        errors.append(f"{topic_id} slide runtime is missing the canonical-v2 marker")
    if css_template.is_file() and css_path.read_bytes() != css_template.read_bytes():
        errors.append(f"{topic_id} slide CSS must use the canonical-v2 template unchanged")
    if js_template.is_file() and js_path.read_bytes() != js_template.read_bytes():
        errors.append(f"{topic_id} slide runtime must use the canonical-v2 template unchanged")
    return errors


def _validate_deck_structure(topic_id: str, parser: SlideHTMLParser) -> list[str]:
    errors: list[str] = []
    if parser.theme != THEME_NAME:
        errors.append(f"{topic_id} slide HTML must declare theme {THEME_NAME}")
    if not MIN_SLIDES <= len(parser.slides) <= MAX_SLIDES:
        errors.append(f"{topic_id} must contain between {MIN_SLIDES} and {MAX_SLIDES} slides")
    if parser.mermaid_count < 1:
        errors.append(f"{topic_id} slide deck must contain at least one Mermaid diagram")
    roles = [_text(slide.get("role")) for slide in parser.slides]
    for role in REQUIRED_ROLES:
        if role not in roles:
            errors.append(f"{topic_id} slide deck is missing required narrative role: {role}")
    if roles:
        if roles[0] != "title":
            errors.append(f"{topic_id} first slide role must be title")
        if roles[-1] != "summary":
            errors.append(f"{topic_id} final slide role must be summary")
        if "map" in roles and roles.index("map") > 2:
            errors.append(f"{topic_id} map slide must appear within the first three slides")
        if "diagram" in roles and "application" in roles and roles.index("diagram") > roles.index("application"):
            errors.append(f"{topic_id} diagram must appear before learner application")
        if "example" in roles and "application" in roles and roles.index("example") > roles.index("application"):
            errors.append(f"{topic_id} worked example must appear before learner application")
    layout_types: set[str] = set()
    for slide in parser.slides:
        layout_types.update(slide.get("layouts", set()))
    if len(layout_types) < 5:
        errors.append(
            f"{topic_id} slide deck must use at least five canonical visual layout types; got {sorted(layout_types)}"
        )
    return errors


def validate_slide_review(
    root: Path,
    topic: Mapping[str, Any],
    review: Mapping[str, Any],
    lesson_path: Path,
    source_paths: list[Path],
) -> list[str]:
    errors: list[str] = []
    topic_id = _text(topic.get("id"))
    content_version = topic.get("content_version")
    outcomes = [
        _text(_mapping(value).get("id"))
        for value in _list(topic.get("learning_outcomes"))
        if _text(_mapping(value).get("id"))
    ]

    if review.get("version") != 2:
        errors.append(f"{topic_id} slide review must use version 2")
    if _text(review.get("topic_id")) != topic_id:
        errors.append(f"{topic_id} slide review topic_id mismatch")
    if review.get("content_version") != content_version:
        errors.append(f"{topic_id} slide review is stale for content_version {content_version}")
    if not _text(review.get("reviewed_at")):
        errors.append(f"{topic_id} slide review is missing reviewed_at")
    if _text(review.get("reviewer_role")) != "study_slides_reviewer":
        errors.append(f"{topic_id} slide review must use study_slides_reviewer")
    if _text(review.get("review_mode")) != "independent_pass":
        errors.append(f"{topic_id} slide review must use independent_pass")
    if _text(review.get("status")) != "approved":
        errors.append(f"{topic_id} slide review status must be approved")

    checks = _mapping(review.get("checks"))
    for check in REQUIRED_REVIEW_CHECKS:
        if _text(checks.get(check)) != "passed":
            errors.append(f"{topic_id} slide review check must pass: {check}")

    lesson_relative = lesson_path.relative_to(root).as_posix()
    if _text(review.get("source_lesson")) != lesson_relative:
        errors.append(f"{topic_id} slide review source_lesson mismatch")
    if _text(review.get("source_lesson_sha256")) != file_sha256(lesson_path):
        errors.append(f"{topic_id} slide review lesson hash is stale")

    index_relative = source_paths[0].relative_to(root).as_posix()
    if _text(review.get("slides_source")) != index_relative:
        errors.append(f"{topic_id} slide review slides_source mismatch")
    expected_source_hash = aggregate_source_sha256(source_paths, root)
    if _text(review.get("slides_source_sha256")) != expected_source_hash:
        errors.append(f"{topic_id} slide review source hash is stale")

    reviewed_outcomes = [_text(value) for value in _list(review.get("outcomes_reviewed")) if _text(value)]
    if reviewed_outcomes != outcomes:
        errors.append(f"{topic_id} slide review outcomes mismatch: expected {outcomes}, got {reviewed_outcomes}")
    if _list(review.get("blocking_findings")):
        errors.append(f"{topic_id} slide review has unresolved blocking findings")
    return errors


def validate_materialized_topic(root: Path, repository: str, topic: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    topic_id = _text(topic.get("id"))
    content_version = topic.get("content_version")
    if not TOPIC_ID.fullmatch(topic_id):
        return [f"invalid topic id for study slides: {topic_id or '<missing>'}"]

    slides_html = _text(topic.get("slides"))
    slides_pdf = _text(topic.get("slides_pdf"))
    slides_review = _text(topic.get("slides_review"))
    expected_dir = f"study/slides/{topic_id}"
    expected_paths = {
        "slides": f"{expected_dir}/index.html",
        "slides_pdf": f"{expected_dir}/slides.pdf",
        "slides_review": f"state/slide-reviews/{topic_id}.yml",
    }
    for key, expected in expected_paths.items():
        if _text(topic.get(key)) != expected:
            errors.append(f"{topic_id} {key} must be {expected}")

    source_paths = [root / expected_dir / name for name in SOURCE_FILENAMES]
    pdf_path = root / slides_pdf
    meta_path = root / expected_dir / "slides.meta.json"
    review_path = root / slides_review
    lesson_path = root / _text(topic.get("module"))
    required_paths = [*source_paths, pdf_path, meta_path, review_path, lesson_path]
    for path in required_paths:
        if not path.is_file():
            errors.append(f"{topic_id} is missing study-slide artifact: {path.relative_to(root)}")
    if not all(path.is_file() for path in required_paths):
        return errors

    parser = parse_slide_html(source_paths[0])
    if parser.topic_id != topic_id:
        errors.append(f"{topic_id} slide HTML topic metadata mismatch")
    if parser.content_version != content_version:
        errors.append(f"{topic_id} slide HTML content version mismatch")
    if parser.stylesheet != "slides.css":
        errors.append(f"{topic_id} slide HTML must load slides.css locally")
    if parser.script != "slides.js":
        errors.append(f"{topic_id} slide HTML must load slides.js locally")
    if parser.external_runtime_urls:
        errors.append(f"{topic_id} slide HTML uses external runtime URLs: {parser.external_runtime_urls}")
    if parser.image_count:
        errors.append(f"{topic_id} slide HTML must not contain generated raster images")
    errors.extend(_validate_assets(root, topic_id, source_paths))
    errors.extend(_validate_deck_structure(topic_id, parser))

    topic_outcomes = [
        _text(_mapping(value).get("id"))
        for value in _list(topic.get("learning_outcomes"))
        if _text(_mapping(value).get("id"))
    ]
    represented: list[str] = []
    for index, slide in enumerate(parser.slides, start=1):
        heading = _text(slide.get("heading"))
        role = _text(slide.get("role"))
        if not heading:
            errors.append(f"{topic_id} slide {index} is missing an h1 or h2 heading")
        words = re.findall(r"\b[\wÀ-ÿ'-]+\b", " ".join(slide.get("text", [])))
        if len(words) > 120:
            errors.append(f"{topic_id} slide {index} exceeds 120 words")
        if role not in {"title", "summary"} and len(words) < 10:
            errors.append(f"{topic_id} slide {index} is too thin to carry explanatory value")
        if role in TRACEABLE_ROLES and not _text(slide.get("lesson_section")):
            errors.append(f"{topic_id} slide {index} role {role} must cite data-lesson-section")
        if role == "diagram" and not slide.get("has_mermaid"):
            errors.append(f"{topic_id} diagram slide {index} must contain Mermaid")
        if role == "diagram" and not slide.get("has_caption"):
            errors.append(f"{topic_id} diagram slide {index} must include an explanatory caption")
        outcomes = [_text(value) for value in _list(slide.get("outcomes")) if _text(value)]
        if not outcomes:
            errors.append(f"{topic_id} slide {index} must declare data-outcome-ids")
        for outcome in outcomes:
            if outcome not in topic_outcomes:
                errors.append(f"{topic_id} slide {index} references unknown outcome {outcome}")
            if outcome not in represented:
                represented.append(outcome)
    if represented != topic_outcomes:
        errors.append(f"{topic_id} slide outcome coverage mismatch: expected {topic_outcomes}, got {represented}")

    lesson_text = lesson_path.read_text(encoding="utf-8")
    expected_url = expected_pdf_url(repository, slides_pdf)
    if lesson_text.count(SLIDES_LINK_START) != 1 or lesson_text.count(SLIDES_LINK_END) != 1:
        errors.append(f"{topic_id} module must contain one delimited slides PDF link block")
    if expected_url not in lesson_text:
        errors.append(f"{topic_id} module is missing the direct slides PDF URL")
    if slides_html in lesson_text or "index.html" in lesson_text:
        errors.append(f"{topic_id} module must not expose the slide HTML source")

    try:
        meta = _mapping(json.loads(meta_path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError) as exc:
        errors.append(f"{topic_id} has invalid slides.meta.json: {exc}")
        meta = {}

    pages, pdf_bytes, pdf_hash, pdf_data, pdf_errors = pdf_info(pdf_path)
    errors.extend(pdf_errors)
    if meta.get("contract_version") != 2:
        errors.append(f"{topic_id} slide metadata must use contract_version 2")
    renderer = _mapping(meta.get("renderer"))
    if _text(renderer.get("id")) != RENDERER_ID:
        errors.append(f"{topic_id} slide metadata renderer id mismatch")
    if _text(meta.get("topic_id")) != topic_id:
        errors.append(f"{topic_id} slide metadata topic mismatch")
    if meta.get("content_version") != content_version:
        errors.append(f"{topic_id} slide metadata content version mismatch")
    if meta.get("slide_count") != len(parser.slides):
        errors.append(f"{topic_id} slide metadata count mismatch")
    if meta.get("mermaid_count") != parser.mermaid_count:
        errors.append(f"{topic_id} slide metadata Mermaid count mismatch")
    if _list(meta.get("outcome_ids")) != topic_outcomes:
        errors.append(f"{topic_id} slide metadata outcome list mismatch")

    current_sources = {
        path.relative_to(root).as_posix(): file_sha256(path)
        for path in [*source_paths, lesson_path]
    }
    if dict(_mapping(meta.get("source_sha256"))) != current_sources:
        errors.append(f"{topic_id} slide metadata source hashes are stale")
    source_digest = aggregate_source_sha256([*source_paths, lesson_path], root)
    if _text(meta.get("source_digest")) != source_digest:
        errors.append(f"{topic_id} slide metadata source digest is stale")
    snapshot_digest = _text(meta.get("rendered_snapshot_sha256"))
    if not SHA256_HEX.fullmatch(snapshot_digest):
        errors.append(f"{topic_id} slide metadata rendered snapshot digest is invalid")

    pdf_meta = _mapping(meta.get("pdf"))
    if pdf_meta.get("pages") != pages or pages != len(parser.slides):
        errors.append(f"{topic_id} PDF page count must match slide count")
    if pdf_meta.get("bytes") != pdf_bytes:
        errors.append(f"{topic_id} PDF byte count metadata is stale")
    if _text(pdf_meta.get("sha256")) != pdf_hash:
        errors.append(f"{topic_id} PDF hash metadata is stale")
    if _text(pdf_meta.get("producer")) != PDF_PRODUCER:
        errors.append(f"{topic_id} PDF producer metadata mismatch")
    if _text(pdf_meta.get("source_digest")) != source_digest:
        errors.append(f"{topic_id} PDF source provenance mismatch")
    if _text(pdf_meta.get("rendered_snapshot_sha256")) != snapshot_digest:
        errors.append(f"{topic_id} PDF rendered-snapshot provenance mismatch")
    embedded, embedded_errors = pdf_metadata(pdf_path)
    errors.extend(embedded_errors)
    expected_subject = (
        f"open-study-path-renderer:{RENDERER_ID};"
        f"source:{source_digest};snapshot:{snapshot_digest}"
    )
    if embedded:
        if embedded.get("title") != f"{topic_id} study slides":
            errors.append(f"{topic_id} committed PDF title provenance mismatch")
        if embedded.get("subject") != expected_subject:
            errors.append(f"{topic_id} committed PDF source or rendered-snapshot provenance mismatch")
        if "reportlab" in embedded.get("producer", "").lower():
            errors.append(f"{topic_id} committed PDF was not produced by the HTML slide renderer")

    diagnostics = _mapping(meta.get("diagnostics"))
    if diagnostics.get("console_errors") != []:
        errors.append(f"{topic_id} render metadata contains console errors")
    if diagnostics.get("overflow_slides") != []:
        errors.append(f"{topic_id} render metadata contains overflowing slides")
    if diagnostics.get("external_requests") != []:
        errors.append(f"{topic_id} render metadata contains external requests")

    review = _mapping(load_yaml(review_path))
    errors.extend(validate_slide_review(root, topic, review, lesson_path, source_paths))
    return errors


def template_contract_errors(root: Path) -> list[str]:
    errors: list[str] = []
    required = [
        root / "docs/study-slides.md",
        root / "instructions/37-review-study-slides.md",
        root / "templates/study-slides/index.html",
        root / "templates/study-slides/slides.css",
        root / "templates/study-slides/slides.js",
        root / "templates/slide-review.yml",
        root / "scripts/render_study_slides.mjs",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing reusable study-slide file: {path.relative_to(root)}")
    if errors:
        return errors

    topic, _ = parse_frontmatter(root / "templates/topic.md")
    expected_topic_paths = {
        "slides": "study/slides/TOPIC-000/index.html",
        "slides_pdf": "study/slides/TOPIC-000/slides.pdf",
        "slides_review": "state/slide-reviews/TOPIC-000.yml",
    }
    for key, value in expected_topic_paths.items():
        if _text(topic.get(key)) != value:
            errors.append(f"templates/topic.md {key} must be {value}")

    module = (root / "templates/module.md").read_text(encoding="utf-8")
    for term in [SLIDES_LINK_START, SLIDES_LINK_END, "/raw/HEAD/", "slides.pdf"]:
        if term not in module:
            errors.append(f"templates/module.md is missing slide link contract term: {term}")
    if "index.html" in module:
        errors.append("templates/module.md must not expose slide HTML")

    parser = parse_slide_html(root / "templates/study-slides/index.html")
    errors.extend(_validate_deck_structure("TOPIC-000", parser))
    if parser.topic_id != "TOPIC-000" or parser.content_version != 1:
        errors.append("study-slide HTML template must define topic and content-version metadata")
    if parser.image_count or parser.external_runtime_urls:
        errors.append("study-slide HTML template must not use images or external runtimes")

    css = (root / "templates/study-slides/slides.css").read_text(encoding="utf-8")
    js = (root / "templates/study-slides/slides.js").read_text(encoding="utf-8")
    if CSS_MARKER not in css:
        errors.append("study-slide CSS template must declare canonical-v2 marker")
    if JS_MARKER not in js:
        errors.append("study-slide JS template must declare canonical-v2 marker")

    review = _mapping(load_yaml(root / "templates/slide-review.yml"))
    if review.get("version") != 2:
        errors.append("templates/slide-review.yml must use version 2")
    if _text(review.get("reviewer_role")) != "study_slides_reviewer":
        errors.append("templates/slide-review.yml must define study_slides_reviewer")
    for check in REQUIRED_REVIEW_CHECKS:
        if check not in _mapping(review.get("checks")):
            errors.append(f"templates/slide-review.yml is missing check: {check}")
    return errors


def validate_repository(root: Path) -> ValidationResult:
    errors = template_contract_errors(root)
    instance_path = root / ".open-study-path" / "instance.yml"
    if not instance_path.is_file():
        return ValidationResult(tuple(errors))
    instance = _mapping(load_yaml(instance_path))
    if not slides_enabled(instance):
        return ValidationResult(tuple(errors))

    repository = _text(instance.get("repository"))
    if not repository or repository == "OWNER/REPOSITORY":
        errors.append("study-slide validation requires the exact instance repository")
        return ValidationResult(tuple(errors))

    topics_dir = root / "study" / "topics"
    if not topics_dir.is_dir():
        return ValidationResult(tuple(errors))
    for topic_path in sorted(topics_dir.glob("TOPIC-*.md")):
        try:
            topic, _ = parse_frontmatter(topic_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        topic_id = _text(topic.get("id"))
        if _text(topic.get("content_status")) != "materialized":
            deck_dir = root / "study" / "slides" / topic_id
            review_path = root / "state" / "slide-reviews" / f"{topic_id}.yml"
            if deck_dir.exists() or review_path.exists():
                errors.append(f"planned topic {topic_id} must not have generated study slides")
            continue
        errors.extend(validate_materialized_topic(root, repository, topic))
    return ValidationResult(tuple(errors))
