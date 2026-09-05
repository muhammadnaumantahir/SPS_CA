from __future__ import annotations

import json
from pathlib import Path

from layers.layer_05_experience.experience_log import ExperienceLog
from layers.layer_05_experience.models import Task
from layers.layer_08_evolution.evolution_engine import EvolutionEngine
from layers.layer_08_evolution.models import EvolutionTrigger


def _log(count: int = 3) -> ExperienceLog:
    log = ExperienceLog()
    for i in range(count):
        log.add_task(Task(id=f"task_{i}", user_request="parse", status="failure", failure_category="Parse error", selected_capability="CAP-004"))
    return log


def test_repeated_failure_triggers_evolution(tmp_path: Path):
    engine = EvolutionEngine(generated_dir=str(tmp_path / "generated"), seeds_dir=str(tmp_path / "seeds"))
    assert engine.should_evolve(_log(3)) is True
    assert engine.should_evolve(_log(2)) is False


def test_next_id_stays_outside_canonical_range(tmp_path: Path):
    seeds = tmp_path / "seeds"
    for number in range(1, 11):
        folder = seeds / f"cap_{number:03d}"
        folder.mkdir(parents=True)
        (folder / "metadata.json").write_text(json.dumps({"id": f"CAP-{number:03d}"}), encoding="utf-8")
    engine = EvolutionEngine(generated_dir=str(tmp_path / "generated"), seeds_dir=str(seeds))
    assert int(engine.next_capability_id().split("-")[1]) > 10


def test_plan_can_create_first_generated_capability_above_baseline(tmp_path: Path):
    engine = EvolutionEngine(generated_dir=str(tmp_path / "generated"), seeds_dir=str(tmp_path / "seeds"))
    trigger = EvolutionTrigger(pattern="Parse error", occurrence_count=3, trigger_task_ids=["task_0", "task_1", "task_2"])
    plan = engine.plan_new_capability(trigger, capability_id="CAP-011")
    assert plan.capability_id == "CAP-011"
    assert plan.entry_point.endswith("cap_011.capability.run")
