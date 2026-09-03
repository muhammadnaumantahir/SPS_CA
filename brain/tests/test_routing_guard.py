import pytest

from brain import Brain


def test_modification_request_containing_testing_does_not_route_to_cap007():
    request = "add this function and make the implementation work correctly for testing"
    code = "def existing(value):\n    return value\n"
    assert Brain.infer_intent_class(request, code, "main.py") == "code_modification"


def test_explicit_add_tests_request_still_routes_to_cap007():
    request = "add unit tests for this function"
    code = "def existing(value):\n    return value\n"
    assert Brain.infer_intent_class(request, code, "main.py") == "test_generation"


def test_generation_without_source_remains_code_generation():
    request = "write Python code for a calculator"
    assert Brain.infer_intent_class(request, "", "main.py") == "code_generation"


@pytest.mark.parametrize(
    "request, expected",
    [
        ("Create a Python function for file processing that supports validation.", "code_generation"),
        ("Create a Python function for file processing that supports logging.", "code_generation"),
        ("Create a Python function for file processing that supports caching.", "code_generation"),
        ("Create a Python function for file processing that supports pagination.", "code_generation"),
        ("Create a Python function for file processing that supports error handling.", "code_generation"),
        ("Modify this Python function to add input validation for file processing while preserving its existing behavior.", "code_modification"),
        ("Modify this Python function to add structured logging for file processing while preserving its existing behavior.", "code_modification"),
        ("Modify this Python function to add type annotations for file processing while preserving its existing behavior.", "code_modification"),
        ("Modify this Python function to add retry handling for file processing while preserving its existing behavior.", "code_modification"),
        ("Modify this Python function to add configuration support for file processing while preserving its existing behavior.", "code_modification"),
        ("Diagnose the division-by-zero risk problem in this Python code for payments and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the type errors problem in this Python code for payments and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the boundary failures problem in this Python code for payments and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the state corruption problem in this Python code for payments and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the race conditions problem in this Python code for payments and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the division-by-zero risk problem in this Python code for inventory and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the type errors problem in this Python code for inventory and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the boundary failures problem in this Python code for inventory and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the state corruption problem in this Python code for inventory and explain the root cause.", "bug_diagnosis"),
        ("Diagnose the race conditions problem in this Python code for inventory and explain the root cause.", "bug_diagnosis"),
        ("Validate this Python code for payments, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for inventory, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for customer profiles, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for file processing, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for reporting, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for notifications, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for authentication, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for analytics, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for scheduling, focusing on resource cleanup.", "validation"),
        ("Validate this Python code for data import, focusing on resource cleanup.", "validation"),
    ],
)
def test_additional_growth_routing_conflicts_are_primary_intents(request, expected):
    code = "def process(value):\n    return value\n" if any(
        verb in request.lower() for verb in ("modify", "validate", "diagnose")
    ) else ""
    assert Brain.infer_intent_class(request, code, "main.py") == expected


def test_generation_and_explicit_validation_action_are_mixed():
    request = "Create a payment function, then validate the resulting code."
    assert Brain.infer_intent_class(request, "", "main.py") == "mixed"


def test_diagnosis_and_explicit_followup_action_are_mixed():
    request = "Diagnose this bug, then explain the root cause in detail."
    assert Brain.infer_intent_class(request, "def process(x): return 10 / x", "main.py") == "mixed"


def test_analysis_of_non_bug_code_remains_analysis():
    request = "Analyze this function and explain how the control flow works."
    code = "def process(value):\n    return value\n"
    assert Brain.infer_intent_class(request, code, "main.py") == "analysis"


def test_generation_with_validation_as_a_target_remains_code_generation():
    request = "Create a Python function for payments that supports validation."
    assert Brain.infer_intent_class(request, "", "main.py") == "code_generation"


def test_generation_with_validation_logic_remains_code_generation():
    request = "Build a payment validator with input validation logic."
    assert Brain.infer_intent_class(request, "", "main.py") == "code_generation"


def test_modification_with_validation_as_a_target_remains_code_modification():
    request = "Update this function to add input validation."
    code = "def process(value):\n    return value\n"
    assert Brain.infer_intent_class(request, code, "main.py") == "code_modification"


def test_standalone_validation_remains_validation():
    request = "Validate this code for correctness."
    code = "def process(value):\n    return value\n"
    assert Brain.infer_intent_class(request, code, "main.py") == "validation"
