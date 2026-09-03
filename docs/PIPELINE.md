# SPS-CA Request Pipeline

## Normal coding request

```text
User request + code
        ↓
Language inference
        ↓
Intent classification
        ↓
Capability eligibility filter
        ↓
Brain planning
        ↓
Knowledge + Experience + Meta-Learning + Adaptation context
        ↓
Canonical/generated capability execution
        ↓
Verification & Validation
        ↓
Governance / Execution
        ↓
Conversation + experience trace
```

## Capability routing rule

The Brain never receives an unrestricted capability list for a clearly classified intent. The canonical planner filters the list first. Returned model steps are checked again after planning.

The most important invariant is:

> A plain code-generation request must not invoke CAP-007 Test Generation.

## Phase 1 — controlled self-programming

Phase 1 adds an internal failure-repair loop while preserving the ten canonical layer names:

```text
Internal SPS failure
      ↓
Layer 08 Evolution: diagnosis
      ↓
Regression case created
      ↓
Minimal repair candidate
      ↓
Layer 01 Software DNA safety proof
      ↓
Layer 02 Governance approval
      ↓
Layer 09 Verification & Validation
      ↓
Layer 10 Execution snapshot/apply
      ↓
Tests + regression verification
   ↙                         ↘
FAIL                         PASS
 ↓                             ↓
Layer 10 rollback        Promote self-change
 ↓                             ↓
Preserve evidence ←──── Experience history
```

The web/application boundary now observes eligible internal failures and can invoke the controlled Layer 08 self-repair engine automatically. Provider/network/model-availability errors are excluded from autonomous mutation because they are normally transient infrastructure conditions. The repair scope is explicit and bounded; protected Software DNA, Governance, audit/traces, and runtime state remain outside autonomous repair.

Chat persistence uses detached turn metadata so a response payload cannot recursively contain itself. This prevents circular-reference serialization failures while retaining structured trace information for reopened conversations.

The repair engine is limited to explicitly diagnosed files, at most five edits, and at most three candidate attempts. Layer 1 verifies the required validation, governance, sandbox, and rollback boundaries before mutation. Layer 2 may require human review. Layer 10 owns snapshot, execution, and rollback.

## Feedback and evolution

```text
User disagreement
      ↓
Experience evidence
      ↓
Meta-learning analysis
      ↓
Adaptation decision
      ↓
Evolution reasoning
   ↙    ↓     ↘
reuse  adapt  create
              ↓
         verification
              ↓
          governance
              ↓
       generated CAP-011+
```

Disagreement is evidence, not an automatic instruction to create a capability.
