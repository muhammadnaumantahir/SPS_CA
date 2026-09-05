import json

import pytest

from layers.layer_01_software_dna.dna_rule import DNARule
from layers.layer_01_software_dna.software_dna import DNAViolation, SoftwareDNA


def make_dna(rules=None):
    rules = rules or [
        DNARule(id="rule_001", constraint="Never modify governance", severity="hard"),
        DNARule(id="rule_002", constraint="Never bypass governance", severity="hard"),
        DNARule(id="rule_003", constraint="Never bypass validation", severity="hard"),
        DNARule(id="rule_004", constraint="Never execute outside sandbox", severity="hard"),
        DNARule(id="rule_007", constraint="Never self-modify without rollback", severity="hard"),
        DNARule(id="rule_009", constraint="Prefer small version bumps", severity="soft"),
    ]
    return SoftwareDNA(rules=rules)


class TestSoftwareDNAInMemory:
    def test_hard_rule_blocks_action(self):
        dna = make_dna()
        result = dna.check_action("edit governance file", matched_rule_ids=["rule_001"])
        assert result.allowed is False
        assert result.violated_hard_rules[0].id == "rule_001"

    def test_hard_rule_cannot_be_bypassed_by_omitting_matched_ids(self):
        dna = make_dna()
        result = dna.check_action("Modify governance configuration", affected_files=["governance/dna_rules.json"])
        assert result.allowed is False
        assert "rule_001" in [rule.id for rule in result.violated_hard_rules]

    def test_self_change_requires_all_safety_boundaries(self):
        dna = make_dna()
        result = dna.check_action(
            "change core logic",
            affected_files=["core/example.py"],
            governed=False,
            validated=False,
            sandboxed=False,
            require_rollback=False,
        )
        assert result.allowed is False
        assert {r.id for r in result.violated_hard_rules} >= {"rule_002", "rule_003", "rule_004", "rule_007"}

    def test_self_change_passes_when_boundaries_are_established(self):
        dna = make_dna()
        result = dna.check_action(
            "change core logic",
            affected_files=["core/example.py"],
            governed=True,
            validated=True,
            sandboxed=True,
            require_rollback=True,
        )
        assert result.allowed is True

    def test_soft_rule_does_not_block(self):
        dna = make_dna()
        result = dna.check_action("bump version by two", matched_rule_ids=["rule_009"])
        assert result.allowed is True
        assert result.warnings == ["rule_009: Prefer small version bumps"]

    def test_no_matched_rules_is_allowed_for_unrelated_action(self):
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
        assert [r.id for r in dna.hard_rules] == ["rule_001", "rule_002", "rule_003", "rule_004", "rule_007"]
        assert [r.id for r in dna.soft_rules] == ["rule_009"]

    def test_rules_is_read_only_view(self):
        dna = make_dna()
        rules_copy = dna.rules
        rules_copy.append(DNARule(id="rule_999", constraint="injected", severity="hard"))
        assert dna.get_rule("rule_999") is None

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("governance/dna_rules.json", True),
            ("layers/layer_01_software_dna/software_dna.py", True),
            ("layers/layer_02_governance/gate.py", True),
            ("layers/layer_03_cognitive/cognitive_core.py", False),
            ("projects/project_a/app.py", False),
        ],
    )
    def test_is_self_modification_of_governance(self, path, expected):
        dna = make_dna()
        assert dna.is_self_modification_of_governance(path) is expected


class TestSoftwareDNAFromRepoFile:
    def test_loads_default_rules_file(self):
        dna = SoftwareDNA()
        assert len(dna.rules) >= 8
        assert dna.get_rule("rule_001") is not None

    def test_default_rules_file_has_governance_self_protection(self):
        dna = SoftwareDNA()
        rule = dna.get_rule("rule_001")
        assert rule.is_hard is True
        assert "governance" in rule.constraint.lower() or "dna" in rule.constraint.lower()

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
        dup_file.write_text(json.dumps({"dna_rules": [
            {"id": "rule_001", "constraint": "a", "severity": "hard"},
            {"id": "rule_001", "constraint": "b", "severity": "soft"},
        ]}))
        with pytest.raises(ValueError):
            SoftwareDNA(rules_path=dup_file)
