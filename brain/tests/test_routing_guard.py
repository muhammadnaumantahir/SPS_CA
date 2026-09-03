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


def test_separate_validation_action_remains_mixed():
    request = "Create a payment function, then validate the resulting code."
    assert Brain.infer_intent_class(request, "", "main.py") == "mixed"


def test_standalone_validation_remains_validation():
    request = "Validate this code for correctness."
    code = "def process(value):\n    return value\n"
    assert Brain.infer_intent_class(request, code, "main.py") == "validation"
