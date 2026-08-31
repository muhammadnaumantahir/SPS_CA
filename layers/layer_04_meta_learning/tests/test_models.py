"""Tests for MetaLearningDecision model (Layer 4)."""

from __future__ import annotations

import pytest

from layers.layer_04_meta_learning.models import MetaLearningDecision


def test_decision_requires_id():
    with pytest.raises(ValueError):
        MetaLearningDecision(
            decision_id="",
            triggered_by="x",
            previous_strategy="a",
            new_strategy="b",
            rationale="r",
        )


def test_decision_roundtrip_dict():
    original = MetaLearningDecision(
        decision_id="MLD_001",
        triggered_by="CAP-002 failure rate >20%",
        previous_strategy="Always try CAP-002 first for syntax fixes",
        new_strategy="For JavaScript, try CAP-003 first",
        rationale="CAP-003 has 15% higher success rate on JS projects",
    )
    restored = MetaLearningDecision.from_dict(original.to_dict())
    assert restored == original
