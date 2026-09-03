import json

from brain import Brain
from models.base import LLMResponse


class FakeProvider:
    def __init__(self, payload):
        self.payload = payload

    def is_available(self):
        return True

    def generate(self, request):
        return LLMResponse(text=json.dumps(self.payload), model=request.model, provider="fake")


def canonical_catalog():
    return [
        {"id": "CAP-001", "name": "Code Generation", "allowed_intents": ["code_generation", "mixed"]},
        {"id": "CAP-002", "name": "Code Modification", "allowed_intents": ["code_modification", "mixed"]},
        {"id": "CAP-003", "name": "Code Explanation & Analysis", "allowed_intents": ["analysis", "mixed"]},
        {"id": "CAP-004", "name": "Bug Detection & Diagnosis", "allowed_intents": ["bug_diagnosis", "mixed"]},
        {"id": "CAP-005", "name": "Bug Fixing", "allowed_intents": ["bug_fixing", "mixed"]},
        {"id": "CAP-006", "name": "Refactoring & Optimization", "allowed_intents": ["refactoring", "mixed"]},
        {"id": "CAP-007", "name": "Test Generation", "allowed_intents": ["test_generation", "mixed"]},
        {"id": "CAP-008", "name": "Documentation Generation", "allowed_intents": ["documentation", "mixed"]},
        {"id": "CAP-009", "name": "Code Validation & Review", "allowed_intents": ["validation", "mixed"]},
        {"id": "CAP-010", "name": "Project/File Operations", "allowed_intents": ["project_operations", "mixed"]},
    ]


def test_plain_code_creation_cannot_route_to_test_generation():
    provider = FakeProvider({
        "language": "python",
        "language_confidence": 0.99,
        "intent": "create a calculator program",
        "reasoning": "The user asked to create source code, not tests.",
        "steps": [{"capability_id": "CAP-007", "reason": "generate tests"}],
    })
    brain = Brain(provider=provider, model="test-model")

    plan = brain.plan(
        request="Write Python code to add, subtract, multiply and divide numbers; first ask how many numbers.",
        code="",
        language="python",
        file_path="main.py",
        capability_catalog=canonical_catalog(),
    )

    assert plan.intent_class == "code_generation"
    assert [step["capability_id"] for step in plan.steps] == ["CAP-001"]


def test_explicit_test_request_can_route_to_test_generation():
    provider = FakeProvider({
        "language": "python",
        "language_confidence": 0.99,
        "intent": "generate tests",
        "reasoning": "The user explicitly requested tests.",
        "steps": [{"capability_id": "CAP-007", "reason": "generate pytest tests"}],
    })
    brain = Brain(provider=provider, model="test-model")

    plan = brain.plan(
        request="Generate pytest tests for this function.",
        code="def add(a, b):\n    return a + b\n",
        language="python",
        file_path="main.py",
        capability_catalog=canonical_catalog(),
    )

    assert plan.intent_class == "test_generation"
    assert [step["capability_id"] for step in plan.steps] == ["CAP-007"]


def test_explicit_analysis_diagnosis_fix_test_document_chain_is_preserved():
    provider = FakeProvider({
        "language": "python",
        "language_confidence": 0.99,
        "intent": "analyze, diagnose, fix, test and document",
        "reasoning": "The user requested five explicit actions.",
        "steps": [{"capability_id": "CAP-003", "reason": "analysis"}],
    })
    brain = Brain(provider=provider, model="test-model")

    plan = brain.plan(
        request="Analyze this code, find the bug, fix it, add tests, and document the change.",
        code="def divide(a, b):\n    return a / b\n",
        language="python",
        file_path="main.py",
        capability_catalog=canonical_catalog(),
    )

    assert plan.intent_class == "mixed"
    assert [step["capability_id"] for step in plan.steps] == [
        "CAP-003", "CAP-004", "CAP-005", "CAP-007", "CAP-008"
    ]


def test_simple_modification_stays_single_capability():
    provider = FakeProvider({
        "language": "python",
        "language_confidence": 0.99,
        "intent": "add a function",
        "reasoning": "single explicit modification",
        "steps": [{"capability_id": "CAP-002", "reason": "modify code"}],
    })
    brain = Brain(provider=provider, model="test-model")

    plan = brain.plan(
        request="Add this function to the module.",
        code="def existing():\n    return 1\n",
        language="python",
        file_path="main.py",
        capability_catalog=canonical_catalog(),
    )

    assert plan.intent_class == "code_modification"
    assert [step["capability_id"] for step in plan.steps] == ["CAP-002"]


def test_explicit_generation_and_tests_are_both_selected():
    provider = FakeProvider({
        "language": "python",
        "language_confidence": 0.99,
        "intent": "generate code and tests",
        "reasoning": "both were explicitly requested",
        "steps": [{"capability_id": "CAP-001", "reason": "generate code"}],
    })
    brain = Brain(provider=provider, model="test-model")

    plan = brain.plan(
        request="Generate Python code for a calculator and generate pytest tests for it.",
        code="",
        language="python",
        file_path="calculator.py",
        capability_catalog=canonical_catalog(),
    )

    assert plan.intent_class == "mixed"
    assert [step["capability_id"] for step in plan.steps] == ["CAP-001", "CAP-007"]
