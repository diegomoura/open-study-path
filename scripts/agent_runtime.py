#!/usr/bin/env python3
"""Minimal Claude coding-agent harness for Open Study Path pilot workflows.

Stage 2 of the multi-agent work proposal: this is the first module that makes
a *real* Anthropic API call. Everything in stage 1 (scripts/agent_model_resolution.py,
scripts/validate_model_config.py) stayed pure logic -- this module is the runtime
that actually sends a request and executes what comes back, scoped to one phase
of instructions/manifest.yml.

Design choices that matter for safety, not just style:

- The model never gets raw filesystem or shell access. It gets three tools
  (read_file, list_dir, write_file for authors; read_file, list_dir,
  submit_review for reviewers) implemented in Python, and every write is
  checked against a deterministic allowlist derived from
  instructions/02-setup-execution.md ("Allowed setup diff") *before* it
  touches disk. An agent asking to write outside the allowlist gets a tool
  error, not a bypass -- the CI-style guardrail described in the work
  proposal applies to agent-written diffs too, not only to human ones.
- Author and reviewer are always two separate `run_agent()` calls with their
  own fresh message history. The reviewer is never handed the author's
  transcript -- only the phase's review contract, the resulting diff, and
  read access to the repository. See docs/claude-agent-pilot.md.
- The HTTP transport is injectable (`transport` parameter) purely so this
  module can be unit-tested offline, without an API key or network access.
  Production code paths always go through `anthropic_transport`.

Stage: Etapa 4 (proposal, section 7, step 4) adds a second, narrower tool
group -- GitHub Issues read/label access -- gated to the `intake` phase only.
The repository these tools operate against is always resolved from the
`GITHUB_REPOSITORY` environment variable that GitHub Actions sets
automatically for the workflow's own repository, never from a
workflow_dispatch input: `instructions/10-intake.md` requires searching only
"the instance repository", and taking that identity from user-controlled
input would let a crafted dispatch point the tool at an unrelated repo. Issue
*classification* itself is never left to the model's judgment: the
`resolve_intake_candidates` tool calls the existing deterministic
`scripts/intake_resolution.py` algorithm directly, exactly as
`instructions/10-intake.md` requires ("Apply the algorithm in
scripts/intake_resolution.py; do not replace it with similarity or
newest-issue heuristics").
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from agent_model_resolution import AGENT_CATALOG, resolve_effective_models
from ensure_repository_labels import github_request_factory
from intake_resolution import DISCOVERY_LABEL, IMPORTED_LABEL, IntakeIssue, resolve_candidates

GITHUB_API_URL_DEFAULT = "https://api.github.com"
RequestJson = Callable[[str, str, dict[str, Any] | None], Any]

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MAX_TOKENS = 4096

# USD per million tokens, verified against platform.claude.com/docs/en/about-claude/pricing
# (checked 2026-08-14). Update this table if Anthropic changes rates -- it is
# only used to produce an estimate for the pilot's cost reporting, never sent
# to the API or used for anything billing-authoritative.
#
# cache_write_5m / cache_read multipliers are relative to base input price
# (1.25x and 0.1x respectively, per the pricing page); stored here as
# absolute per-MTok USD for direct lookup instead of as a multiplier, since
# the actual multiplier the API applied per-call isn't reported back to us --
# only raw cache_creation_input_tokens / cache_read_input_tokens counts are.
# 5-minute cache writes are assumed since neither prompt in this harness sets
# a longer TTL.
MODEL_PRICING_USD_PER_MTOK: dict[str, dict[str, float]] = {
    "claude-haiku-4-5-20251001": {"input": 1.0, "output": 5.0, "cache_write_5m": 1.25, "cache_read": 0.10},
    "claude-sonnet-5": {"input": 2.0, "output": 10.0, "cache_write_5m": 2.50, "cache_read": 0.20},
    "claude-opus-5": {"input": 5.0, "output": 25.0, "cache_write_5m": 6.25, "cache_read": 0.50},
}

# Hard cap on tool-use round trips per agent call. This is a runtime safety
# rail independent of any billing cap configured in the Anthropic Console
# (work proposal, section 6): a bug that makes the model loop on tool calls
# stops here instead of draining the budget.
MAX_TOOL_ITERATIONS = 20

# The exact "Allowed setup diff" list from instructions/02-setup-execution.md,
# duplicated here deliberately rather than parsed out of the markdown: this
# list is a safety boundary and must fail closed (require a code change and
# review) if the instruction file's prose ever changes shape.
SETUP_ALLOWED_EXACT_PATHS: tuple[str, ...] = (
    ".open-study-path/instance.yml",
    "study.config.yml",
    "state/intake-summary.json",
    "state/progress.json",
    "state/integrations.json",
    "study/roadmap.md",
    "README.md",
)
SETUP_ALLOWED_PREFIXES: tuple[str, ...] = ()
# NOTE: instructions/02-setup-execution.md's "Allowed setup diff" also lists
# `state/reviews/<setup-operation>.yml` -- but that's written by whichever
# context runs the review. In the isolated harness that's always the
# reviewer agent, which never gets write_file (it writes its verdict through
# submit_review, recorded by the workflow step, not by touching disk itself).
# The author is deliberately given no prefix-based write access here: letting
# it write anywhere under state/reviews/ would let it author its own
# "independent" review, which is exactly the failure mode this whole
# author/reviewer split exists to prevent. See docs/claude-agent-pilot.md.

# The exact intake domain-output list from instructions/10-intake.md ("Pull
# request and merge": "a PR limited to the instance marker, study.config.yml,
# state/intake-summary.json and one intake review artifact"). The review
# artifact itself is excluded here for the same reason state/reviews/ is
# excluded from SETUP_ALLOWED_*: only the reviewer's submit_review result,
# recorded by the workflow, writes there.
INTAKE_ALLOWED_EXACT_PATHS: tuple[str, ...] = (
    ".open-study-path/instance.yml",
    "study.config.yml",
    "state/intake-summary.json",
)
INTAKE_ALLOWED_PREFIXES: tuple[str, ...] = ()

# Which allowlist applies to which manifest phase. Etapa 4 (proposal, section
# 7, step 4) adds `intake` to the two pilot phases wired up in stage 2.
PHASE_ALLOWLISTS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "bootstrap_instance": (SETUP_ALLOWED_EXACT_PATHS, SETUP_ALLOWED_PREFIXES),
    "configure_intake": (SETUP_ALLOWED_EXACT_PATHS, SETUP_ALLOWED_PREFIXES),
    "intake": (INTAKE_ALLOWED_EXACT_PATHS, INTAKE_ALLOWED_PREFIXES),
}

# Agent ids that exist as real rows in AGENT_CATALOG for the pilot phases.
PHASE_AUTHOR_AGENT: dict[str, str] = {
    "bootstrap_instance": "bootstrap",
    "configure_intake": "configure_intake",
    "intake": "intake_resolution",
}

# Phases where the RepoTools instance also gets a small, separate GitHub
# Issues tool group (list/read/resolve/label), in addition to the repo-file
# tools every phase gets. Kept as its own set -- rather than folding into
# PHASE_ALLOWLISTS -- because it gates a different resource (the GitHub API,
# not the local checkout) with its own authorization model (GITHUB_TOKEN,
# not filesystem paths).
PHASES_WITH_GITHUB_ISSUES: frozenset[str] = frozenset({"intake"})

# The only label the intake author is ever allowed to apply. Restricting this
# at the tool layer (not just in the prompt) means a model that misreads its
# own instructions cannot label an unrelated issue or invent a new label --
# the same "fail closed on a code boundary, not a prompt boundary" posture
# `write_file`'s allowlist check already applies to file writes.
INTAKE_AUTHOR_ALLOWED_LABEL = IMPORTED_LABEL


class AllowlistViolation(RuntimeError):
    """Raised when a tool call would write (or read outside the repo) improperly."""


class AgentBudgetExceeded(RuntimeError):
    """Raised when MAX_TOOL_ITERATIONS is hit without the agent finishing."""


def resolve_phase_reviewer_model(phase: str, config: Mapping[str, Any]) -> str:
    """Resolve the model a *generic* phase_review pass should use.

    Only curriculum/content/slides/publish have a dedicated reviewer row in
    AGENT_CATALOG. Every other phase uses the generic
    instructions/04-review-generated-artifacts.md contract, and the work
    proposal (section 3, last row) states the rule explicitly: a generic
    reviewer "herda o tier da fase" -- it uses the same effective tier as
    that phase's author agent, whatever the dial/override resolved to.
    """
    author_agent_id = PHASE_AUTHOR_AGENT.get(phase)
    if author_agent_id is None:
        raise ValueError(f"no author agent registered for phase: {phase}")
    resolved = resolve_effective_models(config)
    return resolved[author_agent_id].model


def normalize_relative_path(root: Path, candidate: str) -> Path:
    """Resolve `candidate` under `root`, rejecting escapes and absolute paths."""
    if not candidate or candidate.startswith(("/", "~")) or ".." in Path(candidate).parts:
        raise AllowlistViolation(f"refusing unsafe path: {candidate!r}")
    resolved = (root / candidate).resolve()
    root_resolved = root.resolve()
    if root_resolved not in resolved.parents and resolved != root_resolved:
        raise AllowlistViolation(f"path escapes repository root: {candidate!r}")
    return resolved


def is_write_allowed(phase: str, relative_path: str) -> bool:
    exact_paths, prefixes = PHASE_ALLOWLISTS.get(phase, ((), ()))
    normalized = relative_path.replace(os.sep, "/")
    if normalized in exact_paths:
        return True
    return any(normalized.startswith(prefix) for prefix in prefixes)


@dataclass
class ToolCallResult:
    tool_use_id: str
    content: str
    is_error: bool = False


@dataclass
class UsageTotals:
    """Accumulated token usage across every API round trip in one run_agent() call."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

    def add(self, usage: Mapping[str, Any]) -> None:
        self.input_tokens += int(usage.get("input_tokens", 0) or 0)
        self.output_tokens += int(usage.get("output_tokens", 0) or 0)
        self.cache_creation_input_tokens += int(usage.get("cache_creation_input_tokens", 0) or 0)
        self.cache_read_input_tokens += int(usage.get("cache_read_input_tokens", 0) or 0)

    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens + self.cache_creation_input_tokens + self.cache_read_input_tokens

    def estimated_cost_usd(self, model: str) -> float | None:
        """Return an estimated USD cost, or None if `model` isn't in the pricing table.

        This is an estimate for reporting only (see MODEL_PRICING_USD_PER_MTOK) --
        it is never authoritative. Check the Anthropic Console for real billed
        usage; this exists so a course creator deciding whether to run the
        pilot has a number to look at before they do, not so anyone can skip
        checking their actual invoice.
        """
        rates = MODEL_PRICING_USD_PER_MTOK.get(model)
        if rates is None:
            return None
        return (
            self.input_tokens * rates["input"]
            + self.output_tokens * rates["output"]
            + self.cache_creation_input_tokens * rates["cache_write_5m"]
            + self.cache_read_input_tokens * rates["cache_read"]
        ) / 1_000_000

    def as_dict(self, model: str) -> dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
            "total_tokens": self.total_tokens(),
            "estimated_cost_usd": self.estimated_cost_usd(model),
        }


