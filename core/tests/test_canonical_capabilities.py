import json
from pathlib import Path
from capabilities.canonical import CANONICAL_CAPABILITIES
from capabilities.base import CapabilityContext
from capabilities.canonical_runtime import DISPATCH, test_generation, validation

def test_exactly_ten_canonical_capabilities():
    assert [x["id"] for x in CANONICAL_CAPABILITIES]==[f"CAP-{i:03d}" for i in range(1,11)]
    assert len(DISPATCH)==10

def test_test_generation_requires_explicit_request():
    r=test_generation(CapabilityContext(code="def add(a,b):\n    return a+b\n",language="python",file_path="main.py",metadata={"request":"Create a calculator"}))
    assert not r.success

def test_validation_does_not_modify_source():
    source="def add(a,b):\n    return a+b\n"
    r=validation(CapabilityContext(code=source,language="python",file_path="main.py"))
    assert r.success and r.modified_code is None

def test_registry_generated_ids_are_above_reserved_range():
    data=json.loads(Path("capabilities/registry.json").read_text())
    assert [c["id"] for c in data["capabilities"] if c.get("canonical")]==[f"CAP-{i:03d}" for i in range(1,11)]
    assert all(int(c["id"].split("-")[-1])>10 for c in data["capabilities"] if c.get("generated"))
