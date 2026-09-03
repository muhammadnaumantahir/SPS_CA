"""Hardened Phase-1 self-programming facade.

The implementation lives in :mod:`self_programming`, while this facade makes
its Software DNA call prove that the required safety boundaries are actually
established before a mutation can execute.
"""

from __future__ import annotations

from layers.layer_01_software_dna import SoftwareDNA
from layers.layer_10_execution import Change

from .self_programming import SelfProgrammingEngine as BaseSelfProgrammingEngine


class SelfProgrammingEngine(BaseSelfProgrammingEngine):
    """Controlled self-programming with an explicit Layer-1 safety proof."""

    def _check_dna(self, change: Change) -> tuple[str, bool]:
        result = self.dna.check_action(
            action_description=change.description,
            affected_files=[edit.file_path for edit in change.edits],
            require_rollback=True,
            validated=True,
            governed=True,
            sandboxed=True,
            explicit_user_request=False,
        )
        details = []
        if result.violated_hard_rules:
            details.append(
                "hard=" + ",".join(rule.id for rule in result.violated_hard_rules)
            )
        if result.violated_soft_rules:
            details.append(
                "soft=" + ",".join(rule.id for rule in result.violated_soft_rules)
            )
        checked = ",".join(result.checked_rule_ids) or "none"
        return (
            f"DNA checked [{checked}]" + (f" ({'; '.join(details)})" if details else ""),
            result.allowed,
        )


__all__ = ["SelfProgrammingEngine"]
