#!/usr/bin/env python3
"""Phase 4 Definition-of-Done demonstration: one full evolution cycle.

Seeds a Layer 3 (Experience) log with the exact scenario from the Phase 4
spec of the master document -- three repeated "Parse error" failures
(parsing JSON, XML, and CSV) against CAP-001 -- then runs Layer 8
(Evolution Engine) end to end: trigger detection, planning, code
generation, writing ``capabilities/generated/CAP-009/``, running its
generated tests in a sandbox subprocess, passing the result through Layer 7
(Governance), and registering it in ``capabilities/registry.json``.

Run from the repo root:

    python scripts/demo_evolution_cycle.py

This is a manual, reproducible demonstration (not part of the automated
test suite) so a supervisor can see the full self-programming loop run
against real files in the repository, per Phase 4's Definition of Done:
"Generate a test capability (CAP-009) manually following the algorithm."
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from layers.layer_03_experience.experience_log import ExperienceLog
from layers.layer_03_experience.models import Task
from layers.layer_07_governance.governance import GovernanceGate
from layers.layer_08_evolution.evolution_engine import EvolutionEngine


def seed_experience_log() -> ExperienceLog:
    log = ExperienceLog()
    scenario = [
        ("task_010", "Parse this JSON config into a dict"),
        ("task_015", "Parse this XML response into a dict"),
        ("task_020", "Parse this CSV export into a dict"),
    ]
    for task_id, request in scenario:
        log.add_task(
            Task(
                id=task_id,
                user_request=request,
                target_project="demo_project",
                target_language="python",
                status="failure",
                selected_capability="CAP-001",
                outcome="CAP-001 (bug detection) cannot handle structured-data parsing.",
                failure_category="Parse error",
            )
        )
    return log


def main() -> int:
    log = seed_experience_log()
    log.save_to_json()  # experience/logs/experience_log.json (default path)
    log.save_failure_patterns()  # experience/logs/failure_patterns.json

    governance_gate = GovernanceGate()
    engine = EvolutionEngine(governance_gate=governance_gate)

    if not engine.should_evolve(log):
        print("No failure pattern crossed the evolution threshold; nothing to do.")
        return 1

    record = engine.run_evolution_cycle(log)
    if record is None:
        print("Evolution cycle produced no record.")
        return 1

    print(f"Generated capability: {record.capability_id}")
    print(f"Trigger pattern:      {record.trigger_pattern} (tasks: {', '.join(record.trigger_task_ids)})")
    print(f"Tests:                {record.test_result.tests_run} run, {record.test_result.tests_failed} failed")
    print(f"Coverage:             {record.test_result.coverage_percent}%")
    print(f"Governance decision:  {record.governance_decision_id}")
    print(f"Registered:           {record.registered}")
    print()
    print("Commit message:")
    print("-" * 70)
    print(record.commit_message)
    print("-" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
