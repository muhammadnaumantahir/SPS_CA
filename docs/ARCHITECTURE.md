# SPS-CA Architecture

SPS-CA separates ten SPS responsibilities from the replaceable AI Brain and the executable capability system. **The ten layer names are canonical and must not be renamed. New behavior is represented as sub-components.**

## Ten-layer model

| # | Canonical Layer Name | Primary runtime responsibility | Sub-components |
|---|---|---|---|
| L1 | **Software DNA Core** | Absolute constraints, safety/meta-rules and final pre-execution check | Goals, Policies, Constraints, Learning Rules, Repair Rules, Safety Rules, Ethical Rules, Evolution Rules, Meta-Rules |
| L2 | **Governance Core** | Authorizes concrete changes and evolution actions | Authorization, Evolution Approval, Compliance Checking, Risk Management |
| L3 | **Cognitive core** | Request understanding, intent classification, reasoning and planning | Goal Manager, Reasoning Engine, Planning Engine, Decision Engine, Explainability Engine |
| L4 | **Knowledge core** | Structured, validated context supplied to reasoning | Knowledge Base, Knowledge Acquisition Engine, Knowledge Validation, Knowledge Evolution |
| L5 | **Experience core** | Historical task outcomes, feedback and runtime evidence | Memory, Feedback, Monitoring, Learning Engine |
| L6 | **Meta-learning core** | Failure-pattern analysis and learning-strategy improvement | Learning Evaluation, Strategy Optimization, Learning Improvement |
| L7 | **Adaptation core** | Context-dependent behavior and capability reuse without source mutation | Context Awareness, Personalization, Capability Activation, Strategy Selection |
| L8 | **Evolution core** | Genuine structural self-growth and capability lifecycle decisions | Self-Modification, Self-Regeneration, Capability Preservation, Capability Differentiation, Capability Creation, **SPS Growth Decision** |
| L9 | **Verification & Validation Core** | Sandbox testing and safety/performance validation | Testing, Simulation, Safety Validation, Performance Validation |
| L10 | **Execution Core** | Controlled real-world action | Action Executor, Services, APIs, User Interaction |

The canonical machine-readable vocabulary is defined in `layers/architecture.py`. UI, tests, documentation and runtime traces must consume these exact names.

## Brain boundary

The Brain is a replaceable intelligence service. It is not a layer and is not a `CAP-NNN`. It supports the Cognitive core with prompt understanding, language/intent inference, reasoning and planning. The Brain must never directly execute a user project or silently bypass capability, validation, governance, DNA or execution boundaries.

Current local development uses Ollama-backed models, but the provider remains replaceable.

## Capability boundary

Capabilities are executable skills stored in the Capability Registry. The Brain/Cognitive core selects capabilities; capabilities do not become the Brain. Capability Registry and Capability Lineage are supporting subsystems, not additional architectural layers.

## Canonical user-to-execution flow

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
        ├─ L1 Software DNA Core             │
        ├─ L2 Governance Core               │
        ├─ L3 Cognitive core ◄────── Brain  │
        ├─ L4 Knowledge core                │
        ├─ L5 Experience core               │
        ├─ L6 Meta-learning core            │
        ├─ L7 Adaptation core               │
        ├─ L8 Evolution core ─► Capability  │
        │                    reuse/create   │
        ├─ L9 Verification & Validation Core│
        └─ L10 Execution Core               │
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

L1 and L2 can be revisited at the concrete-change boundary. These are revisits of the same canonical layers, not additional SPS layers.

## Layer-8 SPS Growth Decision

`SPS Growth Decision` is a **sub-component of Evolution core** and is the structural-growth decision-maker. Layer 8 must not use a rule such as `if disagreement >= N: create_capability()`.

The decision considers multiple evidence sources and chooses the least-structural action justified by the current state:

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
     ┌────────────┼─────────────┐
     ↓            ↓             ↓
   Reuse        Adapt         Evolve
                                │
                    ┌───────────┼───────────┐
                    ↓           ↓           ↓
                 Improve     Compose      Create
```

Supported decisions:

- `reuse` — an existing capability is sufficient.
- `adapt` — contextual/runtime adaptation is sufficient without structural growth.
- `compose` — an established combination of capabilities deserves reusable composition.
- `improve` — strengthen an existing capability rather than duplicate it.
- `create` — a genuine capability gap or persistent unmet pattern justifies structural growth.
- `defer` — evidence is insufficient or growth should wait.

### Critical invariant

> **DISAGREEMENT ≠ CAPABILITY CREATION**

A disagreement is experience evidence. Repeated disagreement may become evidence of a persistent capability gap, but Layer 8 still evaluates capability relevance, adaptation, composition and improvement before returning `create`. A single disagreement cannot directly create a capability.

A `create` decision then passes through Governance, candidate generation/testing, registry persistence and subsequent real-world evaluation. The decision, reason, reasoning and evidence are persisted for auditability.

## Canonical implementation boundary

`core/canonical_sps_pipeline.py` is the presentation-independent orchestration entry point. The browser UI and `evaluation/scenario_runner.py` both use this entry point, preventing separate execution semantics.

## Result/trace contract

A canonical pipeline result may contain:

```text
brain
pipeline.layers[]
pipeline.growth_decision
capability_id
success
validation
governance
dna
execution
modified_code
scenario_id
```

Each layer trace entry contains its canonical number/name, status, responsible component, evidence artifact and human-readable detail. Downstream layers are reported as `not_reached` when an earlier hard gate blocks the request; the trace must not claim work that did not happen.

## Feedback and evolution

Expected-result evaluation is separate from execution. `agree` or `disagree` is recorded after the actual run. `disagree` contributes Layer-8 evidence; it does not directly create a capability. `SPS Growth Decision` determines whether the evidence supports reuse, adaptation, composition, improvement, creation or deferral.

## UI and evaluation responsibilities

The browser UI is presentation and observability. It invokes `CanonicalSPSPipeline`, shows Brain metadata, capability provenance and the canonical ten-layer trace. `testing/test_sps_scenarios.py` provides deterministic routing/language coverage, while `evaluation/scenario_runner.py --live-evolve` exercises the same canonical path for model-backed experiments.

## Repository boundaries

- `brain/` — replaceable intelligence and planning
- `capabilities/` — canonical and generated executable skills
- `layers/` — SPS architectural responsibilities and canonical vocabulary
- `core/` — canonical orchestration and supporting services
- `validation/`, `governance/`, `execution/` — controlled infrastructure
- `ui/` — presentation and controlled execution adapter
- `docs/` — research and implementation documentation
