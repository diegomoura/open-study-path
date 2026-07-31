#!/usr/bin/env python3
"""Behavioral regressions for curriculum proposal and generation state."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from curriculum_state import validate_repository


MANIFEST = """version: 1
phases:
  - id: diagnostic
    next_phase: propose
  - id: propose
    instruction: instructions/28-propose-path.md
    review_profile: curriculum
    merge_policy_path: workflow.curriculum_merge_policy
    next_phase: generate
  - id: generate
    depends_on: [propose]
"""

PROPOSAL = """Abra um pull request
This wording does not create an implicit learner-approval gate.
Não publique tarefas ainda
curriculum_approved: true
agent_review_then_merge
Crie minha trilha de estudos.
"""

ROADMAP = """# Trilha

```mermaid
flowchart LR
  TOPIC-001 --> TOPIC-002
```
"""


def write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def instance(*, proposed: bool, approved: bool, generated: bool) -> str:
    return f"""kind: open-study-path-instance
status:
  curriculum_proposed: {str(proposed).lower()}
  curriculum_approved: {str(approved).lower()}
  curriculum_generated: {str(generated).lower()}
"""


def base_repository(root: Path) -> None:
    write(root, "instructions/manifest.yml", MANIFEST)
    write(root, "instructions/28-propose-path.md", PROPOSAL)


def test_unreviewed_proposal_state_is_rejected() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        base_repository(root)
        write(root, ".open-study-path/instance.yml", instance(proposed=True, approved=False, generated=False))
        write(root, "study/roadmap.md", ROADMAP)
        errors = validate_repository(root)
        assert any("must become true together" in error for error in errors), errors


def test_reviewed_proposal_without_topics_is_valid() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        base_repository(root)
        write(root, ".open-study-path/instance.yml", instance(proposed=True, approved=True, generated=False))
        write(root, "study/roadmap.md", ROADMAP)
        assert validate_repository(root) == ()


def test_topics_cannot_be_left_in_partial_generation() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        base_repository(root)
        write(root, ".open-study-path/instance.yml", instance(proposed=True, approved=True, generated=False))
        write(root, "study/roadmap.md", ROADMAP)
        write(root, "study/topics/TOPIC-001.md", "---\nid: TOPIC-001\n---\n")
        errors = validate_repository(root)
        assert any("complete the generation operation" in error for error in errors), errors


def test_generated_curriculum_requires_contracts_and_plan() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        base_repository(root)
        write(root, ".open-study-path/instance.yml", instance(proposed=True, approved=True, generated=True))
        write(root, "study/roadmap.md", ROADMAP)
        errors = validate_repository(root)
        assert any("requires topic contracts" in error for error in errors), errors
        assert any("requires study/integrations.md" in error for error in errors), errors


def main() -> None:
    test_unreviewed_proposal_state_is_rejected()
    test_reviewed_proposal_without_topics_is_valid()
    test_topics_cannot_be_left_in_partial_generation()
    test_generated_curriculum_requires_contracts_and_plan()
    print("Curriculum proposal state regressions passed.")


if __name__ == "__main__":
    main()
