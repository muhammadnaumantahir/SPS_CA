"""Canonical 500-case scenario contract suite.

Scenario cases live in evaluation/scenarios/growth_500.json.  The repository's
implementation/unit tests remain colocated with their production modules;
this file is intentionally the single scenario-level pytest entry point.

The suite validates the deterministic front half of SPS-CA's routing contract
(language detection + intent classification) for every expanded scenario. This
keeps all 500 cases fast, reproducible, and independent of an external LLM.
The full scenario runner remains available for model-backed end-to-end runs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from brain.brain import Brain
from evaluation.scenario_runner import expand_suite


SCENARIO_FILE = Path(__file__).resolve().parents[1] / "evaluation" / "scenarios" / "growth_500.json"


@pytest.fixture(scope="module")
def scenarios() -> list[dict]:
    data = json.loads(SCENARIO_FILE.read_text(encoding="utf-8"))
    expanded = expand_suite(data)
    assert len(expanded) == 500, "growth_500.json must expand to exactly 500 scenarios"
    return expanded


@pytest.mark.parametrize("index", range(500))
def test_scenario_contract(index: int, scenarios: list[dict]) -> None:
    """Run one real routing contract check per scenario."""
    scenario = scenarios[index]
    expected = dict(scenario.get("expected", {}))

    assert scenario["id"], f"scenario {index + 1} has no id"
    assert scenario["request"].strip(), f"scenario {scenario['id']} has no request"
    assert scenario["language"], f"scenario {scenario['id']} has no language"
    assert expected.get("intent"), f"scenario {scenario['id']} has no expected intent"

    detected_language, confidence, _ = Brain.detect_language(
        scenario.get("code", ""),
        scenario["request"],
        scenario.get("filename", ""),
    )
    assert detected_language == scenario["language"], (
        f"{scenario['id']}: detected language {detected_language!r}, "
        f"expected {scenario['language']!r}"
    )
    assert 0.0 <= confidence <= 1.0

    intent = Brain.infer_intent_class(
        scenario["request"],
        scenario.get("code", ""),
        scenario.get("filename", ""),
    )
    assert intent == expected["intent"], (
        f"{scenario['id']}: inferred intent {intent!r}, expected {expected['intent']!r}"
    )


def test_suite_is_exactly_500_cases(scenarios: list[dict]) -> None:
    """Guard the benchmark size so accidental shrinking/expansion is visible."""
    assert len(scenarios) == 500
    assert len({scenario["id"] for scenario in scenarios}) == 500
