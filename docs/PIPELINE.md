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

Phase 1 adds a second, internal loop for failures in SPS-CA itself while preserving the ten canonical layer names:

```text
Internal SPS failure
      ↓
Layer 08 Evolution: diagnosis
      ↓
Minimal repair candidate
      ↓
Layer 01 Software DNA
      ↓
Layer 02 Governance
      ↓
Layer 09 Verification & Validation
      ↓
Layer 10 Execution snapshot
      ↓
Tests / regression verification
   ↙                         ↘
FAIL                         PASS
 ↓                             ↓
Layer 10 rollback        Promote self-change
 ↓                             ↓
Regression evidence ←──── Experience history
```

A self-repair candidate is limited to explicitly diagnosed files, at most five edits, and at most three candidate attempts. The candidate cannot target Software DNA, Governance, audit/traces, or runtime state. Layer 1 must receive proof that validation, governance, sandbox execution, and rollback are established before the mutation can proceed. Layer 2 may require human review. Layer 10 owns the snapshot, execution, and rollback boundary.

The repair engine records a reproducible regression case before attempting mutation. Every failed attempt is retained; a successful repair marks the regression case resolved. Source code itself is not copied into the regression ledger.

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