@dataclass
class AgentRun:
    """Outcome of one run_agent() call -- author or reviewer."""

    phase: str
    role: str
    model: str
    transcript: list[dict[str, Any]] = field(default_factory=list)
    finished: bool = False
    finish_payload: dict[str, Any] | None = None
    files_written: list[str] = field(default_factory=list)
    usage: UsageTotals = field(default_factory=UsageTotals)


class RepoTools:
    """Implements the small set of tools exposed to the model.

    `role` gates which tools are actually offered: authors get write_file and
    finish_phase, reviewers get submit_review instead of write access.

    `github_request`/`github_repository` are only required when `phase` is in
    PHASES_WITH_GITHUB_ISSUES. They stay optional constructor args (rather
    than always-on) so every other phase's tests keep working without a
    GitHub token or network access -- the same reasoning `transport` in
    `run_agent()` already follows for the Anthropic call.
    """

    def __init__(
        self,
        root: Path,
        phase: str,
        role: str,
        github_request: RequestJson | None = None,
        github_repository: str | None = None,
    ) -> None:
        self.root = root
        self.phase = phase
        self.role = role
        self.files_written: list[str] = []
        self.finish_payload: dict[str, Any] | None = None
        self.finished = False
        self.github_request = github_request
        self.github_repository = github_repository
        self._issue_summaries: dict[int, dict[str, Any]] | None = None
        self.labels_applied: list[tuple[int, str]] = []
        self._last_candidate_resolution_state: str | None = None

    def read_file(self, path: str) -> str:
        target = normalize_relative_path(self.root, path)
        if not target.is_file():
            raise AllowlistViolation(f"no such file: {path!r}")
        return target.read_text(encoding="utf-8")

    def compute_sha256(self, path: str) -> str:
        """Return the real sha256 of a file's exact current bytes.

        Exists so the reviewer never has to guess or invent a fingerprint --
        docs/review-framework.md binds review approval to exact byte
        fingerprints specifically so a stale review can't authorize a changed
        output; a model-generated hex string that merely looks like a sha256
        defeats that guarantee silently.
        """
        target = normalize_relative_path(self.root, path)
        if not target.is_file():
            raise AllowlistViolation(f"no such file: {path!r}")
        return sha256(target.read_bytes()).hexdigest()

    def list_dir(self, path: str) -> str:
        target = normalize_relative_path(self.root, path or ".")
        if not target.is_dir():
            raise AllowlistViolation(f"no such directory: {path!r}")
        entries = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
        return "\n".join(entries) if entries else "(empty)"

    def _require_github(self) -> tuple[RequestJson, str]:
        if self.phase not in PHASES_WITH_GITHUB_ISSUES:
            raise AllowlistViolation(f"GitHub Issues tools are not available for phase {self.phase!r}")
        if self.github_request is None or not self.github_repository:
            raise AllowlistViolation(
                "GitHub Issues tools are enabled for this phase but no github_request/"
                "github_repository was configured -- this is a harness wiring bug, not a "
                "model error"
            )
        return self.github_request, self.github_repository

    def list_intake_issues(self) -> str:
        """List open, non-PR issues carrying the discovery label, instance repo only.

        Fetches summaries only (number, title, labels, author, created_at) --
        never the body -- to keep this read cheap. `read_github_issue` fetches
        one full issue when the model actually needs its rendered body.
        Results are cached on this instance so `resolve_intake_candidates` can
        reuse them without a second API round trip in the same run.
        """
        request_json, repository = self._require_github()
        raw = request_json(
            "GET",
            f"/repos/{repository}/issues?labels={DISCOVERY_LABEL}&state=all&per_page=100",
            None,
        )
        summaries: dict[int, dict[str, Any]] = {}
        for item in raw or []:
            summaries[item["number"]] = {
                "number": item["number"],
                "title": item.get("title", ""),
                "labels": [label.get("name", "") for label in item.get("labels", [])],
                "author_login": (item.get("user") or {}).get("login"),
                "is_pull_request": "pull_request" in item,
                "created_at": item.get("created_at"),
            }
        self._issue_summaries = summaries
        return json.dumps(list(summaries.values()), indent=2)

    def read_github_issue(self, number: int) -> str:
        """Fetch one issue's full rendered body plus its identity fields."""
        request_json, repository = self._require_github()
        item = request_json("GET", f"/repos/{repository}/issues/{number}", None)
        return json.dumps(
            {
                "number": item["number"],
                "title": item.get("title", ""),
                "body": item.get("body") or "",
                "labels": [label.get("name", "") for label in item.get("labels", [])],
                "author_login": (item.get("user") or {}).get("login"),
                "is_pull_request": "pull_request" in item,
                "created_at": item.get("created_at"),
            },
            indent=2,
        )

    def resolve_intake_candidates(
        self,
        expected_headings: list[str],
        required_response_headings: list[str],
        consent_heading: str,
    ) -> str:
        """Run the real scripts/intake_resolution.py classification, not a model guess.

        instructions/10-intake.md requires applying this exact algorithm and
        forbids replacing it with similarity or newest-issue heuristics; doing
        the classification here in Python, from data the model cannot edit,
        makes that requirement structural instead of advisory. The model
        still supplies expected_headings/required_response_headings/
        consent_heading because those come from reading the checked-in form
        contract (.github/ISSUE_TEMPLATE/create-study-path.yml via read_file),
        which is exactly the "current repository form contract, not a hidden
        comment" the instruction requires -- the harness does not duplicate
        that YAML parsing.

        allowed_authors and imported_references are resolved by the harness
        itself: allowed_authors from the known instance owner in
        .open-study-path/instance.yml when present, imported_references from
        state/intake-summary.json.source_reference when present. The model
        never supplies either -- both are used to reject candidates, and a
        model-supplied allowlist could be used to admit one instead.
        """
        request_json, repository = self._require_github()
        if self._issue_summaries is None:
            self.list_intake_issues()
        assert self._issue_summaries is not None

        allowed_authors = self._known_instance_owner()
        imported_references = self._known_imported_references()

        candidates: list[IntakeIssue] = []
        for summary in self._issue_summaries.values():
            if summary["is_pull_request"] or IMPORTED_LABEL in summary["labels"]:
                # No need to fetch the body for something already excluded by
                # a cheap identity check -- saves an API call per stale issue.
                candidates.append(
                    IntakeIssue(
                        number=summary["number"],
                        title=summary["title"],
                        body="",
                        labels=frozenset(summary["labels"]),
                        is_pull_request=summary["is_pull_request"],
                        source_reference=f"github_issue:{repository}#{summary['number']}",
                        author_login=summary["author_login"],
                    )
                )
                continue
            full = json.loads(self.read_github_issue(summary["number"]))
            candidates.append(
                IntakeIssue(
                    number=full["number"],
                    title=full["title"],
                    body=full["body"],
                    labels=frozenset(full["labels"]),
                    is_pull_request=full["is_pull_request"],
                    source_reference=f"github_issue:{repository}#{full['number']}",
                    author_login=full["author_login"],
                )
            )

        resolution = resolve_candidates(
            candidates,
            expected_headings,
            imported_references,
            required_response_headings=required_response_headings,
            consent_heading=consent_heading or None,
            allowed_authors=allowed_authors,
        )
        self._last_candidate_resolution_state = resolution.state
        return json.dumps(
            {
                "state": resolution.state,
                "accepted": [decision.__dict__ for decision in resolution.accepted],
                "rejected": [decision.__dict__ for decision in resolution.rejected],
            },
            indent=2,
        )

    def _known_instance_owner(self) -> list[str]:
        marker = normalize_relative_path(self.root, ".open-study-path/instance.yml")
        if not marker.is_file():
            return []
        import yaml  # local import: keep base module dependency-free for offline tests

        data = yaml.safe_load(marker.read_text(encoding="utf-8")) or {}
        owner = (data.get("owner") or {}).get("github_login") if isinstance(data.get("owner"), dict) else None
        return [owner] if owner else []

    def _known_imported_references(self) -> list[str]:
        summary_path = normalize_relative_path(self.root, "state/intake-summary.json")
        if not summary_path.is_file():
            return []
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        reference = data.get("source_reference")
        return [reference] if reference else []

    def label_github_issue(self, number: int, label: str) -> str:
        if self.role != "author":
            raise AllowlistViolation("label_github_issue is not available to this role")
        if label != INTAKE_AUTHOR_ALLOWED_LABEL:
            raise AllowlistViolation(
                f"refusing to apply label {label!r}: the intake author may only apply "
                f"{INTAKE_AUTHOR_ALLOWED_LABEL!r}"
            )
        request_json, repository = self._require_github()
        request_json("POST", f"/repos/{repository}/issues/{number}/labels", {"labels": [label]})
        self.labels_applied.append((number, label))
        return f"applied label {label!r} to issue #{number}"

    def write_file(self, path: str, content: str) -> str:
        if self.role != "author":
            raise AllowlistViolation("write_file is not available to this role")
        if not is_write_allowed(self.phase, path):
            raise AllowlistViolation(
                f"{path!r} is outside the allowed setup diff for phase {self.phase!r} "
                "(instructions/02-setup-execution.md); refusing to write it"
            )
        if (
            self.phase == "intake"
            and path.replace(os.sep, "/") == "state/intake-summary.json"
            and self._last_candidate_resolution_state != "unique"
        ):
            # instructions/10-intake.md never authorizes an intake write
            # without exactly one accepted candidate. A prompt note is not
            # enough on its own -- an earlier real dispatch (Etapa 4,
            # docs/claude-agent-pilot-etapa4.md section 5.2) showed the model
            # using this path as an ad hoc status scratchpad in the
            # `ambiguous` state instead of leaving it untouched. Enforcing it
            # here means that failure mode can no longer happen silently,
            # regardless of what the prompt says.
            raise AllowlistViolation(
                "refusing to write state/intake-summary.json: resolve_intake_candidates "
                f"must return state='unique' first (last observed state: "
                f"{self._last_candidate_resolution_state!r}). For 'none' or 'ambiguous', "
                "report the outcome through finish_phase instead of writing this file."
            )
        target = normalize_relative_path(self.root, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.files_written.append(path)
        return f"wrote {len(content)} bytes to {path}"

    def finish_phase(self, summary: str, next_action: str) -> str:
        if self.role != "author":
            raise AllowlistViolation("finish_phase is not available to this role")
        self.finished = True
        self.finish_payload = {"summary": summary, "next_action": next_action}
        return "phase marked finished"

    def submit_review(self, review_yaml: str, status: str, blocking_findings: list[str]) -> str:
        if self.role != "reviewer":
            raise AllowlistViolation("submit_review is not available to this role")
        if status not in ("approved", "action_required"):
            raise AllowlistViolation(f"invalid review status: {status!r}")
        if status == "approved" and blocking_findings:
            raise AllowlistViolation("cannot submit status=approved with non-empty blocking_findings")
        self.finished = True
        self.finish_payload = {
            "review_yaml": review_yaml,
            "status": status,
            "blocking_findings": list(blocking_findings),
        }
        return "review recorded"

    def dispatch(self, name: str, tool_input: Mapping[str, Any]) -> str:
        if name == "read_file":
            return self.read_file(tool_input["path"])
        if name == "list_dir":
            return self.list_dir(tool_input.get("path", "."))
        if name == "compute_sha256":
            return self.compute_sha256(tool_input["path"])
        if name == "write_file":
            return self.write_file(tool_input["path"], tool_input["content"])
        if name == "finish_phase":
            return self.finish_phase(tool_input["summary"], tool_input["next_action"])
        if name == "submit_review":
            return self.submit_review(
                tool_input["review_yaml"],
                tool_input["status"],
                tool_input.get("blocking_findings", []),
            )
        if name == "list_intake_issues":
            return self.list_intake_issues()
        if name == "read_github_issue":
            return self.read_github_issue(tool_input["number"])
        if name == "resolve_intake_candidates":
            return self.resolve_intake_candidates(
                tool_input["expected_headings"],
                tool_input.get("required_response_headings", []),
                tool_input.get("consent_heading", ""),
            )
        if name == "label_github_issue":
            return self.label_github_issue(tool_input["number"], tool_input["label"])
        raise AllowlistViolation(f"unknown tool: {name}")


def _github_issue_read_tools() -> list[dict[str, Any]]:
    """Read-only GitHub Issues tools, shared by both author_tools() and reviewer_tools()."""
    return [
        {
            "name": "list_intake_issues",
            "description": (
                "List open, non-PR issues carrying the intake discovery label in the instance "
                "repository (resolved from GITHUB_REPOSITORY, never user input). Returns "
                "summaries only (no body) -- use read_github_issue for one issue's full body."
            ),
            "input_schema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "read_github_issue",
            "description": "Fetch one GitHub issue's full rendered body, title, labels and author, by number.",
            "input_schema": {
                "type": "object",
                "properties": {"number": {"type": "integer"}},
                "required": ["number"],
            },
        },
    ]


def author_tools(phase: str | None = None) -> list[dict[str, Any]]:
    tools = [
        {
            "name": "read_file",
            "description": "Read a UTF-8 text file from the repository, path relative to repo root.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
        {
            "name": "list_dir",
            "description": "List entries of a directory, path relative to repo root.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": [],
            },
        },
        {
            "name": "write_file",
            "description": (
                "Write a UTF-8 text file, path relative to repo root. Only paths in the "
                "phase's allowed domain-output list are accepted; anything else is rejected."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
        {
            "name": "finish_phase",
            "description": "Call once all required files are written, to end the author run.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "next_action": {"type": "string"},
                },
                "required": ["summary", "next_action"],
            },
        },
    ]
    if phase in PHASES_WITH_GITHUB_ISSUES:
        tools.extend(_github_issue_read_tools())
        tools.append(
            {
                "name": "resolve_intake_candidates",
                "description": (
                    "Deterministically classify every open candidate issue using the real "
                    "scripts/intake_resolution.py algorithm -- never classify candidates "
                    "yourself. Pass expected_headings, required_response_headings and "
                    "consent_heading exactly as read from "
                    ".github/ISSUE_TEMPLATE/create-study-path.yml via read_file. "
                    "allowed_authors and already-imported references are resolved by the "
                    "harness itself from repository state, not supplied by you."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expected_headings": {"type": "array", "items": {"type": "string"}},
                        "required_response_headings": {"type": "array", "items": {"type": "string"}},
                        "consent_heading": {"type": "string"},
                    },
                    "required": ["expected_headings"],
                },
            }
        )
        tools.append(
            {
                "name": "label_github_issue",
                "description": (
                    f"Apply a label to a GitHub issue. Only {INTAKE_AUTHOR_ALLOWED_LABEL!r} is "
                    "accepted -- call this only once, on the accepted candidate's issue number, "
                    "after every domain-output file has been written."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "number": {"type": "integer"},
                        "label": {"type": "string"},
                    },
                    "required": ["number", "label"],
                },
            }
        )
    return tools


