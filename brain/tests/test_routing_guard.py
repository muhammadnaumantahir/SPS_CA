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
