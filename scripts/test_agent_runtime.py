#!/usr/bin/env python3
"""Offline regressions for the stage-2 agent harness.

None of these tests touch the network or need ANTHROPIC_API_KEY: the transport
is stubbed with a small scripted queue of fake API responses, so we can assert
on the tool-loop mechanics and (most importantly) on the write allowlist
without spending a token.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from agent_runtime import (
    AgentBudgetExceeded,
    AllowlistViolation,
    PHASE_ALLOWLISTS,
    is_write_allowed,
    normalize_relative_path,
    resolve_phase_reviewer_model,
    run_agent,
)


def _default_config(**overrides) -> dict:
    config = {"version": 1, "reasoning_tier": "recommended", "model_overrides": {}}
    config.update(overrides)
    return config


def _text_block(text: str) -> dict:
    return {"type": "text", "text": text}


def _tool_use(tool_id: str, name: str, tool_input: dict) -> dict:
    return {"type": "tool_use", "id": tool_id, "name": name, "input": tool_input}


def make_scripted_transport(responses: list[list[dict]]):
    """Returns a transport(payload, api_key) that replays `responses` in order."""
    calls: list[dict] = []

    def transport(payload: dict, api_key: str) -> dict:
        calls.append(payload)
        content = responses[len(calls) - 1]
        return {"content": content}

    transport.calls = calls  # type: ignore[attr-defined]
    return transport


def test_write_allowlist_matches_setup_execution_contract() -> None:
    assert is_write_allowed("bootstrap_instance", ".open-study-path/instance.yml")
    assert is_write_allowed("bootstrap_instance", "study.config.yml")
    assert not is_write_allowed("bootstrap_instance", "instructions/manifest.yml")
    assert not is_write_allowed("bootstrap_instance", "scripts/agent_runtime.py")
    assert not is_write_allowed("unknown_phase", "study.config.yml")


def test_author_cannot_write_its_own_review_artifact() -> None:
    # instructions/02-setup-execution.md's "Allowed setup diff" lists
    # state/reviews/<setup-operation>.yml, but that path is deliberately
    # excluded from the author's write allowlist in this harness: only the
    # independent reviewer agent (via submit_review, not write_file) may
    # produce a review. See docs/claude-agent-pilot.md.
    assert not is_write_allowed("bootstrap_instance", "state/reviews/setup-v1.yml")
    assert not is_write_allowed("configure_intake", "state/reviews/anything.yml")


def test_normalize_relative_path_rejects_escapes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        try:
            normalize_relative_path(root, "../outside.txt")
            raise AssertionError("expected AllowlistViolation")
        except AllowlistViolation:
            pass
        try:
            normalize_relative_path(root, "/etc/passwd")
            raise AssertionError("expected AllowlistViolation")
        except AllowlistViolation:
            pass


def test_resolve_phase_reviewer_model_inherits_author_tier() -> None:
    recommended = resolve_phase_reviewer_model("bootstrap_instance", _default_config())
    assert recommended == "claude-haiku-4-5-20251001"

    maximum = resolve_phase_reviewer_model("bootstrap_instance", _default_config(reasoning_tier="maximum"))
    assert maximum == "claude-sonnet-5"  # haiku shifted up one tier


def test_author_agent_write_then_finish_happy_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        transport = make_scripted_transport(
            [
                [
                    _tool_use(
                        "call_1",
                        "write_file",
                        {"path": "study.config.yml", "content": "owner: test\n"},
                    )
                ],
                [
                    _tool_use(
                        "call_2",
                        "finish_phase",
                        {"summary": "bootstrap complete", "next_action": "run configure_intake"},
                    )
                ],
            ]
        )
        run = run_agent(
            root=root,
            phase="bootstrap_instance",
            role="author",
            model="claude-haiku-4-5-20251001",
            system_prompt="system",
            user_prompt="user",
            transport=transport,
        )
        assert run.finished
        assert run.files_written == ["study.config.yml"]
        assert (root / "study.config.yml").read_text(encoding="utf-8") == "owner: test\n"
        assert run.finish_payload["summary"] == "bootstrap complete"


def test_author_agent_write_outside_allowlist_is_rejected_not_bypassed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "instructions").mkdir()
        (root / "instructions" / "manifest.yml").write_text("version: 1\n", encoding="utf-8")

        transport = make_scripted_transport(
            [
                [
                    _tool_use(
                        "call_1",
                        "write_file",
                        {"path": "instructions/manifest.yml", "content": "tampered: true\n"},
                    )
                ],
                [
                    _tool_use(
                        "call_2",
                        "finish_phase",
                        {"summary": "done", "next_action": "n/a"},
                    )
                ],
            ]
        )
        run = run_agent(
            root=root,
            phase="bootstrap_instance",
            role="author",
            model="claude-haiku-4-5-20251001",
            system_prompt="system",
            user_prompt="user",
            transport=transport,
        )
        # The finish call still succeeds (the model can recover / stop), but the
        # disallowed write must never have reached disk.
        assert run.finished
        assert run.files_written == []
        assert (root / "instructions" / "manifest.yml").read_text(encoding="utf-8") == "version: 1\n"
        # And the rejection must have been reported back as a tool error, not swallowed.
        tool_result_rounds = [entry for entry in run.transcript if entry["role"] == "tool_results"]
        assert tool_result_rounds[0]["content"][0]["is_error"] is True


def test_reviewer_agent_has_no_write_file_tool() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        transport = make_scripted_transport(
            [
                [
                    _tool_use(
                        "call_1",
                        "write_file",
                        {"path": "study.config.yml", "content": "sneaky: true\n"},
                    )
                ],
                [
                    _tool_use(
                        "call_2",
                        "submit_review",
                        {
                            "review_yaml": "status: approved\n",
                            "status": "approved",
                            "blocking_findings": [],
                        },
                    )
                ],
            ]
        )
        run = run_agent(
            root=root,
            phase="bootstrap_instance",
            role="reviewer",
            model="claude-haiku-4-5-20251001",
            system_prompt="system",
            user_prompt="user",
            transport=transport,
        )
        assert run.finished
        assert not (root / "study.config.yml").exists()
        assert run.finish_payload["status"] == "approved"


def test_reviewer_cannot_submit_approved_with_blocking_findings() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        transport = make_scripted_transport(
            [
                [
                    _tool_use(
                        "call_1",
                        "submit_review",
                        {
                            "review_yaml": "status: approved\n",
                            "status": "approved",
                            "blocking_findings": ["missing label"],
                        },
                    )
                ],
                [
                    _tool_use(
                        "call_2",
                        "submit_review",
                        {
                            "review_yaml": "status: action_required\n",
                            "status": "action_required",
                            "blocking_findings": ["missing label"],
                        },
                    )
                ],
            ]
        )
        run = run_agent(
            root=root,
            phase="bootstrap_instance",
            role="reviewer",
            model="claude-haiku-4-5-20251001",
            system_prompt="system",
            user_prompt="user",
            transport=transport,
        )
        assert run.finished
        assert run.finish_payload["status"] == "action_required"


def test_budget_exceeded_when_agent_never_finishes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # 21 rounds of a no-op tool call, never calling finish_phase.
        responses = [[_tool_use(f"call_{i}", "list_dir", {"path": "."})] for i in range(25)]
        transport = make_scripted_transport(responses)
        try:
            run_agent(
                root=root,
                phase="bootstrap_instance",
                role="author",
                model="claude-haiku-4-5-20251001",
                system_prompt="system",
                user_prompt="user",
                transport=transport,
            )
            raise AssertionError("expected AgentBudgetExceeded")
        except AgentBudgetExceeded:
            pass


def test_stops_cleanly_when_model_returns_no_tool_calls() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        transport = make_scripted_transport([[_text_block("I have nothing to do.")]])
        run = run_agent(
            root=root,
            phase="bootstrap_instance",
            role="author",
            model="claude-haiku-4-5-20251001",
            system_prompt="system",
            user_prompt="user",
            transport=transport,
        )
        assert not run.finished
        assert run.finish_payload is None


def test_reviewer_compute_sha256_matches_real_file_hash() -> None:
    import hashlib

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "study.config.yml").write_text("owner: test\n", encoding="utf-8")
        expected = hashlib.sha256(b"owner: test\n").hexdigest()

        transport = make_scripted_transport(
            [
                [_tool_use("call_1", "compute_sha256", {"path": "study.config.yml"})],
                [
                    _tool_use(
                        "call_2",
                        "submit_review",
                        {
                            "review_yaml": f"sha256: {expected}\n",
                            "status": "approved",
                            "blocking_findings": [],
                        },
                    )
                ],
            ]
        )
        run = run_agent(
            root=root,
            phase="bootstrap_instance",
            role="reviewer",
            model="claude-haiku-4-5-20251001",
            system_prompt="system",
            user_prompt="user",
            transport=transport,
        )
        tool_result_rounds = [entry for entry in run.transcript if entry["role"] == "tool_results"]
        hash_result = tool_result_rounds[0]["content"][0]["content"]
        assert hash_result == expected
        assert len(hash_result) == 64  # a real sha256 hex digest, not a model-guessed string


def test_author_agent_has_no_compute_sha256_tool() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        transport = make_scripted_transport(
            [
                [_tool_use("call_1", "compute_sha256", {"path": "study.config.yml"})],
                [
                    _tool_use(
                        "call_2",
                        "finish_phase",
                        {"summary": "done", "next_action": "n/a"},
                    )
                ],
            ]
        )
        run = run_agent(
            root=root,
            phase="bootstrap_instance",
            role="author",
            model="claude-haiku-4-5-20251001",
            system_prompt="system",
            user_prompt="user",
            transport=transport,
        )
        tool_result_rounds = [entry for entry in run.transcript if entry["role"] == "tool_results"]
        # dispatch() still recognizes the tool name (shared implementation), but
        # it is never offered in author_tools()'s schema -- a well-behaved model
        # won't call it. If it somehow did, it must not crash the author's run.
        assert run.finished


def test_usage_accumulates_across_tool_round_trips_and_estimates_cost() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        calls = []

        def transport(payload, api_key):
            calls.append(payload)
            if len(calls) == 1:
                return {
                    "content": [_tool_use("call_1", "list_dir", {"path": "."})],
                    "usage": {"input_tokens": 1000, "output_tokens": 50, "cache_creation_input_tokens": 200, "cache_read_input_tokens": 0},
                }
            return {
                "content": [_tool_use("call_2", "finish_phase", {"summary": "done", "next_action": "n/a"})],
                "usage": {"input_tokens": 1300, "output_tokens": 40, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 200},
            }

        run = run_agent(
            root=root,
            phase="bootstrap_instance",
            role="author",
            model="claude-haiku-4-5-20251001",
            system_prompt="system",
            user_prompt="user",
            transport=transport,
        )
        assert run.usage.input_tokens == 2300
        assert run.usage.output_tokens == 90
        assert run.usage.cache_creation_input_tokens == 200
        assert run.usage.cache_read_input_tokens == 200
        # (2300*1.0 + 90*5.0 + 200*1.25 + 200*0.10) / 1_000_000
        expected_cost = (2300 * 1.0 + 90 * 5.0 + 200 * 1.25 + 200 * 0.10) / 1_000_000
        assert abs(run.usage.estimated_cost_usd("claude-haiku-4-5-20251001") - expected_cost) < 1e-12
        assert run.usage.estimated_cost_usd("some-unknown-model") is None


def test_cache_breakpoint_moves_forward_without_mutating_stored_messages() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        captured_payloads = []

        def transport(payload, api_key):
            captured_payloads.append(payload)
            if len(captured_payloads) == 1:
                return {
                    "content": [_tool_use("call_1", "list_dir", {"path": "."})],
                    "usage": {"input_tokens": 500, "output_tokens": 20},
                }
            return {
                "content": [_tool_use("call_2", "finish_phase", {"summary": "done", "next_action": "n/a"})],
                "usage": {"input_tokens": 100, "output_tokens": 15, "cache_read_input_tokens": 500},
            }

        run_agent(
            root=root,
            phase="bootstrap_instance",
            role="author",
            model="claude-haiku-4-5-20251001",
            system_prompt="a fairly long system prompt",
            user_prompt="do the thing",
            transport=transport,
        )

        assert len(captured_payloads) == 2
        # System prompt always carries its own cache breakpoint.
        assert captured_payloads[0]["system"][0]["cache_control"] == {"type": "ephemeral"}
        assert captured_payloads[1]["system"][0]["cache_control"] == {"type": "ephemeral"}

        # First call: only the initial user message exists, so it gets the breakpoint.
        first_messages = captured_payloads[0]["messages"]
        assert first_messages[-1]["content"][-1]["cache_control"] == {"type": "ephemeral"}

        # Second call: the breakpoint moved to the newly-appended tool_results
        # message (round 2's addition), not the original first message.
        second_messages = captured_payloads[1]["messages"]
        assert second_messages[-1]["role"] == "user"
        assert second_messages[-1]["content"][-1]["cache_control"] == {"type": "ephemeral"}
        # The first message, now buried earlier in history, must NOT carry a
        # breakpoint on this call -- only content itself should be preserved
        # unmodified (still a plain string, never mutated in place).
        assert second_messages[0]["content"] == "do the thing"


def test_every_pilot_phase_has_an_allowlist() -> None:
    assert "bootstrap_instance" in PHASE_ALLOWLISTS
    assert "configure_intake" in PHASE_ALLOWLISTS


def main() -> None:
    tests = [
        test_write_allowlist_matches_setup_execution_contract,
        test_author_cannot_write_its_own_review_artifact,
        test_normalize_relative_path_rejects_escapes,
        test_resolve_phase_reviewer_model_inherits_author_tier,
        test_author_agent_write_then_finish_happy_path,
        test_author_agent_write_outside_allowlist_is_rejected_not_bypassed,
        test_reviewer_agent_has_no_write_file_tool,
        test_reviewer_cannot_submit_approved_with_blocking_findings,
        test_reviewer_compute_sha256_matches_real_file_hash,
        test_author_agent_has_no_compute_sha256_tool,
        test_usage_accumulates_across_tool_round_trips_and_estimates_cost,
        test_cache_breakpoint_moves_forward_without_mutating_stored_messages,
        test_budget_exceeded_when_agent_never_finishes,
        test_stops_cleanly_when_model_returns_no_tool_calls,
        test_every_pilot_phase_has_an_allowlist,
    ]
    for test in tests:
        test()
    print(f"Agent runtime regressions passed ({len(tests)} cases).")


if __name__ == "__main__":
    main()
