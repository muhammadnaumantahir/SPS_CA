"""Compatibility aliases for pre-core package paths.

Canonical code should import the *_core packages. These aliases keep older
scripts and persisted references working while the repository migrates.

Layer 10 is registered first because Layer 8 self-programming depends on its
``Change`` model. Registering aliases in numeric order used to create a
circular bootstrap where Layer 8 was imported before the Layer 10 alias
existed.
"""
from __future__ import annotations

import importlib
import sys

_ALIASES = {
    "layer_10_execution": "layer_10_execution_core",
    "layer_01_software_dna": "layer_01_software_dna_core",
    "layer_02_governance": "layer_02_governance_core",
    "layer_03_cognitive": "layer_03_cognitive_core",
    "layer_04_knowledge": "layer_04_knowledge_core",
    "layer_05_experience": "layer_05_experience_core",
    "layer_06_meta_learning": "layer_06_meta_learning_core",
    "layer_07_adaptation": "layer_07_adaptation_core",
    "layer_08_evolution": "layer_08_evolution_core",
    "layer_09_validation": "layer_09_verification_validation_core",
}

for _old, _new in _ALIASES.items():
    try:
        sys.modules[f"{__name__}.{_old}"] = importlib.import_module(f"{__name__}.{_new}")
    except ModuleNotFoundError:
        # Allows lightweight tooling to import layers before every package is present.
        pass
