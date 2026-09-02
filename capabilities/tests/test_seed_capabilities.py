from capabilities.base import CapabilityContext
from capabilities.seeds.cap_001_bug_detection.capability import run as cap001
from capabilities.seeds.cap_002_syntax_error_fix.capability import run as cap002
from capabilities.seeds.cap_003_unit_test_generation.capability import run as cap003
from capabilities.seeds.cap_004_loop_optimization.capability import run as cap004
from capabilities.seeds.cap_005_error_handling_pattern.capability import run as cap005
from capabilities.seeds.cap_006_unused_variable_removal.capability import run as cap006
from capabilities.seeds.cap_007_type_annotation_addition.capability import run as cap007
from capabilities.seeds.cap_008_documentation_generation.capability import run as cap008


def ctx(code, file_path="module.py", **parameters):
    return CapabilityContext(
        code=code,
        language="python",
        file_path=file_path,
        parameters=parameters,
    )


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
    def test_generates_executable_smoke_test_for_function(self):
        result = cap003(ctx("def add(a, b):\n    return a + b\n"))
        assert result.success is True
        assert "def test_add" in result.modified_code
        assert "assert add(2, 3) == 5" in result.modified_code

    def test_generates_string_smoke_test_from_literal_return(self):
        result = cap003(ctx('def greet(name):\n    return "Hello, " + name\n'))
        assert result.success is True
        assert "assert greet('x') == 'Hello, x'" in result.modified_code

    def test_no_functions_returns_empty_result(self):
        result = cap003(ctx("x = 1\n"))
        assert result.success is True
        assert result.modified_code is None


class TestCap004LoopOptimization:
    def test_rewrites_identity_append_loop(self):
        code = "def f(items):\n    out = []\n    for i in items:\n        out.append(i)\n    return out\n"
        result = cap004(ctx(code, apply=True))
        assert result.success is True
        assert result.modified_code is not None
        assert "out = [i for i in items]" in result.modified_code

    def test_reports_unsupported_append_expression_without_rewrite(self):
        code = "def f(items):\n    out = []\n    for i in items:\n        out.append(i * 2)\n    return out\n"
        result = cap004(ctx(code))
        assert any(f["issue"] == "append-loop-to-comprehension" for f in result.findings)
        assert result.modified_code is None

    def test_ignores_multi_statement_loop_body(self):
        code = "def f(items):\n    out = []\n    for i in items:\n        j = i * 2\n        out.append(j)\n    return out\n"
        result = cap004(ctx(code, apply=True))
        assert result.modified_code is None


class TestCap005ErrorHandlingPattern:
    def test_flags_unwrapped_open_call(self):
        result = cap005(ctx("def f(path):\n    return open(path)\n"))
        assert any(f["issue"] == "unhandled-risky-call" for f in result.findings)

    def test_does_not_flag_wrapped_call(self):
        code = "def f(path):\n    try:\n        return open(path)\n    except OSError:\n        return None\n"
        result = cap005(ctx(code))
        assert result.findings == []

    def test_invalid_syntax_fails_gracefully(self):
        result = cap005(ctx("def f(:\n"))
        assert result.success is False


class TestCap006UnusedVariableRemoval:
    def test_removes_literal_unused_variable_when_apply_requested(self):
        code = "def f():\n    unused = 1\n    return 2\n"
        result = cap006(ctx(code, apply=True))
        assert result.success is True
        assert result.modified_code is not None
        assert "unused = 1" not in result.modified_code
        compile(result.modified_code, "<generated>", "exec")

    def test_does_not_remove_side_effecting_unused_variable(self):
        code = "def f():\n    unused = open('x.txt')\n    return 2\n"
        result = cap006(ctx(code, apply=True))
        assert any(f["issue"] == "unused-variable" for f in result.findings)
        assert result.modified_code is None

    def test_does_not_flag_used_variable(self):
        result = cap006(ctx("def f():\n    x = 1\n    return x\n"))
        assert result.findings == []


class TestCap007TypeAnnotationAddition:
    def test_adds_safe_parameter_annotation_from_default(self):
        result = cap007(ctx("def f(x=1):\n    return x\n", apply=True))
        assert result.success is True
        assert result.modified_code is not None
        assert "def f(x: int = 1)" in result.modified_code

    def test_flags_uninferable_parameter_without_guessing(self):
        result = cap007(ctx("def f(x):\n    return x\n", apply=True))
        assert any(f["issue"] == "missing-parameter-annotation" for f in result.findings)
        assert result.modified_code is None

    def test_fully_annotated_function_has_no_findings(self):
        result = cap007(ctx("def f(x: int) -> int:\n    return x\n"))
        assert result.findings == []


class TestCap008DocumentationGeneration:
    def test_inserts_function_docstring_when_apply_requested(self):
        code = "def f(x):\n    return x\n"
        result = cap008(ctx(code, apply=True))
        assert result.success is True
        assert result.modified_code is not None
        assert '"""TODO: describe what f does.' in result.modified_code

    def test_does_not_change_documented_function(self):
        code = 'def f(x):\n    """Return x."""\n    return x\n'
        result = cap008(ctx(code, apply=True))
        assert result.modified_code is None
        assert result.findings == []

    def test_flags_undocumented_class(self):
        result = cap008(ctx("class Foo:\n    pass\n"))
        assert any(f["issue"] == "missing-class-docstring" for f in result.findings)
