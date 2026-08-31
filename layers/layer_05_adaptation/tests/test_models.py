"""Tests for AdaptationRecord model (Layer 5)."""

from __future__ import annotations

import pytest

from layers.layer_05_adaptation.models import AdaptationRecord


def test_record_requires_id():
    with pytest.raises(ValueError):
        AdaptationRecord(
            id="", base_capability_id="CAP-003", applied_to_task_id="task_045"
        )


def test_record_requires_base_capability_id():
    with pytest.raises(ValueError):
        AdaptationRecord(
            id="adaptation_001", base_capability_id="", applied_to_task_id="task_045"
        )


def test_record_roundtrip_dict():
    original = AdaptationRecord(
        id="adaptation_001",
        base_capability_id="CAP-003",
        applied_to_task_id="task_045",
        parameters_changed={"timeout": "5s -> 15s", "language": "python -> java"},
        success=True,
    )
    data = original.to_dict()
    assert data["change_type"] == 6
    restored = AdaptationRecord.from_dict(data)
    assert restored.id == original.id
    assert restored.base_capability_id == original.base_capability_id
    assert restored.parameters_changed == original.parameters_changed
    assert restored.success == original.success
