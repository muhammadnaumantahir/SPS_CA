# SPS-CA Architecture

SPS-CA is organized around ten canonical SPS layers. The Brain is a separate model-backed reasoning boundary and is intentionally not counted as Layer 11.

## Layer manifest

The authoritative vocabulary is `layers/architecture.py`:

```text
L1  Software DNA Core
L2  Governance Core
L3  Cognitive Core
L4  Knowledge Core
L5  Experience Core
L6  Meta-Learning Core
L7  Adaptation Core
L8  Evolution Core
L9  Verification & Validation Core
L10 Execution Core
```

## System boundary

```text
                         USER
                          │
                 Prompt + Code/File
                          │
                          ▼
               CanonicalSPSPipeline
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      SPS Architecture          Brain boundary
             │                         │
             ├─ L1 Software DNA       │
             ├─ L2 Governance         │
             ├─ L3 Cognitive ◄──────── Brain
             ├─ L4 Knowledge          │
             ├─ L5 Experience         │
             ├─ L6 Meta-Learning      │
             ├─ L7 Adaptation         │
             ├─ L8 Evolution ──► Capability
             │                 reuse/create
             ├─ L9 Verification
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

## Architectural responsibilities

L1 defines system and capability contracts. L2 controls risk, authorization, policies and rollback. L3 interprets intent and coordinates reasoning with the Brain. L4 gathers project and code knowledge. L5 records experience and disagreement evidence. L6 evaluates capability fitness and strategy. L7 adapts behavior to environmental conditions. L8 performs the SPS Growth Decision and governed capability evolution. L9 validates outputs in controlled conditions. L10 applies authorized execution and file changes.

Supporting components such as the capability registry, lineage, provider abstraction, memory and sandbox support the layers; they do not create additional architectural layers.

## Brain boundary

The Brain is replaceable model infrastructure used for reasoning, prompt analysis, planning, strategy analysis and code-generation assistance. Its provider/model can change without redefining the SPS architecture. It is not a capability and it does not own capability registration.
