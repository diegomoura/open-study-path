#!/usr/bin/env python3
"""Deterministic GitHub Issue Form intake resolution.

Version 4 is the current form. Versions 3 and 2 remain accepted through explicit
markers, while unmarked legacy submissions require the stricter legacy signals.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence

CURRENT_FORM_ID = "create-study-path"
CURRENT_FORM_VERSION = 4
COMPATIBLE_FORM_VERSIONS = frozenset({2, 3})
SUPPORTED_FORM_VERSIONS = frozenset({CURRENT_FORM_VERSION, *COMPATIBLE_FORM_VERSIONS})
CURRENT_MARKER = (
    "<!-- open-study-path:intake "
    f"form_id={CURRENT_FORM_ID} version={CURRENT_FORM_VERSION} -->"
)
VERSION_3_MARKER = (
    "<!-- open-study-path:intake "
    f"form_id={CURRENT_FORM_ID} version=3 -->"
)
VERSION_2_MARKER = (
    "<!-- open-study-path:intake "
    f"form_id={CURRENT_FORM_ID} version=2 -->"
)
LEGACY_CURRENT_PREFIX = "[Nova trilha]"
LEGACY_PREFIX = "[Study Path]:"
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
    value = title.strip()
    return bool(value) and value not in {LEGACY_CURRENT_PREFIX, LEGACY_PREFIX}


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

    marker_matches = list(ANY_MARKER_RE.finditer(issue.body))
    detail_matches = list(INTAKE_MARKER_RE.finditer(issue.body))

    if marker_matches:
        if (
            len(marker_matches) != 1
            or len(detail_matches) != 1
            or marker_matches[0].span() != detail_matches[0].span()
        ):
            reasons.append("unsupported_or_ambiguous_marker")
            return CandidateDecision(issue.number, False, None, tuple(reasons), ())

        marker = detail_matches[0]
        form_id = marker.group("form_id")
        version = int(marker.group("version"))
        if form_id != CURRENT_FORM_ID or version not in SUPPORTED_FORM_VERSIONS:
            reasons.append("unsupported_or_ambiguous_marker")
            return CandidateDecision(issue.number, False, None, tuple(reasons), ())
        if version in {CURRENT_FORM_VERSION, 3} and not _has_course_title(issue.title):
            reasons.append("missing_course_title")
        if reasons:
            return CandidateDecision(issue.number, False, None, tuple(reasons), ())

        if DISCOVERY_LABEL not in labels:
            repairs.append("add_study_request_label")
        if version == CURRENT_FORM_VERSION:
            mode = "current_marker"
        else:
            mode = f"compatible_marker_v{version}"
        return CandidateDecision(issue.number, True, mode, (), tuple(repairs))

    legacy_title = issue.title.startswith(LEGACY_CURRENT_PREFIX) or issue.title.startswith(LEGACY_PREFIX)
    if DISCOVERY_LABEL not in labels:
        reasons.append("legacy_missing_study_request_label")
    if not legacy_title:
        reasons.append("legacy_unrecognized_title")

    if reasons:
        return CandidateDecision(issue.number, False, None, tuple(reasons), ())
    return CandidateDecision(issue.number, True, "legacy_signals", (), ())


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
