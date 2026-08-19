from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from task_projection_engine import (  # noqa: E402
    AmbiguousMatchError,
    FakeBackend,
    OperationJournal,
    PartialWriteError,
    ReadbackValidationError,
    TopicProjection,
    VISIBLE_STATES,
    VisibleFields,
    apply_assessment_result,
    build_projection_plan,
    ensure_focused_review_resource,
    migrate_legacy_backend,
    normalized_integration_state,
    publish_projection,
    render_learner_integration_summary,
    roadmap_fingerprint,
    validate_readback,
    validate_visible_fields,
)


def topic(
    number: int,
    *,
    prerequisites=(),
    state="planned",
    materialized=True,
    external_id=None,
    title=None,
):
    topic_id = f"TOPIC-{number:03d}"
    return TopicProjection(
        topic_id=topic_id,
        lesson_number=number,
        title=title or f"Tema {number}",
        direct_prerequisite_ids=tuple(prerequisites),
        content_version=1 if materialized else 0,
        canonical_state=state,
        materialized=materialized,
        external_id=external_id,
        lesson_url=(f"https://github.example/aula-{number}" if materialized else None),
        slides_url=(f"https://github.example/slides-{number}.pdf" if materialized else None),
        assessment_url=(f"https://github.example/avaliacao-{number}" if materialized else None),
    )


