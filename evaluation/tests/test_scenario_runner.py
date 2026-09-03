from evaluation.scenario_runner import _match_expected, expand_suite


class _Turn:
    intent = "code_modification"
    success = True
    output_code = "def add(x):\n    return x\n"
    capability_results = [{"capability_id": "CAP-002"}]
    trace = {"status": "completed"}
    elapsed_ms = 1.0


def test_group_expansion_is_130_scenarios():
    import json
    from pathlib import Path
    suite = json.loads(Path("evaluation/scenarios/default_120.json").read_text(encoding="utf-8"))
    scenarios = expand_suite(suite)
    assert len(scenarios) == 130
    assert len({s["id"] for s in scenarios}) == 130


def test_expected_match_accepts_matching_intent_and_capability():
    ok, failures = _match_expected(_Turn(), {"intent": "code_modification", "capability_id": "CAP-002", "status": "success", "output_required": True})
    assert ok
    assert failures == []


def test_expected_match_reports_mismatch():
    ok, failures = _match_expected(_Turn(), {"intent": "test_generation", "capability_id": "CAP-007"})
    assert not ok
    assert failures