def reviewer_tools(phase: str | None = None) -> list[dict[str, Any]]:
    tools = [
        {
            "name": "read_file",
            "description": "Read a UTF-8 text file from the repository, path relative to repo root.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
        {
            "name": "list_dir",
            "description": "List entries of a directory, path relative to repo root.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": [],
            },
        },
        {
            "name": "compute_sha256",
            "description": (
                "Compute the real sha256 of a file's exact current bytes, path relative to "
                "repo root. Always use this for the 'artifacts[].sha256' fields in the review "
                "document -- never write a hex string from memory or estimation."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
        {
            "name": "submit_review",
            "description": (
                "Submit the final review verdict matching templates/review.yml. "
                "status='approved' requires blocking_findings to be empty."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "review_yaml": {"type": "string"},
                    "status": {"type": "string", "enum": ["approved", "action_required"]},
                    "blocking_findings": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["review_yaml", "status"],
            },
        },
    ]
    if phase in PHASES_WITH_GITHUB_ISSUES:
        # Reviewer gets read-only issue access -- enough to independently
        # re-fetch the source issue and compare its rendered fields against
        # what the author normalized, but never label_github_issue: the
        # reviewer must never be able to cause the external side effect it is
        # supposed to be checking.
        tools.extend(_github_issue_read_tools())
    return tools


def anthropic_transport(payload: Mapping[str, Any], api_key: str) -> dict[str, Any]:
    """Real HTTP transport. Kept dependency-free (urllib) like the rest of the repo's scripts."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Anthropic API error {error.code}: {detail}") from error


def _with_trailing_cache_breakpoint(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a copy of `messages` with a cache_control breakpoint on the last content block.

    Anthropic's prompt caching reuses everything up to (and including) a
    cache_control breakpoint on a subsequent call, provided the prefix is
    byte-identical. In a tool-use loop the message list only ever grows by
    appending, so marking the *last* block on every outgoing request means
    each round's newly-added content becomes the next round's cached prefix
    -- the growing history is paid for once, not resent at full price on
    every one of MAX_TOOL_ITERATIONS round trips. Without this, a run's
    total input tokens scale roughly with the square of its round-trip
    count; with it, they scale roughly linearly.

    Only the outgoing copy is touched; the caller's own `messages` list,
    which the loop keeps appending to, is left without cache_control keys.
    """
    if not messages:
        return messages
    copied = [dict(message) for message in messages]
    last = copied[-1]
    content = last["content"]
    if isinstance(content, str):
        last["content"] = [{"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}]
    elif isinstance(content, list) and content:
        content = [dict(block) for block in content]
        content[-1] = {**content[-1], "cache_control": {"type": "ephemeral"}}
        last["content"] = content
    return copied


def run_agent(
    *,
    root: Path,
    phase: str,
    role: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str | None = None,
    transport: Callable[[Mapping[str, Any], str], dict[str, Any]] = anthropic_transport,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    github_request: RequestJson | None = None,
    github_repository: str | None = None,
) -> AgentRun:
    """Run one author or reviewer agent call to completion (or until the budget runs out).

    Returns an AgentRun with the full transcript for logging/debugging plus the
    structured finish_payload the caller (author -> commit+PR, reviewer ->
    state/reviews/*.yml) needs to act on.

    `github_request`/`github_repository` are only consulted when `phase` is in
    PHASES_WITH_GITHUB_ISSUES; every other phase ignores them, same as `role`
    ignoring `transport`'s implementation details.
    """
    if role not in ("author", "reviewer"):
        raise ValueError(f"unknown role: {role}")

    tools = RepoTools(
        root=root,
        phase=phase,
        role=role,
        github_request=github_request,
        github_repository=github_repository,
    )
    tool_schemas = author_tools(phase) if role == "author" else reviewer_tools(phase)

    messages: list[dict[str, Any]] = [{"role": "user", "content": user_prompt}]
    run = AgentRun(phase=phase, role=role, model=model)

    # The system prompt is identical on every round trip of this loop, so it
    # gets its own permanent cache breakpoint -- separate from the messages
    # breakpoint above, which moves forward each round as the conversation grows.
    system_blocks = [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]

    for _ in range(MAX_TOOL_ITERATIONS):
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system_blocks,
            "messages": _with_trailing_cache_breakpoint(messages),
            "tools": tool_schemas,
        }
        response = transport(payload, api_key or "")
        run.transcript.append({"role": "assistant_response", "content": response.get("content", [])})
        if "usage" in response:
            run.usage.add(response["usage"])
        content = response.get("content", [])
        messages.append({"role": "assistant", "content": content})

        tool_use_blocks = [block for block in content if block.get("type") == "tool_use"]
        if not tool_use_blocks:
            break

        tool_results: list[dict[str, Any]] = []
        for block in tool_use_blocks:
            try:
                result_text = tools.dispatch(block["name"], block.get("input", {}))
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": result_text,
                    }
                )
            except (AllowlistViolation, KeyError) as error:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": str(error),
                        "is_error": True,
                    }
                )
        messages.append({"role": "user", "content": tool_results})
        run.transcript.append({"role": "tool_results", "content": tool_results})

        if tools.finished:
            break
    else:
        raise AgentBudgetExceeded(
            f"{role} agent for phase {phase!r} did not finish within {MAX_TOOL_ITERATIONS} tool round trips"
        )

    run.finished = tools.finished
    run.finish_payload = tools.finish_payload
    run.files_written = tools.files_written
    return run


