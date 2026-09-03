from types import SimpleNamespace

from ui.sps_service import SPSScenarioService


def _caps(*ids):
    return [SimpleNamespace(id=cap_id) for cap_id in ids]


def test_type_checking_routes_to_code_modification_not_tests():
    selected = SPSScenarioService._select_capability(
        _caps("CAP-002", "CAP-007"),
        [],
        "Add type checking to this function while preserving unrelated behavior.",
        code="def calculate(value):\n    return value * 2\n",
        file_path="main.py",
    )
    assert selected.id == "CAP-002"


def test_return_type_annotation_routes_to_code_modification_not_tests():
    selected = SPSScenarioService._select_capability(
        _caps("CAP-002", "CAP-007"),
        [],
        "Add a return type annotation to this function while preserving unrelated behavior.",
        code="def calculate(value):\n    return value * 2\n",
        file_path="main.py",
    )
    assert selected.id == "CAP-002"


def test_explicit_test_request_routes_to_test_generation():
    selected = SPSScenarioService._select_capability(
        _caps("CAP-002", "CAP-007"),
        [],
        "Generate unit tests for this function.",
        code="def calculate(value):\n    return value * 2\n",
        file_path="main.py",
    )
    assert selected.id == "CAP-007"
