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

# Which allowlist applies to which manifest phase. Only the two pilot phases
# are wired up in stage 2; extending PHASE_ALLOWLISTS is exactly the work of
# later steps in the proposal's rollout plan (section 7, steps 4-6).
PHASE_ALLOWLISTS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "bootstrap_instance": (SETUP_ALLOWED_EXACT_PATHS, SETUP_ALLOWED_PREFIXES),
    "configure_intake": (SETUP_ALLOWED_EXACT_PATHS, SETUP_ALLOWED_PREFIXES),
}

# Agent ids that exist as real rows in AGENT_CATALOG for the pilot phases.
PHASE_AUTHOR_AGENT: dict[str, str] = {
    "bootstrap_instance": "bootstrap",
    "configure_intake": "configure_intake",
}


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
    """

    def __init__(self, root: Path, phase: str, role: str) -> None:
        self.root = root
        self.phase = phase
        self.role = role
        self.files_written: list[str] = []
        self.finish_payload: dict[str, Any] | None = None
        self.finished = False

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

    def write_file(self, path: str, content: str) -> str:
        if self.role != "author":
            raise AllowlistViolation("write_file is not available to this role")
        if not is_write_allowed(self.phase, path):
            raise AllowlistViolation(
                f"{path!r} is outside the allowed setup diff for phase {self.phase!r} "
                "(instructions/02-setup-execution.md); refusing to write it"
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
        raise AllowlistViolation(f"unknown tool: {name}")


def author_tools() -> list[dict[str, Any]]:
    return [
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
                "phase's allowed setup diff are accepted; anything else is rejected."
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


def reviewer_tools() -> list[dict[str, Any]]:
    return [
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
) -> AgentRun:
    """Run one author or reviewer agent call to completion (or until the budget runs out).

    Returns an AgentRun with the full transcript for logging/debugging plus the
    structured finish_payload the caller (author -> commit+PR, reviewer ->
    state/reviews/*.yml) needs to act on.
    """
    if role not in ("author", "reviewer"):
        raise ValueError(f"unknown role: {role}")

    tools = RepoTools(root=root, phase=phase, role=role)
    tool_schemas = author_tools() if role == "author" else reviewer_tools()

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

    run = run_agent(
        root=Path(args.repo_root),
        phase=args.phase,
        role=args.role,
        model=model,
        system_prompt=_read_text(args.system_prompt_file),
        user_prompt=_read_text(args.user_prompt_file),
        api_key=api_key,
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
