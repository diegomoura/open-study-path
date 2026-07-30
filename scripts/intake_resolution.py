#!/usr/bin/env python3
"""Deterministic GitHub Issue Form intake resolution.

Only the current marked form is supported. The hidden marker, expected headings,
course title and import state jointly identify a valid submission.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence

CURRENT_FORM_ID = "create-study-path"
CURRENT_FORM_VERSION = 4
CURRENT_MARKER = (
    "<!-- open-study-path:intake "
    f"form_id={CURRENT_FORM_ID} version={CURRENT_FORM_VERSION} -->"
)
DISCOVERY_LABEL = "study-request"
IMPORTED_LABEL = "intake:imported"

ANY_MARKER_RE = re.compile(r"<!--\s*open-study-path:intake\b[^>]*-->", re.IGNORECASE)
INTAKE_MARKER_RE = re.compile(
    r"<!--\s*open-study-path:intake\s+"
    r"form_id=(?P<form_id>[A-Za-z0-9_-]+)\s+"
    r"version=(?P<version>\d+)\s*-->",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class IntakeIssue:
    number: int
    title: str
    body: str
    labels: frozenset[str]
    is_pull_request: bool = False
    source_reference: str | None = None


@dataclass(frozen=True)
class CandidateDecision:
    issue_number: int
    accepted: bool
    mode: str | None
    reasons: tuple[str, ...]
    repairs: tuple[str, ...]


@dataclass(frozen=True)
class Resolution:
    state: str
    accepted: tuple[CandidateDecision, ...]
    rejected: tuple[CandidateDecision, ...]


def _normalized_labels(labels: Iterable[str]) -> set[str]:
    return {label.strip().lower() for label in labels if label.strip()}


def _has_expected_headings(body: str, expected_headings: Sequence[str]) -> bool:
    return bool(expected_headings) and all(heading in body for heading in expected_headings)


def _has_course_title(title: str) -> bool:
    return bool(title.strip())


def classify_issue(
    issue: IntakeIssue,
    expected_headings: Sequence[str],
    imported_references: Iterable[str] = (),
) -> CandidateDecision:
    """Classify one issue without selecting it."""

    reasons: list[str] = []
    repairs: list[str] = []
    labels = _normalized_labels(issue.labels)
    imported = {reference for reference in imported_references if reference}

    if issue.is_pull_request:
        reasons.append("pull_request")
    if issue.source_reference and issue.source_reference in imported:
        reasons.append("already_recorded")
    if IMPORTED_LABEL in labels:
        reasons.append("already_labeled_imported")
    if not _has_expected_headings(issue.body, expected_headings):
        reasons.append("missing_expected_headings")
    if not _has_course_title(issue.title):
        reasons.append("missing_course_title")

    marker_matches = list(ANY_MARKER_RE.finditer(issue.body))
    detail_matches = list(INTAKE_MARKER_RE.finditer(issue.body))
    if not marker_matches:
        reasons.append("missing_current_marker")
    elif (
        len(marker_matches) != 1
        or len(detail_matches) != 1
        or marker_matches[0].span() != detail_matches[0].span()
    ):
        reasons.append("unsupported_or_ambiguous_marker")
    else:
        marker = detail_matches[0]
        form_id = marker.group("form_id")
        version = int(marker.group("version"))
        if form_id != CURRENT_FORM_ID or version != CURRENT_FORM_VERSION:
            reasons.append("unsupported_or_ambiguous_marker")

    if reasons:
        return CandidateDecision(issue.number, False, None, tuple(reasons), ())

    if DISCOVERY_LABEL not in labels:
        repairs.append("add_study_request_label")
    return CandidateDecision(issue.number, True, "current_marker", (), tuple(repairs))


def resolve_candidates(
    issues: Iterable[IntakeIssue],
    expected_headings: Sequence[str],
    imported_references: Iterable[str] = (),
) -> Resolution:
    accepted: list[CandidateDecision] = []
    rejected: list[CandidateDecision] = []

    for issue in issues:
        decision = classify_issue(issue, expected_headings, imported_references)
        (accepted if decision.accepted else rejected).append(decision)

    state = "unique" if len(accepted) == 1 else "none" if not accepted else "ambiguous"
    return Resolution(state, tuple(accepted), tuple(rejected))
