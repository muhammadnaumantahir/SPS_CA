# SPS-CA — Experimental Scenarios

This document defines **what will be tested**. It is separate from the system description in `docs/master.md` so the architecture documentation can stay focused on what SPS-CA is.

## Purpose

The evaluation compares three conditions using controlled coding tasks:

- **Baseline A:** model-only/naive coding assistant behavior.
- **Baseline B:** coding assistant with deterministic coding tools but without SPS learning/evolution.
- **SPS-CA:** ten-layer architecture, separate Brain, capabilities, experience, meta-learning, adaptation, evolution, verification and governance.

The central experimental question is whether the SPS mechanisms improve repeated-task handling and enable reusable capability development beyond ordinary coding-assistant behavior.

## Test dimensions

Every relevant scenario records:

| Dimension | What is recorded |
|---|---|
| Task result | success, failure or partial |
| Correctness | expected behavior and regression result |
| Time | elapsed task time |
| Retries | number of recovery attempts |
| Brain plan | intent, reasoning and selected capabilities |
| Capability use | selected, composed and reused capabilities |
| Experience | stored outcome and failure evidence |
| Adaptation | strategy/parameter change without self-modification |
| Evolution | capability candidate generation when triggered |
| Verification | tests, sandbox, safety and performance evidence |
| Governance | approval, rejection or escalation with rationale |
| Lineage | relationship between trigger, candidate and registered capability |
| Recovery | rollback or alternative strategy after failure |

## Controlled projects

Three functionally equivalent projects are used so that the same task intent can be examined across languages:

1. `projects/project_a_python`
2. `projects/project_b_java`
3. `projects/project_c_typescript`

The implementation is designed to be extended to additional languages later.

## Scenario catalog

### A. Basic coding-assistant behavior

#### S1 — Syntax Error Fix
**Purpose:** establish basic repair behavior.  
**Input:** seeded syntax defect.  
**Expected:** repaired source parses and tests pass.  
**Compare:** Baseline A vs Baseline B vs SPS-CA.

#### S2 — Feature Addition
**Purpose:** test natural-language feature implementation.  
**Input:** feature request against existing code.  
**Expected:** requested behavior exists without unrelated changes.  
**Observe:** Brain plan, capability choice, verification outcome.

#### S3 — Test Generation
**Purpose:** test explicit test-generation behavior.  
**Input:** request for tests for an existing function/module.  
**Expected:** executable tests covering requested behavior.  
**Observe:** test quality and whether the system avoids treating every validation request as test generation.

#### S4 — Code Refactoring
**Purpose:** test behavior-preserving transformation.  
**Input:** refactoring request.  
**Expected:** intended structural improvement with preserved externally visible behavior.

#### S5 — Single Failure Detection
**Purpose:** establish one failure signal before learning can be demonstrated.  
**Input:** one seeded defect/failure.  
**Expected:** failure is detected, categorized and recorded as experience.

### B. Experience, adaptation and capability behavior

#### S6 — Repeated Failure Pattern
**Purpose:** test whether repeated failures become a recognizable pattern.  
**Input:** repeated tasks producing the same failure category.  
**Expected:** Experience core records recurrence and Meta-learning can identify it.

#### S7 — Capability Adaptation
**Purpose:** distinguish adaptation from evolution.  
**Input:** a task where an existing capability can succeed after context/parameter changes.  
**Expected:** strategy or parameters change without creating/modifying a capability.

#### S8 — Capability Composition
**Purpose:** test whether multiple existing skills can be composed.  
**Input:** task requiring analysis followed by transformation/testing.  
**Expected:** an ordered multi-capability plan and successful result.

#### S9 — Cross-Project Capability Reuse
**Purpose:** test portability/reuse.  
**Input:** a learned/reusable capability applied to another controlled project.  
**Expected:** the capability is reused with necessary adaptation rather than regenerated unnecessarily.

#### S10 — Meta-Learning Strategy Switch
**Purpose:** test whether the system can change strategy after evidence of failure.  
**Input:** repeated task where the first strategy underperforms.  
**Expected:** later attempt selects a better strategy/capability sequence.

#### S11 — Single Capability Generation
**Purpose:** demonstrate structural self-growth.  
**Input:** repeated limitation not adequately handled by existing capabilities.  
**Expected:** Evolution core proposes a new executable capability candidate.

#### S12 — Generated Capability Reuse
**Purpose:** demonstrate that an evolved capability becomes useful after creation.  
**Input:** a later task matching the capability's learned failure pattern.  
**Expected:** existing generated capability is selected and reused.

