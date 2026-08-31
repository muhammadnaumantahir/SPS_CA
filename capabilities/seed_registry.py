"""Discovery of seed capabilities.

This is intentionally lightweight: it walks ``capabilities/seeds/*/metadata.json``
and returns :class:`~layers.layer_01_software_dna.CapabilityTemplate` objects.
Layer 9 (Capability Registry) will later own the full lifecycle (activation,
deprecation, generated-capability registration); this module only covers
what Phase 1 needs -- discovering the built-in seed set.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Callable, List

from layers.layer_01_software_dna import CapabilityTemplate

SEEDS_DIR = Path(__file__).resolve().parent / "seeds"


def list_seed_metadata_paths() -> List[Path]:
    if not SEEDS_DIR.exists():
        return []
    return sorted(SEEDS_DIR.glob("*/metadata.json"))


def load_seed_capabilities() -> List[CapabilityTemplate]:
    """Load every seed capability's metadata as a CapabilityTemplate."""
    templates = []
    for path in list_seed_metadata_paths():
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        templates.append(CapabilityTemplate.from_dict(data))
    return templates


def load_entry_point(template: CapabilityTemplate) -> Callable:
    """Resolve a capability's ``entry_point`` dotted path to a callable."""
    module_path, _, func_name = template.entry_point.rpartition(".")
    if not module_path:
        raise ValueError(f"Malformed entry_point: {template.entry_point!r}")
    module = importlib.import_module(module_path)
    return getattr(module, func_name)
