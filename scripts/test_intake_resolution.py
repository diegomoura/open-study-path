#!/usr/bin/env python3
"""Behavioral regressions for deterministic intake resolution."""

from __future__ import annotations

from intake_resolution import CURRENT_MARKER, IntakeIssue, resolve_candidates

HEADINGS = (
    "### O que você quer aprender?",
    "### Conte um pouco mais sobre seu objetivo",
    "### Como você descreve seu nível atual?",
)
BODY = "\n\n".join(HEADINGS)


def issue(
    number: int,
    *,
    title: str = "Engenharia de Aplicações com IA Generativa",
    body: str = BODY,
    labels: tuple[str, ...] = ("study-request",),
    is_pull_request: bool = False,
    source_reference: str | None = None,
) -> IntakeIssue:
    return IntakeIssue(
        number=number,
        title=title,
        body=body,
        labels=frozenset(labels),
        is_pull_request=is_pull_request,
        source_reference=source_reference,
    )


def assert_state(expected: str, *issues: IntakeIssue, imported: tuple[str, ...] = ()):
    result = resolve_candidates(issues, HEADINGS, imported)
    if result.state != expected:
        raise SystemExit(f"expected {expected}, got {result.state}: {result}")
    return result


def main() -> None:
    current = issue(1, body=f"{CURRENT_MARKER}\n\n{BODY}", labels=())
    resolved = assert_state("unique", current)
    if resolved.accepted[0].mode != "current_marker":
        raise SystemExit("version 4 issue was not classified as current")
    if set(resolved.accepted[0].repairs) != {"add_study_request_label"}:
        raise SystemExit(f"current candidate repairs changed: {resolved.accepted[0].repairs}")

    missing_title = issue(2, title="", body=f"{CURRENT_MARKER}\n\n{BODY}")
    assert_state("none", missing_title)

    headings_only = issue(3, title="Curso sem marcador", labels=())
    assert_state("none", headings_only)

    unsupported = issue(
        4,
        body="<!-- open-study-path:intake form_id=create-study-path version=3 -->\n\n" + BODY,
    )
    assert_state("none", unsupported)

    duplicate_marker = issue(5, body=f"{CURRENT_MARKER}\n{CURRENT_MARKER}\n\n{BODY}")
    assert_state("none", duplicate_marker)

    imported_label = issue(6, body=f"{CURRENT_MARKER}\n\n{BODY}", labels=("intake:imported",))
    assert_state("none", imported_label)

    pull_request = issue(7, body=f"{CURRENT_MARKER}\n\n{BODY}", is_pull_request=True)
    assert_state("none", pull_request)

    missing_heading = issue(8, body=f"{CURRENT_MARKER}\n\n{HEADINGS[0]}")
    assert_state("none", missing_heading)

    first = issue(9, body=f"{CURRENT_MARKER}\n\n{BODY}")
    second = issue(10, body=f"{CURRENT_MARKER}\n\n{BODY}")
    assert_state("ambiguous", first, second)

    recorded = issue(11, body=f"{CURRENT_MARKER}\n\n{BODY}", source_reference="github_issue:11")
    assert_state("none", recorded, imported=("github_issue:11",))

    print("Deterministic intake resolution regressions passed.")


if __name__ == "__main__":
    main()
