#!/usr/bin/env python3
"""Regression tests for deterministic practice-link synchronization."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from sync_practice_links import END_MARKER, START_MARKER, sync_repository


def write_fixture(root: Path, content_version: int, quizlet_version: int | None) -> None:
    (root / "study/topics").mkdir(parents=True, exist_ok=True)
    (root / "study/modules").mkdir(parents=True, exist_ok=True)
    (root / "study/flashcards").mkdir(parents=True, exist_ok=True)
    (root / "state").mkdir(parents=True, exist_ok=True)

    (root / "study/topics/TOPIC-001.md").write_text(
        f"""---
id: TOPIC-001
title: Aula de teste
content_status: materialized
content_version: {content_version}
module: study/modules/TOPIC-001.md
flashcards: study/flashcards/TOPIC-001.tsv
flashcards_study: study/flashcards/TOPIC-001.md
---

# TOPIC-001 — Aula de teste
""",
        encoding="utf-8",
    )
    (root / "study/modules/TOPIC-001.md").write_text(
        """# Aula de teste

## Pratique e revise

- [Estudar os flashcards no GitHub](../flashcards/TOPIC-001.md)
- [Baixar ou importar o TSV](../flashcards/TOPIC-001.tsv)

Os flashcards ajudam a praticar; a etapa é concluída pela avaliação.

## Avaliação

Continue.
""",
        encoding="utf-8",
    )
    (root / "study/flashcards/TOPIC-001.md").write_text("cards\n", encoding="utf-8")
    (root / "study/flashcards/TOPIC-001.tsv").write_text("Front\tBack\tTags\n", encoding="utf-8")

    resources = []
    if quizlet_version is not None:
        resources.append(
            {
                "capability": "formative_practice",
                "provider": "quizlet",
                "external_type": "set",
                "external_id": f"set-{quizlet_version}",
                "topic": "TOPIC-001",
                "content_version": quizlet_version,
                "url": f"https://quizlet.example/topic-001-v{quizlet_version}",
                "status": "success",
                "reconciled_at": "2026-07-29T12:00:00Z",
            }
        )
    (root / "state/integrations.json").write_text(
        json.dumps({"resources": resources}), encoding="utf-8"
    )


def assert_current_quizlet_is_added() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_fixture(root, content_version=1, quizlet_version=1)
        changed = sync_repository(root)
        assert len(changed) == 1
        body = (root / "study/modules/TOPIC-001.md").read_text(encoding="utf-8")
        assert body.count(START_MARKER) == 1
        assert body.count(END_MARKER) == 1
        assert "[Praticar no Quizlet](https://quizlet.example/topic-001-v1)" in body
        assert "[Estudar os flashcards no GitHub](../flashcards/TOPIC-001.md)" in body
        assert "[Baixar ou importar o TSV](../flashcards/TOPIC-001.tsv)" in body
        assert sync_repository(root, check=True) == []


def assert_old_quizlet_is_not_linked() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_fixture(root, content_version=2, quizlet_version=1)
        sync_repository(root)
        body = (root / "study/modules/TOPIC-001.md").read_text(encoding="utf-8")
        assert "Praticar no Quizlet" not in body
        assert body.count(START_MARKER) == 1
        assert body.count(END_MARKER) == 1


def assert_changed_version_replaces_external_link_only() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_fixture(root, content_version=1, quizlet_version=1)
        sync_repository(root)
        module_path = root / "study/modules/TOPIC-001.md"
        original = module_path.read_text(encoding="utf-8")

        topic_path = root / "study/topics/TOPIC-001.md"
        topic_path.write_text(
            topic_path.read_text(encoding="utf-8").replace("content_version: 1", "content_version: 2"),
            encoding="utf-8",
        )
        state = {
            "resources": [
                {
                    "capability": "formative_practice",
                    "provider": "quizlet",
                    "external_type": "set",
                    "external_id": "set-2",
                    "topic": "TOPIC-001",
                    "content_version": 2,
                    "url": "https://quizlet.example/topic-001-v2",
                    "status": "success",
                    "reconciled_at": "2026-07-29T13:00:00Z",
                }
            ]
        }
        (root / "state/integrations.json").write_text(json.dumps(state), encoding="utf-8")
        sync_repository(root)
        updated = module_path.read_text(encoding="utf-8")

        assert "topic-001-v1" not in updated
        assert "topic-001-v2" in updated
        original_outside = original.split(START_MARKER, 1)[0] + original.split(END_MARKER, 1)[1]
        updated_outside = updated.split(START_MARKER, 1)[0] + updated.split(END_MARKER, 1)[1]
        assert original_outside == updated_outside


def main() -> None:
    assert_current_quizlet_is_added()
    assert_old_quizlet_is_not_linked()
    assert_changed_version_replaces_external_link_only()
    print("Practice-link synchronization regressions passed.")


if __name__ == "__main__":
    main()
