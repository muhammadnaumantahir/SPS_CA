"""Compatibility package for the renamed Layer 8 implementation.

The canonical implementation lives in :mod:`layers.layer_08_evolution_core`.
Keep legacy package and submodule imports working for existing code/tests.
"""

from importlib import import_module
import sys

from layers.layer_08_evolution_core import *

for _module_name in (
    "capability_improvement",
    "controlled_evolution",
    "evolution_cycle",
    "evolution_engine",
    "evolution_evidence",
    "evolution_transaction",
    "execution_authority",
    "gap_planner",
    "governed_self_programming",
    "growth_decision",
    "models",
    "optimization_action_planner",
    "retirement",
    "self_programming",
):
    sys.modules[f"{__name__}.{_module_name}"] = import_module(
        f"layers.layer_08_evolution_core.{_module_name}"
    )

del import_module, sys, _module_name
