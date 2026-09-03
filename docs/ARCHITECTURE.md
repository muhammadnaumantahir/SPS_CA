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
| L8 | Evolution | `EvolutionEngine` + `GrowthDecisionEngine` + gap planner + registry | Reasoned structural self-growth and capability lifecycle decisions |
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

L1 and L2 can be revisited at the concrete-change boundary because the final affected files, validation state and governance decision are only known after capability analysis/execution. These are revisits of the same canonical layers, not additional SPS layers.

## Layer-8 SPS Growth Decision

Layer 8 is the structural-growth decision-maker. It must not implement `if disagreement >= N: create_capability()` logic. Instead, it evaluates evidence and chooses the least-structural action justified by the current state:

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

The supported decisions are:

- `reuse` — the existing capability is sufficient.
- `adapt` — context-specific behavior can solve the task without structural growth.
- `compose` — an established combination of capabilities deserves reusable composition.
- `improve` — an existing capability should be strengthened rather than duplicated.
- `create` — a genuine capability gap or persistent unmet pattern justifies structural growth.
- `defer` — evidence is insufficient or growth should wait.

### Disagreement invariant

**Disagreement is evidence, not a creation command.** A single disagreement never directly creates a capability. Repeated disagreement can become evidence of a persistent capability gap, but Layer 8 still considers adaptation, composition, improvement and existing capability relevance before returning `create`.

A `create` decision then passes through Governance, candidate generation/testing, registry persistence and subsequent real-world evaluation. The decision, reason code, reasoning and evidence are persisted for auditability.

## Canonical implementation boundary

`core/canonical_sps_pipeline.py` is the presentation-independent orchestration entry point. It delegates actual controlled changes to `ui/sps_execution.py` and enriches the response with canonical ten-layer/component evidence.

The browser UI and `evaluation/scenario_runner.py` both use this entry point. This is the important architectural rule: **UI behavior and research evaluation must not maintain separate implementations of the SPS execution flow.**

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

Each layer trace entry contains its canonical number/name, status, responsible component, evidence artifact, and human-readable detail. Downstream layers are reported as `not_reached` when an earlier hard gate blocks the request; the trace must not claim work that did not happen.

## Feedback and evolution

Expected-result evaluation is separate from the execution mechanism. A scenario's `agree` or `disagree` is recorded after the actual run. `disagree` creates Layer-8 evidence; it does not mean an immediate capability is created. The evidence is analyzed by `GrowthDecisionEngine`, and only a `create` decision proceeds to capability generation/testing/registration.

```text
Actual result
   ↓
Expected match
   ├─ agree ──────► Experience evidence
   └─ disagree ──► Evolution evidence
                         ↓
                  Growth Decision
                         ↓
          reuse / adapt / compose / improve
                         │
                         └──────── create?
                                  ↓
                         generate → test
                         → govern → register
```

## UI responsibilities

The browser UI is presentation and observability. It collects the user's prompt/code/file, invokes `CanonicalSPSPipeline`, shows Brain metadata and the selected/generated capability, renders the canonical ten-layer trace including the Layer-8 growth decision, and exposes persisted capability/evolution history. It does not implement a second capability-selection or execution engine.

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
