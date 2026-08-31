"""Layer 02: Cognitive Core.

Request understanding, language-agnostic project analysis (tree-sitter),
task decomposition, capability selection, and modification planning.
"""

from .cognitive_core import CognitiveCore
from .llm_interface import LLMInterface, LLMQueryError
from .models import (
    FileAnalysis,
    FunctionInfo,
    ModificationPlan,
    ProjectAnalysis,
    Request,
    Subtask,
)
from .project_analyzer import (
    ProjectAnalyzer,
    SUPPORTED_LANGUAGES,
    UnsupportedLanguageError,
)

__all__ = [
    "CognitiveCore",
    "LLMInterface",
    "LLMQueryError",
    "ProjectAnalyzer",
    "SUPPORTED_LANGUAGES",
    "UnsupportedLanguageError",
    "Request",
    "ProjectAnalysis",
    "FileAnalysis",
    "FunctionInfo",
    "Subtask",
    "ModificationPlan",
]
