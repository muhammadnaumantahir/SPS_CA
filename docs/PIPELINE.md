# SPS-CA Request Pipeline

SPS-CA treats every request as one continuous flow from understanding the user's intent to returning a verified result.

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

The browser also shows this work as an activity timeline while the request is running, so a slow local model does not look like a frozen interface.

## Capability routing

The Brain never receives an unrestricted capability list for a clearly classified intent. The canonical planner filters the list first, and returned model steps are checked again after planning.

The key invariant is:

> A normal code request must not invoke CAP-007 Test Generation.

A request such as `add this function` is treated as code modification when source is present. Test Generation is selected only when the request explicitly asks for tests.

## Self-programming

```text
Observed failure or capability gap
              ↓
        Layer 08 Evolution
              ↓
     Diagnosis / capability plan
              ↓
        Regression evidence
              ↓
       Candidate generation
              ↓
     Software DNA boundary
              ↓
       Governance decision
              ↓
 Verification & Validation checks
              ↓
        Layer 10 execution
              ↓
       PASS → controlled promote
       FAIL → rollback + evidence
              ↓
       Real usage becomes evidence
              ↓
       Meta-learning improves routing
```

Self-programming is bounded to explicit repository scope. Protected Software DNA, Governance, audit/traces, and runtime state are outside autonomous repair. Candidates are validated before promotion, and failed changes are removed or rolled back rather than becoming active capability behavior.

Generated capability creation is not itself a performance success. Later real task outcomes are recorded as the evidence used for capability scoring, routing decisions, comparison, and retirement.

Provider and network failures are kept separate from source defects. A temporary Ollama outage or slow response does not cause autonomous source mutation.

## Feedback and learning

```text
User result
    ↓
Agreement / disagreement
    ↓
Experience evidence
    ↓
Meta-learning analysis
    ↓
Adaptation
    ↓
Reuse, switch, compare, or create
    ↓
Verification + Governance
    ↓
Capability registry
```

Disagreement is evidence, not an automatic instruction to create a capability. The system requires sufficient evidence before changing future routing, comparing alternatives, or retiring an underperforming generated capability.
