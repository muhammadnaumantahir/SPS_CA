"""Tests for CAP-009 (Parse Error Handler)."""

from __future__ import annotations

from capabilities.base import CapabilityContext
from capabilities.generated.cap_010.capability import run


def test_parse_error_detects_reported_pattern():
    context = CapabilityContext(code="reproduces the trigger pattern", language='python')
    result = run(context)
    assert result.success
    assert result.findings
    assert result.findings[0]["trigger_pattern"] == 'Parse error'


def test_parse_error_fails_gracefully_on_empty_input():
    context = CapabilityContext(code="", language='python')
    result = run(context)
    assert not result.success
    assert result.error


def test_parse_error_no_ops_on_unsupported_language():
    context = CapabilityContext(code="some code", language="__unsupported__")
    result = run(context)
    assert result.success
    assert result.modified_code is None
