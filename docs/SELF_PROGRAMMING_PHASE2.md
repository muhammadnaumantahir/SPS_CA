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

Layer 6 now provides four complementary controls:

- `CapabilityEvaluator` measures observed behavior from Layer 5 Experience;
- `StrategyPolicy` decides whether an alternative is strong enough to recommend;
- `ABComparisonEngine` provides deterministic, evidence-gated A/B comparison for compatible capability arms;
- `OptimizationCycleController` decides when accumulated evidence is sufficient to start another controlled optimization cycle.

Layer 8 also provides `GovernedRetirementManager` for evidence-gated lifecycle deactivation of generated capabilities that remain persistently poor.

## Controlled A/B comparison

`ABComparisonEngine` compares two compatible capability versions using only Layer 5 Experience evidence. Assignment is deterministic, so request-time LLM behavior cannot bias arm selection. A winner is withheld until both arms have enough evidence, are reasonably balanced, and the behavioral score margin is meaningful.

## Governed retirement

Generated capabilities are never deleted merely because they underperform. Retirement first requires minimum evidence and a low behavioral score. Canonical capabilities are protected. An eligible generated capability is deprecated only after a Governance decision, preserving metadata, lineage, source history, and historical Experience evidence.

## Threshold-triggered optimization cycles

`OptimizationCycleController` turns accumulated Experience into an auditable `OptimizationCyclePlan`. By default a cycle becomes eligible when there are at least 10 observations, the aggregate failure rate reaches 30%, or a candidate capability has at least five observations with a behavioral score at or below 0.35.

A five-minute cooldown prevents repeated triggering without new evidence. The controller is advisory: it does not mutate source, execute capabilities, approve Governance, or directly create new capabilities.

`OptimizationCycleService` is the runtime boundary. After each conversational task is recorded in Layer 5, the service evaluates the thresholds and cooldown. Only triggered plans are persisted as optimization-cycle state; the resulting plan is then available to the Evolution boundary for a subsequent governed action.

This is threshold-triggered rather than a background thread, so the normal request path remains deterministic and there is no hidden autonomous source mutation.

## Live Brain routing

Evidence-qualified generated capabilities participate in the live Brain boundary only when active, intent-safe, language-compatible, and supported by enough Experience evidence to clear the strategy margin. The canonical capability remains the fallback.

Test Generation remains independently protected and is never selected as a side effect of ordinary code-generation, modification, diagnosis, fixing, refactoring, documentation, validation, or project-operation requests.

## Closed learning loop

```text
Task execution
    ↓
Experience record
    ↓
Behavioral evaluation / controlled A-B comparison
    ↓
Threshold-triggered optimization assessment
    ↓
Conservative strategy recommendation
    ↓
Adaptation / live routing
    ↓
Governed retirement when a generated capability persistently underperforms
    ↓
Governed Evolution when a genuine capability gap remains
    ↓
New Experience evidence
```

## Safety boundary

Layer 6 produces evidence and recommendations. It does not authorize source mutation. The optimization-cycle runtime service persists only audit state for triggered cycles and hands the resulting plan to the appropriate governed Evolution boundary.

Any structural self-change still follows the Phase 1 Software DNA → Governance → Verification & Validation → Layer 10 execution/rollback boundary.

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
- deterministic controlled A/B capability comparison with minimum evidence and balance gates;
- governed retirement/deactivation of persistently poor generated capabilities;
- threshold-triggered optimization-cycle assessment;
- runtime integration after Experience recording;
- regression/unit coverage for the new learning policy;
- separation of seeded benchmark targets from normal architecture quality checks.

Next work:

- feed triggered optimization plans into a governed Evolution action planner;
- persist richer A/B and retirement outcome telemetry;
- improve long-horizon evidence aggregation without expanding conversational prompt history.
