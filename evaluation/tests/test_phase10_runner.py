from pathlib import Path

from evaluation.phase10_runner import read_results, run_matrix
from evaluation.scenarios import load_catalog


def test_run_matrix_executes_each_concrete_case_and_persists_jsonl(tmp_path: Path):
    scenarios = [
        {
            "id": "S1",
            "name": "Smoke",
            "type": "coding",
            "projects": ["project_a_python"],
            "baselines": ["A", "B", "SPS-CA"],
            "request": "run smoke",
            "context": "ctx",
        }
    ]
    calls = []

    def adapter(name):
        def run(request, context, project):
            calls.append((name, request, context, project))
            return {"success": name != "B", "tool_calls": ["run_tests"] if name == "B" else []}
        return run

    output = tmp_path / "results.jsonl"
    results = run_matrix(
        scenarios,
        {"A": adapter("A"), "B": adapter("B"), "SPS-CA": adapter("SPS-CA")},
        output,
    )
    assert len(results) == 3
    assert len(calls) == 3
    assert sum(1 for row in results if row["success"]) == 2
    assert read_results(output) == results


def test_full_catalog_expands_to_nonempty_evaluation_matrix():
    from evaluation.scenarios import build_execution_matrix

    matrix = build_execution_matrix(load_catalog())
    assert len(matrix) >= 75
    assert {row["baseline"] for row in matrix} == {"A", "B", "SPS-CA"}
    assert {row["scenario_id"] for row in matrix} == {f"S{i}" for i in range(1, 26)}
