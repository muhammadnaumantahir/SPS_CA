# SPS-CA Phase 2 — Behavioral Capability Learning

Phase 2 builds the first learning loop on top of Phase 1. Instead of treating every capability as equally effective, SPS-CA converts Experience evidence into deterministic behavioral scores and uses conservative evidence rules to influence future routing.

## The ten layers remain

1. Software DNA
2. Governance
3. Cognitive
4. Knowledge
5. Experience
6. Meta-Learning
7. Adaptation
8. Evolution
9. Verification & Validation
10. Execution

The Brain remains a separate replaceable intelligence service.

## What Phase 2 adds

Layer 6 now provides two complementary controls:

- `CapabilityEvaluator` measures observed behavior from Layer 5 Experience;
- `StrategyPolicy` decides whether an alternative is strong enough to recommend.

For every observed capability, the evaluator derives observation count, raw success rate, partial-outcome rate, mean task duration, evidence confidence, and a bounded behavioral score from 0.0 to 1.0.

Small samples are shrunk toward a neutral 50% success prior so one lucky or unlucky task does not immediately dominate strategy selection. Latency contributes a bounded penalty while success remains dominant.

## Evidence-aware strategy switching

`CapabilityEvaluator.rank()` only returns capabilities with the configured minimum evidence (three observations by default).

`StrategyPolicy` adds a second guard: the best alternative must beat the current capability by at least a configurable score margin (0.08 by default). A strategy switch is therefore based on both sufficient evidence and a meaningful behavioral advantage.

A short routing cooldown also suppresses immediate switching back to a capability that was just selected, reducing strategy oscillation.

## Live Brain routing

Evidence-qualified generated capabilities now participate in the live Brain boundary.

The routing sequence is:

```text
User request
    ↓
Software DNA
    ↓
Cognitive intent classification
    ↓
Canonical intent eligibility
    ↓
Layer 6 evidence evaluation
    ↓
StrategyPolicy margin + cooldown check
    ↓
Generated capability may replace canonical default
    ↓
Capability execution
    ↓
New Experience evidence
```

A generated capability can participate only when it is active, explicitly declares the classified intent as allowed, does not forbid that intent, supports the current language, and has enough historical evidence to clear the strategy margin. The canonical Stage-0 capability remains the fallback.

Test Generation remains independently protected and is never selected as a side effect of ordinary code-generation, modification, diagnosis, fixing, refactoring, documentation, validation, or project-operation requests.

## Persisted learning evidence

When Layer 6 has enough evidence to produce a recommendation, SPS-CA persists a `MetaLearningDecision` record containing the previous strategy, proposed strategy, rationale, timestamp, and the measured recommendation evidence.

These records are append-only and advisory. They provide an audit trail for why a future routing strategy was preferred; they do not authorize source mutation.

## Closed learning loop

```text
Task execution
    ↓
Experience record
    ↓
Capability behavioral evaluation
    ↓
Evidence-aware ranking
    ↓
Conservative strategy recommendation
    ↓
Persist recommendation evidence
    ↓
Adaptation / live routing
    ↓
New Experience evidence
    ↓
Evolution only when a genuine capability gap remains
```

## Safety boundary

The evaluator and strategy policy are read-only with respect to source code and capabilities. They operate on Experience records and produce plain recommendation objects.

Any structural self-change still follows the Phase 1 Software DNA → Governance → Verification & Validation → Layer 10 execution/rollback boundary. Layer 6 cannot authorize a source mutation by itself.

## CI benchmark separation

The repository contains intentionally seeded defects used to validate self-programming. Those benchmark targets remain available as observable Evolution inputs rather than being silently removed from the project.

The stable project contracts and architecture tests remain the primary blocking quality gate; seeded benchmark behavior is evaluated separately when the workflow exposes it as a target.

## Phase 2 status

Completed:

- deterministic capability behavioral scoring;
- evidence confidence;
- latency-aware scoring;
- minimum-evidence ranking;
- conservative strategy switching with a score margin;
- routing cooldown against strategy oscillation;
- generated-capability intent metadata exposure;
- evidence-qualified generated-capability routing in the Brain boundary;
- persisted evidence-backed meta-learning decisions;
- regression/unit coverage for the new learning policy;
- separation of seeded benchmark targets from normal architecture quality checks.

Next work:

- run controlled A/B comparisons between competing generated capability versions;
- introduce governed retirement/deactivation of persistently poor generated capabilities;
- add scheduled or threshold-triggered optimization cycles;
- use those measurements to drive the next Evolution improvements.
