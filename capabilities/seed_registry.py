"""Discovery of SPS-CA seed capabilities.

The Brain is deliberately outside this registry. This registry contains only
executable SPS capabilities. Legacy prompt-processing metadata is ignored so
CAP-001 remains a real coding capability rather than becoming the Brain.
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
    """Load executable built-in capabilities in numeric ID order."""
    templates = []
    for path in list_seed_metadata_paths():
        with path.open("r", encoding="utf-8") as fh:
            metadata = json.load(fh)
        if metadata.get("status") == "retired":
            continue
        templates.append(CapabilityTemplate.from_dict(metadata))
    return sorted(templates, key=lambda template: int(template.id.split("-")[-1]))


def load_entry_point(template: CapabilityTemplate) -> Callable:
    """Resolve a capability's ``entry_point`` dotted path to a callable."""
    module_path, _, func_name = template.entry_point.rpartition(".")
    if not module_path:
        raise ValueError(f"Malformed entry_point: {template.entry_point!r}")
    module = importlib.import_module(module_path)
    return getattr(module, func_name)
