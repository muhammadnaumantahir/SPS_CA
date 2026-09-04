"""Regression tests for legacy layer package compatibility imports."""

import subprocess
import sys


def test_layer_05_legacy_submodules():
    from layers.layer_05_experience.experience_log import ExperienceLog
    from layers.layer_05_experience.long_term_learning import LongTermLearningStore
    from layers.layer_05_experience.models import Task

    assert ExperienceLog
    assert LongTermLearningStore
    assert Task


def test_layer_08_legacy_submodules():
    from layers.layer_08_evolution.evolution_engine import EvolutionEngine
    from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore
    from layers.layer_08_evolution.growth_decision import GrowthDecisionEngine
    from layers.layer_08_evolution.models import CapabilityPlan

    assert EvolutionEngine
    assert EvolutionEvidenceStore
    assert GrowthDecisionEngine
    assert CapabilityPlan


def test_layer_08_legacy_import_from_fresh_process():
    code = "from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore; print(EvolutionEvidenceStore.__name__)"
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "EvolutionEvidenceStore" in result.stdout


def test_canonical_pipeline_import():
    from core.canonical_sps_pipeline import CanonicalSPSPipeline

    assert CanonicalSPSPipeline
