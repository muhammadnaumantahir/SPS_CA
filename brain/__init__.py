"""Provider-neutral SPS-CA brain subsystem."""

from .brain import Brain, BrainPlan, BrainError
from .routing_guard import intent_guard

_original_infer_intent_class = Brain.infer_intent_class
_original_plan = Brain.plan


def _guarded_infer_intent_class(request: str, code: str = "", file_path: str = "") -> str:
    return intent_guard(_original_infer_intent_class, request, code, file_path)


def _fast_plan(self, **kwargs):
    """Build a deterministic plan only for the built-in provider path.

    Custom providers (including test doubles and externally supplied Brain
    implementations) must remain authoritative about their explicit plan.
    Otherwise a local keyword classifier can silently replace the capability
    the caller's Brain selected.
    """
    if self.provider is not None:
        return None
    request = str(kwargs.get("request", "")).strip()
    code = str(kwargs.get("code", ""))
    file_path = str(kwargs.get("file_path", ""))
    intent_class = self.infer_intent_class(request, code, file_path)
    if intent_class in {"unknown", "mixed"}:
        return None
    try:
        from capabilities.canonical import capability_ids_for_intent
        primary_ids = capability_ids_for_intent(intent_class)
    except (KeyError, TypeError, ValueError):
        return None
    if not primary_ids:
        return None
    catalog = list(kwargs.get("capability_catalog") or [])
    available = {str(item.get("id")) for item in catalog if isinstance(item, dict)}
    primary = next((cid for cid in primary_ids if cid in available), None)
    if not primary:
        return None
    language = str(kwargs.get("language") or "unknown")
    inferred_language, confidence, _ = self.detect_language(code, request, file_path)
    if language == "unknown":
        language = inferred_language
    return BrainPlan(
        intent=request,
        reasoning=f"Deterministic intent routing selected {primary} for '{intent_class}'.",
        steps=[{"capability_id": primary, "reason": f"intent-safe canonical routing for '{intent_class}'"}],
        provider=self.provider_name,
        model=self.model,
        language=language,
        language_confidence=max(0.0, min(1.0, confidence)),
        intent_class=intent_class,
    )


def _learning_aware_plan(self, **kwargs):
    """Plan safely, using deterministic routing or the configured Brain provider."""
    plan = _fast_plan(self, **kwargs)
    if plan is None:
        plan = _original_plan(self, **kwargs)
    if plan.intent_class in {"unknown", "mixed", "test_generation"} or not plan.steps:
        return plan

    catalog = list(kwargs.get("capability_catalog") or [])
    if not any(item.get("allowed_intents") for item in catalog if isinstance(item, dict)):
        try:
            from layers.capability_registry import CapabilityRegistryManager
            registry = CapabilityRegistryManager("capabilities/registry.json")
            catalog = [{"id": cap.id, "status": cap.status, "generated": bool(cap.generated), "allowed_intents": list(getattr(cap, "allowed_intents", []) or []), "forbidden_intents": list(getattr(cap, "forbidden_intents", []) or []), "supported_languages": list(getattr(cap, "supported_languages", []) or [])} for cap in registry.list_all_capabilities()]
        except (OSError, ValueError, TypeError):
            return plan

    experience_context = list(kwargs.get("experience_context") or [])
    from layers.layer_05_experience import ExperienceLog, Task
    from layers.layer_06_meta_learning import MetaLearningDecisionLog, StrategyPolicy
    tasks = []
    for item in experience_context:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        try: tasks.append(Task.from_dict(item))
        except (KeyError, TypeError, ValueError): continue
    if not tasks:
        return plan

    current_id = plan.steps[0].get("capability_id", "")
    experience = ExperienceLog(tasks)
    language = str(kwargs.get("language") or plan.language or "").lower()
    eligible_generated = []
    for item in catalog:
        cid = str(item.get("id", ""))
        if not cid or not item.get("generated") or str(item.get("status", "active")) != "active":
            continue
        allowed = {str(value) for value in (item.get("allowed_intents") or [])}; forbidden = {str(value) for value in (item.get("forbidden_intents") or [])}; languages = {str(value).lower() for value in (item.get("supported_languages") or [])}
        if plan.intent_class not in allowed or plan.intent_class in forbidden: continue
        if languages and language and language not in languages: continue
        eligible_generated.append(cid)
    if not current_id or not eligible_generated:
        return plan

    recent_selected = [task.selected_capability for task in tasks if task.selected_capability]
    policy = StrategyPolicy()
    recommendation = policy.recommended_for_future_routing(experience, current_id, eligible_generated, recent_selected_capabilities=recent_selected)
    try:
        if recommendation.evidence_sufficient:
            from layers.layer_06_meta_learning import MetaLearner
            learner = MetaLearner(policy=policy); decision = learner.create_decision(recommendation, triggered_by=kwargs.get("request", "")); log = MetaLearningDecisionLog.load_from_json(); log.add_decision(decision); log.save_to_json()
    except (OSError, ValueError, TypeError):
        pass
    winner = recommendation.recommended_capability_id
    if not winner:
        return plan
    return BrainPlan(intent=plan.intent, reasoning=f"{plan.reasoning} Layer 6 evidence recommended {winner} over {current_id}: {recommendation.reason}", steps=[{"capability_id": winner, "reason": recommendation.reason}], provider=plan.provider, model=plan.model, language=plan.language, language_confidence=plan.language_confidence, intent_class=plan.intent_class)


Brain.infer_intent_class = staticmethod(_guarded_infer_intent_class)
Brain.plan = _learning_aware_plan

__all__ = ["Brain", "BrainPlan", "BrainError"]
