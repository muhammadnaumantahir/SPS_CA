import pytest

from layers.layer_03_cognitive.project_analyzer import (
    ProjectAnalyzer,
    UnsupportedLanguageError,
)

SAMPLES = {
    "python": ("a.py", "def foo(a, b):\n    return a + b\n"),
    "java": ("b.java", "class Foo { int bar(int a, int b) { return a+b; } }"),
    "javascript": ("c.js", "function foo(a, b) { return a + b; }"),
    "typescript": (
        "d.ts",
        "function foo(a: number, b: number): number { return a + b; }",
    ),
    "go": ("e.go", "package main\nfunc Foo(a int, b int) int { return a + b }"),
    "csharp": ("f.cs", "class Foo { int Bar(int a, int b) { return a+b; } }"),
}


class TestLanguageDetection:
    @pytest.mark.parametrize(
        "path,expected",
        [
            ("app.py", "python"),
            ("Main.java", "java"),
            ("index.js", "javascript"),
            ("component.tsx", "typescript"),
            ("main.go", "go"),
            ("Program.cs", "csharp"),
            ("README.md", None),
        ],
    )
    def test_detect_language(self, path, expected):
        assert ProjectAnalyzer.detect_language(path) == expected


class TestProjectAnalyzerAllLanguages:
    @pytest.mark.parametrize("language", list(SAMPLES.keys()))
    def test_parses_and_extracts_function(self, language):
        analyzer = ProjectAnalyzer()
        path, code = SAMPLES[language]
        result = analyzer.analyze_file(path, code)
        assert result.parse_ok is True
        assert result.language == language
        names = [f.name for f in result.functions]
        assert names, f"expected at least one function extracted for {language}"

    @pytest.mark.parametrize("language", list(SAMPLES.keys()))
    def test_extracts_parameter_names(self, language):
        analyzer = ProjectAnalyzer()
        path, code = SAMPLES[language]
        result = analyzer.analyze_file(path, code)
        func = result.functions[0]
        assert set(func.parameters) >= {"a", "b"}


class TestProjectAnalyzerEdgeCases:
    def test_unknown_extension_reports_error(self):
        analyzer = ProjectAnalyzer()
        result = analyzer.analyze_file("README.md", "# hello")
        assert result.parse_ok is False
        assert result.error is not None

    def test_explicit_unsupported_language_reports_error(self):
        analyzer = ProjectAnalyzer()
        result = analyzer.analyze_file(
            "f.cob", "IDENTIFICATION DIVISION.", language="cobol"
        )
        assert result.parse_ok is False

    def test_syntactically_broken_python_flagged(self):
        analyzer = ProjectAnalyzer()
        result = analyzer.analyze_file("bad.py", "def f(:\n    pass\n")
        assert result.parse_ok is False

    def test_parser_is_cached_per_language(self):
        analyzer = ProjectAnalyzer()
        analyzer.analyze_file("a.py", "x = 1")
        analyzer.analyze_file("b.py", "y = 2")
        assert len(analyzer._parsers) == 1


class TestAnalyzeProject:
    def test_aggregates_multiple_files(self):
        analyzer = ProjectAnalyzer()
        files = {
            "a.py": "def foo():\n    pass\n",
            "b.py": "def bar():\n    pass\n",
        }
        analysis = analyzer.analyze_project("project_a", files)
        assert len(analysis.files) == 2
        assert analysis.total_functions == 2
        assert analysis.languages_detected == ["python"]

    def test_mixed_language_project(self):
        analyzer = ProjectAnalyzer()
        files = {
            "a.py": "def foo():\n    pass\n",
            "b.go": "package main\nfunc Foo() {}\n",
        }
        analysis = analyzer.analyze_project("mixed", files)
        assert sorted(analysis.languages_detected) == ["go", "python"]
