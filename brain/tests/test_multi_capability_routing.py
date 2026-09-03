from brain.multi_capability import compose_explicit_capabilities


AVAILABLE = {f"CAP-{index:03d}" for index in range(1, 11)}


def ids(request: str, code: str = "def add(a, b):\n    return a + b\n") -> list[str]:
    return [
        step["capability_id"]
        for step in compose_explicit_capabilities(
            request,
            has_code=bool(code.strip()),
            available_ids=AVAILABLE,
        )
    ]


def test_fixing_and_refactoring_compose_without_bug_keyword():
    assert ids("Diagnose the root cause, fix it, and refactor the function.") == [
        "CAP-004",
        "CAP-005",
        "CAP-006",
    ]


def test_analysis_and_documentation_compose_as_two_capabilities():
    assert ids("Analyze this module, then add project-level documentation for it.") == [
        "CAP-003",
        "CAP-008",
    ]


def test_project_setup_terms_are_recognized():
    assert ids(
        "Perform the project operation to set up a blue-green deployment layout for this project.",
        code="",
    ) == []
    assert ids("Create a new utility function, then set up a plugins directory for the project.") == [
        "CAP-001",
        "CAP-010",
    ]
