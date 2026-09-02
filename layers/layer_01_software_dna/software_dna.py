"""Layer 1: Software DNA.

Loads the immutable rule set from ``governance/dna_rules.json`` and provides
the single enforcement surface every other layer must consult before an
action that changes SPS-CA's own logic is allowed to proceed.

Design intent (per the master document / architecture v2): DNA rules are
read-only at runtime. There is deliberately no public API on this class
that mutates a loaded rule. ``reload()`` re-reads from disk, it does not
patch rules in place.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

from .dna_rule import DNARule

DEFAULT_DNA_RULES_PATH = (
    Path(__file__).resolve().parents[2] / "governance" / "dna_rules.json"
)


class DNAViolation(Exception):
    """Raised when a proposed action violates a hard DNA rule."""

    def __init__(self, rule: DNARule, action_description: str):
        self.rule = rule
        self.action_description = action_description
        super().__init__(
            f"DNA violation: action {action_description!r} violates "
            f"{rule.id} ({rule.constraint!r})"
        )


@dataclass
class DNACheckResult:
    """Outcome of checking a proposed action against all DNA rules."""

    allowed: bool
    violated_hard_rules: List[DNARule] = field(default_factory=list)
    violated_soft_rules: List[DNARule] = field(default_factory=list)

    @property
    def warnings(self) -> List[str]:
        return [f"{r.id}: {r.constraint}" for r in self.violated_soft_rules]


class SoftwareDNA:
    """Loads and enforces the immutable SPS-CA rule set.

    Usage:
        dna = SoftwareDNA()
        result = dna.check_action(
            action_description="Modify governance/dna_rules.json",
            matched_rule_ids=["rule_001"],
        )
        if not result.allowed:
            ...
    """

    def __init__(
        self,
        rules_path: Optional[Path] = None,
        rules: Optional[Iterable[DNARule]] = None,
    ):
        self._rules_path = Path(rules_path) if rules_path else DEFAULT_DNA_RULES_PATH
        if rules is not None:
            self._rules: List[DNARule] = list(rules)
        else:
            self._rules = self._load(self._rules_path)

    @staticmethod
    def _load(path: Path) -> List[DNARule]:
        if not path.exists():
            raise FileNotFoundError(
                f"DNA rules file not found at {path}. "
                "SPS-CA cannot operate without its governance rules."
            )
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        raw_rules = data.get("dna_rules", [])
        if not raw_rules:
            raise ValueError(f"DNA rules file at {path} contains no rules")
        rules = [DNARule.from_dict(r) for r in raw_rules]
        ids = [r.id for r in rules]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate DNA rule ids found in rules file")
        return rules

    def reload(self) -> None:
        """Re-read rules from disk. Does not mutate any existing rule object."""
        self._rules = self._load(self._rules_path)

    @property
    def rules(self) -> List[DNARule]:
        """All loaded rules (read-only view)."""
        return list(self._rules)

    @property
    def hard_rules(self) -> List[DNARule]:
        return [r for r in self._rules if r.is_hard]

    @property
    def soft_rules(self) -> List[DNARule]:
        return [r for r in self._rules if not r.is_hard]

    def get_rule(self, rule_id: str) -> Optional[DNARule]:
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None

    def check_action(
        self,
        action_description: str,
        matched_rule_ids: Optional[Iterable[str]] = None,
    ) -> DNACheckResult:
        """Check whether a proposed action is permitted.

        ``matched_rule_ids`` is the set of rule ids that upstream analysis
        (typically Layer 7: Governance) has determined are relevant to this
        action. Layer 1 itself does not decide relevance — it enforces
        severity once relevance has been established. This keeps rule
        matching logic out of the immutable DNA layer, which is intentional:
        the DNA layer's job is to be a stable, minimal enforcement point.
        """
        matched_rule_ids = set(matched_rule_ids or [])
        violated_hard: List[DNARule] = []
        violated_soft: List[DNARule] = []

        for rule_id in matched_rule_ids:
            rule = self.get_rule(rule_id)
            if rule is None:
                continue
            if rule.is_hard:
                violated_hard.append(rule)
            else:
                violated_soft.append(rule)

        return DNACheckResult(
            allowed=len(violated_hard) == 0,
            violated_hard_rules=violated_hard,
            violated_soft_rules=violated_soft,
        )

    def enforce(
        self,
        action_description: str,
        matched_rule_ids: Optional[Iterable[str]] = None,
    ) -> DNACheckResult:
        """Like :meth:`check_action`, but raises :class:`DNAViolation` on a
        hard-rule violation instead of returning a result the caller might
        forget to check."""
        result = self.check_action(action_description, matched_rule_ids)
        if not result.allowed:
            raise DNAViolation(result.violated_hard_rules[0], action_description)
        return result

    def is_self_modification_of_governance(self, target_path: str) -> bool:
        """Convenience check used across layers: is a target path part of
        the governance/DNA surface itself? Modifying these paths is the
        canonical hard-rule violation (rule_001)."""
        protected_prefixes = (
            "governance/",
            "layers/layer_01_software_dna/",
            "layers/layer_02_governance/",
        )
        normalized = target_path.replace("\\", "/").lstrip("./")
        return normalized.startswith(protected_prefixes)
