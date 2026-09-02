"""Tests for the Task model (Layer 3)."""

from __future__ import annotations

from datetime import datetime

import pytest

from layers.layer_05_experience.models import Task


def test_task_requires_id():
    with pytest.raises(ValueError):
        Task(id="", user_request="do something")


def test_task_rejects_invalid_status():
    with pytest.raises(ValueError):
        Task(id="task_001", user_request="x", status="bogus")  # type: ignore[arg-type]


def test_task_defaults_failure_category_when_missing():
    task = Task(id="task_002", user_request="fix bug", status="failure")
    assert task.failure_category == "Uncategorized"


def test_task_keeps_explicit_failure_category():
    task = Task(
        id="task_003",
        user_request="fix bug",
        status="failure",
        failure_category="Pattern mismatch",
    )
    assert task.failure_category == "Pattern mismatch"


def test_task_success_has_no_forced_failure_category():
    task = Task(id="task_004", user_request="add feature", status="success")
    assert task.failure_category is None


def test_task_is_failure_property():
    ok = Task(id="task_005", user_request="x", status="success")
    bad = Task(id="task_006", user_request="x", status="failure")
    assert ok.is_failure is False
    assert bad.is_failure is True


def test_task_roundtrip_dict():
    original = Task(
        id="task_007",
        user_request="Add error handling",
        target_project="projects/project_a_python",
        target_language="python",
        status="failure",
        selected_capability="CAP-005",
        outcome="raised TypeError",
        failure_category="Pattern mismatch",
        time_taken_seconds=62.5,
    )
    data = original.to_dict()
    restored = Task.from_dict(data)
    assert restored == original


def test_task_accepts_iso_string_timestamp():
    task = Task(id="task_008", user_request="x", timestamp="2024-01-15T10:30:00+00:00")
    assert isinstance(task.timestamp, datetime)
