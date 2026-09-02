import json

from capabilities.base import CapabilityContext
from capabilities.seeds.cap_001_prompt_processing.capability import run


class FakeProvider:
    name = "ollama-test-double"

    def __init__(self, response):
        self.response = response

    def is_available(self):
        return True

    def generate(self, request):
        from models.base import LLMResponse
        return LLMResponse(
            text=self.response,
            model=request.model or "test-model",
            provider=self.name,
        )


def test_prompt_processing_is_first_class_brain_stage():
    provider = FakeProvider(json.dumps({
        "intent": "add validation",
        "steps": [{"capability_id": "CAP-011", "reason": "the request changes source code"}],
    }))
    result = run(CapabilityContext(
        code="def add(a, b):\n    return a + b\n",
        language="python",
        file_path="app.py",
        parameters={"llm_provider": provider, "capability_catalog": [
            {"id": "CAP-011", "name": "Natural Language Code Modification", "description": "modify source", "tags": ["modification"]}
        ]},
        metadata={"request": "add input validation"},
    ))
    assert result.success is True
    assert result.findings[0]["brain"] == "Ollama"
    assert result.findings[0]["steps"][0]["capability_id"] == "CAP-011"


def test_prompt_processing_rejects_capability_not_in_allowlist():
    provider = FakeProvider(json.dumps({
        "intent": "do something",
        "steps": [{"capability_id": "CAP-999", "reason": "bad"}],
    }))
    result = run(CapabilityContext(
        code="x = 1\n",
        language="python",
        file_path="app.py",
        parameters={"llm_provider": provider, "capability_catalog": [
            {"id": "CAP-011", "name": "Natural Language Code Modification", "description": "modify source", "tags": []}
        ]},
        metadata={"request": "do something"},
    ))
    assert result.success is False
    assert "outside the allowlist" in result.error
