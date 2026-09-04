"""Compatibility package for the renamed Layer 5 implementation.

The canonical implementation lives in :mod:`layers.layer_05_experience_core`.
Keep legacy package and submodule imports working for existing code/tests.
"""

from importlib import import_module
import sys

# Register legacy submodules before importing the canonical package exports.
# Layer 8 can import ExperienceLog while Layer 5 is still initializing.
for _module_name in ("experience_log", "models", "long_term_learning"):
    sys.modules[f"{__name__}.{_module_name}"] = import_module(
        f"layers.layer_05_experience_core.{_module_name}"
    )

from layers.layer_05_experience_core import *

del import_module, sys, _module_name
