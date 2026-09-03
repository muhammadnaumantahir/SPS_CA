# SPS-CA Architecture

SPS-CA separates ten SPS responsibilities from the replaceable AI Brain and the executable capability system.

## Ten-layer model

| # | Canonical layer | Primary runtime component(s) | Responsibility |
|---|---|---|---|
| L1 | Software DNA | `SoftwareDNA` | Absolute constraints, safety/meta-rules, final pre-execution check |
| L2 | Governance | `GovernanceGate` | Authorizes concrete changes and evolution actions |
| L3 | Cognitive | `CognitiveCore` + `Brain` | Request understanding, intent classification, reasoning and planning |
| L4 | Knowledge | `KnowledgeCore` | Structured, validated context supplied to reasoning |
| L5 | Experience | `ExperienceLog` + traces | Historical task outcomes, feedback and runtime evidence |
| L6 | Meta-Learning | `MetaLearner` + optimization services | Failure-pattern analysis and strategy improvement evidence |
| L7 | Adaptation | `Adaptation` | Context-dependent parameter changes and capability reuse checks |
| L8 | Evolution | `EvolutionEngine` + gap planner + registry | Structural self-growth, capability differentiation and governed capability creation |
| L9 | Verification & Validation | `Validator` | Sandbox tests and safety/performance validation |
| L10 | Execution | `ExecutionEngine` | Controlled real-world action, snapshots and rollback |

The canonical names are defined once in `layers/architecture.py`. The UI and runtime trace consume that vocabulary rather than maintaining a second layer list.

## Brain boundary

The Brain is a replaceable intelligence service. It is not a layer and is not a `CAP-NNN`. It supports the Cognitive layer with prompt understanding, language/intent inference, reasoning and planning. The Brain must never directly execute a user project or silently bypass a capability, validation, governance, DNA or execution boundary.

Current local development uses Ollama-backed models, but the architecture keeps the provider replaceable.

## Capability boundary

Capabilities are executable skills stored in the Capability Registry. The Brain/Cognitive layer selects capabilities; capabilities do not become the Brain, and the Brain is not registered as a capability.

Stage-0 contains the ten canonical capabilities. Generated capabilities extend the portfolio using CAP-011 and above while retaining provenance, lineage, versioning and test evidence.

## Canonical user-to-execution flow

```text
USER
  │
  │ prompt + source code / uploaded file + language
  ▼
CanonicalSPSPipeline
  │
  ├─ L1  Software DNA
  │       request/scope constraints
  │
  ├─ L2  Governance context
  │       change/evolution policy context
  │
  ├─ L3  Cognitive + Brain
  │       understand → classify → reason → plan
  │
  ├─ L4  Knowledge
  │       validated structured context
  │
  ├─ L5  Experience
  │       prior outcomes + feedback evidence
  │
  ├─ L6  Meta-Learning
  │       recurring-failure / strategy evidence
  │
  ├─ L7  Adaptation
  │       context-specific parameters/reuse
  │
  ├─ L8  Evolution
  │       reuse capability OR governed gap generation
  │
  ├─ L9  Verification & Validation
  │       sandbox validation
  │
  ├─ L2  Governance authorization
  │       authorize concrete change
  │
  ├─ L1  Software DNA final gate
  │       independent final safety check
  │
  └─ L10 Execution
          apply approved change + rollback snapshot
  │
  ▼
result + modified source + layer trace + capability provenance
  │
  ▼
Experience / trace / evolution evidence
```

L1 and L2 can be revisited at the concrete-change boundary because the final affected files, validation state and governance decision are only known after capability execution. These are revisits of the same canonical layers, not additional SPS layers.

## Canonical implementation boundary

`core/canonical_sps_pipeline.py` is the presentation-independent orchestration entry point. It delegates actual controlled changes to `ui/sps_execution.py` and enriches the response with canonical ten-layer/component evidence.

The browser UI and `evaluation/scenario_runner.py` both use this entry point. This is the important architectural rule: **UI behavior and research evaluation must not maintain separate implementations of the SPS execution flow.**

## Result/trace contract

A canonical pipeline result may contain:

```text
brain
pipeline.layers[]
capability_id
success
validation
governance
dna
execution
modified_code
scenario_id
```

Each layer trace entry contains its canonical number/name, status, responsible component, evidence artifact, and human-readable detail. Downstream layers are reported as `not_reached` when an earlier hard gate blocks the request; the trace must not claim work that did not happen.

## Feedback and evolution

Expected-result evaluation is separate from the execution mechanism. A scenario's `agree` or `disagree` is recorded after the actual run. `disagree` creates Layer-8 evidence; it does not mean an immediate capability is created. Layer 8 analyzes recurring evidence and only a governed `create` decision proceeds to capability generation/testing/registration.

```text
Actual result
   ↓
Expected match
   ├─ agree ──────► Experience evidence
   └─ disagree ──► Evolution evidence
                         ↓
                      analyze()
                         ↓
                create decision?
                   ├─ no → retain/reuse
                   └─ yes → generate → test → govern → register
```

## UI responsibilities

The browser UI is presentation and observability. It collects the user's prompt/code/file, invokes `CanonicalSPSPipeline`, shows Brain metadata and the selected/generated capability, renders the canonical ten-layer trace, and exposes persisted capability/evolution history. It does not implement a second capability-selection or execution engine.

## Evaluation responsibilities

`testing/test_sps_scenarios.py` is the deterministic 500-case language/intent contract. `evaluation/scenario_runner.py --live-evolve` is the model-backed execution experiment and uses the same `CanonicalSPSPipeline` as the UI.

## Repository boundaries

- `brain/` — replaceable intelligence and planning
- `capabilities/` — canonical and generated executable skills
- `layers/` — SPS architectural responsibilities
- `core/` — canonical orchestration, conversation and supporting services
- `validation/`, `governance/`, `execution/` — controlled infrastructure
- `ui/` — presentation plus the controlled execution adapter used by the canonical pipeline
- `docs/` — research and implementation documentation
