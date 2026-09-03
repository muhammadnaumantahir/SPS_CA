# SPS-CA Phase 2 — Behavioral Capability Learning

Phase 2 builds the first learning layer on top of Phase 1. Instead of treating every capability as equally effective, SPS-CA now converts Experience evidence into a deterministic behavioral score that can guide future strategy decisions.

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

Layer 6 now exposes `CapabilityEvaluator` and `CapabilityEvaluation`.

For every observed capability, the evaluator records or derives:

- observation count;
- raw success rate;
- partial-outcome rate;
- mean task duration;
- evidence confidence, which increases as observations accumulate;
- a bounded behavioral score from 0.0 to 1.0.

Small samples are shrunk toward a neutral 50% success prior so one lucky or unlucky task does not immediately dominate strategy selection.

Latency contributes a bounded penalty rather than becoming the primary objective. Success remains the dominant signal.

## Evidence-aware ranking

`CapabilityEvaluator.rank()` only returns capabilities with the configured minimum evidence (three observations by default). `choose_best()` then selects the highest-scoring observed candidate deterministically.

This prevents SPS-CA from declaring a new capability "better" when it has little or no evidence.

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
Strategy recommendation
    ↓
Adaptation / future routing
    ↓
New Experience evidence
    ↓
Evolution only when a genuine capability gap remains
```

Phase 2 does not silently rewrite routing rules, capabilities, or source code. A score is evidence, not authorization. Any structural self-change still follows the Phase 1 Software DNA → Governance → Layer 10 execution boundary.

## Safety boundary

The evaluator is read-only with respect to capabilities and source code. It operates on `ExperienceLog` records and returns plain data objects.

No LLM call is required to compute the score. This makes the measurement reproducible and prevents an unavailable provider from being interpreted as evidence that one capability is better than another.

## Phase 2 scope

Completed:

- deterministic capability behavioral scoring;
- evidence confidence;
- latency-aware scoring;
- minimum-evidence ranking;
- best-observed capability selection;
- regression/unit coverage for the evaluator.

Next work:

- feed evaluator rankings directly into the live capability-routing context;
- persist strategy recommendations with before/after evidence;
- compare competing generated capability versions under controlled verification;
- retire generated capabilities that remain below a governed quality floor;
- add scheduled/triggered optimization cycles instead of only reacting to failures.
