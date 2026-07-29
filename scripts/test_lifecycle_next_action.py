#!/usr/bin/env python3
"""Behavioral regression tests for lifecycle next-action resolution."""

from __future__ import annotations

from lifecycle_next_action import (
    EVALUATE_COMMAND_TEMPLATE,
    GENERATE_COMMAND,
    PUBLISH_COMMAND,
    publication_complete,
    resolve_next_action,
)


def instance(*, generated: bool) -> dict:
    return {"status": {"curriculum_generated": generated}}


def integrations(status: str = "not_started", success_at: str | None = None) -> dict:
    return {
        "sync": {
            "status": status,
            "last_success_at": success_at,
        }
    }


def test_generation_precedes_publication() -> None:
    action = resolve_next_action(instance(generated=False), integrations())
    assert action.phase == "generate"
    assert action.command == GENERATE_COMMAND


def test_agent_authored_deferral_cannot_skip_publication() -> None:
    # The agent may suggest "sem publicar tarefas ainda", but that wording is
    # not persisted lifecycle state and cannot authorize generate -> evaluate.
    action = resolve_next_action(instance(generated=True), integrations("not_started"))
    assert action.phase == "publish"
    assert action.command == PUBLISH_COMMAND
    assert "Avalie minhas respostas" not in action.command


def test_missing_integration_state_keeps_publication_pending() -> None:
    action = resolve_next_action(instance(generated=True), None)
    assert action.phase == "publish"
    assert action.command == PUBLISH_COMMAND


def test_failed_or_partial_publication_cannot_enable_evaluation() -> None:
    for status in ["failed", "blocked", "partial", "in_progress"]:
        action = resolve_next_action(instance(generated=True), integrations(status))
        assert action.phase == "publish", status
        assert action.command == PUBLISH_COMMAND, status


def test_success_requires_timestamp() -> None:
    assert publication_complete(integrations("success", None)) is False
    action = resolve_next_action(instance(generated=True), integrations("success", None))
    assert action.phase == "publish"


def test_evaluation_is_available_only_after_publication() -> None:
    state = integrations("success", "2026-07-28T22:00:00Z")
    action = resolve_next_action(
        instance(generated=True),
        state,
        lesson_title="Como os LLMs geram texto",
    )
    assert action.phase == "evaluate"
    assert action.command == EVALUATE_COMMAND_TEMPLATE.format(
        lesson_title="Como os LLMs geram texto"
    )


def main() -> None:
    test_generation_precedes_publication()
    test_agent_authored_deferral_cannot_skip_publication()
    test_missing_integration_state_keeps_publication_pending()
    test_failed_or_partial_publication_cannot_enable_evaluation()
    test_success_requires_timestamp()
    test_evaluation_is_available_only_after_publication()
    print("Lifecycle next-action behavioral regressions passed.")


if __name__ == "__main__":
    main()
