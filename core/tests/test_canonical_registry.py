import json
from pathlib import Path
from capabilities.canonical import CANONICAL_CAPABILITIES

def test_canonical_range_is_exactly_ten():
    assert [c["id"] for c in CANONICAL_CAPABILITIES] == [f"CAP-{i:03d}" for i in range(1,11)]
    assert len({c["id"] for c in CANONICAL_CAPABILITIES}) == 10

def test_registry_has_exactly_ten_canonical_capabilities_and_generated_above_ten():
    data=json.loads(Path("capabilities/registry.json").read_text())
    canonical=[c for c in data["capabilities"] if c.get("canonical")]
    generated=[c for c in data["capabilities"] if c.get("generated")]
    assert [c["id"] for c in canonical] == [f"CAP-{i:03d}" for i in range(1,11)]
    assert all(int(c["id"].split("-")[-1]) > 10 for c in generated)

def test_canonical_metadata_has_intent_contracts():
    for c in CANONICAL_CAPABILITIES:
        assert c["intent_class"]
        assert c["allowed_intents"]
        assert "test_generation" in c["forbidden_intents"] or c["id"] == "CAP-007"
        assert c["risk_level"] in {"low","medium","high"}
