from brain.task_planner import BrainTaskPlanner


def test_validate_compound_analysis_then_fix_plan():
    data = {
        "tasks": [
            {
                "id": "task_001",
                "instruction": "Analyze this function for the root cause of the bug.",
                "intent_class": "analysis",
                "capability_id": "CAP-003",
                "depends_on": [],
            },
            {
                "id": "task_002",
                "instruction": "Fix the bug identified by the analysis.",
                "intent_class": "bug_fixing",
                "capability_id": "CAP-005",
                "depends_on": ["task_001"],
            },
        ]
    }
    tasks = BrainTaskPlanner._validate(data, allowed_ids={f"CAP-{i:03d}" for i in range(1, 11)})
    assert [task.capability_id for task in tasks] == ["CAP-003", "CAP-005"]
    assert tasks[0].depends_on == []
    assert tasks[1].depends_on == ["task_001"]


def test_validate_rejects_capability_intent_mismatch():
    data = {
        "tasks": [
            {
                "id": "task_001",
                "instruction": "Analyze this function.",
                "intent_class": "analysis",
                "capability_id": "CAP-007",
                "depends_on": [],
            }
        ]
    }
    try:
        BrainTaskPlanner._validate(data, allowed_ids={f"CAP-{i:03d}" for i in range(1, 11)})
    except ValueError as exc:
        assert "not eligible" in str(exc)
    else:
        raise AssertionError("expected capability/intent mismatch to be rejected")
