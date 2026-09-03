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
