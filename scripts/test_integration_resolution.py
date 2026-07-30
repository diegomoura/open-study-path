#!/usr/bin/env python3
"""Behavioral regressions for selected integration resolution."""

from __future__ import annotations

from integration_resolution import validate_documents


PLAN = """
# Ferramentas

### Quizlet
- provider: quizlet
- decision: recommended
- preflight: optional_probe
- return command: `Conectei o Quizlet. Crie meus flashcards.`

### Gmail
- provider: gmail
- decision: selected
- preflight: optional_probe

## Ferramentas que não foram escolhidas

Habitify não entra agora.
"""

NO_EXTERNAL_PLAN = """
# Ferramentas

- account_connections: no_external_accounts

### GitHub Issues
- provider: github_issues
- decision: selected
- preflight: required_for_selected_publication
- connection-offer eligibility: not_enabled

## Ferramentas que não foram escolhidas

Aplicativos que exigem outras contas não serão sugeridos.
"""


def config() -> dict:
    return {
        "integration_preferences": {
            "experience": "guided_recommendations",
            "account_connections": "ask_per_provider",
            "already_uses": ["quizlet"],
            "willing_to_connect": ["flashcards"],
            "notes": None,
        },
        "integrations": {
            "task_manager": {"provider": "trello"},
            "formative_practice": {"provider": "auto", "preferred": "quizlet"},
            "calendar": {"provider": "google_calendar", "enabled": "enabled"},
            "notifications": {"provider": "gmail", "email_enabled": True},
        },
    }


def no_external_config() -> dict:
    return {
        "integration_preferences": {
            "experience": "minimal",
            "account_connections": "no_external_accounts",
            "already_uses": ["quizlet", "trello"],
            "willing_to_connect": ["flashcards"],
            "notes": None,
        },
        "integrations": {
            "task_manager": {"provider": "github_issues"},
            "formative_practice": {"provider": "auto", "preferred": "quizlet"},
            "calendar": {"provider": "auto", "enabled": "auto"},
            "notifications": {"provider": "chat", "email_enabled": False},
        },
    }


def resolved_state() -> dict:
    return {
        "selected_capabilities": {
            "task_manager": {
                "provider": "trello",
                "status": "success",
                "resolution_status": "resolved",
            },
            "formative_practice": {
                "provider": "markdown_flashcards",
                "preferred_provider": "quizlet",
                "status": "fallback_active",
                "resolution_status": "resolved",
                "connection_offer_status": "shown",
            },
            "scheduling": {
                "provider": "google_calendar",
                "status": "not_activated",
                "reason": "no_days_or_times_selected",
                "learner_notice_status": "shown",
                "resolution_status": "resolved",
            },
            "notifications": {
                "provider": "gmail",
                "status": "configured",
                "delivery_policy": "on_request",
                "resolution_status": "resolved",
            },
        },
        "resolution": {
            "status": "resolved",
            "unresolved_capabilities": [],
            "validated_at": "2026-07-29T23:00:00Z",
        },
        "resources": [{"provider": "trello"}],
        "sync": {
            "status": "success",
            "last_success_at": "2026-07-29T23:00:00Z",
        },
    }


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
            "validated_at": "2026-07-30T18:00:00Z",
        },
        "sync": {
            "status": "success",
            "last_success_at": "2026-07-30T18:00:00Z",
        },
    }


def assert_error(state: dict, fragment: str, plan: str = PLAN, selected_config: dict | None = None) -> None:
    result = validate_documents(selected_config or config(), state, plan, decks_exist=True)
    if not any(fragment in error for error in result.errors):
        raise AssertionError(f"missing error containing {fragment!r}: {result.errors}")


def test_fully_resolved_state_passes() -> None:
    result = validate_documents(config(), resolved_state(), PLAN, decks_exist=True)
    assert not result.errors, result.errors
    assert result.unresolved == ()


def test_quizlet_cannot_be_silently_deferred() -> None:
    state = resolved_state()
    state["selected_capabilities"]["formative_practice"]["connection_offer_status"] = "deferred_until_explicit_request"
    assert_error(state, "invalid connection_offer_status")


def test_email_choice_cannot_disappear() -> None:
    state = resolved_state()
    del state["selected_capabilities"]["notifications"]
    state["resolution"] = {
        "status": "resolved",
        "unresolved_capabilities": [],
        "validated_at": "2026-07-29T23:00:00Z",
    }
    assert_error(state, "selected capability disappeared from publication state: notifications")


def test_email_without_cadence_blocks_success() -> None:
    state = resolved_state()
    notification = state["selected_capabilities"]["notifications"]
    notification["status"] = "pending_configuration"
    notification["resolution_status"] = "action_required"
    notification.pop("delivery_policy")
    state["resolution"] = {
        "status": "action_required",
        "unresolved_capabilities": ["notifications"],
        "validated_at": "2026-07-29T23:00:00Z",
    }
    assert_error(state, "sync.status cannot be success")


def test_plan_cannot_list_selected_gmail_as_unchosen() -> None:
    broken_plan = PLAN.replace("Habitify não entra agora.", "Gmail não entra agora.")
    assert_error(resolved_state(), "selected email provider is incorrectly listed as not chosen", broken_plan)


def test_top_level_resolution_must_match_capabilities() -> None:
    state = resolved_state()
    state["selected_capabilities"]["notifications"] = {
        "provider": "gmail",
        "status": "pending_configuration",
        "resolution_status": "action_required",
    }
    assert_error(state, "resolution.status must be action_required")


def test_no_external_accounts_uses_only_internal_capabilities() -> None:
    result = validate_documents(no_external_config(), no_external_state(), NO_EXTERNAL_PLAN, decks_exist=True)
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


def test_no_external_accounts_requires_plan_disposition() -> None:
    assert_error(
        no_external_state(),
        "must record account_connections: no_external_accounts",
        "# Ferramentas\n\nSomente GitHub.",
        no_external_config(),
    )


def main() -> None:
    tests = [
        test_fully_resolved_state_passes,
        test_quizlet_cannot_be_silently_deferred,
        test_email_choice_cannot_disappear,
        test_email_without_cadence_blocks_success,
        test_plan_cannot_list_selected_gmail_as_unchosen,
        test_top_level_resolution_must_match_capabilities,
        test_no_external_accounts_uses_only_internal_capabilities,
        test_no_external_accounts_rejects_explicit_external_provider,
        test_no_external_accounts_requires_plan_disposition,
    ]
    for test in tests:
        test()
    print(f"Selected integration resolution regressions passed ({len(tests)} cases).")


if __name__ == "__main__":
    main()
