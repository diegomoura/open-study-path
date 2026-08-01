#!/usr/bin/env python3
"""Behavioral regressions for active integration resolution."""

from __future__ import annotations

from integration_resolution import validate_documents


FIXED_PLAN = """
# Ferramentas que podem ajudar nesta trilha

- routine mode: fixed_calendar

### Trello
- provider: trello
- decision: selected
- preflight: required_for_selected_publication

### Google Calendar
- provider: google_calendar
- decision: selected
- preflight: optional_current_action
"""

FLEXIBLE_PLAN = """
# Ferramentas que podem ajudar nesta trilha

- routine mode: flexible_reminders

### Trello
- provider: trello
- decision: selected
- preflight: required_for_selected_publication

### Todoist
- provider: todoist
- decision: selected
- preflight: optional_current_action
"""

NO_EXTERNAL_PLAN = """
# Ferramentas que podem ajudar nesta trilha

- account_connections: no_external_accounts
- routine mode: none

### GitHub Issues
- provider: github_issues
- decision: selected
- preflight: required_for_selected_publication
- connection-offer eligibility: not_enabled
"""


def config(mode: str = "fixed_calendar") -> dict:
    fixed = mode == "fixed_calendar"
    flexible = mode == "flexible_reminders"
    return {
        "integration_preferences": {
            "experience": "guided_recommendations",
            "account_connections": "ask_per_provider",
            "already_uses": [],
            "willing_to_connect": [],
            "routine": {"mode": mode, "details": "segunda às 19h, 45 minutos, America/Sao_Paulo"},
            "notes": None,
        },
        "integrations": {
            "task_manager": {"provider": "trello"},
            "reminders": {
                "provider": "todoist" if flexible else "calendar" if fixed else "none",
                "enabled": "enabled" if fixed or flexible else "disabled",
            },
            "calendar": {
                "provider": "google_calendar" if fixed else "none",
                "enabled": "enabled" if fixed else "disabled",
            },
            "notifications": {"provider": "chat", "email_enabled": False},
        },
    }


def untouched_config(task_provider: str = "auto") -> dict:
    return {
        "integration_preferences": {
            "experience": "guided_recommendations",
            "account_connections": "ask_per_provider",
            "already_uses": [],
            "willing_to_connect": [],
            "routine": {"mode": "decide_later", "details": None},
            "notes": None,
        },
        "integrations": {
            "task_manager": {"provider": task_provider},
            "reminders": {"provider": "none", "enabled": "disabled"},
            "calendar": {"provider": "none", "enabled": "disabled"},
            "notifications": {"provider": "chat", "email_enabled": False},
        },
    }


def untouched_state() -> dict:
    return {
        "selected_capabilities": {},
        "resources": [],
        "resolution": {
            "status": "not_started",
            "unresolved_capabilities": [],
            "validated_at": None,
        },
        "sync": {
            "status": "not_started",
            "last_attempt_at": None,
            "last_success_at": None,
            "errors": [],
        },
    }


def resolved_fixed_state() -> dict:
    return {
        "selected_capabilities": {
            "task_manager": {
                "provider": "trello",
                "status": "success",
                "resolution_status": "resolved",
            },
            "scheduling": {
                "provider": "google_calendar",
                "status": "success",
                "resolution_status": "resolved",
            },
        },
        "resolution": {
            "status": "resolved",
            "unresolved_capabilities": [],
            "validated_at": "2026-08-01T23:00:00Z",
        },
        "resources": [{"provider": "trello"}, {"provider": "google_calendar"}],
        "sync": {
            "status": "success",
            "last_success_at": "2026-08-01T23:00:00Z",
        },
    }


def resolved_flexible_state() -> dict:
    state = resolved_fixed_state()
    del state["selected_capabilities"]["scheduling"]
    state["selected_capabilities"]["reminders"] = {
        "provider": "todoist",
        "status": "success",
        "resolution_status": "resolved",
    }
    state["resources"] = [{"provider": "trello"}, {"provider": "todoist"}]
    return state


def no_external_config() -> dict:
    selected = untouched_config("github_issues")
    selected["integration_preferences"].update(
        {
            "experience": "minimal",
            "account_connections": "no_external_accounts",
            "routine": {"mode": "none", "details": None},
        }
    )
    return selected


def no_external_state() -> dict:
    return {
        "selected_capabilities": {
            "task_manager": {
                "provider": "github_issues",
                "status": "success",
                "resolution_status": "resolved",
            }
        },
        "resolution": {
            "status": "resolved",
            "unresolved_capabilities": [],
            "validated_at": "2026-08-01T23:00:00Z",
        },
        "sync": {"status": "success", "last_success_at": "2026-08-01T23:00:00Z"},
    }


