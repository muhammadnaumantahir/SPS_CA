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

For every observed capability, the evaluator derives:

- observation count;
- raw success rate;
- partial-outcome rate;
- mean task duration;
- evidence confidence, which increases as observations accumulate;
- a bounded behavioral score from 0.0 to 1.0.

Small samples are shrunk toward a neutral 50% success prior so one lucky or unlucky task does not immediately dominate strategy selection. Latency contributes a bounded penalty while success remains dominant.

## Evidence-aware strategy switching

`CapabilityEvaluator.rank()` only returns capabilities with the configured minimum evidence (three observations by default).

`StrategyPolicy` adds a second guard: the best alternative must beat the current capability by at least a configurable score margin (0.08 by default). A recommendation therefore requires both sufficient evidence and a meaningful behavioral advantage.

The recommendation is advisory data, not authorization for source mutation.

## Live Brain routing

Phase 2 now feeds evidence-qualified generated capabilities into the Brain routing boundary without weakening intent safety.

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
StrategyPolicy margin check
    ↓
Generated capability may replace canonical default
    ↓
Capability execution
    ↓
New Experience evidence
```

A generated capability can participate only when its registry metadata explicitly allows the classified intent, does not forbid that intent, is active, and has enough historical evidence to clear the strategy margin. The canonical Stage-0 capability remains the fallback.

Test Generation remains independently protected and is never selected as a side effect of ordinary code-generation, modification, diagnosis, fixing, refactoring, documentation, validation, or project-operation requests.

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

The repository contains intentionally seeded defects used to validate self-programming. Those benchmark failures are executed as observable, non-blocking workflow steps so they remain available as Evolution targets without falsely presenting the repository's stable contract suite as broken.

The stable project tests remain blocking for CI. The current TypeScript benchmark is isolated from the stable contract suite while preserving the seeded defect for later self-repair evaluation.

## Phase 2 status

Completed:

- deterministic capability behavioral scoring;
- evidence confidence;
- latency-aware scoring;
- minimum-evidence ranking;
- conservative strategy switching with a score margin;
- generated-capability intent metadata exposure;
- evidence-qualified generated-capability routing in the Brain boundary;
- regression/unit coverage for the new learning policy;
- separation of seeded benchmark failures from blocking target-project CI.

Next work:

- persist strategy recommendations with before/after outcomes;
- run controlled A/B comparisons between competing generated capability versions;
- introduce governed retirement/deactivation of persistently poor generated capabilities;
- add scheduled or threshold-triggered optimization cycles;
- use those measurements to drive the next Evolution improvements.
