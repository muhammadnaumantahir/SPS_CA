"""Supervisor-facing SPS scenario orchestration.

Presentation-adjacent orchestration for the research prototype. The canonical
SPS architecture remains exactly ten layers; this service coordinates those
layers for a submitted scenario and persists the research trace.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from experience.evolution_trace import EvolutionTraceStore
from layers.layer_02_cognitive_core import CognitiveCore
from layers.layer_07_governance import ChangeType, GovernanceGate
from layers.layer_08_evolution import CapabilityGapPlanner, EvolutionEngine
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
    """Run the supervisor SPS scenario through analysis and capability growth."""

    def __init__(
        self,
        *,
        trace_history_path: str | Path = "experience/traces/evolution_history.json",
        trace_stage_path: str | Path = "experience/traces/stage_state.json",
        registry_path: str = "capabilities/registry.json",
        seeds_dir: str = "capabilities/seeds",
        generated_dir: str = "capabilities/generated",
        evaluation_dir: str = "evaluation/evolution",
        cognitive_core: Optional[CognitiveCore] = None,
        registry: Optional[CapabilityRegistryManager] = None,
        governance: Optional[GovernanceGate] = None,
    ) -> None:
        self.core = cognitive_core or CognitiveCore()
        self.registry = registry or CapabilityRegistryManager(registry_path)
        self.governance = governance or GovernanceGate()
        self.trace_store = EvolutionTraceStore(
            history_path=trace_history_path,
            stage_path=trace_stage_path,
        )
        self.evolution = EvolutionEngine(
            governance_gate=self.governance,
            generated_dir=generated_dir,
            seeds_dir=seeds_dir,
            registry_path=registry_path,
            evaluation_dir=evaluation_dir,
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
        project_root: str = ".",
    ) -> SupervisorAnalysisResult:
        """Analyze a submitted scenario and develop a missing capability when needed."""
        scenario = self.trace_store.start_scenario(
            user_request=user_request,
            code=code,
            language=language,
            file_path=file_path,
            metadata={"source": "supervisor_service"},
        )
        scenario_id = scenario["scenario_id"]
        stage = int(scenario["stage_before"])

        try:
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

            registry_matches = self.registry.search_capabilities(user_request, language=language)
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

            if selected is None:
                plan = self.evolution.plan_capability_for_gap(
                    task_description=user_request,
                    language=language,
                    reason="No suitable registered capability was found for the requested behavior.",
                    task_id=scenario_id,
                )
                self.trace_store.append_event(
                    scenario_id,
                    "capability_gap_planned",
                    {
                        "why": plan.provenance.get("why", "Capability gap detected."),
                        "what": plan.provenance.get("what", user_request),
                        "how": plan.provenance.get("how", "Layer 8 planned the capability gap."),
                        "when": plan.provenance.get("when", "scenario_time"),
                        "capability_id": plan.capability_id,
                    },
                )

                governance_decision = self._govern_generated_capability(plan)
                development = self.evolution.develop_capability_for_gap(
                    plan,
                    project_root=project_root,
                    governance_decision_status=governance_decision.decision,
                )
                generation = {
                    "required": True,
                    "layer": "Layer 8 - Evolution",
                    "capability_id": plan.capability_id,
                    "name": plan.name,
                    "trigger_pattern": plan.trigger_pattern,
                    "provenance": plan.provenance,
                    "developed": True,
                    "governance": {
                        "decision_id": governance_decision.id,
                        "decision": governance_decision.decision.value,
                        "rationale": governance_decision.rationale,
                    },
                    **development,
                }
                generation_status = "capability_developed" if development["registered"] else "capability_development_failed"
                self.trace_store.append_event(
                    scenario_id,
                    "capability_developed" if development["registered"] else "capability_development_failed",
                    {
                        "why": "The requested behavior had no suitable registered capability.",
                        "what": f"Generated {plan.capability_id} and ran its quality gates.",
                        "how": "Layer 8 generation/test pipeline followed by Layer 7 governance and Layer 9 registry persistence.",
                        "capability_id": plan.capability_id,
                        "registered": development["registered"],
                        "tests_passed": development["test_result"]["passed"],
                        "governance_decision": governance_decision.decision.value,
                    },
                )
            else:
                generation = {
                    "required": False,
                    "layer": "Layer 8 - Evolution",
                    "reason": "Existing capability is available; capability generation is not required for this scenario.",
                    "reused": selected.id,
                }
                generation_status = "analyzed"

            completed = self.trace_store.complete_scenario(
                scenario_id,
                status=generation_status,
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
        except Exception as exc:
            self.trace_store.complete_scenario(
                scenario_id,
                status="failed",
                result={"success": False, "error": str(exc)},
            )
            raise

    def _govern_generated_capability(self, plan: Any):
        module_dir = Path(self.evolution.generated_dir) / plan.capability_id.lower().replace("-", "_")
        affected = [
            str(module_dir / "capability.py"),
            str(module_dir / "tests.py"),
            str(module_dir / "metadata.json"),
        ]
        return self.governance.make_decision(
            change_id=f"evolution_{plan.capability_id}",
            change_type=ChangeType.EVOLUTION,
            change_description=plan.description,
            affected_files=affected,
            related_capabilities=[plan.capability_id],
        )

    @staticmethod
    def _select_capability(candidates: List[Any], registry_matches: List[Any], request: str):
        """Select only an explicitly relevant capability; generic candidates are not a match."""
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
        if registry_matches:
            exact = SupervisorScenarioService._best_registry_text_match(registry_matches, request_lower)
            if exact is not None:
                return exact
        return None

    @staticmethod
    def _best_registry_text_match(matches: List[Any], request_lower: str):
        tokens = {token for token in request_lower.split() if len(token) > 3}
        scored = []
        for capability in matches:
            text = f"{getattr(capability, 'name', '')} {getattr(capability, 'description', '')}".lower()
            score = sum(1 for token in tokens if token in text)
            if score:
                scored.append((score, capability))
        if not scored:
            return None
        scored.sort(key=lambda item: (-item[0], getattr(item[1], "id", "")))
        return scored[0][1]