def assert_error(state: dict, fragment: str, plan: str, selected_config: dict) -> None:
    result = validate_documents(selected_config, state, plan)
    if not any(fragment in error for error in result.errors):
        raise AssertionError(f"missing error containing {fragment!r}: {result.errors}")


def test_fresh_setup_may_remain_not_started() -> None:
    result = validate_documents(untouched_config(), untouched_state(), "")
    assert not result.errors, result.errors
    assert result.expected == ()


def test_explicit_task_choice_may_wait_for_publication() -> None:
    result = validate_documents(untouched_config("trello"), untouched_state(), "")
    assert not result.errors, result.errors
    assert result.expected == ("task_manager",)


def test_not_started_is_rejected_after_publication_begins() -> None:
    state = untouched_state()
    state["sync"]["status"] = "in_progress"
    state["sync"]["last_attempt_at"] = "2026-08-01T22:00:00Z"
    result = validate_documents(untouched_config(), state, "")
    assert any("cannot remain not_started" in error for error in result.errors), result.errors


def test_fixed_calendar_state_passes() -> None:
    result = validate_documents(config("fixed_calendar"), resolved_fixed_state(), FIXED_PLAN)
    assert not result.errors, result.errors
    assert result.expected == ("scheduling", "task_manager")


def test_flexible_reminder_state_passes() -> None:
    result = validate_documents(config("flexible_reminders"), resolved_flexible_state(), FLEXIBLE_PLAN)
    assert not result.errors, result.errors
    assert result.expected == ("reminders", "task_manager")


def test_missing_routine_resource_blocks_success() -> None:
    state = resolved_fixed_state()
    del state["selected_capabilities"]["scheduling"]
    assert_error(
        state,
        "selected capability disappeared from publication state: scheduling",
        FIXED_PLAN,
        config("fixed_calendar"),
    )


def test_pending_routine_details_block_success() -> None:
    state = resolved_fixed_state()
    state["selected_capabilities"]["scheduling"] = {
        "provider": "google_calendar",
        "status": "pending_configuration",
        "resolution_status": "action_required",
    }
    state["resolution"] = {
        "status": "action_required",
        "unresolved_capabilities": ["scheduling"],
        "validated_at": "2026-08-01T23:00:00Z",
    }
    assert_error(state, "sync.status cannot be success", FIXED_PLAN, config("fixed_calendar"))


def test_removed_flashcard_state_is_rejected() -> None:
    state = resolved_fixed_state()
    state["selected_capabilities"]["formative_practice"] = {
        "provider": "quizlet",
        "status": "success",
        "resolution_status": "resolved",
    }
    assert_error(
        state,
        "removed or on-request capability must not be selected",
        FIXED_PLAN,
        config("fixed_calendar"),
    )


def test_email_is_not_selected_during_publication() -> None:
    state = resolved_fixed_state()
    state["selected_capabilities"]["notifications"] = {
        "provider": "gmail",
        "status": "configured",
        "resolution_status": "resolved",
    }
    assert_error(
        state,
        "removed or on-request capability must not be selected",
        FIXED_PLAN,
        config("fixed_calendar"),
    )


def test_no_routine_mode_activates_no_scheduler() -> None:
    result = validate_documents(untouched_config("trello"), resolved_fixed_state(), "")
    assert result.expected == ("task_manager",)


def test_no_external_accounts_uses_only_internal_capabilities() -> None:
    result = validate_documents(no_external_config(), no_external_state(), NO_EXTERNAL_PLAN)
    assert not result.errors, result.errors
    assert result.expected == ("task_manager",)


def test_no_external_accounts_rejects_explicit_external_provider() -> None:
    selected = no_external_config()
    selected["integrations"]["task_manager"]["provider"] = "trello"
    assert_error(
        no_external_state(),
        "task_manager selects external provider trello",
        NO_EXTERNAL_PLAN,
        selected,
    )


def test_plan_rejects_removed_capabilities() -> None:
    broken = FIXED_PLAN + "\nQuizlet e flashcards TSV\n"
    assert_error(resolved_fixed_state(), "removed flashcard capabilities", broken, config())


def main() -> None:
    tests = [
        test_fresh_setup_may_remain_not_started,
        test_explicit_task_choice_may_wait_for_publication,
        test_not_started_is_rejected_after_publication_begins,
        test_fixed_calendar_state_passes,
        test_flexible_reminder_state_passes,
        test_missing_routine_resource_blocks_success,
        test_pending_routine_details_block_success,
        test_removed_flashcard_state_is_rejected,
        test_email_is_not_selected_during_publication,
        test_no_routine_mode_activates_no_scheduler,
        test_no_external_accounts_uses_only_internal_capabilities,
        test_no_external_accounts_rejects_explicit_external_provider,
        test_plan_rejects_removed_capabilities,
    ]
    for test in tests:
        test()
    print(f"Active integration resolution regressions passed ({len(tests)} cases).")


if __name__ == "__main__":
    main()
