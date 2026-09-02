"""Metric aggregation for experimental results."""
from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any, Iterable


def _success_rate(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return round(100.0 * sum(bool(row.get("success")) for row in rows) / len(rows), 2)


def summarize_results(results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(results)
    by_baseline: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_baseline[str(row.get("baseline", "unknown"))].append(row)

    baseline_summary: dict[str, Any] = {}
    for baseline, items in sorted(by_baseline.items()):
        durations = [float(x["duration_seconds"]) for x in items if x.get("duration_seconds") is not None]
        baseline_summary[baseline] = {
            "execution_count": len(items),
            "success_count": sum(bool(x.get("success")) for x in items),
            "success_rate": _success_rate(items),
            "average_execution_time_seconds": round(mean(durations), 3) if durations else 0.0,
        }

    sps_rate = baseline_summary.get("SPS-CA", {}).get("success_rate", 0.0)
    b_rate = baseline_summary.get("B", {}).get("success_rate", 0.0)
    return {
        "overall_execution_count": len(rows),
        "by_baseline": baseline_summary,
        "sps_minus_b_success_points": round(sps_rate - b_rate, 2),
        "all_under_60_seconds": all(float(x.get("duration_seconds", 0)) < 60 for x in rows),
    }


def write_summary(results: Iterable[dict[str, Any]], path: str) -> None:
    import json
    from pathlib import Path

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(summarize_results(results), indent=2, sort_keys=True), encoding="utf-8")
