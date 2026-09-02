import json

import pytest

from brain import Brain, BrainError
from models.base import LLMResponse


class FakeProvider:
    def __init__(self, text):
        self.text = text

    def is_available(self):
        return True

    def generate(self, request):
        return LLMResponse(text=self.text, model=request.model, provider="fake")


def test_brain_is_not_a_capability_and_routes_only_allowlisted_ids():
    provider = FakeProvider(json.dumps({
        "intent": "modify the function",
        "reasoning": "The user explicitly requested a source change.",
        "steps": [{"capability_id": "CAP-011", "reason": "Apply the requested modification."}],
    }))
    brain = Brain(provider=provider, model="test-model")
    plan = brain.plan(
        request="Add input validation to this function",
        code="def add(a, b):\n    return a + b\n",
        language="python",
        file_path="main.py",
        capability_catalog=[{"id": "CAP-001", "name": "Bug Detection"}, {"id": "CAP-011", "name": "Code Modification"}],
    )
    assert plan.provider == "Fake"
    assert plan.model == "test-model"
    assert plan.steps[0]["capability_id"] == "CAP-011"


def test_brain_rejects_unknown_capability():
    provider = FakeProvider(json.dumps({
        "intent": "x",
        "reasoning": "x",
        "steps": [{"capability_id": "CAP-999", "reason": "x"}],
    }))
    brain = Brain(provider=provider)
    with pytest.raises(BrainError, match="unavailable capability"):
        brain.plan(
            request="do x",
            code="x = 1\n",
            language="python",
            file_path="main.py",
            capability_catalog=[{"id": "CAP-001", "name": "Bug Detection"}],
        )
