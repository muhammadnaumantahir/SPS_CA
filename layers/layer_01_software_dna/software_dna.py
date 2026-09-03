"""Layer 1: Software DNA.

The DNA layer is the non-bypassable enforcement point for hard SPS-CA
self-programming constraints. It loads the immutable rule set and performs
its own mechanical checks from the requested action and target paths; callers
may add matched rule ids, but they cannot make a hard rule disappear by
omitting an id.
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
    checked_rule_ids: List[str] = field(default_factory=list)

    @property
    def warnings(self) -> List[str]:
        return [f"{r.id}: {r.constraint}" for r in self.violated_soft_rules]


class SoftwareDNA:
    """Load and enforce the immutable SPS-CA rule set.

    ``matched_rule_ids`` is only supplemental evidence. Layer 1 independently
    evaluates the action description and target files for hard constraints.
    This is deliberate: an upstream caller cannot bypass DNA by passing an
    empty or incomplete matched-rule list.
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
                f"DNA rules file not found at {path}. SPS-CA cannot operate without its governance rules."
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
        affected_files: Optional[Iterable[str]] = None,
        *,
        require_rollback: bool = False,
        validated: bool = False,
        governed: bool = False,
        sandboxed: bool = False,
        explicit_user_request: bool = True,
    ) -> DNACheckResult:
        """Check an action against supplied evidence and mechanical DNA rules.

        Hard rules are inferred from the action, files, and execution-state
        flags. ``matched_rule_ids`` can add evidence but is never required for
        a hard rule to trigger.
        """
        action = (action_description or "").strip().lower()
        files = {self._normalize_path(p) for p in (affected_files or []) if p}
        matched = set(matched_rule_ids or [])
        violated_hard: List[DNARule] = []
        violated_soft: List[DNARule] = []

        def add(rule_id: str, *, hard: Optional[bool] = None) -> None:
            rule = self.get_rule(rule_id)
            if rule is None:
                return
            is_hard = rule.is_hard if hard is None else hard
            target = violated_hard if is_hard else violated_soft
            if all(existing.id != rule.id for existing in target):
                target.append(rule)

        # Caller evidence remains supported, but only as an additional signal.
        for rule_id in matched:
            rule = self.get_rule(rule_id)
            if rule:
                add(rule_id, hard=rule.is_hard)

        # rule_001 / rule_005: protected control and audit surfaces.
        governance_words = ("governance", "dna", "software dna", "approval gate", "governance gate")
        trace_words = ("experience log", "audit trail", "lineage", "evolution history", "trace")
        if files and any(self.is_self_modification_of_governance(p) for p in files):
            add("rule_001")
        if files and any(self._is_trace_path(p) for p in files):
            if any(word in action for word in ("delete", "overwrite", "truncate", "clear", "replace")):
                add("rule_005")
        if any(word in action for word in governance_words) and any(
            word in action for word in ("disable", "bypass", "modify", "change", "remove", "overwrite", "rewrite")
        ):
            add("rule_001")

        # rule_002 / rule_003 / rule_004: the self-programming pipeline cannot
        # skip its safety boundaries.
        if any(word in action for word in ("bypass governance", "skip governance", "disable governance", "without approval")):
            add("rule_002")
        if any(word in action for word in ("bypass validation", "skip validation", "disable validation", "without tests")):
            add("rule_003")
        if any(word in action for word in ("run outside sandbox", "execute unsandboxed", "disable sandbox", "bypass sandbox")):
            add("rule_004")

        # State assertions prevent an execution path from claiming compliance
        # when its required boundary was not actually established.
        self_change = bool(files) and any(
            p.startswith(("brain/", "core/", "layers/", "capabilities/", "experience/", "governance/"))
            for p in files
        )
        if self_change and not governed:
            add("rule_002")
        if self_change and not validated:
            add("rule_003")
        if self_change and not sandboxed:
            add("rule_004")
        if self_change and require_rollback is False:
            add("rule_007")

        # rule_006: reject obvious credentials in descriptions or target names.
        secret_tokens = ("ghp_", "github_pat_", "api_key", "apikey", "access_token", "secret_key", "password=")
        if any(token in action for token in secret_tokens) or any(
            token in p.lower() for p in files for token in (".env", "secret", "credential")
        ):
            add("rule_006")

        # rule_008: target-project writes need explicit user scope.
        if files and any(p.startswith("projects/") or p.startswith("project/") for p in files) and not explicit_user_request:
            add("rule_008")

        # Soft rule 011 is intentionally advisory; unsupported language should
        # not be converted into a hard denial.
        supported = {"python", "java", "javascript", "typescript", "go", "csharp"}
        if any(word in action for word in (" generate ", " generated ", " capability ")) and not any(
            language in action for language in supported
        ):
            add("rule_011")

        checked_ids = sorted({r.id for r in self._rules if r.id in matched or r in violated_hard or r in violated_soft})
        return DNACheckResult(
            allowed=not violated_hard,
            violated_hard_rules=violated_hard,
            violated_soft_rules=violated_soft,
            checked_rule_ids=checked_ids,
        )

    def enforce(self, action_description: str, matched_rule_ids: Optional[Iterable[str]] = None, **kwargs) -> DNACheckResult:
        result = self.check_action(action_description, matched_rule_ids, **kwargs)
        if not result.allowed:
            raise DNAViolation(result.violated_hard_rules[0], action_description)
        return result

    @staticmethod
    def _normalize_path(path: str) -> str:
        return path.replace("\\", "/").lstrip("./")

    @staticmethod
    def _is_trace_path(path: str) -> bool:
        normalized = SoftwareDNA._normalize_path(path)
        return normalized.startswith(("experience/", "runtime/evolution", "runtime/trace"))

    def is_self_modification_of_governance(self, target_path: str) -> bool:
        protected_prefixes = (
            "governance/",
            "layers/layer_01_software_dna/",
            "layers/layer_02_governance/",
        )
        normalized = self._normalize_path(target_path)
        return normalized.startswith(protected_prefixes)
