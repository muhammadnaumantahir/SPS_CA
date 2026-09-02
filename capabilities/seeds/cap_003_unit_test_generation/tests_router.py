from __future__ import annotations

from capabilities.base import CapabilityContext, CapabilityResult
from capabilities.seeds.cap_003_unit_test_generation import capability as cap003
from capabilities.seeds.cap_003_unit_test_generation.request_router import _is_explicit_modification, run


def test_add_function_is_not_test_generation():
    assert _is_explicit_modification("add this function")


def test_input_validation_is_not_test_generation():
    assert _is_explicit_modification("add input validation to this function")


def test_validate_inputs_is_not_test_generation():
    assert _is_explicit_modification("validate inputs in this function")


def test_add_tests_still_uses_test_capability():
    assert not _is_explicit_modification("add unit tests for this function")


def test_direct_cap003_entry_point_routes_explicit_modification(monkeypatch):
    calls = []

    def fake_modify(context):
        calls.append(context.metadata.get("request"))
        return CapabilityResult.ok(
            summary="fake modification",
            modified_code=context.code + "\n# modified\n",
        )

    monkeypatch.setattr(cap003, "modify_code", fake_modify)
    context = CapabilityContext(
        code="def add(a, b):\n    return a + b\n",
        language="python",
        file_path="module.py",
        metadata={"request": "add input validation to this function"},
    )

    result = cap003.run(context)

    assert result.success is True
    assert result.modified_code is not None
    assert calls == ["add input validation to this function"]


def test_router_routes_explicit_modification(monkeypatch):
    calls = []

    def fake_modify(context):
        calls.append("modify")
        return CapabilityResult.ok(summary="fake modification", modified_code="changed")

    monkeypatch.setattr(
        "capabilities.seeds.cap_003_unit_test_generation.request_router.modify_code",
        fake_modify,
    )
    context = CapabilityContext(
        code="def add(a, b):\n    return a + b\n",
        language="python",
        metadata={"request": "add this function"},
    )

    result = run(context)

    assert result.modified_code == "changed"
    assert calls == ["modify"]
