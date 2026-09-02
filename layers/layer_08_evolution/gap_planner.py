"""Capability-gap planning within Layer 8 (Evolution).

A capability gap is a first-class evolution trigger for the SPS-CA
prototype. Unlike the historical repeated-failure trigger, a gap can be
identified immediately when the task requires a behavior absent from the
registered capability set. This module only plans the capability; the existing
Layer 8 generation/testing pipeline remains responsible for implementation and
quality gates.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from .models import CapabilityPlan


FIRST_GENERATED_NUMBER = 9


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "capability"


def _module_name(capability_id: str) -> str:
    return capability_id.lower().replace("-", "_")


class CapabilityGapPlanner:
    """Create research-traceable Layer 8 plans when no capability fits."""

    def __init__(
        self,
        *,
        seeds_dir: str = "capabilities/seeds",
        generated_dir: str = "capabilities/generated",
    ) -> None:
        self.seeds_dir = Path(seeds_dir)
        self.generated_dir = Path(generated_dir)

    def plan(
        self,
        *,
        task_description: str,
        language: str,
        reason: str,
        task_id: Optional[str] = None,
    ) -> CapabilityPlan:
        """Produce a new capability plan from an explicit capability gap."""
        if not task_description.strip():
            raise ValueError("task_description must be non-empty")
        if not language.strip():
            raise ValueError("language must be non-empty")
        if not reason.strip():
            raise ValueError("reason must be non-empty")

        capability_id = self.next_capability_id()
        trigger_pattern = self._infer_trigger_pattern(task_description)
        name = f"{self._display_name(trigger_pattern)} Handler"
        module = _module_name(capability_id)
        task_suffix = f" (task: {task_id})" if task_id else ""

        return CapabilityPlan(
            capability_id=capability_id,
            name=name,
            description=(
                f"Generated to address a capability gap: {reason}. "
                f"The requested behavior is '{task_description.strip()}'{task_suffix}."
            ),
            entry_point=f"capabilities.generated.{module}.capability.run",
            supported_languages=[language.lower()],
            trigger_pattern=trigger_pattern,
            trigger_task_ids=[task_id] if task_id else [],
            test_case_names=[
                f"test_{trigger_pattern}_handles_supported_input",
                f"test_{trigger_pattern}_fails_cleanly_without_code",
                f"test_{trigger_pattern}_no_ops_on_unsupported_language",
            ],
            provenance={
                "trigger": "capability_gap",
                "why": reason,
                "what": task_description.strip(),
                "when": "scenario_time",
                "how": "Layer 8 gap planner converted an unmet capability requirement into a CapabilityPlan",
                "language": language.lower(),
                "task_id": task_id,
            },
        )

    def next_capability_id(self) -> str:
        """Return the smallest unused generated CAP-NNN identifier."""
        used = set()
        for root in (self.seeds_dir, self.generated_dir):
            if not root.exists():
                continue
            for metadata_path in root.glob("*/metadata.json"):
                try:
                    data = json.loads(metadata_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                match = re.fullmatch(r"CAP-(\d+)", str(data.get("id", "")))
                if match:
                    used.add(int(match.group(1)))

        candidate = FIRST_GENERATED_NUMBER
        while candidate in used:
            candidate += 1
        return f"CAP-{candidate:03d}"

    @staticmethod
    def _infer_trigger_pattern(task_description: str) -> str:
        text = task_description.lower()
        rules = (
            (r"input\s+validat|validat(?:e|ion).*input", "input_validation"),
            (r"parameteri[sz].*sql|sql.*parameteri[sz]", "sql_parameterization"),
            (r"authentication|authorize|authorization", "authentication"),
            (r"logging|log\s+request|audit\s+log", "logging"),
            (r"cache|caching", "caching"),
            (r"serialization|deserialize|serialize", "serialization"),
        )
        for pattern, trigger in rules:
            if re.search(pattern, text):
                return trigger
        words = [word for word in re.findall(r"[a-z0-9]+", text) if len(word) > 3]
        return _slugify("_".join(words[:4])) or "general_capability_gap"

    @staticmethod
    def _display_name(trigger_pattern: str) -> str:
        return trigger_pattern.replace("_", " ").strip().title()
