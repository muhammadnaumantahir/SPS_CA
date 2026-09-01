"""CAP-009 Universal Parser generated from repeated parsing failures.

Supports JSON, XML, CSV and a deliberately small YAML subset without adding a
runtime dependency. The module follows the SPS-CA capability contract.
"""
from __future__ import annotations

import csv
import io
import json
import re
import xml.etree.ElementTree as ET
from typing import Any

from capabilities.base import CapabilityContext, CapabilityResult


def universal_parser(data: str, format: str) -> Any:
    """Parse JSON, XML, CSV or a simple YAML document into Python values."""
    normalized = format.strip().lower()
    if normalized == "json":
        return json.loads(data)
    if normalized == "xml":
        root = ET.fromstring(data)
        return _xml_to_value(root)
    if normalized == "csv":
        return list(csv.DictReader(io.StringIO(data)))
    if normalized in {"yaml", "yml"}:
        return _parse_simple_yaml(data)
    raise ValueError(f"Unsupported format: {format}")


def run(context: CapabilityContext) -> CapabilityResult:
    """Parse ``context.code`` using the requested ``format`` parameter."""
    fmt = str(context.parameters.get("format", "json"))
    try:
        value = universal_parser(context.code, fmt)
        return CapabilityResult.ok(
            summary=f"Parsed {fmt} input successfully",
            findings=[{"format": fmt, "value": value}],
        )
    except (ValueError, TypeError, json.JSONDecodeError, ET.ParseError) as exc:
        return CapabilityResult.fail(str(exc), summary=f"Unable to parse {fmt} input")


def _xml_to_value(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return (element.text or "").strip()
    result: dict[str, Any] = {}
    for child in children:
        value = _xml_to_value(child)
        if child.tag in result:
            existing = result[child.tag]
            result[child.tag] = existing + [value] if isinstance(existing, list) else [existing, value]
        else:
            result[child.tag] = value
    return {element.tag: result}


def _parse_simple_yaml(data: str) -> dict[str, Any]:
    """Parse the simple key/value YAML used by the evolution experiment."""
    result: dict[str, Any] = {}
    for raw_line in data.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key):
            raise ValueError(f"Invalid YAML key: {key}")
        if value.lower() in {"null", "~"}:
            parsed: Any = None
        elif value.lower() in {"true", "false"}:
            parsed = value.lower() == "true"
        elif (value.startswith("\"") and value.endswith("\"")) or (value.startswith("'") and value.endswith("'")):
            parsed = value[1:-1]
        else:
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = value
        result[key] = parsed
    return result
