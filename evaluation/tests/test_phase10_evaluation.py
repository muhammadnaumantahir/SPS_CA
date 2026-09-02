import json
from pathlib import Path

from evaluation.scenarios import load_catalog, build_execution_matrix
from evaluation.metrics import summarize_results


def test_catalog_contains_all_25_scenarios():
    catalog = load_catalog()
    assert len(catalog) == 25
    assert [scenario["id"] for scenario in catalog] == [f"S{i}" for i in range(1, 26)]


def test_matrix_matches_master_distribution_for_basic_and_sps_cases():
    catalog = load_catalog()
    matrix = build_execution_matrix(catalog)
    lookup = {(item["scenario_id"], item["project"], item["baseline"]): item for item in matrix}

    # S1 is full matrix: 3 projects x 3 baselines.
    assert len([x for x in matrix if x["scenario_id"] == "S1"]) == 9

    # S11 is SPS-only on Project A, 3 baseline slots are not created.
    assert len([x for x in matrix if x["scenario_id"] == "S11"]) == 1
    assert lookup[("S11", "project_a_python", "SPS-CA")]["baseline"] == "SPS-CA"
    assert not any(x["scenario_id"] == "S11" and x["baseline"] != "SPS-CA" for x in matrix)

    # S9 has explicit cross-project SPS-only execution.
    s9 = [x for x in matrix if x["scenario_id"] == "S9"]
    assert {x["project"] for x in s9} == {"project_a_python", "project_b_java"}
    assert all(x["baseline"] == "SPS-CA" for x in s9)


def test_metrics_calculate_success_rate_and_sps_delta():
    results = [
        {"scenario_id": "S1", "project": "project_a_python", "baseline": "A", "success": True, "duration_seconds": 10},
        {"scenario_id": "S2", "project": "project_a_python", "baseline": "A", "success": False, "duration_seconds": 20},
        {"scenario_id": "S1", "project": "project_a_python", "baseline": "B", "success": True, "duration_seconds": 30},
        {"scenario_id": "S2", "project": "project_a_python", "baseline": "B", "success": False, "duration_seconds": 40},
        {"scenario_id": "S1", "project": "project_a_python", "baseline": "SPS-CA", "success": True, "duration_seconds": 15},
        {"scenario_id": "S2", "project": "project_a_python", "baseline": "SPS-CA", "success": True, "duration_seconds": 25},
    ]
    summary = summarize_results(results)
    assert summary["by_baseline"]["A"]["success_rate"] == 50.0
    assert summary["by_baseline"]["B"]["success_rate"] == 50.0
    assert summary["by_baseline"]["SPS-CA"]["success_rate"] == 100.0
    assert summary["sps_minus_b_success_points"] == 50.0
    assert summary["overall_execution_count"] == 6


def test_result_schema_is_json_serializable(tmp_path: Path):
    output = tmp_path / "results.jsonl"
    record = {
        "scenario_id": "S1",
        "project": "project_a_python",
        "baseline": "A",
        "success": True,
        "duration_seconds": 1.25,
    }
    output.write_text(json.dumps(record) + "\n", encoding="utf-8")
    loaded = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert loaded["scenario_id"] == "S1"
