#!/usr/bin/env python3
"""Resolve and validate selected integration capabilities.

The learner may continue with repository-native fallbacks, but every explicit
integration choice must have a visible, persisted disposition. A capability
cannot disappear between intake, the approved plan and publication state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

TERMINAL_OFFER_STATUSES = {"shown", "not_needed", "connected", "declined", "unavailable"}
VALID_RESOLUTION_STATUSES = {"resolved", "action_required"}
VALID_EMAIL_CADENCES = {"on_request", "after_each_assessment", "weekly", "monthly"}
NONE_VALUES = {"", "none", "disabled", "false", "null"}


@dataclass(frozen=True)
class ResolutionResult:
    expected: tuple[str, ...]
    unresolved: tuple[str, ...]
    errors: tuple[str, ...]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any) -> str:
    return str(value or "").strip().lower()


def _section(markdown: str, heading: str) -> str:
    marker = heading.lower()
    lower = markdown.lower()
    start = lower.find(marker)
    if start < 0:
        return ""
    next_heading = lower.find("\n## ", start + len(marker))
    return markdown[start:] if next_heading < 0 else markdown[start:next_heading]


def has_materialized_flashcards(root: Path) -> bool:
    flashcards = root / "study" / "flashcards"
    return flashcards.is_dir() and any(flashcards.glob("TOPIC-*.tsv"))


def expected_capabilities(config: Mapping[str, Any], plan_markdown: str, *, decks_exist: bool) -> dict[str, str]:
    integrations = _mapping(config.get("integrations"))
    preferences = _mapping(config.get("integration_preferences"))
    expected: dict[str, str] = {}

    task = _mapping(integrations.get("task_manager"))
    task_provider = _text(task.get("provider"))
    if task_provider not in NONE_VALUES | {"auto"}:
        expected["task_manager"] = task_provider

    calendar = _mapping(integrations.get("calendar"))
    calendar_provider = _text(calendar.get("provider"))
    calendar_enabled = _text(calendar.get("enabled"))
    if calendar_provider not in NONE_VALUES | {"auto"} and calendar_enabled not in {"disabled", "false", "none"}:
        expected["scheduling"] = calendar_provider

    notifications = _mapping(integrations.get("notifications"))
    notification_provider = _text(notifications.get("provider"))
    if notifications.get("email_enabled") is True and notification_provider in {"gmail", "outlook_email"}:
        expected["notifications"] = notification_provider

    practice = _mapping(integrations.get("formative_practice"))
    practice_provider = _text(practice.get("provider"))
    preferred_provider = _text(practice.get("preferred"))
    already_uses = {_text(value) for value in preferences.get("already_uses", []) if value}
    willing = {_text(value) for value in preferences.get("willing_to_connect", []) if value}
    plan_lower = plan_markdown.lower()
    quizlet_expected = (
        decks_exist
        and (
            practice_provider == "quizlet"
            or (
                practice_provider == "auto"
                and preferred_provider == "quizlet"
                and (
                    "quizlet" in already_uses
                    or "formative_practice" in willing
                    or "provider: quizlet" in plan_lower
                )
            )
        )
    )
    if quizlet_expected:
        expected["formative_practice"] = "quizlet"

    return expected


def validate_plan(config: Mapping[str, Any], plan_markdown: str, *, decks_exist: bool) -> list[str]:
    errors: list[str] = []
    lower = plan_markdown.lower()
    expected = expected_capabilities(config, plan_markdown, decks_exist=decks_exist)
    unchosen = _section(plan_markdown, "## Ferramentas que não foram escolhidas").lower()

    if "notifications" in expected:
        provider = expected["notifications"]
        for required in [f"provider: {provider}", "decision: selected", "preflight: optional_probe"]:
            if required not in lower:
                errors.append(f"selected email integration is missing from approved plan: {required}")
        if provider in unchosen:
            errors.append(f"selected email provider is incorrectly listed as not chosen: {provider}")

    if "formative_practice" in expected:
        if "provider: quizlet" not in lower:
            errors.append("eligible Quizlet practice is missing provider: quizlet in approved plan")
        if "decision: selected" not in lower and "decision: recommended" not in lower:
            errors.append("eligible Quizlet practice must be selected or recommended in approved plan")
        for required in ["preflight: optional_probe", "conectei o quizlet"]:
            if required not in lower:
                errors.append(f"eligible Quizlet practice is missing approved-plan contract: {required}")
        if "quizlet" in unchosen:
            errors.append("Quizlet is eligible now but is incorrectly listed as not chosen")

    return errors


def _capability_resolved(name: str, entry: Mapping[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    status = _text(entry.get("status"))
    resolution_status = _text(entry.get("resolution_status"))
    if resolution_status not in VALID_RESOLUTION_STATUSES:
        errors.append(f"{name} has invalid resolution_status: {resolution_status or '<missing>'}")
        return False, errors

    if name == "task_manager":
        resolved = status in {"success", "completed"} and resolution_status == "resolved"
        if not resolved:
            errors.append("task_manager must be successful before publication resolves")
        return resolved, errors

    if name == "formative_practice":
        offer = _text(entry.get("connection_offer_status"))
        if offer and offer not in TERMINAL_OFFER_STATUSES:
            errors.append(f"formative_practice has invalid connection_offer_status: {offer}")
        if status in {"success", "completed"}:
            resolved = resolution_status == "resolved" and offer in {"connected", "not_needed"}
        elif status == "fallback_active":
            resolved = resolution_status == "resolved" and offer in {"shown", "declined", "unavailable"}
        else:
            resolved = False
        if not resolved:
            errors.append("formative_practice must publish Quizlet or persist a shown/declined/unavailable offer with fallback")
        return resolved, errors

    if name == "scheduling":
        if status in {"success", "completed", "deferred_by_learner", "unavailable"}:
            resolved = resolution_status == "resolved"
        elif status == "not_activated":
            resolved = resolution_status == "resolved" and _text(entry.get("learner_notice_status")) == "shown"
        else:
            resolved = False
        if not resolved:
            errors.append("scheduling must be activated, explicitly deferred, unavailable, or visibly explained")
        return resolved, errors

    if name == "notifications":
        cadence = _text(entry.get("delivery_policy"))
        if status in {"success", "configured"}:
            resolved = resolution_status == "resolved" and cadence in VALID_EMAIL_CADENCES
            if cadence not in VALID_EMAIL_CADENCES:
                errors.append("notifications requires a valid delivery_policy before it is configured")
        elif status in {"deferred_by_learner", "unavailable", "declined"}:
            resolved = resolution_status == "resolved"
        else:
            resolved = False
        if not resolved:
            errors.append("notifications selected in intake require cadence configuration or an explicit terminal disposition")
        return resolved, errors

    resolved = resolution_status == "resolved"
    if not resolved:
        errors.append(f"{name} remains unresolved")
    return resolved, errors


def validate_documents(
    config: Mapping[str, Any],
    state: Mapping[str, Any],
    plan_markdown: str,
    *,
    decks_exist: bool,
) -> ResolutionResult:
    errors = validate_plan(config, plan_markdown, decks_exist=decks_exist) if plan_markdown else []
    expected = expected_capabilities(config, plan_markdown, decks_exist=decks_exist)
    selected = _mapping(state.get("selected_capabilities"))
    unresolved: list[str] = []

    for capability, provider in expected.items():
        entry = _mapping(selected.get(capability))
        if not entry:
            errors.append(f"selected capability disappeared from publication state: {capability}")
            unresolved.append(capability)
            continue
        state_provider = _text(entry.get("provider"))
        if state_provider and state_provider != provider and not (
            capability == "formative_practice" and state_provider == "markdown_flashcards"
        ):
            errors.append(f"{capability} provider changed from {provider} to {state_provider}")
        resolved, capability_errors = _capability_resolved(capability, entry)
        errors.extend(capability_errors)
        if not resolved:
            unresolved.append(capability)

    resolution = _mapping(state.get("resolution"))
    resolution_status = _text(resolution.get("status"))
    declared_unresolved = tuple(sorted(_text(value) for value in resolution.get("unresolved_capabilities", []) if value))
    computed_unresolved = tuple(sorted(set(unresolved)))

    if expected and not resolution:
        errors.append("publication state is missing top-level integration resolution")
    if resolution:
        expected_status = "resolved" if not computed_unresolved else "action_required"
        if resolution_status != expected_status:
            errors.append(f"resolution.status must be {expected_status}, got {resolution_status or '<missing>'}")
        if declared_unresolved != computed_unresolved:
            errors.append(
                "resolution.unresolved_capabilities does not match computed unresolved capabilities: "
                f"expected {computed_unresolved}, got {declared_unresolved}"
            )

    sync = _mapping(state.get("sync"))
    if _text(sync.get("status")) in {"success", "succeeded", "completed"} and computed_unresolved:
        errors.append("sync.status cannot be success while selected integrations remain unresolved")

    return ResolutionResult(tuple(sorted(expected)), computed_unresolved, tuple(errors))