class TaskProjectionEngineTests(unittest.TestCase):
    def base_topics(self):
        return (
            topic(1),
            topic(2),
            topic(3, prerequisites=("TOPIC-001",)),
            topic(4, materialized=False),
        )

    def test_initial_publication_multiple_lessons(self):
        backend = FakeBackend("trello")
        result = publish_projection(
            topics=self.base_topics(), backend=backend, operation_id="publication-v1"
        )
        managed = [
            item
            for item in result.normalized_snapshot["resources"]
            if item.get("managed") and item.get("kind") == "lesson"
        ]
        self.assertEqual(4, len(managed))
        self.assertEqual("success", result.journal["status"])

    def test_exactly_one_primary_and_one_parallel(self):
        plan = build_projection_plan(self.base_topics(), provider="trello")
        primary = [lesson for lesson in plan.lessons if lesson.visible_state == "Próxima aula"]
        parallel = [
            lesson
            for lesson in plan.lessons
            if lesson.visible_state == "Disponível em paralelo"
        ]
        self.assertEqual(["TOPIC-001"], [lesson.topic.topic_id for lesson in primary])
        self.assertEqual(["TOPIC-002"], [lesson.topic.topic_id for lesson in parallel])

    def test_blocked_and_unmaterialized_lessons_remain_planned(self):
        plan = build_projection_plan(self.base_topics(), provider="trello")
        states = {lesson.topic.topic_id: lesson.visible_state for lesson in plan.lessons}
        self.assertEqual("Planejado", states["TOPIC-003"])
        self.assertEqual("Planejado", states["TOPIC-004"])

    def test_orientation_is_not_counted_as_a_lesson(self):
        backend = FakeBackend("todoist")
        result = publish_projection(
            topics=self.base_topics(), backend=backend, operation_id="publication-v1"
        )
        readback = result.integration_state["projection"]["readback"]
        self.assertEqual(4, readback["lesson_card_count"])
        self.assertEqual(5, readback["managed_card_count"])

    def test_second_execution_creates_no_duplicates_or_writes(self):
        backend = FakeBackend("trello")
        first = publish_projection(
            topics=self.base_topics(), backend=backend, operation_id="publication-v1"
        )
        writes = backend.write_count
        second = publish_projection(
            topics=self.base_topics(),
            backend=backend,
            operation_id="publication-v1",
            journal_state=first.journal,
            previous_integration_state=first.integration_state,
        )
        self.assertEqual(writes, backend.write_count)
        lesson_ids = [
            item["id"]
            for item in second.normalized_snapshot["resources"]
            if item.get("kind") == "lesson"
        ]
        self.assertEqual(len(lesson_ids), len(set(lesson_ids)))

    def test_partial_failure_resumes_with_same_operation_id(self):
        backend = FakeBackend("trello", fail_after_writes=5)
        with self.assertRaises(PartialWriteError) as raised:
            publish_projection(
                topics=self.base_topics(),
                backend=backend,
                operation_id="publication-resume-v1",
            )
        journal = raised.exception.journal
        self.assertEqual("partial", journal["status"])
        backend.fail_after_writes = None
        result = publish_projection(
            topics=self.base_topics(),
            backend=backend,
            operation_id="publication-resume-v1",
            journal_state=journal,
        )
        self.assertEqual("publication-resume-v1", result.journal["operation_id"])
        self.assertEqual("success", result.journal["status"])

    def test_existing_resource_is_found_by_durable_id(self):
        durable_id = "trello-lesson-existing"
        backend = FakeBackend(
            "trello",
            resources=[
                {
                    "id": durable_id,
                    "url": "https://trello.example/existing",
                    "kind": "lesson",
                    "managed": True,
                    "visible": {"title": "Old", "description": "", "checklist": [], "managed_comments": []},
                    "internal_metadata": {},
                    "visible_state": "Planejado",
                    "student_fields": {"note": "preserve"},
                    "student_comments": ["my comment"],
                }
            ],
        )
        result = publish_projection(
            topics=(topic(1, external_id=durable_id),),
            backend=backend,
            operation_id="publication-existing-id",
        )
        lessons = [item for item in result.normalized_snapshot["resources"] if item.get("kind") == "lesson"]
        self.assertEqual([durable_id], [item["id"] for item in lessons])
        self.assertEqual("preserve", lessons[0]["student_fields"]["note"])

    def test_unique_title_match_is_adopted_without_durable_id(self):
        backend = FakeBackend(
            "todoist",
            resources=[
                {
                    "id": "todoist-task-existing",
                    "url": "https://todoist.example/existing",
                    "kind": "lesson",
                    "managed": False,
                    "visible": {
                        "title": "Aula 01 · Tema 1",
                        "description": "student text",
                        "checklist": [],
                        "managed_comments": [],
                    },
                    "internal_metadata": {},
                    "visible_state": "Planejado",
                    "student_fields": {"custom": True},
                    "student_comments": [],
                }
            ],
        )
        result = publish_projection(
            topics=(topic(1),), backend=backend, operation_id="publication-unique-match"
        )
        lessons = [item for item in result.normalized_snapshot["resources"] if item.get("kind") == "lesson"]
        self.assertEqual("todoist-task-existing", lessons[0]["id"])
        self.assertTrue(lessons[0]["student_fields"]["custom"])

    def test_ambiguous_match_blocks_all_writes(self):
        duplicate = {
            "url": "https://trello.example/existing",
            "kind": "lesson",
            "managed": False,
            "visible": {
                "title": "Aula 01 · Tema 1",
                "description": "",
                "checklist": [],
                "managed_comments": [],
            },
            "internal_metadata": {},
            "visible_state": "Planejado",
            "student_fields": {},
            "student_comments": [],
        }
        backend = FakeBackend(
            "trello",
            resources=[
                {**deepcopy(duplicate), "id": "duplicate-1"},
                {**deepcopy(duplicate), "id": "duplicate-2"},
            ],
        )
        with self.assertRaises(AmbiguousMatchError):
            publish_projection(
                topics=(topic(1),), backend=backend, operation_id="publication-ambiguous"
            )
        self.assertEqual(0, backend.write_count)

    def test_visible_validator_rejects_html_comment_and_internal_metadata(self):
        fields = VisibleFields(
            title="Aula 01",
            description=(
                '<!-- open-study-path topic_id=TOPIC-001 --> '
                '{"content_version": 1, "roadmap_fingerprint": "abc"}'
            ),
        )
        errors = validate_visible_fields(fields)
        self.assertTrue(any("HTML comment" in error for error in errors))
        self.assertTrue(any("internal topic id" in error for error in errors))
        self.assertTrue(any("content_version" in error for error in errors))

    def test_learner_summary_does_not_false_positive_on_repo_name_substring(self):
        # Real finding, documented in Etapa 6a's fixture commit and fixed in
        # Etapa 6d: render_learner_integration_summary() used to raise an
        # uncaught AssertionError whenever the container/project URL
        # contained the literal substring "open-study-path" -- which any
        # repository actually named with that product-name prefix (e.g.
        # this pilot's own disposable test repos) always does in its URL,
        # even though nothing was leaking. The real marker syntax always has
        # a colon immediately after ("open-study-path:topic_id=..."); a bare
        # repository name never does.
        state = {
            "selected_capabilities": {"task_manager": {"provider": "github_issues"}},
            "resources": [
                {
                    "capability": "task_manager",
                    "type": "project",
                    "url": "https://github.com/someone/open-study-path-agent-test-1",
                }
            ],
        }
        summary = render_learner_integration_summary(state)
        self.assertIn("open-study-path-agent-test-1", summary)

        # The real leak this pattern exists to catch must still be caught.
        leaking_state = deepcopy(state)
        leaking_state["resources"][0]["url"] = (
            "https://example.com/<!-- open-study-path:topic_id=TOPIC-001 -->"
        )
        with self.assertRaises(AssertionError):
            render_learner_integration_summary(leaking_state)

    def test_readback_fails_when_list_order_is_wrong(self):
        backend = FakeBackend("trello")
        result = publish_projection(
            topics=(topic(1), topic(2)),
            backend=backend,
            operation_id="publication-order",
        )
        snapshot = deepcopy(result.normalized_snapshot)
        managed = [item for item in snapshot["sections"] if item.get("managed")]
        unmanaged = [item for item in snapshot["sections"] if not item.get("managed")]
        snapshot["sections"] = list(reversed(managed)) + unmanaged
        plan = build_projection_plan((topic(1), topic(2)), provider="trello")
        errors = validate_readback(plan, snapshot)
        self.assertTrue(any("order is incorrect" in error for error in errors))

    def test_student_sections_resources_comments_and_attachments_are_preserved(self):
        backend = FakeBackend(
            "trello",
            sections=[{"id": "student-list", "name": "Minhas notas", "managed": False}],
            resources=[
                {
                    "id": "student-card",
                    "url": "https://trello.example/student-card",
                    "kind": "note",
                    "managed": False,
                    "visible": {"title": "Meu cartão", "description": "não alterar"},
                    "internal_metadata": {},
                    "visible_state": "Minhas notas",
                    "student_fields": {"attachments": ["file.pdf"]},
                    "student_comments": ["comentário do aluno"],
                }
            ],
        )
        publish_projection(
            topics=(topic(1),), backend=backend, operation_id="publication-preserve"
        )
        student = next(item for item in backend.resources if item["id"] == "student-card")
        self.assertEqual("não alterar", student["visible"]["description"])
        self.assertEqual(["file.pdf"], student["student_fields"]["attachments"])
        self.assertEqual(["comentário do aluno"], student["student_comments"])
        self.assertEqual("Minhas notas", backend.sections[-1]["name"])

    def test_passing_assessment_moves_lesson_and_recomposes_window(self):
        topics = (
            topic(1),
            topic(2),
            topic(3, prerequisites=("TOPIC-001",)),
        )
        updated = apply_assessment_result(topics, topic_id="TOPIC-001", passed=True)
        plan = build_projection_plan(updated, provider="trello")
        states = {lesson.topic.topic_id: lesson.visible_state for lesson in plan.lessons}
        self.assertEqual("Concluído", states["TOPIC-001"])
        self.assertEqual("Próxima aula", states["TOPIC-002"])
        self.assertEqual("Disponível em paralelo", states["TOPIC-003"])

    def test_insufficient_assessment_reuses_focused_review(self):
        backend = FakeBackend("trello")
        target = topic(1)
        first = ensure_focused_review_resource(
            backend=backend, topic=target, feedback="Revise o conceito central."
        )
        writes = backend.write_count
        second = ensure_focused_review_resource(
            backend=backend, topic=target, feedback="Revise o conceito central."
        )
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(writes, backend.write_count)

    def test_roadmap_update_invalidates_and_rewrites_fingerprint(self):
        backend = FakeBackend("trello")
        first_topics = (topic(1), topic(2))
        first = publish_projection(
            topics=first_topics, backend=backend, operation_id="publication-roadmap"
        )
        second_topics = (topic(1), topic(2, title="Tema 2 revisado"), topic(3))
        second = publish_projection(
            topics=second_topics,
            backend=backend,
            operation_id="publication-roadmap",
            journal_state=first.journal,
            previous_integration_state=first.integration_state,
        )
        self.assertNotEqual(
            roadmap_fingerprint(first_topics), roadmap_fingerprint(second_topics)
        )
        self.assertEqual(
            roadmap_fingerprint(second_topics),
            second.integration_state["projection"]["roadmap_fingerprint"],
        )
        lessons = [item for item in backend.resources if item.get("kind") == "lesson"]
        self.assertEqual(3, len(lessons))

    def test_optional_reminder_failure_does_not_undo_board_publication(self):
        backend = FakeBackend("trello")

        def fail_reminder(_container):
            raise RuntimeError("Todoist unavailable")

        result = publish_projection(
            topics=(topic(1),),
            backend=backend,
            operation_id="publication-reminder",
            reminder_writer=fail_reminder,
        )
        self.assertEqual("success", result.journal["status"])
        self.assertTrue(result.journal["warnings"])
        self.assertEqual("success", result.integration_state["sync"]["status"])
        self.assertTrue(result.integration_state["sync"]["errors"])

    def test_migration_is_idempotent_and_removes_only_known_markers(self):
        backend = FakeBackend(
            "trello",
            sections=[
                {"id": "legacy-ready", "name": "Pronto para estudar", "managed": True},
                {"id": "legacy-progress", "name": "Em andamento", "managed": True},
                {"id": "student", "name": "Arquivo pessoal", "managed": False},
            ],
            resources=[
                {
                    "id": "legacy-card",
                    "url": "https://trello.example/legacy",
                    "kind": "lesson",
                    "managed": True,
                    "visible": {
                        "title": "Aula 01 · Tema 1",
                        "description": "Texto útil <!-- open-study-path topic=TOPIC-001 --> manter",
                        "checklist": ["Passo útil"],
                        "managed_comments": ["<!-- open-study-path sync -->", "Comentário conhecido"],
                    },
                    "internal_metadata": {},
                    "visible_state": "Pronto para estudar",
                    "student_fields": {"attachments": ["keep"]},
                    "student_comments": ["<!-- outro marcador desconhecido -->"],
                }
            ],
        )
        first = migrate_legacy_backend(
            backend=backend, topics=(topic(1),), operation_id="migration-v1"
        )
        writes = backend.write_count
        second = migrate_legacy_backend(
            backend=backend, topics=(topic(1),), operation_id="migration-v1"
        )
        self.assertEqual(writes, backend.write_count)
        card = next(item for item in backend.resources if item.get("kind") == "lesson")
        self.assertNotIn("open-study-path", card["visible"]["description"])
        self.assertIn("Texto útil", card["visible"]["description"])
        self.assertEqual(["keep"], card["student_fields"]["attachments"])
        self.assertEqual(
            ["<!-- outro marcador desconhecido -->"], card["student_comments"]
        )
        self.assertEqual(
            [item.get("id") for item in first.integration_state["resources"]],
            [item.get("id") for item in second.integration_state["resources"]],
        )

    def test_github_issues_keeps_legacy_ready_label_and_materialized_scope(self):
        backend = FakeBackend("github_issues")
        topics = (topic(1), topic(2), topic(3, materialized=False))
        result = publish_projection(
            topics=topics, backend=backend, operation_id="publication-github"
        )
        issues = [item for item in backend.resources if item.get("kind") == "lesson"]
        self.assertEqual(2, len(issues))
        labels = {label for item in issues for label in item.get("labels", [])}
        self.assertIn("study:ready", labels)
        self.assertNotIn("study:ready-primary", labels)
        self.assertNotIn("study:ready-parallel", labels)


    def test_complete_trello_fixture_initial_and_assessment_update(self):
        backend = FakeBackend("trello")
        topics = (
            topic(1),
            topic(2),
            topic(3, prerequisites=("TOPIC-001",)),
        )
        initial = publish_projection(
            topics=topics, backend=backend, operation_id="publication-complete-fixture"
        )
        self.assertEqual("success", initial.journal["status"])
        updated_topics = apply_assessment_result(
            topics, topic_id="TOPIC-001", passed=True
        )
        updated = publish_projection(
            topics=updated_topics,
            backend=backend,
            operation_id="publication-complete-fixture",
            journal_state=initial.journal,
            previous_integration_state=initial.integration_state,
        )
        states = {
            item["internal_metadata"].get("topic_id"): item["visible_state"]
            for item in updated.normalized_snapshot["resources"]
            if item.get("kind") == "lesson"
        }
        self.assertEqual("Concluído", states["TOPIC-001"])
        self.assertEqual("Próxima aula", states["TOPIC-002"])
        self.assertEqual("Disponível em paralelo", states["TOPIC-003"])
        self.assertEqual(3, len(states))

    def test_readback_failure_prevents_success_declaration(self):
        class CorruptingBackend(FakeBackend):
            def read_normalized_snapshot(self):
                snapshot = deepcopy(super().read_normalized_snapshot())
                lesson = next(item for item in snapshot["resources"] if item.get("kind") == "lesson")
                lesson["visible"]["description"] += " <!-- open-study-path sync -->"
                return snapshot

        backend = CorruptingBackend("trello")
        with self.assertRaises(ReadbackValidationError) as raised:
            publish_projection(
                topics=(topic(1),),
                backend=backend,
                operation_id="publication-corrupt-readback",
            )
        self.assertEqual("partial", raised.exception.journal["status"])


if __name__ == "__main__":
    unittest.main()
