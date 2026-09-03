"""Tests for exposing generated capability intent metadata to Brain."""

from __future__ import annotations

from types import SimpleNamespace

from core import SpsAssistantService


def test_capability_catalog_keeps_active_capabilities_and_adds_routing_metadata():
    generated = SimpleNamespace(
        id="CAP-011",
        name="Generated Modifier",
        description="Generated modification capability",
        version="1.0.0",
        generated=True,
        tags=["generated"],
        status="active",
        intent_class="code_modification",
        allowed_intents=["code_modification"],
        forbidden_intents=["test_generation"],
        risk_level="medium",
        supported_languages=["python"],
    )
    inactive = SimpleNamespace(
        id="CAP-012",
        name="Inactive",
        description="unused",
        version="1.0.0",
        generated=True,
        tags=[],
        status="inactive",
        intent_class="code_modification",
        allowed_intents=["code_modification"],
        forbidden_intents=[],
        risk_level="medium",
        supported_languages=["python"],
    )

    class Registry:
        def list_all_capabilities(self):
            return [generated, inactive]

    fake_service = object.__new__(SpsAssistantService)
    fake_service.registry = Registry()

    catalog = SpsAssistantService.capability_catalog(fake_service)

    assert [item["id"] for item in catalog] == ["CAP-011"]
    assert catalog[0]["allowed_intents"] == ["code_modification"]
    assert catalog[0]["forbidden_intents"] == ["test_generation"]
    assert catalog[0]["supported_languages"] == ["python"]
