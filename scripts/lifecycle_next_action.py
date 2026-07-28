#!/usr/bin/env python3
"""Resolve the next learner-facing lifecycle command from persisted state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

GENERATE_COMMAND = "Crie minha trilha de estudos."
PUBLISH_COMMAND = "Organize minha trilha nas ferramentas que escolhemos."
EVALUATE_COMMAND_TEMPLATE = "Terminei {lesson_title}. Avalie minhas respostas."
PUBLISHED_SYNC_STATUSES = {"success", "succeeded", "completed"}


@dataclass(frozen=True)
class NextAction:
    phase: str
    command: str
    reason: str


def _status(document: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(document, Mapping):
        return {}
    value = document.get("status", {})
    return value if isinstance(value, Mapping) else {}


def publication_complete(integrations: Mapping[str, Any] | None) -> bool:
    if not isinstance(integrations, Mapping):
        return False
    sync = integrations.get("sync", {})
    if not isinstance(sync, Mapping):
        return False
    status = str(sync.get("status", "")).strip().lower()
    return status in PUBLISHED_SYNC_STATUSES and bool(sync.get("last_success_at"))


def resolve_next_action(
    instance: Mapping[str, Any] | None,
    integrations: Mapping[str, Any] | None,
    *,
    lesson_title: str = "<título da aula>",
) -> NextAction:
    """Return the only normal next phase and command allowed by persisted state."""

    status = _status(instance)

    if status.get("curriculum_generated") is not True:
        return NextAction(
            phase="generate",
            command=GENERATE_COMMAND,
            reason="curriculum_not_generated",
        )

    if not publication_complete(integrations):
        return NextAction(
            phase="publish",
            command=PUBLISH_COMMAND,
            reason="publication_pending",
        )

    title = lesson_title.strip() or "<título da aula>"
    return NextAction(
        phase="evaluate",
        command=EVALUATE_COMMAND_TEMPLATE.format(lesson_title=title),
        reason="publication_complete",
    )
