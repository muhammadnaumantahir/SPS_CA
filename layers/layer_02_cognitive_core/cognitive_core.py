"""Layer 2: Cognitive Core.

Receives user requests, analyzes target projects (via tree-sitter,
language-agnostic), decomposes tasks, selects candidate capabilities, and
produces a modification plan. This layer reasons and plans; it does not
execute changes (that's Layer 10) and it does not decide governance
approval (that's Layer 7) -- it hands a plan downstream.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from capabilities.seed_registry import load_seed_capabilities
from layers.layer_01_software_dna import CapabilityTemplate

from .llm_interface import LLMInterface
from .models import ModificationPlan, ProjectAnalysis, Request, Subtask
from .project_analyzer import EXTENSION_LANGUAGE_MAP, ProjectAnalyzer

# Splits a compound task description on common sequencing/coordinating words.
_SUBTASK_SPLIT_RE = re.compile(
    r"\s*(?:,\s*(?:and\s+)?|\s+and\s+then\s+|\s+then\s+|\s+and\s+)\s*",
    re.IGNORECASE,
)

# Very small keyword -> tag map used for heuristic capability relevance.
# This is intentionally simple for Phase 1; Layer 4 (Meta-Learning) is where
# selection actually improves from experience over time.
_KEYWORD_TAG_HINTS = {
    "bug": {"bug-detection"},
    "fix": {"bug-detection", "syntax", "repair"},
    "error": {"bug-detection", "reliability"},
    "exception": {"reliability"},
    "test": {"testing"},
    "tests": {"testing"},
    "optimi": {"optimization"},
    "loop": {"optimization"},
    "unused": {"cleanup"},
    "dead code": {"cleanup"},
    "type": {"typing"},
    "annotat": {"typing"},
    "doc": {"documentation"},
    "comment": {"documentation"},
    "syntax": {"syntax"},
}


class CognitiveCore:
    """Understands requests, analyzes code, and plans a modification strategy."""

    def __init__(
        self,
        analyzer: Optional[ProjectAnalyzer] = None,
        llm: Optional[LLMInterface] = None,
        capability_loader=load_seed_capabilities,
    ):
        self.analyzer = analyzer or ProjectAnalyzer()
        self.llm = llm  # Not constructed eagerly: querying a local LLM is
        # optional for Phase 1's structural flow and shouldn't be required
        # just to instantiate CognitiveCore (e.g. in unit tests, or when
        # Ollama isn't running).
        self._capability_loader = capability_loader

    # -- 1. Receiving requests -------------------------------------------------

    def receive_request(
        self,
        user_request: str,
        code_context: str = "",
        target_project: str = "",
        target_language: str = "",
    ) -> Request:
        """Wrap a raw user request into a structured Request object."""
        if not user_request or not user_request.strip():
            raise ValueError("user_request must not be empty")
        return Request(
            user_request=user_request.strip(),
            code_context=code_context,
            target_project=target_project,
            target_language=target_language,
        )

    # -- 2. Analyzing the target project ---------------------------------------

    def analyze_target_project(
        self, project_path: str, max_files: int = 500
    ) -> ProjectAnalysis:
        """Walk ``project_path`` and analyze every file in a supported language.

        Reads from disk relative to ``project_path``. Files that don't match
        a known extension (see ``EXTENSION_LANGUAGE_MAP``) are skipped rather
        than reported as errors -- most projects contain plenty of non-code
        files (README, config, etc) that aren't analysis targets.
        """
        root = Path(project_path)
        files: Dict[str, str] = {}
        if root.exists():
            count = 0
            for path in sorted(root.rglob("*")):
                if count >= max_files:
                    break
                if not path.is_file():
                    continue
                if path.suffix not in EXTENSION_LANGUAGE_MAP:
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                rel = str(path.relative_to(root))
                files[rel] = text
                count += 1
        return self.analyzer.analyze_project(project_path, files)

    def analyze_single_file(self, file_path: str, code: str) -> ProjectAnalysis:
        """Convenience wrapper for analyzing a single in-memory snippet,
        for the common case of a request scoped to one file's code_context."""
        file_analysis = self.analyzer.analyze_file(file_path, code)
        return ProjectAnalysis(
            project_path=file_path,
            files=[file_analysis],
            languages_detected=(
                [file_analysis.language] if file_analysis.parse_ok else []
            ),
        )

    # -- 3. Task decomposition ---------------------------------------------------

    def decompose_task(self, task: str) -> List[Subtask]:
        """Split a (possibly compound) task description into ordered subtasks.

        Splits on coordinating language ("and", "then", commas). Each
        subtask depends on the previous one, reflecting that Phase 1's
        decomposition is sequential rather than a dependency graph -- true
        parallel/branching planning is future work beyond this phase's scope.
        """
        task = task.strip()
        if not task:
            return []
        parts = [p.strip() for p in _SUBTASK_SPLIT_RE.split(task) if p.strip()]
        if not parts:
            parts = [task]

        subtasks: List[Subtask] = []
        for i, part in enumerate(parts, start=1):
            depends_on = [f"subtask_{i - 1:03d}"] if i > 1 else []
            subtasks.append(
                Subtask(id=f"subtask_{i:03d}", description=part, depends_on=depends_on)
            )
        return subtasks

    # -- 4. Capability selection --------------------------------------------------

    def select_candidate_capabilities(
        self,
        analysis: ProjectAnalysis,
        user_request: str = "",
    ) -> List[CapabilityTemplate]:
        """Select capabilities that are plausible candidates for this request.

        Filtering happens in two stages:
          1. Language match: a capability must declare support for at least
             one language detected in ``analysis`` (or declare no languages,
             treated as language-agnostic).
          2. Keyword relevance (only when ``user_request`` is given): capabilities
             whose tags intersect words found in the request are ranked first.

        Stage 2 is a heuristic, not a hard filter -- if nothing matches by
        keyword, all language-eligible capabilities are still returned so
        the caller (or the LLM, via ``plan_modification_strategy``) can
        choose among them.
        """
        all_capabilities = self._capability_loader()
        languages = set(analysis.languages_detected)

        eligible = [
            cap
            for cap in all_capabilities
            if not cap.target_languages or languages & set(cap.target_languages)
        ]

        if not user_request:
            return eligible

        request_lower = user_request.lower()
        hinted_tags = set()
        for keyword, tags in _KEYWORD_TAG_HINTS.items():
            if keyword in request_lower:
                hinted_tags |= tags

        if not hinted_tags:
            return eligible

        ranked = [cap for cap in eligible if hinted_tags & set(cap.tags)]
        return ranked or eligible

    # -- 5. Planning ---------------------------------------------------------------

    def plan_modification_strategy(
        self,
        analysis: ProjectAnalysis,
        selected_capabilities: List[CapabilityTemplate],
        subtasks: Optional[List[Subtask]] = None,
    ) -> ModificationPlan:
        """Combine analysis + selected capabilities into a ModificationPlan."""
        subtasks = subtasks or [
            Subtask(
                id="subtask_001",
                description=(
                    f"Apply selected capabilities to {analysis.project_path} "
                    f"({analysis.total_functions} function(s) across "
                    f"{len(analysis.files)} file(s))."
                ),
            )
        ]
        capability_ids = [cap.id for cap in selected_capabilities]
        rationale = (
            f"Selected {len(capability_ids)} candidate capability(ies) "
            f"({', '.join(capability_ids) or 'none'}) based on detected "
            f"language(s) {', '.join(analysis.languages_detected) or 'unknown'} "
            f"and {len(subtasks)} planned subtask(s)."
        )
        return ModificationPlan(
            subtasks=subtasks,
            selected_capability_ids=capability_ids,
            rationale=rationale,
        )
