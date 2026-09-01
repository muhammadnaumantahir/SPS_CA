"""Tests for CAP-009 Universal Parser."""
from capabilities.base import CapabilityContext
from capability import run, universal_parser


def test_parse_json():
    assert universal_parser('{"key": "value"}', "json") == {"key": "value"}


def test_parse_xml():
    assert universal_parser("<root><item>value</item></root>", "xml") == {"root": {"item": "value"}}


def test_parse_csv():
    assert universal_parser("name,age\nNomi,30\nSara,25\n", "csv") == [
        {"name": "Nomi", "age": "30"},
        {"name": "Sara", "age": "25"},
    ]


def test_parse_yaml():
    assert universal_parser("name: Nomi\nactive: true\ncount: 2\n", "yaml") == {
        "name": "Nomi", "active": True, "count": 2
    }


def test_run_returns_structured_result():
    result = run(CapabilityContext(code='{"ok": true}', language="python", parameters={"format": "json"}))
    assert result.success
    assert result.findings[0]["value"] == {"ok": True}


def test_invalid_format():
    try:
        universal_parser("x", "toml")
    except ValueError as exc:
        assert "Unsupported format" in str(exc)
    else:
        raise AssertionError("Expected unsupported format error")


def test_invalid_json_is_reported():
    result = run(CapabilityContext(code="{bad", language="python", parameters={"format": "json"}))
    assert not result.success
    assert result.error
