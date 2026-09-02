"""Phase-10 experimental scenario catalog and execution-matrix builder."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

PROJECTS = ["project_a_python", "project_b_java", "project_c_typescript"]
BASELINES = ["A", "B", "SPS-CA"]

# Scenario definitions preserve the master plan's S1-S25 names and intent.
SCENARIOS: list[dict[str, Any]] = [
    {"id": "S1", "name": "Syntax Error Fix", "type": "Change Type 2", "projects": PROJECTS, "baselines": BASELINES},
    {"id": "S2", "name": "Feature Addition", "type": "Change Type 3", "projects": PROJECTS, "baselines": BASELINES},
    {"id": "S3", "name": "Test Generation", "type": "Change Type 5", "projects": PROJECTS, "baselines": BASELINES},
    {"id": "S4", "name": "Code Refactoring", "type": "Change Type 4", "projects": PROJECTS, "baselines": BASELINES},
    {"id": "S5", "name": "Single Failure Detection", "type": "Change Type 7", "projects": ["project_a_python"], "baselines": BASELINES},
    {"id": "S6", "name": "Repeated Failure Pattern", "type": "Evolution trigger", "projects": PROJECTS, "baselines": BASELINES},
    {"id": "S7", "name": "Capability Adaptation", "type": "Change Type 6", "projects": PROJECTS, "baselines": BASELINES},
    {"id": "S8", "name": "Capability Composition", "type": "Change Types 6+7", "projects": ["project_a_python"], "baselines": BASELINES},
    {"id": "S9", "name": "Cross-Project Capability Reuse", "type": "Change Type 6", "projects": ["project_a_python", "project_b_java"], "baselines": ["SPS-CA"], "context": "A→B/B→C reuse"},
    {"id": "S10", "name": "Meta-Learning Strategy Switch", "type": "Change Type 6", "projects": ["project_a_python"], "baselines": BASELINES},
    {"id": "S11", "name": "Single Capability Generation", "type": "Change Type 7", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
    {"id": "S12", "name": "Capability Reuse (Generated)", "type": "Change Type 6", "projects": ["project_a_python", "project_b_java"], "baselines": ["SPS-CA"]},
    {"id": "S13", "name": "Multiple Capability Generation", "type": "Change Type 7", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
    {"id": "S14", "name": "Meta-Learning Improvement Measurement", "type": "Meta-Learning", "projects": PROJECTS, "baselines": BASELINES},
    {"id": "S15", "name": "Experience Log Continuity", "type": "Experience Accumulation", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
    {"id": "S16", "name": "DNA Violation Rejection", "type": "Governance rejection", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
    {"id": "S17", "name": "Risk Assessment - Low Risk Auto-Approval", "type": "Governance", "projects": ["project_a_python", "project_b_java"], "baselines": ["SPS-CA"]},
    {"id": "S18", "name": "Risk Assessment - High Risk Escalation", "type": "Governance", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
    {"id": "S19", "name": "Sandbox Validation - Success Path", "type": "Validation", "projects": PROJECTS, "baselines": BASELINES},
    {"id": "S20", "name": "Sandbox Validation - Failure Path", "type": "Validation rejection", "projects": ["project_a_python", "project_b_java"], "baselines": BASELINES},
    {"id": "S21", "name": "Rollback Execution", "type": "Change Type 7", "projects": ["project_a_python", "project_b_java"], "baselines": ["SPS-CA"]},
    {"id": "S22", "name": "Governance Audit Trail", "type": "Governance", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
    {"id": "S23", "name": "Capability Retirement", "type": "Change Type 7", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
    {"id": "S24", "name": "Evolution Lineage Tracking", "type": "Evolution", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
    {"id": "S25", "name": "Recovery from Failed Evolution", "type": "Evolution error handling", "projects": ["project_a_python"], "baselines": ["SPS-CA"]},
]


def load_catalog(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load catalog from JSON when supplied, otherwise return the source-of-truth catalog."""
    if path is None:
        return list(SCENARIOS)
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("scenario catalog must contain a JSON list")
    if len(data) != 25:
        raise ValueError("scenario catalog must contain exactly 25 scenarios")
    return data


def build_execution_matrix(catalog: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expand scenario project/baseline scopes into concrete execution records."""
    matrix: list[dict[str, Any]] = []
    for scenario in catalog:
        for project in scenario["projects"]:
            for baseline in scenario["baselines"]:
                matrix.append(
                    {
                        "scenario_id": scenario["id"],
                        "scenario_name": scenario["name"],
                        "scenario_type": scenario.get("type", ""),
                        "project": project,
                        "baseline": baseline,
                        "request": scenario.get("request", scenario["name"]),
                        "context": scenario.get("context", ""),
                    }
                )
    return matrix


def write_matrix(matrix: Iterable[dict[str, Any]], path: str | Path) -> None:
    """Write the execution matrix as deterministic JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(list(matrix), indent=2, sort_keys=True), encoding="utf-8")
