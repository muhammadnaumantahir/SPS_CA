"""
Unit tests for Layer 10 (Execution Engine).

Run from repo root:
    pytest layers/layer_10_execution/tests/ -v

Covers:
    - Applying a successful change (new file + modified file)
    - Applying a change that fails tests -> automatic rollback
    - Rollback restores exact original content (hash-verified)
    - Rollback of a file that didn't exist before (should be deleted)
    - Execution metrics are logged to execution_log.json
    - Success ratio by capability
    - monitor_execution returns a previously logged result
"""

import json
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from layers.layer_10_execution import (  # noqa: E402
    Change,
    ExecutionEngine,
    ExecutionStatus,
    FileEdit,
)


@pytest.fixture
def target_project(tmp_path: Path) -> Path:
    project = tmp_path / "project_a_python"
    project.mkdir()
    (project / "app.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    tests_dir = project / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text(
        textwrap.dedent(
            """
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from app import add

            def test_add():
                assert add(2, 3) == 5
            """
        ),
        encoding="utf-8",
    )
    return project


@pytest.fixture
def engine(tmp_path: Path) -> ExecutionEngine:
    return ExecutionEngine(
        snapshot_dir=str(tmp_path / "snapshots"),
        log_path=str(tmp_path / "evaluation" / "execution" / "execution_log.json"),
    )


class TestSuccessfulExecution:
    def test_applies_change_and_passes_tests(self, engine, target_project):
        change = Change.new(
            capability_id="CAP-002",
            description="Validated no-op change",
            edits=[FileEdit(file_path="app.py", new_content="def add(a, b):\n    return a + b\n")],
            test_command="pytest tests/ -q",
        )
        result = engine.execute_change(change, str(target_project))
        assert result.status == ExecutionStatus.SUCCESS
        assert result.rollback_triggered is False
        assert result.tests_failing == 0
        assert result.tests_passing >= 1

    def test_new_file_creation(self, engine, target_project):
        change = Change.new(
            capability_id="CAP-009",
            description="Add a utility module",
            edits=[FileEdit(file_path="utils.py", new_content="def double(x):\n    return x * 2\n")],
        )
        result = engine.execute_change(change, str(target_project))
        assert result.status == ExecutionStatus.SUCCESS
        assert (target_project / "utils.py").read_text() == "def double(x):\n    return x * 2\n"


class TestFailureAndRollback:
    def test_failing_tests_trigger_rollback(self, engine, target_project):
        original = (target_project / "app.py").read_text()
        change = Change.new(
            capability_id="CAP-002",
            description="Introduce a bug",
            edits=[FileEdit(file_path="app.py", new_content="def add(a, b):\n    return a - b\n")],
            test_command="pytest tests/ -q",
        )
        result = engine.execute_change(change, str(target_project))
        assert result.status == ExecutionStatus.ROLLED_BACK
        assert result.rollback_triggered is True
        assert result.tests_failing >= 1
        assert (target_project / "app.py").read_text() == original

    def test_rollback_removes_newly_created_file(self, engine, target_project):
        change = Change.new(
            capability_id="CAP-009",
            description="Add a broken new module",
            edits=[
                FileEdit(file_path="broken.py", new_content="def f(:\n    pass\n"),
                FileEdit(file_path="app.py", new_content="def add(a, b):\n    return a + b\n"),
            ],
            test_command="python -c \"import broken\"",
        )
        result = engine.execute_change(change, str(target_project))
        assert result.status == ExecutionStatus.ROLLED_BACK
        assert not (target_project / "broken.py").exists()

    def test_manual_rollback_is_verified(self, engine, target_project):
        original = (target_project / "app.py").read_text()
        change = Change.new(
            capability_id="CAP-002",
            description="Manual rollback check",
            edits=[FileEdit(file_path="app.py", new_content="def add(a, b):\n    return 0\n")],
        )
        engine.execute_change(change, str(target_project))
        rollback = engine.execute_rollback(change.change_id, target_project)
        assert rollback.success is True
        assert rollback.verified is True
        assert (target_project / "app.py").read_text() == original


class TestMetricsAndLogging:
    def test_execution_is_logged(self, engine, target_project):
        change = Change.new(
            capability_id="CAP-002",
            description="Logged change",
            edits=[FileEdit(file_path="app.py", new_content="def add(a, b):\n    return a + b\n")],
            test_command="pytest tests/ -q",
        )
        engine.execute_change(change, str(target_project))
        log = json.loads(engine.log_path.read_text())
        assert len(log["executions"]) == 1
        entry = log["executions"][0]
        assert entry["change_id"] == change.change_id
        assert entry["capability_id"] == "CAP-002"
        assert entry["status"] == "success"

    def test_success_ratio_by_capability(self, engine, target_project):
        ok_change = Change.new(
            capability_id="CAP-002",
            description="ok",
            edits=[FileEdit(file_path="app.py", new_content="def add(a, b):\n    return a + b\n")],
            test_command="pytest tests/ -q",
        )
        bad_change = Change.new(
            capability_id="CAP-002",
            description="bad",
            edits=[FileEdit(file_path="app.py", new_content="def add(a, b):\n    return a - b\n")],
            test_command="pytest tests/ -q",
        )
        engine.execute_change(ok_change, str(target_project))
        engine.execute_change(bad_change, str(target_project))
        assert engine.get_success_ratio("CAP-002") == pytest.approx(0.5)

    def test_monitor_execution_returns_logged_result(self, engine, target_project):
        change = Change.new(
            capability_id="CAP-002",
            description="Monitor test",
            edits=[FileEdit(file_path="app.py", new_content="def add(a, b):\n    return a + b\n")],
            test_command="pytest tests/ -q",
        )
        engine.execute_change(change, str(target_project))
        monitored = engine.monitor_execution(change.change_id)
        assert monitored is not None
        assert monitored.change_id == change.change_id
        assert monitored.status == ExecutionStatus.SUCCESS

    def test_monitor_unknown_change_returns_none(self, engine):
        assert engine.monitor_execution("change_does_not_exist") is None
