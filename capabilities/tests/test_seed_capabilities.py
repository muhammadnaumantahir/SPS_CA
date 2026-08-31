from capabilities.base import CapabilityContext
from capabilities.seeds.cap_001_bug_detection.capability import run as cap001
from capabilities.seeds.cap_002_syntax_error_fix.capability import run as cap002
from capabilities.seeds.cap_003_unit_test_generation.capability import run as cap003
from capabilities.seeds.cap_004_loop_optimization.capability import run as cap004
from capabilities.seeds.cap_005_error_handling_pattern.capability import run as cap005
from capabilities.seeds.cap_006_unused_variable_removal.capability import run as cap006
from capabilities.seeds.cap_007_type_annotation_addition.capability import run as cap007
from capabilities.seeds.cap_008_documentation_generation.capability import run as cap008


def ctx(code, file_path="module.py"):
    return CapabilityContext(code=code, language="python", file_path=file_path)


class TestCap001BugDetection:
    def test_detects_bare_except(self):
        result = cap001(ctx("try:\n    pass\nexcept:\n    pass\n"))
        assert any(f["issue"] == "bare-except" for f in result.findings)

    def test_detects_mutable_default_argument(self):
        result = cap001(ctx("def f(x=[]):\n    return x\n"))
        assert any(f["issue"] == "mutable-default-argument" for f in result.findings)

    def test_detects_equality_with_none(self):
        result = cap001(ctx("def f(x):\n    return x == None\n"))
        assert any(f["issue"] == "equality-with-none" for f in result.findings)

    def test_clean_code_has_no_findings(self):
        result = cap001(ctx("def f(x):\n    return x is None\n"))
        assert result.findings == []

    def test_syntax_error_fails_gracefully(self):
        result = cap001(ctx("def f(:\n"))
        assert result.success is False
        assert result.error is not None


class TestCap002SyntaxErrorFix:
    def test_valid_code_reports_no_errors(self):
        result = cap002(ctx("def f(x):\n    return x\n"))
        assert result.success is True
        assert result.modified_code is None

    def test_fixes_missing_colon(self):
        result = cap002(ctx("def f(x)\n    return x\n"))
        assert result.success is True
        assert result.modified_code is not None
        assert "def f(x):" in result.modified_code

    def test_unrecognized_syntax_error_reported_as_failure(self):
        result = cap002(ctx("def (x):\n    return x\n"))
        assert result.success is False


class TestCap003UnitTestGeneration:
    def test_generates_stub_for_each_function(self):
        result = cap003(ctx("def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n"))
        assert result.success is True
        assert "def test_add" in result.modified_code
        assert "def test_sub" in result.modified_code

    def test_no_functions_returns_empty_result(self):
        result = cap003(ctx("x = 1\n"))
        assert result.success is True
        assert result.modified_code is None

    def test_skips_private_functions(self):
        result = cap003(ctx("def _helper():\n    pass\n"))
        assert result.modified_code is None


class TestCap004LoopOptimization:
    def test_detects_append_loop(self):
        code = "def f(items):\n    out = []\n    for i in items:\n        out.append(i)\n    return out\n"
        result = cap004(ctx(code))
        assert any(f["issue"] == "append-loop-to-comprehension" for f in result.findings)

    def test_ignores_multi_statement_loop_body(self):
        code = "def f(items):\n    out = []\n    for i in items:\n        j = i * 2\n        out.append(j)\n    return out\n"
        result = cap004(ctx(code))
        assert result.findings == []


class TestCap005ErrorHandlingPattern:
    def test_flags_unwrapped_open_call(self):
        result = cap005(ctx("def f(path):\n    return open(path)\n"))
        assert any(f["issue"] == "unhandled-risky-call" for f in result.findings)

    def test_does_not_flag_wrapped_call(self):
        code = "def f(path):\n    try:\n        return open(path)\n    except OSError:\n        return None\n"
        result = cap005(ctx(code))
        assert result.findings == []


class TestCap006UnusedVariableRemoval:
    def test_detects_unused_variable(self):
        result = cap006(ctx("def f():\n    unused = 1\n    return 2\n"))
        assert any(f["issue"] == "unused-variable" and "unused" in f["detail"] for f in result.findings)

    def test_does_not_flag_used_variable(self):
        result = cap006(ctx("def f():\n    x = 1\n    return x\n"))
        assert result.findings == []


class TestCap007TypeAnnotationAddition:
    def test_flags_missing_parameter_annotation(self):
        result = cap007(ctx("def f(x):\n    return x\n"))
        assert any(f["issue"] == "missing-parameter-annotation" for f in result.findings)

    def test_infers_type_from_default(self):
        result = cap007(ctx("def f(x=1):\n    return x\n"))
        match = [f for f in result.findings if f["issue"] == "missing-parameter-annotation"]
        assert match and match[0]["inferred_type"] == "int"

    def test_fully_annotated_function_has_no_findings(self):
        result = cap007(ctx("def f(x: int) -> int:\n    return x\n"))
        assert result.findings == []


class TestCap008DocumentationGeneration:
    def test_flags_undocumented_function(self):
        result = cap008(ctx("def f(x):\n    return x\n"))
        assert any(f["issue"] == "missing-function-docstring" for f in result.findings)

    def test_documented_function_not_flagged(self):
        result = cap008(ctx('def f(x):\n    """Return x."""\n    return x\n'))
        assert result.findings == []

    def test_flags_undocumented_class(self):
        result = cap008(ctx("class Foo:\n    pass\n"))
        assert any(f["issue"] == "missing-class-docstring" for f in result.findings)