def _load_models_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {"version": 1, "reasoning_tier": "recommended", "model_overrides": {}}
    import yaml  # local import: keep base module dependency-free for tests

    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=["author", "reviewer"])
    parser.add_argument("--phase", required=True, choices=sorted(PHASE_ALLOWLISTS))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--system-prompt-file", required=True)
    parser.add_argument("--user-prompt-file", required=True)
    parser.add_argument("--models-config", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Resolve the model and exit without calling the API")
    args = parser.parse_args(argv)

    config = _load_models_config(args.models_config)
    if args.role == "author":
        agent_id = PHASE_AUTHOR_AGENT[args.phase]
        model = resolve_effective_models(config)[agent_id].model
    else:
        model = resolve_phase_reviewer_model(args.phase, config)

    if args.dry_run:
        print(f"role={args.role} phase={args.phase} model={model}")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY is not set")

    github_request: RequestJson | None = None
    github_repository: str | None = None
    if args.phase in PHASES_WITH_GITHUB_ISSUES:
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise SystemExit(f"GITHUB_TOKEN is not set (required for phase {args.phase!r})")
        # Deliberately GITHUB_REPOSITORY, the Actions-provided identity of the
        # repository this workflow run belongs to -- never a CLI flag or
        # workflow_dispatch input. See the module docstring and
        # RepoTools._require_github for why that boundary matters.
        github_repository = os.environ.get("GITHUB_REPOSITORY")
        if not github_repository:
            raise SystemExit(f"GITHUB_REPOSITORY is not set (required for phase {args.phase!r})")
        github_api_url = os.environ.get("GITHUB_API_URL", GITHUB_API_URL_DEFAULT)
        github_request = github_request_factory(github_token, github_api_url)

    run = run_agent(
        root=Path(args.repo_root),
        phase=args.phase,
        role=args.role,
        model=model,
        system_prompt=_read_text(args.system_prompt_file),
        user_prompt=_read_text(args.user_prompt_file),
        api_key=api_key,
        github_request=github_request,
        github_repository=github_repository,
    )

    if not run.finished:
        raise SystemExit(f"{args.role} agent did not call its finish tool")

    output = dict(run.finish_payload or {})
    output["model"] = model
    output["usage"] = run.usage.as_dict(model)
    print(json.dumps(output, indent=2))

    if run.files_written:
        print("files written:", ", ".join(run.files_written), file=sys.stderr)

    cost = run.usage.estimated_cost_usd(model)
    cost_str = f"${cost:.4f}" if cost is not None else "unknown (model not in local pricing table)"
    print(
        f"usage: {run.usage.input_tokens} input + {run.usage.output_tokens} output "
        f"+ {run.usage.cache_creation_input_tokens} cache-write + {run.usage.cache_read_input_tokens} cache-read "
        f"tokens -- estimated cost {cost_str} (model={model})",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
