from brain import Brain


CODE = "def calculate(value):\n    return value * 2\n"


def test_multi_action_request_is_classified_as_mixed():
    request = "First analyze this function for issues, then fix the bug you find."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "mixed"


def test_generation_and_tests_are_classified_as_mixed():
    request = "Generate a helper function, then write tests for it."
    assert Brain.infer_intent_class(request, "", "main.py") == "mixed"


def test_generate_tests_for_function_is_test_generation_only():
    request = "Create unit tests for this function."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "test_generation"


def test_create_tests_for_validator_is_test_generation_only():
    request = "Write tests for the validator function."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "test_generation"


def test_fixing_does_not_require_bug_keyword():
    request = "Fix the root cause of a distributed deadlock and return the corrected source."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "bug_fixing"


def test_diagnosis_does_not_require_bug_keyword():
    request = "Diagnose the heisenbug that only appears under load in this code."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "bug_diagnosis"


def test_project_setup_is_project_operation():
    request = "Perform the project operation to set up a blue-green deployment layout for this project."
    assert Brain.infer_intent_class(request, "", "main.py") == "project_operations"


def test_existing_source_docstring_change_is_code_modification():
    request = "Add a docstring to this function while preserving unrelated behavior."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "code_modification"


def test_input_validation_change_is_code_modification_only():
    request = "Add input validation to this function while preserving unrelated behavior."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "code_modification"


def test_modification_then_validation_is_mixed():
    request = "Add input validation to this function, then review it for security risks."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "mixed"


def test_security_review_then_patch_is_mixed():
    request = "Review this for security risks, then patch the risk you find."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "mixed"


def test_analysis_plus_project_documentation_is_mixed_not_modification():
    request = "Analyze this module, then add project-level documentation for it."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "mixed"


def test_validation_only_stays_validation():
    request = "Validate this code for syntax correctness and report the result without rewriting it."
    assert Brain.infer_intent_class(request, CODE, "main.py") == "validation"
