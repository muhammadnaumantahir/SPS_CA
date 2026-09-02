"""Reproducible Phase-10 execution harness.

The harness deliberately separates experiment orchestration from the actual
baseline implementations. A caller supplies adapters for A, B, and SPS-CA;
results are persisted as JSONL and can later be summarized with metrics.py.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from evaluation.scenarios import BASELINES, build_execution_matrix, load_catalog, write_matrix

Adapter = Callable[[str, str, str], Any]


def _normalize_success(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        return bool(value.get("success", value.get("tests_passed", False)))
    return bool(getattr(value, "success", getattr(value, "tests_passed", False)))


def run_matrix(
    scenarios: Iterable[dict[str, Any]],
    adapters: dict[str, Adapter],
    output_path: str | Path,
    matrix_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Execute every concrete matrix row using the supplied baseline adapters."""
    matrix = build_execution_matrix(scenarios)
    unknown = set(x["baseline"] for x in matrix) - set(adapters)
    if unknown:
        raise ValueError(f"missing adapters for baselines: {sorted(unknown)}")
    if set(adapters) != set(BASELINES):
        raise ValueError(f"adapters must exactly cover {BASELINES}")

    if matrix_path is not None:
        write_matrix(matrix, matrix_path)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for item in matrix:
        started = time.perf_counter()
        error = None
        raw: Any = None
        try:
            raw = adapters[item["baseline"]](item["request"], item["context"], item["project"])
            success = _normalize_success(raw)
        except Exception as exc:  # capture experiment failures as data
            success = False
            error = f"{type(exc).__name__}: {exc}"
        duration = time.perf_counter() - started
        result = {
            **item,
            "success": success,
            "duration_seconds": round(duration, 6),
            "error": error,
        }
        if isinstance(raw, dict):
            if "tool_calls" in raw:
                result["tool_calls"] = raw["tool_calls"]
            if "retries" in raw:
                result["retries"] = raw["retries"]
        else:
            for key in ("tool_calls", "retries", "tests_passed"):
                if hasattr(raw, key):
                    result[key] = getattr(raw, key)
        results.append(result)
        with output.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True) + "\n")
    return results


def load_and_write_matrix(scenario_path: str | Path, matrix_path: str | Path) -> None:
    """Materialize a deterministic matrix without calling a model."""
    write_matrix(build_execution_matrix(load_catalog(scenario_path)), matrix_path)


def read_results(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    raise SystemExit("Use run_matrix(...) from a controlled experiment script; CI only validates the harness.")