#### S13 — Multiple Capability Generation
**Purpose:** test repeated evolution events.  
**Input:** multiple distinct recurring limitations.  
**Expected:** more than one capability candidate can be developed independently, with separate lineage.

#### S14 — Meta-Learning Improvement Measurement
**Purpose:** quantify improvement over repeated tasks.  
**Method:** compare early and later attempts using matched scenario families.  
**Expected evidence:** changed strategy selection and measurable outcome differences.

#### S15 — Experience Log Continuity
**Purpose:** verify that history affects subsequent turns/tasks.  
**Method:** complete a task, start a related follow-up or repeated task, inspect historical context.  
**Expected:** later reasoning can use prior stored outcomes rather than treating the task as completely new.

### C. Governance, verification and safe evolution

#### S16 — DNA Violation Rejection
**Purpose:** verify Software DNA is an absolute constraint boundary.  
**Input:** change that violates a defined DNA rule.  
**Expected:** rejected before deployment with an auditable reason.

#### S17 — Low-Risk Auto-Approval
**Purpose:** verify ordinary low-risk changes can pass governance efficiently.  
**Input:** low-risk repair/refactor within allowed rules.  
**Expected:** authorization without unnecessary escalation.

#### S18 — High-Risk Escalation
**Purpose:** verify risk-sensitive governance.  
**Input:** change classified as high risk.  
**Expected:** escalation/human approval requirement rather than silent execution.

#### S19 — Sandbox Validation — Success Path
**Purpose:** verify safe validation before deployment.  
**Input:** valid proposed change.  
**Expected:** isolated validation succeeds and evidence is recorded.

#### S20 — Sandbox Validation — Failure Path
**Purpose:** verify a bad proposal cannot silently reach execution.  
**Input:** intentionally regressive/unsafe change.  
**Expected:** validation rejects or blocks the change.

#### S21 — Rollback Execution
**Purpose:** verify recovery after a failed approved execution attempt.  
**Input:** change that becomes invalid after execution-stage checks.  
**Expected:** previous safe state can be restored and the recovery is recorded.

#### S22 — Governance Audit Trail
**Purpose:** verify explainability and traceability.  
**Input:** governed change.  
**Expected:** record contains request, decision, rationale, related capability and outcome.

#### S23 — Capability Retirement
**Purpose:** test capability lifecycle management.  
**Input:** inactive/unsafe/obsolete capability condition.  
**Expected:** capability can be retired without corrupting historical lineage.

#### S24 — Evolution Lineage Tracking
**Purpose:** prove that self-growth is traceable.  
**Input:** evolution-triggering failure pattern.  
**Expected lineage:** failure/task → experience → evolution proposal → capability candidate → verification → governance → registry.

#### S25 — Recovery from Failed Evolution
**Purpose:** verify that failed self-programming does not damage the active capability system.  
**Input:** evolution proposal that fails validation or governance.  
**Expected:** candidate is rejected/isolated, active capabilities remain intact, and failure becomes experience.

## Multi-turn conversational tests

The web interface is itself part of the coding-assistant evaluation. A multi-turn task should be tested like:

```text
Turn 1
User: Add input validation to this function.

Turn 2
User: Also reject negative values.

Turn 3
User: Now add tests for those cases.

Turn 4
User: The previous validation is too strict; allow zero.
```

For each turn record:

- current working source
- recent conversation context
- Brain intent/reasoning
- selected capabilities
- latest diff
- validation result
- Experience record
- whether the system correctly interpreted feedback relative to the prior turn

## Expected evidence for SPS behavior

A successful coding task alone is **not** sufficient evidence of self-programming. Evidence of SPS behavior requires an observable transition such as:

```text
repeated failure
      ↓
experience retained
      ↓
pattern recognized
      ↓
strategy adapted
      ↓
existing capabilities insufficient
      ↓
evolution proposal
      ↓
new capability candidate
      ↓
verification + governance
      ↓
capability registered
      ↓
later reuse
```

## Baseline discipline

The same scenario intent, source condition and expected behavior should be used across the comparison conditions wherever practical. Changes to model/provider, project, timeout or external conditions must be recorded because they can confound comparisons.

## Result artifacts

Each experiment should produce enough evidence to reconstruct what happened:

- input request
- source snapshot/hash
- Brain plan
- selected capability IDs
- capability results
- validation evidence
- governance decision
- execution result
- experience record
- evolution/lineage record when applicable
- final source/diff
- timing and retry metrics

The executable scenario definitions live in `evaluation/scenarios.py`. This document explains the experimental meaning of those scenarios.
