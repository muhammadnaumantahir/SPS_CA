from __future__ import annotations

from capabilities.base import CapabilityContext
from capabilities.seeds.cap_009_natural_language_code_modification import capability
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


def test_handles_leading_preamble_before_fence():
    """Real models (e.g. Ollama) often add a one-line preamble before the fence."""
    original = "def add(a, b):\n    return a + b\n"
    generated = (
        "Here's the modified code:\n\n"
        "```python\n"
        "def add(a, b):\n"
        "    return a + b\n\n"
        "def find_even_numbers(numbers):\n"
        "    return [n for n in numbers if n % 2 == 0]\n"
        "```"
    )

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
    assert "Here's the modified code" not in result.modified_code
    assert "def find_even_numbers" in result.modified_code


def test_handles_trailing_note_after_fence():
    """Real models often add an explanatory note after the fence too."""
    original = "def add(a, b):\n    return a + b\n"
    generated = (
        "```python\n"
        "def add(a, b):\n"
        "    return a + b\n\n"
        "def find_even_numbers(numbers):\n"
        "    return [n for n in numbers if n % 2 == 0]\n"
        "```\n\n"
        "This adds a function to filter even numbers from a list."
    )

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
    assert "This adds a function" not in result.modified_code
    assert "def find_even_numbers" in result.modified_code


def test_handles_bare_code_with_no_fences():
    """Some models skip fences entirely and return bare source (with a preamble)."""
    original = "def add(a, b):\n    return a + b\n"
    generated = (
        "Here's the modified code:\n"
        "def add(a, b):\n"
        "    return a + b\n\n"
        "def find_even_numbers(numbers):\n"
        "    return [n for n in numbers if n % 2 == 0]\n"
    )

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
    assert "Here's the modified code" not in result.modified_code
    assert "def find_even_numbers" in result.modified_code
