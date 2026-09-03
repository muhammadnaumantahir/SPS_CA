# SPS-CA Request Pipeline

SPS-CA treats every request as one continuous flow from understanding the user's intent to returning a verified result and preserving evidence for future evolution.

## Canonical SPS flow

```text
                         USER
                          │
                 Prompt + Code/File
                          │
                          ▼
              CanonicalSPSPipeline
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
   SPS Architecture                    Brain boundary
        │                                   │
        ├─ L1 Software DNA                 │
        ├─ L2 Governance                   │
        ├─ L3 Cognitive ◄──────────── Brain │
        ├─ L4 Knowledge                    │
        ├─ L5 Experience                   │
        ├─ L6 Meta-Learning                │
        ├─ L7 Adaptation                   │
        ├─ L8 Evolution ──► Capability     │
        │                   reuse/create    │
        ├─ L9 Verification                 │
        └─ L10 Execution                   │
                          │
                          ▼
              Result + Modified Code
                          │
                          ▼
             Experience / Trace / Evidence
                          │
                          ▼
                  Future Evolution
```

The browser UI and evaluation runner use the same `CanonicalSPSPipeline`. The Brain is a replaceable reasoning boundary connected to the Cognitive layer; it is not a layer or capability.

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
Brain / Cognitive planning
        ↓
Knowledge + Experience + Meta-Learning + Adaptation context
        ↓
Layer-8 SPS Growth Decision
        ↓
Reuse / Adapt / Compose / Improve / Create / Defer
        ↓
Capability execution or governed growth
        ↓
Verification & Validation
        ↓
Governance / Software DNA / Execution
        ↓
Conversation + experience trace
```

The browser also shows this work as an activity timeline while the request is running, so a slow local model does not look like a frozen interface.

## Layer-8 SPS Growth Decision

Layer 8 is the decision-maker for structural self-growth. The decision is evidence-driven rather than disagreement-driven.

```text
Disagreement / Gap / Performance Signal
              ↓
       Experience Evidence
              ↓
    Meta-Learning Analysis
              ↓
     Brain + Cognitive Reasoning
              ↓
       SPS Growth Decision
              ↓
   ┌──────────┼───────────┐
   ↓          ↓           ↓
 Reuse      Adapt       Evolve
                          │
              ┌───────────┼───────────┐
              ↓           ↓           ↓
           Improve     Compose      Create
```

### Decision meanings

- **Reuse:** the existing capability is sufficient.
- **Adapt:** change runtime/context parameters without structural mutation.
- **Compose:** repeatedly useful combinations of existing capabilities become reusable composition.
- **Improve:** strengthen an existing capability rather than create a duplicate.
- **Create:** a genuine capability gap or persistent unmet pattern justifies structural growth.
- **Defer:** evidence is insufficient or the system should wait for more evidence.

### Critical invariant

> **DISAGREEMENT ≠ CAPABILITY CREATION**

A disagreement is recorded as evidence. It can contribute to a persistent-gap conclusion, but Layer 8 must consider the full evidence before choosing `create`. A single disagreement is never a direct capability-creation instruction.

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
       Growth Decision
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
SPS Growth Decision
    ↓
Reuse / Adapt / Compose / Improve / Create / Defer
    ↓
Verification + Governance
    ↓
Capability registry
```

Disagreement is evidence, not an automatic instruction to create a capability. The Layer-8 evidence ledger records the signal and `GrowthDecisionEngine` returns an auditable decision with a reason code, reasoning and evidence payload.
