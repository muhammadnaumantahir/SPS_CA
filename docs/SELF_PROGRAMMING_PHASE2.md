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

Layer 8 also provides `GovernedRetirementManager` for evidence-gated lifecycle deactivation of generated capabilities that remain persistently poor, plus `OptimizationActionPlanner` for converting a triggered cycle into explicit Evolution capability plans.

## Controlled A/B comparison

`ABComparisonEngine` compares two compatible capability versions using only Layer 5 Experience evidence. Assignment is deterministic, so request-time LLM behavior cannot bias arm selection. A winner is withheld until both arms have enough evidence, are reasonably balanced, and the behavioral score margin is meaningful.

## Governed retirement

Generated capabilities are never deleted merely because they underperform. Retirement first requires minimum evidence and a low behavioral score. Canonical capabilities are protected. An eligible generated capability is deprecated only after a Governance decision, preserving metadata, lineage, source history, and historical Experience evidence.

## Threshold-triggered optimization cycles

`OptimizationCycleController` turns accumulated Experience into an auditable `OptimizationCyclePlan`. By default a cycle becomes eligible when there are at least 10 observations, the aggregate failure rate reaches 30%, or a candidate capability has at least five observations with a behavioral score at or below 0.35.

A five-minute cooldown prevents repeated triggering without new evidence. The controller is advisory: it does not mutate source, execute capabilities, approve Governance, or directly create new capabilities.

`OptimizationCycleService` is the runtime boundary. After each conversational task is recorded in Layer 5, the service evaluates the thresholds and cooldown. Triggered plans are persisted as optimization-cycle state and converted into an explicit Layer-8 `EvolutionActionPlan` using the latest task request/language as context.

## Authorized automatic Evolution

The Layer-8 execution boundary is `EvolutionExecutionAuthority`. It is default-deny and reads deployment authority from:

- `SPS_CA_AUTO_EVOLVE=true` (or `1`, `yes`, `on`, `enabled`) to permit automatic execution;
- `SPS_CA_AUTO_EVOLVE_MAX_ACTIONS` to cap automatic actions per cycle, constrained to 1–10 and defaulting to 1.

When authority is absent or disabled, SPS-CA still records the trigger and action plan but performs no Evolution mutation. When authority is enabled, the optimization-cycle service executes the prepared action through the existing candidate generation → tests → Software DNA → Governance → registration/promotion or rollback path. The execution decision and result are persisted for auditability.

Evolution lifecycle events are kept separate from Layer 5 capability-performance observations. A capability is **not** counted as successful merely because it was promoted. Only subsequent real task execution contributes to its behavioral score.

`OptimizationActionPlanner` converts triggered plans into explicit `CapabilityPlan` objects. It does not implement, register, execute, or retire anything itself.

## Self-improvement benchmark

`evaluation/self_improvement_benchmark.py` provides a deterministic before/after measurement harness. It requires both successful promotion/registration and a configured minimum behavioral score delta (default `+0.05`) before reporting that Evolution actually improved the capability.

The benchmark is deliberately deterministic and does not mutate production source; it proves the control flow and measurement contract before live provider-backed Evolution is used.

## Live provider-backed Evolution

`evaluation/live_self_programming.py` provides the controlled real-provider experiment. It copies the current repository into a temporary workspace, seeds deterministic underperformance evidence, enables one explicitly authorized Evolution action, and runs the normal `OptimizationCycleService` against the actual Ollama-backed `LLMInterface`.

The runner requires `--confirm-live-evolution`. It deletes the temporary workspace by default, so experiments do not modify the caller's checkout. Use `--keep-workspace` to inspect generated artifacts after the run.

Example from Colab or a local checkout:

```bash
cd /content/SPS_CA
python -m evaluation.live_self_programming \
  --task "add a reusable input validation capability" \
  --language python \
  --confirm-live-evolution \
  --keep-workspace
```

The command reports the optimization cycle, action plan, execution authorization, generated capability result, and temporary workspace location. Promotion is not treated as proof of improvement; real subsequent task observations remain necessary to establish that the evolved capability performs better.

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
Layer 8 Evolution action planning
    ↓
Explicit execution authority
    ↓
Real provider candidate generation → tests → DNA → Governance → promotion/rollback
    ↓
Evolution lifecycle telemetry (not capability-performance credit)
    ↓
Subsequent real task evidence measures whether the evolved capability improved behavior
    ↓
Conservative routing / retirement
```

## Safety boundary

Layer 6 produces evidence and recommendations. The optimization-cycle runtime records audit state and hands triggered work to an explicit Layer 8 action planner. `EvolutionExecutionAuthority` is a separate default-deny boundary for automatic execution. Any authorized implementation still requires the established Software DNA, Governance, validation, and execution/rollback controls.

Any structural self-change still follows the Phase 1 Software DNA → Governance → Verification & Validation → Layer 10 execution/rollback boundary.

## CI benchmark separation

The repository contains intentionally seeded defects used to validate self-programming. Those benchmark targets remain available as observable Evolution inputs rather than being silently removed from the project.

The evaluation workflow runs deterministic benchmark tests as part of `evaluation/tests`, keeping self-improvement proof separate from provider-dependent runtime experiments.

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
- governed Layer 8 action planning from triggered optimization cycles;
- explicit default-deny execution authority for automatic Evolution;
- automatic authorized handoff through the existing governed Evolution pipeline;
- auditable Evolution lifecycle outcome records;
- deterministic self-improvement measurement;
- end-to-end trigger → authorization → Evolution → measurement regression coverage;
- controlled real-provider Evolution runner with disposable workspace isolation;
- separation of seeded benchmark targets from normal architecture quality checks.

Next work:

- persist richer A/B and retirement outcome telemetry;
- improve long-horizon evidence aggregation without expanding conversational prompt history;
- use real provider-backed runs to collect enough post-Evolution task evidence to prove measurable improvement;
- run and verify the complete GitHub Actions suite after the Colab import regression fixes.
