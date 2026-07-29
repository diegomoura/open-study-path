#!/usr/bin/env python3
"""Synchronize bounded learner-facing practice links from durable integration state."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOPICS = Path("study/topics")
START_MARKER = "<!-- open-study-path:practice-links:start -->"
END_MARKER = "<!-- open-study-path:practice-links:end -->"
PRACTICE_HEADING = "## Pratique e revise"
LINK_BULLET = re.compile(r"^- \[[^\n]+\]\([^\n]+\)\s*$")


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError(f"missing frontmatter: {path}")
    try:
        _, raw, body = content.split("---", 2)
    except ValueError as exc:
        raise ValueError(f"malformed frontmatter: {path}") from exc
    metadata = yaml.safe_load(raw)
    if not isinstance(metadata, dict):
        raise ValueError(f"frontmatter must be an object: {path}")
    return metadata, body


def load_integration_state(root: Path) -> dict[str, Any]:
    path = root / "state/integrations.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def current_quizlet_resource(
    state: dict[str, Any], topic_id: str, content_version: Any
) -> dict[str, Any] | None:
    resources = state.get("resources", [])
    if not isinstance(resources, list):
        return None

    matches: list[dict[str, Any]] = []
    for resource in resources:
        if not isinstance(resource, dict):
            continue
        if (
            resource.get("capability") == "formative_practice"
            and resource.get("provider") == "quizlet"
            and resource.get("external_type") == "set"
            and resource.get("topic") == topic_id
            and str(resource.get("content_version")) == str(content_version)
            and resource.get("status") == "success"
            and isinstance(resource.get("url"), str)
            and resource["url"].startswith("https://")
        ):
            matches.append(resource)

    if not matches:
        return None

    matches.sort(
        key=lambda item: (
            str(item.get("reconciled_at", "")),
            str(item.get("external_id", "")),
        )
    )
    return matches[-1]


def relative_link(root: Path, module_path: Path, target: str) -> str:
    absolute = root / target
    return os.path.relpath(absolute, module_path.parent).replace(os.sep, "/")


def render_practice_block(
    root: Path,
    module_path: Path,
    metadata: dict[str, Any],
    quizlet: dict[str, Any] | None,
) -> str:
    study_value = metadata.get("flashcards_study")
    tsv_value = metadata.get("flashcards")
    if not isinstance(study_value, str) or not isinstance(tsv_value, str):
        raise ValueError(f"topic {metadata.get('id')} does not declare both flashcard formats")

    lines = [START_MARKER]
    if quizlet is not None:
        lines.append(f"- [Praticar no Quizlet]({quizlet['url']})")
    lines.extend(
        [
            f"- [Estudar os flashcards no GitHub]({relative_link(root, module_path, study_value)})",
            f"- [Baixar ou importar o TSV]({relative_link(root, module_path, tsv_value)})",
            END_MARKER,
        ]
    )
    return "\n".join(lines)


def practice_section_bounds(body: str) -> tuple[int, int, int]:
    heading = re.search(r"^## Pratique e revise\s*$", body, re.MULTILINE)
    if heading is None:
        raise ValueError(f"missing section: {PRACTICE_HEADING}")
    next_heading = re.search(r"^##\s+", body[heading.end() :], re.MULTILINE)
    section_end = heading.end() + (next_heading.start() if next_heading else len(body[heading.end() :]))
    return heading.start(), heading.end(), section_end


def strip_unmarked_practice_links(body: str) -> str:
    _, section_start, section_end = practice_section_bounds(body)
    section = body[section_start:section_end]
    lines = section.splitlines()
    inside_markers = False
    kept: list[str] = []
    for line in lines:
        if line.strip() == START_MARKER:
            inside_markers = True
            kept.append(line)
            continue
        if line.strip() == END_MARKER:
            inside_markers = False
            kept.append(line)
            continue
        if not inside_markers and LINK_BULLET.match(line.strip()):
            continue
        kept.append(line)
    normalized = "\n".join(kept).strip("\n")
    return body[:section_start] + "\n\n" + normalized + "\n\n" + body[section_end:].lstrip("\n")


def replace_practice_block(body: str, block: str) -> str:
    start_count = body.count(START_MARKER)
    end_count = body.count(END_MARKER)
    if start_count != end_count or start_count > 1:
        raise ValueError("practice-link markers must appear exactly once as a pair")

    if start_count == 1:
        start = body.index(START_MARKER)
        end = body.index(END_MARKER, start) + len(END_MARKER)
        updated = body[:start] + block + body[end:]
        return strip_unmarked_practice_links(updated)

    _, section_start, section_end = practice_section_bounds(body)
    section = body[section_start:section_end]
    preserved_lines = [line for line in section.splitlines() if not LINK_BULLET.match(line.strip())]
    preserved = "\n".join(preserved_lines).strip("\n")
    new_section = "\n\n" + block
    if preserved.strip():
        new_section += "\n\n" + preserved.strip()
    new_section += "\n\n"
    return body[:section_start] + new_section + body[section_end:].lstrip("\n")


def synchronized_module_text(
    root: Path,
    module_path: Path,
    metadata: dict[str, Any],
    state: dict[str, Any],
) -> str:
    body = module_path.read_text(encoding="utf-8")
    quizlet = current_quizlet_resource(
        state, str(metadata.get("id")), metadata.get("content_version")
    )
    block = render_practice_block(root, module_path, metadata, quizlet)
    return replace_practice_block(body, block)


def sync_repository(root: Path, check: bool = False) -> list[Path]:
    state = load_integration_state(root)
    changed: list[Path] = []
    topics_dir = root / TOPICS
    if not topics_dir.is_dir():
        return changed

    for topic_path in sorted(topics_dir.glob("TOPIC-*.md")):
        metadata, _ = parse_frontmatter(topic_path)
        if metadata.get("content_status") != "materialized":
            continue
        if metadata.get("flashcards") is None and metadata.get("flashcards_study") is None:
            continue
        module_value = metadata.get("module")
        if not isinstance(module_value, str):
            raise ValueError(f"materialized topic {metadata.get('id')} has no module")
        module_path = root / module_value
        updated = synchronized_module_text(root, module_path, metadata, state)
        current = module_path.read_text(encoding="utf-8")
        if updated != current:
            changed.append(module_path)
            if not check:
                module_path.write_text(updated, encoding="utf-8")

    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when synchronization would change files")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    try:
        changed = sync_repository(args.root.resolve(), check=args.check)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check and changed:
        for path in changed:
            print(f"ERROR: practice links are out of sync: {path.relative_to(args.root.resolve())}", file=sys.stderr)
        return 1

    if changed:
        print(f"Synchronized practice links in {len(changed)} module(s).")
    else:
        print("Practice links already synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
