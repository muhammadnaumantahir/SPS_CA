from __future__ import annotations

from capabilities.base import CapabilityContext
from capabilities.seeds.cap_003_unit_test_generation.request_router import _is_explicit_modification


def test_add_function_is_not_test_generation():
    assert _is_explicit_modification("add this function")


def test_input_validation_is_not_test_generation():
    assert _is_explicit_modification("add input validation to this function")


def test_add_tests_still_uses_test_capability():
    assert not _is_explicit_modification("add unit tests for this function")
