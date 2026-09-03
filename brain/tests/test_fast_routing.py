import pytest

from brain import Brain
from models.base import LLMProvider, LLMRequest, LLMResponse


class FailingProvider(LLMProvider):
    name = "fake"

    def is_available(self):
        return True

    def generate(self, request: LLMRequest) -> LLMResponse:
        raise AssertionError("deterministic routing should not query the model")


def test_clear_code_modification_skips_brain_model_call():
    brain = Brain(provider=FailingProvider(), model="test-model")
    plan = brain.plan(
        request="Add this function to validate input",
        code="def add(a, b):\n    return a + b\n",
        language="python",
        file_path="main.py",
        capability_catalog=[
            {"id": "CAP-002", "name": "Code Modification"},
            {"id": "CAP-007", "name": "Test Generation"},
        ],
    )
    assert plan.intent_class == "code_modification"
    assert plan.steps == [{"capability_id": "CAP-002", "reason": "intent-safe canonical routing for 'code_modification'"}]


def test_ambiguous_request_still_uses_model():
    class Provider(LLMProvider):
        name = "fake"

        def is_available(self):
            return True

        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text='{"intent":"do something","reasoning":"ambiguous","steps":[]}',
                model="test-model",
                provider=self.name,
            )

    brain = Brain(provider=Provider(), model="test-model")
    plan = brain.plan(
        request="Can you help with this?",
        code="value = 1\n",
        language="python",
        file_path="main.py",
        capability_catalog=[{"id": "CAP-001", "name": "Code Generation"}],
    )
    assert plan.intent_class == "unknown"
