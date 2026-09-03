from brain.evolution_designer import AICapabilityDesigner


def test_ai_capability_design_requires_runtime_contract():
    valid = """
from capabilities.base import CapabilityContext, CapabilityResult


def run(context: CapabilityContext) -> CapabilityResult:
    return CapabilityResult.ok(summary="ok")
"""
    tests = "def test_generated():\n    assert True\n"
    assert AICapabilityDesigner._require_source(valid) == valid.strip()
    assert AICapabilityDesigner._require_tests(tests) == tests.strip()


def test_ai_capability_design_rejects_missing_run_contract():
    try:
        AICapabilityDesigner._require_source("print('not a capability')")
    except ValueError as exc:
        assert "run(CapabilityContext)" in str(exc)
    else:
        raise AssertionError("expected invalid capability contract to be rejected")
