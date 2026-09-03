# Canonical Pipeline

`CanonicalSPSPipeline` is presentation-independent orchestration.

```text
USER prompt + code/file + detected language
        ↓
L1 Software DNA Core
        ↓
L2 Governance Core
        ↓
L3 Cognitive core ↔ SPS-CA Brain
        ↓
L4 Knowledge core
        ↓
L5 Experience core
        ↓
L6 Meta-learning core
        ↓
L7 Adaptation core
        ↓
L8 Evolution core / SPS Growth Decision
        ↓
L9 Verification & Validation Core
        ↓
L2 Governance revisit + L1 DNA check
        ↓
L10 Execution Core
        ↓
result + modified code + trace/evidence
```

Layer terminology comes from `layers/architecture.py`; UI code must consume that manifest rather than maintain a second layer list.

## Growth decision

A disagreement is recorded as experience evidence. It is not itself a capability-creation command. The Evolution core evaluates evidence and selects reuse, adapt, compose, improve, create, or defer.
