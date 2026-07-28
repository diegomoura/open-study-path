#!/usr/bin/env python3
"""Deterministic GitHub Issue Form intake resolution.

The current form marker is authoritative. Title and discovery labels are repairable
consistency signals only for marked submissions. Unmarked legacy submissions must
satisfy every legacy identity signal; matching field headings alone are never enough.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence

CURRENT_FORM_ID = "create-study-path"
CURRENT_FORM_VERSION = 2
CURRENT_MARKER = (
    "<!-- open-study-path:intake "
    f"form_id={CURRENT_FORM_ID} version={CURRENT_FORM_VERSION} -->"
)
CURRENT_PREFIX = "[Nova trilha]"
LEGACY_PREFIX = "[Study Path]:"
DISCOVERY_LABEL = "study-request"
IMPORTED_LABEL = "intake:imported"

ANY_MARKER_RE = re.compile(r"<!--\s*open-study-path:intake\b[^>]*-->", re.IGNORECASE)
CURRENT_MARKER_RE = re.compile(
    r"<!--\s*open-study-path:intake\s+"
    rf"form_id={re.escape(CURRENT_FORM_ID)}\s+"
    rf"version={CURRENT_FORM_VERSION}\s*-->",
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


def classify_issue(
    issue: IntakeIssue,
    expected_headings: Sequence[str],
    imported_references: Iterable[str] = (),
) -> CandidateDecision:
    """Classify one issue without selecting it.

    Current marked submissions may have their title and discovery label repaired after
    unique selection. Legacy submissions have no marker and therefore require label,
    recognized title prefix and expected headings together.
    """

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

    markers = ANY_MARKER_RE.findall(issue.body)
    current_markers = CURRENT_MARKER_RE.findall(issue.body)

    if markers:
        if len(markers) != 1 or len(current_markers) != 1:
            reasons.append("unsupported_or_ambiguous_marker")
            return CandidateDecision(issue.number, False, None, tuple(reasons), ())
        if reasons:
            return CandidateDecision(issue.number, False, None, tuple(reasons), ())

        if DISCOVERY_LABEL not in labels:
            repairs.append("add_study_request_label")
        if not issue.title.startswith(CURRENT_PREFIX):
            repairs.append("normalize_current_title")
        return CandidateDecision(issue.number, True, "current_marker", (), tuple(repairs))

    legacy_title = issue.title.startswith(CURRENT_PREFIX) or issue.title.startswith(LEGACY_PREFIX)
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
