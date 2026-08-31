import json

import pytest

from layers.layer_01_software_dna.dna_rule import DNARule
from layers.layer_01_software_dna.software_dna import (
    DNAViolation,
    SoftwareDNA,
)


def make_dna(rules=None):
    rules = rules or [
        DNARule(id="rule_001", constraint="Never modify governance", severity="hard"),
        DNARule(
            id="rule_009", constraint="Prefer small version bumps", severity="soft"
        ),
    ]
    return SoftwareDNA(rules=rules)


class TestSoftwareDNAInMemory:
    def test_hard_rule_blocks_action(self):
        dna = make_dna()
        result = dna.check_action("edit governance file", matched_rule_ids=["rule_001"])
        assert result.allowed is False
        assert result.violated_hard_rules[0].id == "rule_001"

    def test_soft_rule_does_not_block(self):
        dna = make_dna()
        result = dna.check_action("bump version by two", matched_rule_ids=["rule_009"])
        assert result.allowed is True
        assert result.warnings == ["rule_009: Prefer small version bumps"]

    def test_no_matched_rules_is_allowed(self):
        dna = make_dna()
        result = dna.check_action("do something unrelated")
        assert result.allowed is True
        assert result.violated_hard_rules == []

    def test_unknown_rule_id_is_ignored(self):
        dna = make_dna()
        result = dna.check_action("do something", matched_rule_ids=["rule_999"])
        assert result.allowed is True

    def test_enforce_raises_on_hard_violation(self):
        dna = make_dna()
        with pytest.raises(DNAViolation) as excinfo:
            dna.enforce("edit governance file", matched_rule_ids=["rule_001"])
        assert excinfo.value.rule.id == "rule_001"

    def test_enforce_passes_on_soft_violation(self):
        dna = make_dna()
        result = dna.enforce("bump version by two", matched_rule_ids=["rule_009"])
        assert result.allowed is True

    def test_get_rule(self):
        dna = make_dna()
        assert dna.get_rule("rule_001") is not None
        assert dna.get_rule("does_not_exist") is None

    def test_hard_and_soft_partitioning(self):
        dna = make_dna()
        assert [r.id for r in dna.hard_rules] == ["rule_001"]
        assert [r.id for r in dna.soft_rules] == ["rule_009"]

    def test_rules_is_read_only_view(self):
        dna = make_dna()
        rules_copy = dna.rules
        rules_copy.append(
            DNARule(id="rule_999", constraint="injected", severity="hard")
        )
        assert dna.get_rule("rule_999") is None

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("governance/dna_rules.json", True),
            ("layers/layer_01_software_dna/software_dna.py", True),
            ("layers/layer_07_governance/gate.py", True),
            ("layers/layer_02_cognitive_core/cognitive_core.py", False),
            ("projects/project_a/app.py", False),
        ],
    )
    def test_is_self_modification_of_governance(self, path, expected):
        dna = make_dna()
        assert dna.is_self_modification_of_governance(path) is expected


class TestSoftwareDNAFromRepoFile:
    """Exercises the real governance/dna_rules.json shipped in the repo."""

    def test_loads_default_rules_file(self):
        dna = SoftwareDNA()
        assert len(dna.rules) >= 8
        assert dna.get_rule("rule_001") is not None

    def test_default_rules_file_has_governance_self_protection(self):
        dna = SoftwareDNA()
        rule = dna.get_rule("rule_001")
        assert rule.is_hard is True
        assert (
            "governance" in rule.constraint.lower() or "dna" in rule.constraint.lower()
        )

    def test_reload_reads_from_disk(self):
        dna = SoftwareDNA()
        before = len(dna.rules)
        dna.reload()
        assert len(dna.rules) == before


class TestSoftwareDNAMissingFile:
    def test_missing_file_raises(self, tmp_path):
        missing = tmp_path / "does_not_exist.json"
        with pytest.raises(FileNotFoundError):
            SoftwareDNA(rules_path=missing)

    def test_empty_rules_file_raises(self, tmp_path):
        empty_file = tmp_path / "dna_rules.json"
        empty_file.write_text(json.dumps({"dna_rules": []}))
        with pytest.raises(ValueError):
            SoftwareDNA(rules_path=empty_file)

    def test_duplicate_rule_ids_raise(self, tmp_path):
        dup_file = tmp_path / "dna_rules.json"
        dup_file.write_text(
            json.dumps(
                {
                    "dna_rules": [
                        {"id": "rule_001", "constraint": "a", "severity": "hard"},
                        {"id": "rule_001", "constraint": "b", "severity": "soft"},
                    ]
                }
            )
        )
        with pytest.raises(ValueError):
            SoftwareDNA(rules_path=dup_file)
