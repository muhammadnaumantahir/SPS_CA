"""Phase-9 runner for reproducible baseline executions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from baselines.baseline_a_naive_llm import BaselineA_NaiveLLM
from baselines.baseline_b_coding_agent import BaselineB_CodingAgent
from baselines.local_llm import build_local_llm
from baselines.runner import ResultStore

MODEL = "qwen2.5-coder:7b"


def load_scenarios(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("scenario file must contain a JSON list")
    return data


def run_scenarios(scenarios: Iterable[dict[str, Any]], output: str | Path) -> None:
    llm = build_local_llm(MODEL)
    store = ResultStore(output)
    baseline_a = BaselineA_NaiveLLM(llm, model=MODEL, store=store)
    baseline_b = BaselineB_CodingAgent(llm, model=MODEL, store=store)

    for scenario in scenarios:
        request = str(scenario["request"])
        context = str(scenario.get("project_context", ""))
        project = str(scenario["project"])
        baseline_a.process_request(request, context, project)
        baseline_b.process_request(request, context, project)

if __name__ == "__main__":
    run_scenarios(
        load_scenarios("evaluation/baselines/sample_scenarios.json"),
        "evaluation/baselines/results.jsonl",
    )
