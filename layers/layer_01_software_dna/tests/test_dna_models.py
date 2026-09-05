import pytest

from layers.layer_01_software_dna.capability_template import CapabilityTemplate
from layers.layer_01_software_dna.dna_rule import DNARule


class TestDNARule:
    def test_valid_rule_construction(self):
        rule = DNARule(id="rule_001", constraint="Never do X", severity="hard")
        assert rule.is_hard is True

    def test_soft_rule_is_not_hard(self):
        rule = DNARule(id="rule_002", constraint="Prefer Y", severity="soft")
        assert rule.is_hard is False

    def test_empty_id_rejected(self):
        with pytest.raises(ValueError):
            DNARule(id="", constraint="Never do X", severity="hard")

    def test_empty_constraint_rejected(self):
        with pytest.raises(ValueError):
            DNARule(id="rule_001", constraint="", severity="hard")

    def test_invalid_severity_rejected(self):
        with pytest.raises(ValueError):
            DNARule(id="rule_001", constraint="Never do X", severity="medium")

    def test_rule_is_immutable(self):
        rule = DNARule(id="rule_001", constraint="Never do X", severity="hard")
        with pytest.raises(Exception):
            rule.constraint = "Something else"

    def test_round_trip_dict(self):
        original = DNARule(
            id="rule_003",
            constraint="Never do Z",
            severity="soft",
            category="quality",
            rationale="because reasons",
        )
        restored = DNARule.from_dict(original.to_dict())
        assert restored == original


class TestCapabilityTemplate:
    def test_valid_construction(self):
        cap = CapabilityTemplate(
            id="CAP-001",
            name="Simple Bug Detection",
            version="0.1.0",
            description="Detects bugs",
            entry_point="capabilities.seeds.cap_001.run",
        )
        assert cap.origin == "seed"
        assert cap.status == "draft"

    def test_invalid_id_rejected(self):
        with pytest.raises(ValueError):
            CapabilityTemplate(
                id="not-a-cap-id",
                name="X",
                version="0.1.0",
                description="",
                entry_point="x.run",
            )

    def test_invalid_version_rejected(self):
        with pytest.raises(ValueError):
            CapabilityTemplate(
                id="CAP-001",
                name="X",
                version="v1",
                description="",
                entry_point="x.run",
            )

    @pytest.mark.parametrize(
        "bump,expected",
        [
            ("patch", "1.2.4"),
            ("minor", "1.3.0"),
            ("major", "2.0.0"),
        ],
    )
    def test_next_version(self, bump, expected):
        cap = CapabilityTemplate(
            id="CAP-001",
            name="X",
            version="1.2.3",
            description="",
            entry_point="x.run",
        )
        assert cap.next_version(bump) == expected

    def test_next_version_invalid_bump(self):
        cap = CapabilityTemplate(
            id="CAP-001",
            name="X",
            version="1.2.3",
            description="",
            entry_point="x.run",
        )
        with pytest.raises(ValueError):
            cap.next_version("sideways")

    def test_round_trip_dict(self):
        original = CapabilityTemplate(
            id="CAP-009",
            name="Generated One",
            version="0.2.1",
            description="An evolved capability",
            entry_point="capabilities.generated.cap_010.run",
            origin="generated",
            status="active",
            target_languages=["python"],
            parent_capability_id="CAP-002",
            tags=["repair"],
        )
        restored = CapabilityTemplate.from_dict(original.to_dict())
        assert restored == original
