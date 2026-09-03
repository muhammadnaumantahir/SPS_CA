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


def plan_with_response(response):
    return Brain(provider=FakeProvider(response), model="test-model").plan(
        request="Add input validation to this function",
        code="def add(a,b):\n    return a+b\n",
        language="python",
        file_path="main.py",
        capability_catalog=[{"id": "CAP-002", "name": "Code Modification"}],
    )


def test_brain_routes_modification_to_canonical_capability():
    provider = FakeProvider(json.dumps({"language": "python", "language_confidence": 0.9, "intent_class": "code_modification", "intent": "modify", "reasoning": "explicit change", "steps": [{"capability_id": "CAP-007", "reason": "wrong model choice"}]}))
    plan = Brain(provider=provider, model="test-model").plan(request="Add input validation to this function", code="def add(a,b):\n    return a+b\n", language="python", file_path="main.py", capability_catalog=[{"id": "CAP-002", "name": "Code Modification"}, {"id": "CAP-007", "name": "Test Generation"}])
    assert plan.intent_class == "code_modification"
    assert plan.steps[0]["capability_id"] == "CAP-002"


def test_brain_rejects_unknown_capability():
    brain = Brain(provider=FakeProvider(json.dumps({"intent": "x", "reasoning": "x", "steps": [{"capability_id": "CAP-999", "reason": "x"}]})))
    with pytest.raises(BrainError, match="unavailable capability"):
        brain.plan(request="do x", code="x = 1\n", language="python", file_path="main.py", capability_catalog=[{"id": "CAP-001", "name": "Bug Detection"}])


def test_brain_accepts_single_quoted_local_model_dict():
    plan = plan_with_response("{'language': 'python', 'language_confidence': 0.91, 'intent_class': 'code_modification', 'intent': 'add validation', 'reasoning': 'source change requested', 'steps': [{'capability_id': 'CAP-002', 'reason': 'modify the function'}]}")
    assert plan.language == "python"
    assert plan.steps[0]["capability_id"] == "CAP-002"


def test_brain_accepts_json_inside_fenced_response():
    plan = plan_with_response("Here is the plan:\n```json\n{\"language\":\"python\",\"language_confidence\":0.9,\"intent_class\":\"code_modification\",\"intent\":\"add validation\",\"reasoning\":\"source change requested\",\"steps\":[{\"capability_id\":\"CAP-002\",\"reason\":\"modify the function\"}]}\n```\n")
    assert plan.intent_class == "code_modification"
    assert plan.steps[0]["capability_id"] == "CAP-002"


def test_brain_rejects_non_object_response():
    with pytest.raises(BrainError, match="invalid planning JSON"):
        plan_with_response("I cannot create a plan")
