"""Validation adapter for generated SPS-CA capability packages.

Layer 8 produces a package rather than replacing an existing project file.
This adapter gives Layer 6 a package-native validation boundary while keeping
sandbox execution and regression responsibilities in this layer.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class PackageValidationResult:
    """Result of validating one staged capability package."""

    passed: bool
    return_code: int = 0
    output: str = ""
    coverage_percent: Optional[float] = None
    error: Optional[str] = None


class CapabilityPackageValidator:
    """Validate generated capability syntax and tests in an isolated process."""

    def __init__(self, project_root: str = ".", timeout_seconds: float = 120.0) -> None:
        self.project_root = Path(project_root).resolve()
        self.timeout_seconds = timeout_seconds

    def validate(self, package_path: str | Path) -> PackageValidationResult:
        package = Path(package_path).resolve()
        capability = package / "capability.py"
        tests = package / "tests.py"
        if not capability.exists() or not tests.exists():
            return PackageValidationResult(
                False,
                error="Generated package must contain capability.py and tests.py",
            )

        syntax_error = self._syntax_error(capability) or self._syntax_error(tests)
        if syntax_error:
            return PackageValidationResult(False, error=syntax_error)

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            [str(self.project_root), env.get("PYTHONPATH", "")]
        ).rstrip(os.pathsep)
        try:
            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    str(tests),
                    f"--cov={capability}",
                    "--cov-report=term",
                ],
                cwd=str(self.project_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return PackageValidationResult(False, error=f"Validation timed out: {exc}")
        except OSError as exc:
            return PackageValidationResult(False, error=f"Validation process failed: {exc}")

        output = (process.stdout + "\n" + process.stderr).strip()
        coverage = self._extract_coverage(output)
        passed = process.returncode == 0 and coverage is not None and coverage >= 80.0
        if process.returncode != 0:
            error = "Generated capability tests failed"
        elif coverage is None:
            error = "Coverage report was not produced"
        elif coverage < 80.0:
            error = f"Coverage below 80%: {coverage:.1f}%"
        else:
            error = None
        return PackageValidationResult(
            passed=passed,
            return_code=process.returncode,
            output=output,
            coverage_percent=coverage,
            error=error,
        )

    @staticmethod
    def _syntax_error(path: Path) -> Optional[str]:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            return f"Invalid generated Python in {path.name}: {exc}"
        return None

    @staticmethod
    def _extract_coverage(output: str) -> Optional[float]:
        import re

        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        return float(match.group(1)) if match else None
