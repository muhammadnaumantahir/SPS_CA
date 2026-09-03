"""Controlled live self-programming runner for local/Colab experiments.

This command exercises the real Ollama-backed Layer-8 Evolution pipeline in a
throwaway workspace. It requires an explicit live-evolution confirmation and
never changes the caller's checkout unless ``--keep-workspace`` is supplied.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path

from core.optimization_cycle_service import OptimizationCycleService
from layers.layer_05_experience import ExperienceLog, Task
from layers.layer_06_meta_learning import OptimizationCycleConfig, OptimizationCycleController
from layers.layer_08_evolution import EvolutionExecutionAuthority


def _seed_failure_log(task: str, language: str) -> ExperienceLog:
    """Create deterministic failure evidence for one controlled optimization cycle."""
    return ExperienceLog([
        Task(
            id=f"live_seed_{index}",
            user_request=task,
            target_project="live-evolution",
            target_language=language,
            status="failure",
            selected_capability="CAP-001",
            outcome="Seeded benchmark failure evidence for controlled Evolution.",
            failure_category="CapabilityUnderperformance",
            time_taken_seconds=1.0,
        )
        for index in range(1, 6)
    ])


def run_live(
    *,
    repo_root: Path,
    task: str,
    language: str,
    keep_workspace: bool,
) -> dict:
    """Run one provider-backed Evolution cycle inside a disposable workspace."""
    source = repo_root.resolve()
    original_cwd = Path.cwd()
    workspace = Path(tempfile.mkdtemp(prefix="sps_ca_live_evolution_"))
    try:
        shutil.copytree(
            source,
            workspace / source.name,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
        )
        target = workspace / source.name
        os.chdir(target)

        os.environ["SPS_CA_AUTO_EVOLVE"] = "true"
        os.environ.setdefault("SPS_CA_AUTO_EVOLVE_MAX_ACTIONS", "1")

        experience = _seed_failure_log(task, language)
        controller = OptimizationCycleController(
            config=OptimizationCycleConfig(
                minimum_total_observations=5,
                minimum_failure_rate=0.30,
                minimum_capability_observations=5,
                minimum_capability_score=0.90,
                cooldown_seconds=0,
            )
        )
        service = OptimizationCycleService(
            experience=experience,
            controller=controller,
            execution_authority=EvolutionExecutionAuthority(
                enabled=True,
                max_actions_per_cycle=1,
                source="live-runner-confirmed",
            ),
        )
        cycle = service.assess_after_task(["CAP-001"])
        state_path = Path("experience/logs/optimization_cycle_state.json")
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

        return {
            "cycle": cycle.to_dict(),
            "authority": state.get("execution_authority", {}),
            "action_plan": state.get("last_action_plan"),
            "execution": state.get("last_auto_evolution", []),
            "workspace": str(target) if keep_workspace else None,
            "temporary_workspace": str(target),
        }
    finally:
        os.chdir(original_cwd)
        if not keep_workspace:
            shutil.rmtree(workspace, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="SPS-CA repository root")
    parser.add_argument(
        "--task",
        required=True,
        help="Capability requirement used by the real provider-backed Evolution run",
    )
    parser.add_argument("--language", default="python")
    parser.add_argument(
        "--confirm-live-evolution",
        action="store_true",
        help="Explicitly authorize this real provider-backed Evolution experiment",
    )
    parser.add_argument(
        "--keep-workspace",
        action="store_true",
        help="Keep the disposable workspace for inspection",
    )
    args = parser.parse_args()

    if not args.confirm_live_evolution:
        parser.error("--confirm-live-evolution is required for a real Evolution run")

    result = run_live(
        repo_root=Path(args.repo_root),
        task=args.task,
        language=args.language,
        keep_workspace=args.keep_workspace,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
