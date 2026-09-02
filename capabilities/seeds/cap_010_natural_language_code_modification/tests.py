from __future__ import annotations

from capabilities.base import CapabilityContext
from capabilities.seeds.cap_010_natural_language_code_modification import capability
from models.base import LLMProvider, LLMRequest, LLMResponse


class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(self, text: str):
        self.text = text

    def generate(self, request: LLMRequest) -> LLMResponse:
        assert "add input validation" in request.prompt.lower()
        return LLMResponse(
            text=self.text,
            model="fake",
            provider=self.name,
        )

    def is_available(self) -> bool:
        return True


def test_explicit_modification_returns_source_only():
    original = "def add(a, b):\n    return a + b\n"
    generated = "```python\ndef add(a, b):\n    if not isinstance(a, int) or not isinstance(b, int):\n        raise TypeError('a and b must be integers')\n    return a + b\n```"

    result = capability.run(
        CapabilityContext(
            code=original,
            language="python",
            file_path="app.py",
            parameters={"llm_provider": FakeProvider(generated)},
            metadata={"request": "add input validation to this function"},
        )
    )

    assert result.success
    assert "```" not in result.modified_code
    assert "raise TypeError" in result.modified_code
    assert "pytest" not in result.modified_code
