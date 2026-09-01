"""Run one local Ollama -> Layer 8 -> Layer 6 -> Layer 7 -> Layer 9 evolution cycle.

Usage:
    python scripts/run_evolution_demo.py
    python scripts/run_evolution_demo.py --approve

The demo never promotes a generated capability unless ``--approve`` is given.
It is intentionally local and uses the repository's Ollama provider.
"""
from __future__ import annotations

import argparse

from layers.layer_03_experience.experience_log import ExperienceLog
from layers.layer_03_experience.models import Task
from layers.layer_07_governance import GovernanceGate
from layers.layer_08_evolution import EvolutionEngine, EvolutionWorkflow
from layers.layer_09_capability_registry import CapabilityRegistry
from models.ollama import OllamaProvider


def build_failure_history() -> ExperienceLog:
    log = ExperienceLog()
    for index in range(1, 4):
        log.add_task(
            Task(
                id=f"evolution_demo_{index}",
                user_request="Fix recurring parser failure",
                target_project="demo-project",
                target_language="python",
                status="failure",
                selected_capability="CAP-001",
                outcome="Parser capability failed",
                failure_category="parser_failure",
            )
        )
    return log


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:7b",
        help="Local Ollama model used for capability generation",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Allow promotion after Layer 7 governance",
    )
    args = parser.parse_args()

    provider = OllamaProvider(default_model=args.model)
    if not provider.is_available():
        print("Ollama is unavailable at http://localhost:11434")
        print("Start Ollama and ensure the requested model is installed.")
        return 2

    engine = EvolutionEngine(provider=provider, model=args.model)
    governance = GovernanceGate()
    registry = CapabilityRegistry()
    workflow = EvolutionWorkflow(engine, governance, registry)

    result = workflow.evolve(
        build_failure_history(),
        evidence=[
            "Three independent task failures share parser_failure.",
            "Existing seed capability CAP-001 was selected for each failed task.",
        ],
        approved=args.approve,
    )

    print(f"Capability: {result.capability_id}")
    print(f"Trigger: {result.trigger_pattern}")
    print(f"Layer 6 validation: {'PASS' if result.test_results.passed else 'FAIL'}")
    print(f"Coverage: {result.test_results.coverage_percent}%")
    print(f"Layer 7 governance: {result.governance_status}")
    print(f"Promoted: {result.promoted_path}")
    print(f"Registered: {result.registered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
