"""Language-agnostic code analysis using tree-sitter.

Supports the five target languages from the master document: Python,
Java, JavaScript/TypeScript, Go, C#. Each language's grammar package is
imported lazily so that a machine missing one optional grammar can still
use the others (extensibility mentioned in REQUIREMENTS.md / Section 8 of
the master document: "Tree-sitter has wide language support").

Design note: rather than hand-writing a tree-sitter query per language for
"what is a function", this module relies on the fact that every supported
grammar exposes a ``name`` field on its function/method declaration nodes.
That keeps the extraction logic identical across languages and only the
per-language *node type names* need to be configured (see ``_LANGUAGES``).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from tree_sitter import Language, Node, Parser

from .models import FileAnalysis, FunctionInfo, ProjectAnalysis

# File extension -> language id used throughout SPS-CA.
EXTENSION_LANGUAGE_MAP: Dict[str, str] = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".cs": "csharp",
}


@dataclass
class _LanguageSpec:
    loader: Callable[[], Language]
    function_node_types: tuple


def _load_python() -> Language:
    import tree_sitter_python as mod

    return Language(mod.language())


def _load_java() -> Language:
    import tree_sitter_java as mod

    return Language(mod.language())


def _load_javascript() -> Language:
    import tree_sitter_javascript as mod

    return Language(mod.language())


def _load_typescript() -> Language:
    import tree_sitter_typescript as mod

    return Language(mod.language_typescript())


def _load_go() -> Language:
    import tree_sitter_go as mod

    return Language(mod.language())


def _load_csharp() -> Language:
    import tree_sitter_c_sharp as mod

    return Language(mod.language())


_LANGUAGES: Dict[str, _LanguageSpec] = {
    "python": _LanguageSpec(_load_python, ("function_definition",)),
    "java": _LanguageSpec(
        _load_java, ("method_declaration", "constructor_declaration")
    ),
    "javascript": _LanguageSpec(
        _load_javascript,
        (
            "function_declaration",
            "generator_function_declaration",
            "method_definition",
        ),
    ),
    "typescript": _LanguageSpec(
        _load_typescript,
        (
            "function_declaration",
            "generator_function_declaration",
            "method_definition",
            "function_signature",
        ),
    ),
    "go": _LanguageSpec(_load_go, ("function_declaration", "method_declaration")),
    "csharp": _LanguageSpec(_load_csharp, ("method_declaration",)),
}

SUPPORTED_LANGUAGES = tuple(_LANGUAGES.keys())


class UnsupportedLanguageError(Exception):
    pass


class ProjectAnalyzer:
    """Parses source files across the five supported target languages."""

    def __init__(self):
        self._parsers: Dict[str, Parser] = {}

    def _get_parser(self, language: str) -> Parser:
        if language not in _LANGUAGES:
            raise UnsupportedLanguageError(
                f"'{language}' is not a supported target language. "
                f"Supported: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        if language not in self._parsers:
            ts_language = _LANGUAGES[language].loader()
            self._parsers[language] = Parser(ts_language)
        return self._parsers[language]

    @staticmethod
    def detect_language(file_path: str) -> Optional[str]:
        return EXTENSION_LANGUAGE_MAP.get(Path(file_path).suffix)

    def _extract_functions(self, root: Node, language: str) -> List[FunctionInfo]:
        function_types = _LANGUAGES[language].function_node_types
        results: List[FunctionInfo] = []

        def walk(node: Node):
            if node.is_named and node.type in function_types:
                name_node = node.child_by_field_name("name")
                name = name_node.text.decode("utf-8") if name_node else "<anonymous>"
                params = self._extract_parameter_names(node)
                results.append(
                    FunctionInfo(
                        name=name,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        parameters=params,
                    )
                )
            for child in node.children:
                walk(child)

        walk(root)
        return results

    @staticmethod
    def _extract_parameter_names(func_node: Node) -> List[str]:
        params_node = func_node.child_by_field_name(
            "parameters"
        ) or func_node.child_by_field_name("parameter_list")
        if params_node is None:
            return []
        names = []
        for child in params_node.children:
            if not child.is_named:
                continue
            # Plain identifier parameter (Python, Go, C#-ish simple cases).
            if child.type == "identifier":
                names.append(child.text.decode("utf-8"))
                continue
            # Wrapper nodes (TypeScript's required_parameter/optional_parameter,
            # Java/C#/Go's typed parameter nodes) usually expose the bound name
            # under a "name" or "pattern" field.
            name_node = child.child_by_field_name("name") or child.child_by_field_name(
                "pattern"
            )
            if name_node is not None:
                # "pattern" can itself be an identifier or a nested destructuring
                # pattern; only take simple identifiers to stay conservative.
                if name_node.type == "identifier":
                    names.append(name_node.text.decode("utf-8"))
                else:
                    inner = name_node.child_by_field_name("name")
                    if inner is not None:
                        names.append(inner.text.decode("utf-8"))
        return names

    def analyze_file(
        self, file_path: str, code: str, language: Optional[str] = None
    ) -> FileAnalysis:
        language = language or self.detect_language(file_path)
        if language is None:
            return FileAnalysis(
                file_path=file_path,
                language="unknown",
                parse_ok=False,
                error="Could not detect language from file extension",
            )
        try:
            parser = self._get_parser(language)
        except UnsupportedLanguageError as exc:
            return FileAnalysis(
                file_path=file_path, language=language, parse_ok=False, error=str(exc)
            )

        tree = parser.parse(code.encode("utf-8"))
        functions = self._extract_functions(tree.root_node, language)
        has_error = tree.root_node.has_error
        return FileAnalysis(
            file_path=file_path,
            language=language,
            functions=functions,
            parse_ok=not has_error,
            error="Parse tree contains error node(s)" if has_error else None,
        )

    def analyze_project(
        self, project_path: str, files: Dict[str, str]
    ) -> ProjectAnalysis:
        """Analyze a set of in-memory files (path -> source text).

        Taking file contents as a dict (rather than reading from disk here)
        keeps this class easy to unit test and keeps filesystem access at
        the caller's discretion (relevant once ``coding/`` owns repository
        discovery in a later phase).
        """
        analyses = [self.analyze_file(path, code) for path, code in files.items()]
        languages = sorted({a.language for a in analyses if a.parse_ok})
        return ProjectAnalysis(
            project_path=project_path, files=analyses, languages_detected=languages
        )
