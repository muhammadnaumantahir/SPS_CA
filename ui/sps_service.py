"""SPS-CA scenario orchestration for analysis, capability routing, and growth."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from brain import Brain
from experience.evolution_trace import EvolutionTraceStore
from layers.layer_03_cognitive import CognitiveCore
from layers.layer_02_governance import ChangeType, GovernanceGate
from layers.layer_08_evolution import CapabilityGapPlanner, EvolutionEngine
from layers.layer_08_evolution.growth_decision import GrowthDecision, GrowthDecisionEngine
from layers.capability_registry import CapabilityRegistryManager


@dataclass
class SPSAnalysisResult:
    """Structured result from the SPS scenario analysis/route stage."""

    scenario_id: str
    stage: int
    analysis: Dict[str, Any]
    capability_search: Dict[str, Any]
    capability_generation: Dict[str, Any]


class SPSScenarioService:
    """Run an SPS scenario through analysis and capability growth."""

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
        self.growth_decision = GrowthDecisionEngine()
        self.trace_store = EvolutionTraceStore(history_path=trace_history_path, stage_path=trace_stage_path)
        self.evolution = EvolutionEngine(
            governance_gate=self.governance,
            generated_dir=generated_dir,
            seeds_dir=seeds_dir,
            registry_path=registry_path,
            evaluation_dir=evaluation_dir,
        )
        self.gap_planner = CapabilityGapPlanner(seeds_dir=seeds_dir, generated_dir=generated_dir)

    def analyze_submission(
        self,
        *,
        user_request: str,
        code: str,
        language: str,
        file_path: str = "",
        project_root: str = ".",
    ) -> SPSAnalysisResult:
        """Analyze, route, and apply an explicit Layer-8 growth decision."""
        scenario = self.trace_store.start_scenario(
            user_request=user_request,
            code=code,
            language=language,
            file_path=file_path,
            metadata={"source": "sps_service"},
        )
        scenario_id = scenario["scenario_id"]
        stage = int(scenario["stage_before"])

        try:
            request = self.core.receive_request(user_request, code_context=code, target_project=file_path, target_language=language)
            file_label = file_path or "<submitted-code>"
            project_analysis = self.core.analyze_single_file(file_label, code)
            candidates = self.core.select_candidate_capabilities(project_analysis, user_request=user_request)
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
            self.trace_store.append_event(scenario_id, "task_and_code_analysis", {
                "why": "Combine the user's requested change with the submitted source code before selecting a capability.",
                "what": "Task intent, language, parse status, and code structure summary.",
                "how": "Cognitive Core analyzed the submitted single-file code.",
                "functions_discovered": project_analysis.total_functions,
                "parse_ok": analysis["parse_ok"],
            })

            registry_matches = self.registry.search_capabilities(user_request, language=language)
            core_ids = [candidate.id for candidate in candidates]
            registry_ids = [cap.id for cap in registry_matches]
            capability_ids = list(dict.fromkeys(core_ids + registry_ids))
            selected = self._select_capability(candidates, registry_matches, user_request, code=code, file_path=file_path)
            search = {
                "query": user_request,
                "candidate_source": {"layer_02_ids": core_ids, "layer_09_ids": registry_ids},
                "selected": selected.id if selected else None,
                "found": selected is not None,
                "capability_ids": capability_ids,
                "intent_class": Brain.infer_intent_class(user_request, code, file_path),
                "why": f"Selected {selected.id} from the canonical intent route." if selected else "No registered capability matched the requested behavior.",
            }
            self.trace_store.append_event(scenario_id, "capability_search", {
                "why": search["why"],
                "what": "Cognitive candidates and registered capability matches.",
                "how": "Deterministic Brain intent classification is the primary route; registry/Cognitive results are used only as the candidate set.",
                "capability_ids": capability_ids,
                "selected": search["selected"],
                "intent_class": search["intent_class"],
            })

            growth = self.growth_decision.decide(
                existing_capability_id=selected.id if selected else "",
                capability_match=selected is not None,
                disagreement_count=0,
                repeated_pattern=False,
                adaptation_viable=False,
                composition_viable=False,
                improvement_viable=False,
            )
            self.trace_store.append_event(scenario_id, "sps_growth_decision", {
                "why": growth.reasoning,
                "what": "Layer 8 selected the least-structural growth action justified by current evidence.",
                "how": "GrowthDecisionEngine evaluated capability match and available growth alternatives.",
                "decision": growth.decision.value,
                "reason_code": growth.reason_code,
                "evidence": growth.evidence,
            })

            if growth.decision == GrowthDecision.CREATE:
                plan = self.evolution.plan_capability_for_gap(
                    task_description=user_request,
                    language=language,
                    reason=growth.reasoning,
                    task_id=scenario_id,
                )
                self.trace_store.append_event(scenario_id, "capability_gap_planned", {
                    "why": growth.reasoning,
                    "what": plan.provenance.get("what", user_request),
                    "how": plan.provenance.get("how", "Layer 8 planned the capability gap."),
                    "when": plan.provenance.get("when", "scenario_time"),
                    "capability_id": plan.capability_id,
                    "growth_decision": growth.decision.value,
                })
                governance_decision = self._govern_generated_capability(plan)
                development = self.evolution.develop_capability_for_gap(
                    plan, project_root=project_root, governance_decision_status=governance_decision.decision,
                )
                generation = {
                    "required": True,
                    "layer": "Layer 8 - Evolution",
                    "capability_id": plan.capability_id,
                    "name": plan.name,
                    "trigger_pattern": plan.trigger_pattern,
                    "provenance": plan.provenance,
                    "growth_decision": {
                        "decision": growth.decision.value,
                        "reason_code": growth.reason_code,
                        "reasoning": growth.reasoning,
                        "evidence": growth.evidence,
                    },
                    "developed": True,
                    "governance": {"decision_id": governance_decision.id, "decision": governance_decision.decision.value, "rationale": governance_decision.rationale},
                    **development,
                }
                generation_status = "capability_developed" if development["registered"] else "capability_development_failed"
                self.trace_store.append_event(scenario_id, generation_status, {
                    "why": growth.reasoning,
                    "what": f"Generated {plan.capability_id} and ran its quality gates.",
                    "how": "Layer 8 generation/test pipeline followed by governance and registry persistence.",
                    "capability_id": plan.capability_id,
                    "registered": development["registered"],
                    "tests_passed": development["test_result"]["passed"],
                    "governance_decision": governance_decision.decision.value,
                })
            else:
                generation = {
                    "required": False,
                    "layer": "Layer 8 - Evolution",
                    "growth_decision": {
                        "decision": growth.decision.value,
                        "reason_code": growth.reason_code,
                        "reasoning": growth.reasoning,
                        "evidence": growth.evidence,
                    },
                    "reason": growth.reasoning,
                    "reused": selected.id if selected else None,
                }
                generation_status = "analyzed"

            completed = self.trace_store.complete_scenario(
                scenario_id, status=generation_status, analysis=analysis,
                capability_search=search, capability_generation=generation,
            )
            return SPSAnalysisResult(
                scenario_id=scenario_id,
                stage=stage,
                analysis=completed["analysis"],
                capability_search=completed["capability_search"],
                capability_generation=completed["capability_generation"],
            )
        except Exception as exc:
            self.trace_store.complete_scenario(scenario_id, status="failed", result={"success": False, "error": str(exc)})
            raise

    def _govern_generated_capability(self, plan: Any):
        module_dir = Path(self.evolution.generated_dir) / plan.capability_id.lower().replace("-", "_")
        affected = [str(module_dir / name) for name in ("capability.py", "tests.py", "metadata.json")]
        return self.governance.make_decision(
            change_id=f"evolution_{plan.capability_id}",
            change_type=ChangeType.EVOLUTION,
            change_description=plan.description,
            affected_files=affected,
            related_capabilities=[plan.capability_id],
        )

    @staticmethod
    def _select_capability(
        candidates: List[Any],
        registry_matches: List[Any],
        request: str,
        *,
        code: str = "",
        file_path: str = "",
    ):
        """Route from the canonical Brain intent instead of stale keyword mappings.

        The previous implementation contained an incorrect table where words such
        as ``type`` and ``annotation`` routed to CAP-007 (tests), while ``test``
        routed to CAP-003 (analysis). That made valid code-modification scenarios
        generate tests instead of implementing the requested change.
        """
        by_id = {getattr(item, "id", ""): item for item in candidates + registry_matches}
        intent = Brain.infer_intent_class(request, code, file_path)
        canonical_by_intent = {
            "code_generation": "CAP-001",
            "code_modification": "CAP-002",
            "analysis": "CAP-003",
            "bug_diagnosis": "CAP-004",
            "bug_fixing": "CAP-005",
            "refactoring": "CAP-006",
            "test_generation": "CAP-007",
            "documentation": "CAP-008",
            "validation": "CAP-009",
            "project_operations": "CAP-010",
        }
        primary_id = canonical_by_intent.get(intent)
        if primary_id and primary_id in by_id:
            return by_id[primary_id]
        if intent == "mixed":
            # Mixed requests are composed in the Brain/routing layer. When this
            # service must execute one capability, choose the first explicit
            # executable step rather than guessing from a keyword collision.
            from brain.multi_capability import compose_explicit_capabilities
            available = set(by_id)
            steps = compose_explicit_capabilities(request, has_code=bool(code.strip()), available_ids=available)
            if steps:
                return by_id.get(steps[0]["capability_id"])
        return None

    @staticmethod
    def _best_registry_text_match(matches: List[Any], request_lower: str):
        tokens = {token for token in request_lower.split() if len(token) > 3}
        if not tokens:
            return None
        scored = []
        for capability in matches:
            text = f"{getattr(capability, 'name', '')} {getattr(capability, 'description', '')}".lower()
            score = sum(1 for token in tokens if token in text)
            if score:
                scored.append((score, capability))
        if not scored:
            return None
        scored.sort(key=lambda item: (-item[0], getattr(item[1], "id", "")))
        return scored[0][1] if scored[0][0] >= 2 else None
