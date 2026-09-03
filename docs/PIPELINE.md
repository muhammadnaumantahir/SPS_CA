# Canonical SPS-CA Pipeline

`CanonicalSPSPipeline` is presentation-independent orchestration. User interaction, CLI and web UI feed the same SPS flow.

```text
USER
 │
 ├─ prompt
 ├─ code / file (optional)
 └─ feedback (optional)
 │
 ▼
CanonicalSPSPipeline
 │
 ├─ detect language + classify intent
 ├─ L1 Software DNA
 ├─ L2 Governance
 ├─ L3 Cognitive ↔ Brain
 ├─ L4 Knowledge
 ├─ L5 Experience
 ├─ L6 Meta-Learning
 ├─ L7 Adaptation
 ├─ L8 Evolution / SPS Growth Decision
 ├─ L9 Verification & Validation
 ├─ governance + DNA re-check
 └─ L10 Execution
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

## Growth decision

A disagreement becomes evidence. It is not converted directly into a new capability.

```text
                 SPS Growth Decision
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        Reuse          Adapt          Evolve
          │              │              │
          │              │       ┌──────┼──────┐
          │              │       ▼      ▼      ▼
          │              │    Improve Compose Create
```

The evolution path uses the evidence accumulated by Experience and Meta-Learning and the reasoning supplied by the Brain/Cognitive layer. The decision can also defer evolution when evidence is insufficient or governance disallows the proposed mutation.

## Request-to-result flow

1. The user provides a prompt and may attach or paste source code/file content.
2. SPS detects the language from the supplied code and/or prompt context.
3. Cognitive reasoning classifies the request and creates an execution plan.
4. Knowledge and the capability registry provide relevant project and capability context.
5. Meta-Learning scores available strategies and capability fitness.
6. Adaptation handles environmental constraints where needed.
7. Evolution decides whether to reuse, adapt, improve, compose, create or defer.
8. Verification validates the proposed result before execution.
9. Governance and Software DNA are checked again before mutation.
10. Execution applies only authorized changes and returns result plus evidence.
11. Experience records outcomes for later requests.

## Capability lifecycle

```text
request
  ↓
find candidate capability
  ↓
reason about fitness
  ├── reuse ───────────────► execute
  ├── adapt ───────────────► adapt strategy → verify → execute
  └── evolve
        ├── improve
        ├── compose
        └── create
                ↓
             generate
                ↓
             test
                ↓
          Software DNA check
                ↓
           Governance check
                ↓
             register
                ↓
             verify/reuse
```

Creation is persistent capability growth; execution of a one-off request is not automatically capability creation.

## Failure and feedback loop

```text
execution result
      ↓
  success? ── yes ──► experience → reuse evidence
      │
      no
      ↓
 disagreement / failure evidence
      ↓
 experience → meta-learning → cognitive reasoning
      ↓
 SPS Growth Decision
```

This loop is the mechanism by which the system can improve over time without treating every failed request as permission to mutate itself.
