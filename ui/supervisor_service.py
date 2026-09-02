"""Supervisor-facing SPS scenario orchestration.

This service keeps research orchestration outside the CLI presentation layer.
It connects a user prompt + source code to Layer 2 analysis, Layer 9 capability
lookup, and Layer 8 capability-gap planning while recording the decisions in
Layer 3's persistent research trace.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from experience.evolution_trace import EvolutionTraceStore
from layers.layer_02_cognitive_core import CognitiveCore
from layers.layer_08_evolution import CapabilityGapPlanner
from layers.layer_09_capability_registry import CapabilityRegistryManager


@dataclass
class SupervisorAnalysisResult:
    """Structured result from the supervisor-facing analysis/route stage."""

    scenario_id: str
    stage: int
    analysis: Dict[str, Any]
    capability_search: Dict[str, Any]
    capability_generation: Dict[str, Any]


class SupervisorScenarioService:
    """Run the non-mutating front half of a supervisor SPS scenario."""

    def __init__(
        self,
        *,
        trace_history_path: str | Path = "experience/traces/evolution_history.json",
        trace_stage_path: str | Path = "experience/traces/stage_state.json",
        registry_path: str = "capabilities/registry.json",
        seeds_dir: str = "capabilities/seeds",
        generated_dir: str = "capabilities/generated",
        cognitive_core: Optional[CognitiveCore] = None,
        registry: Optional[CapabilityRegistryManager] = None,
    ) -> None:
        self.core = cognitive_core or CognitiveCore()
        self.registry = registry or CapabilityRegistryManager(registry_path)
        self.trace_store = EvolutionTraceStore(
            history_path=trace_history_path,
            stage_path=trace_stage_path,
        )
        self.gap_planner = CapabilityGapPlanner(
            seeds_dir=seeds_dir,
            generated_dir=generated_dir,
        )

    def analyze_submission(
        self,
        *,
        user_request: str,
        code: str,
        language: str,
        file_path: str = "",
    ) -> SupervisorAnalysisResult:
        """Analyze a single submitted code scenario and route capability needs.

        No user source is modified in this stage. The returned plan tells the
        next execution step which existing capability to use or which Layer 8
        gap plan to develop.
        """
        scenario = self.trace_store.start_scenario(
            user_request=user_request,
            code=code,
            language=language,
            file_path=file_path,
            metadata={"source": "supervisor_service"},
        )
        scenario_id = scenario["scenario_id"]
        stage = int(scenario["stage_before"])

        request = self.core.receive_request(
            user_request,
            code_context=code,
            target_project=file_path,
            target_language=language,
        )
        file_label = file_path or "<submitted-code>"
        project_analysis = self.core.analyze_single_file(file_label, code)
        candidates = self.core.select_candidate_capabilities(
            project_analysis,
            user_request=user_request,
        )

        analysis = {
            "user_intent": request.user_request,
            "language": language.lower(),
            "code_present": bool(code.strip()),
            "file_path": file_path,
            "files_analyzed": len(project_analysis.files),
            "functions_discovered": project_analysis.total_functions,
            "parse_ok": bool(project_analysis.files and project_analysis.files[0].parse_ok),
            "candidate_count": len(candidates),
        }
        self.trace_store.append_event(
            scenario_id,
            "task_and_code_analysis",
            {
                "why": "Combine the user's requested change with the submitted source code before selecting a capability.",
                "what": "Task intent, language, parse status, and code structure summary.",
                "how": "Layer 2 Cognitive Core analyzed the submitted single-file code.",
                "functions_discovered": project_analysis.total_functions,
                "parse_ok": analysis["parse_ok"],
            },
        )

        registry_matches = self.registry.search_capabilities(user_request)
        core_ids = [candidate.id for candidate in candidates]
        registry_ids = [cap.id for cap in registry_matches]
        capability_ids = list(dict.fromkeys(core_ids + registry_ids))
        selected = self._select_capability(candidates, registry_matches, user_request)
        search = {
            "query": user_request,
            "candidate_source": {
                "layer_02_ids": core_ids,
                "layer_09_ids": registry_ids,
            },
            "capability_ids": capability_ids,
            "selected": selected.id if selected else None,
            "found": selected is not None,
            "why": (
                f"Selected {selected.id} because its registered metadata or Layer 2 tags matched the request."
                if selected
                else "No registered capability matched the requested behavior."
            ),
        }
        self.trace_store.append_event(
            scenario_id,
            "capability_search",
            {
                "why": search["why"],
                "what": "Layer 2 candidates and Layer 9 registered capability matches.",
                "how": "Cognitive Core relevance ranking plus Capability Registry search.",
                "capability_ids": capability_ids,
            },
        )

        generation: Dict[str, Any]
        if selected is None:
            plan = self.gap_planner.plan(
                task_description=user_request,
                language=language,
                reason="No suitable registered capability was found for the requested behavior.",
                task_id=scenario_id,
            )
            generation = {
                "required": True,
                "layer": "Layer 8 - Evolution",
                "capability_id": plan.capability_id,
                "name": plan.name,
                "trigger_pattern": plan.trigger_pattern,
                "provenance": plan.provenance,
            }
            self.trace_store.append_event(
                scenario_id,
                "capability_gap_planned",
                {
                    "why": plan.provenance["why"],
                    "what": plan.provenance["what"],
                    "how": plan.provenance["how"],
                    "when": plan.provenance["when"],
                    "capability_id": plan.capability_id,
                },
            )
            status = "capability_planned"
        else:
            generation = {
                "required": False,
                "layer": "Layer 8 - Evolution",
                "reason": "Existing capability is available; capability generation is not required for this scenario.",
            }
            status = "analyzed"

        completed = self.trace_store.complete_scenario(
            scenario_id,
            status=status,
            analysis=analysis,
            capability_search=search,
            capability_generation=generation,
        )
        return SupervisorAnalysisResult(
            scenario_id=scenario_id,
            stage=stage,
            analysis=completed["analysis"],
            capability_search=completed["capability_search"],
            capability_generation=completed["capability_generation"],
        )

    @staticmethod
    def _select_capability(candidates: List[Any], registry_matches: List[Any], request: str):
        """Prefer a Core candidate, then a registry result, using request keywords."""
        request_lower = request.lower()
        priority = (
            ("syntax", "CAP-002"),
            ("test", "CAP-003"),
            ("loop", "CAP-004"),
            ("exception", "CAP-005"),
            ("error handling", "CAP-005"),
            ("unused", "CAP-006"),
            ("annotation", "CAP-007"),
            ("type", "CAP-007"),
            ("doc", "CAP-008"),
            ("documentation", "CAP-008"),
        )
        by_id = {getattr(item, "id", ""): item for item in candidates + registry_matches}
        for keyword, capability_id in priority:
            if keyword in request_lower and capability_id in by_id:
                return by_id[capability_id]
        return candidates[0] if candidates else (registry_matches[0] if registry_matches else None)
