"""Additional 500-case routing contract suite.

The companion generator creates evaluation/scenarios/growth_500_additional.json.
These cases add 50 scenarios for each canonical Stage-0 capability and include
repeated disagreement evidence for Layer-8 SPS Growth Decision analysis.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from brain.brain import Brain
from evaluation.scenario_runner import expand_suite

SCENARIO_FILE = Path(__file__).resolve().parents[1] / "evaluation" / "scenarios" / "growth_500_additional.json"


def _scenarios() -> list[dict]:
    data = json.loads(SCENARIO_FILE.read_text(encoding="utf-8"))
    cases = expand_suite(data)
    assert len(cases) == 500
    assert len({case["id"] for case in cases}) == 500
    return cases


@pytest.mark.parametrize("index", range(500))
def test_additional_scenario_contract(index: int) -> None:
    scenario = _scenarios()[index]
    expected = scenario["expected"]
    language, confidence, _ = Brain.detect_language(
        scenario.get("code", ""), scenario["request"], scenario.get("filename", "")
    )
    assert language == scenario["language"]
    assert 0.0 <= confidence <= 1.0
    intent = Brain.infer_intent_class(
        scenario["request"], scenario.get("code", ""), scenario.get("filename", "")
    )
    assert intent == expected["intent"]
