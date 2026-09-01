from pathlib import Path

from layers.layer_06_validation.capability_package_validator import CapabilityPackageValidator


def _write_package(root: Path, tests: str) -> Path:
    package = root / "CAP-TEST"
    package.mkdir()
    (package / "capability.py").write_text(
        "from capabilities.base import CapabilityContext, CapabilityResult\n\n"
        "def run(context: CapabilityContext) -> CapabilityResult:\n"
        "    return CapabilityResult.ok('validated')\n"
    )
    (package / "tests.py").write_text(tests)
    return package


def test_rejects_missing_package_files(tmp_path):
    result = CapabilityPackageValidator(project_root=str(tmp_path)).validate(tmp_path / "missing")
    assert result.passed is False
    assert "capability.py and tests.py" in (result.error or "")


def test_rejects_invalid_python(tmp_path):
    package = tmp_path / "CAP-TEST"
    package.mkdir()
    (package / "capability.py").write_text("def broken(:\n")
    (package / "tests.py").write_text("def test_ok():\n    assert True\n")
    result = CapabilityPackageValidator(project_root=str(tmp_path)).validate(package)
    assert result.passed is False
    assert "Invalid generated Python" in (result.error or "")


def test_runs_package_tests_with_project_import_path(tmp_path):
    tests = (
        "from capabilities.base import CapabilityContext\n"
        "from capability import run\n\n"
        "def test_run_returns_success():\n"
        "    result = run(CapabilityContext(code='', language='python'))\n"
        "    assert result.success\n"
    )
    package = _write_package(tmp_path, tests)
    result = CapabilityPackageValidator(project_root=str(tmp_path)).validate(package)
    # pytest-cov may not be available in minimal environments; the contract
    # intentionally requires an actual coverage report for promotion.
    if result.error == "Coverage report was not produced":
        assert result.return_code == 0
    else:
        assert result.passed is True
        assert result.coverage_percent is not None
        assert result.coverage_percent >= 80.0
