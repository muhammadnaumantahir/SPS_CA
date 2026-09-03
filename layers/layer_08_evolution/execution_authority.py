"""Explicit execution authority for automated Layer-8 evolution.

Optimization evidence may propose Evolution work, but proposal alone is never
permission to mutate the capability registry. This policy creates a single,
explicit authority boundary that can be enabled by the deployment environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


@dataclass(frozen=True)
class EvolutionExecutionAuthority:
    """Deployment-level permission for automatic Evolution execution."""

    enabled: bool = False
    max_actions_per_cycle: int = 1
    source: str = "default-deny"

    @classmethod
    def from_environment(cls) -> "EvolutionExecutionAuthority":
        raw_enabled = os.getenv("SPS_CA_AUTO_EVOLVE", "").strip().lower()
        enabled = raw_enabled in TRUE_VALUES
        try:
            max_actions = int(os.getenv("SPS_CA_AUTO_EVOLVE_MAX_ACTIONS", "1"))
        except ValueError:
            max_actions = 1
        return cls(
            enabled=enabled,
            max_actions_per_cycle=max(1, min(max_actions, 10)),
            source="environment",
        )

    def authorize(self, action_count: int) -> tuple[bool, str]:
        """Return whether this number of actions may execute automatically."""
        if not self.enabled:
            return False, "automatic Evolution execution is disabled"
        if action_count < 1:
            return False, "no Evolution actions were proposed"
        if action_count > self.max_actions_per_cycle:
            return False, f"action count {action_count} exceeds authority limit {self.max_actions_per_cycle}"
        return True, "automatic Evolution execution is explicitly authorized"


__all__ = ["EvolutionExecutionAuthority"]
