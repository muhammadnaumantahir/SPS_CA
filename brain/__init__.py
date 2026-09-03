"""Provider-neutral SPS-CA brain subsystem."""

from .brain import Brain, BrainPlan, BrainError
from .routing_guard import intent_guard

# Preserve the existing Brain API while adding a deterministic final guard.
# The Brain remains replaceable and the guard only resolves explicit intent
# ambiguity; it does not create or execute capabilities.
_original_infer_intent_class = Brain.infer_intent_class
_original_plan = Brain.plan


def _guarded_infer_intent_class(request: str, code: str = "", file_path: str = "") -> str:
    return intent_guard(_original_infer_intent_class, request, code, file_path)


def _learning_aware_plan(self, **kwargs):
    """Allow evidence-qualified generated capabilities to win normal routing.

    The canonical capability remains the safe fallback. A generated capability
    can replace it only when it explicitly declares the current intent as
    allowed and Layer 6 has enough historical evidence plus a meaningful score
    margin to recommend the switch.
    """
    plan = _original_plan(self, **kwargs)
    if plan.intent_class in {"unknown", "mixed", "test_generation"}:
        return plan

    catalog = list(kwargs.get("capability_catalog") or [])
    experience_context = list(kwargs.get("experience_context") or [])
    tasks = []
    from layers.layer_05_experience import ExperienceLog, Task
    from layers.layer_06_meta_learning import StrategyPolicy

    for item in experience_context:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        try:
            tasks.append(Task.from_dict(item))
        except (KeyError, TypeError, ValueError):
            continue
    if not tasks or not plan.steps:
        return plan

    experience = ExperienceLog(tasks)
    current_id = plan.steps[0].get("capability_id", "")
    eligible_generated = []
    for item in catalog:
        cid = str(item.get("id", ""))
        if not cid or cid.startswith("CAP-0"):
            continue
        allowed_intents = {str(value) for value in (item.get("allowed_intents") or [])}
        forbidden_intents = {str(value) for value in (item.get("forbidden_intents") or [])}
        if plan.intent_class not in allowed_intents or plan.intent_class in forbidden_intents:
            continue
        if str(item.get("status", "active")) != "active":
            continue
        eligible_generated.append(cid)

    if not current_id or not eligible_generated:
        return plan

    recommendation = StrategyPolicy().recommend(
        experience,
        current_id,
        eligible_generated,
    )
    winner = recommendation.recommended_capability_id
    if not winner:
        return plan

    return BrainPlan(
        intent=plan.intent,
        reasoning=(
            f"{plan.reasoning} Layer 6 evidence recommended {winner} over "
            f"{current_id}: {recommendation.reason}"
        ),
        steps=[{
            "capability_id": winner,
            "reason": recommendation.reason,
        }],
        provider=plan.provider,
        model=plan.model,
        language=plan.language,
        language_confidence=plan.language_confidence,
        intent_class=plan.intent_class,
    )


Brain.infer_intent_class = staticmethod(_guarded_infer_intent_class)
Brain.plan = _learning_aware_plan

__all__ = ["Brain", "BrainPlan", "BrainError"]
