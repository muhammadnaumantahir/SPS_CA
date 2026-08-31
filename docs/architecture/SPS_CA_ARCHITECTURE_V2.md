# SPS-CA Architecture v2

## 1. Purpose

SPS-CA is a research prototype for a governed self-programming coding assistant. The architecture separates SPS reasoning/evolution from coding infrastructure, model providers, user projects, persistent runtime data, UI, testing, and analytics.

## 2. Ten SPS layers

Each layer is a first-class package under `layers/` and owns its implementation and layer-local tests.

1. Software DNA — immutable constraints, invariants, seed rules.
2. Cognitive Core — task understanding, planning, decomposition, reasoning and context requests.
3. Experience — structured observations, outcomes and failures.
4. Meta-Learning — learns which strategies work under which conditions.
5. Adaptation — changes strategies/parameters based on evidence.
6. Validation — verifies proposed changes and generated capabilities.
7. Governance — policy, risk classification, approval and rejection decisions.
8. Evolution — proposes and develops new capabilities from repeated limitations.
9. Capability Registry — lifecycle, versions, dependencies and provenance.
10. Execution — controlled tools, processes, snapshots and rollback.

## 3. Cross-layer orchestration

Layers do not become tightly coupled by directly calling arbitrary implementation details. `core/` owns orchestration, state and event contracts.

Conceptual flow:

`Request → Cognition → Capability/Experience context → Adaptation → Governance → Execution → Validation → Experience/Trace → Learning/Evolution`

Failure creates a feedback loop rather than simply ending the task.

## 4. Model abstraction

`models/` is provider-neutral. SPS-CA talks to a model interface, not directly to Qwen or a cloud provider. Initial local deployment uses Ollama. Future adapters may support OpenAI, Anthropic and other providers.

Model/provider configuration must never require changes to the ten SPS layers.

## 5. Coding subsystem

`coding/` handles repository discovery, AST/symbol analysis, context assembly, code generation coordination, controlled modification and local Git operations. It supplies services to SPS layers but does not own governance or learning decisions.

## 6. User/project data isolation

`projects/` represents target projects. `memory/` and `data/` represent runtime information such as conversations, experiences, memories, traces, sessions and exports. Runtime user data must not be committed to Git.

A configurable external storage root should be supported later so the same SPS-CA installation can manage multiple projects/users.

## 7. Capability lifecycle and lineage

Every generated capability should have a stable ID and version and record provenance:

`Task/Failure → Experience → Pattern → Adaptation Proposal → Capability Candidate → Governance → Validation → Registry → Reuse`

Lineage records should include parent capabilities, triggering experience/task IDs, proposal IDs, model/provider metadata, validation evidence, versions and activation history.

## 8. Analytics and explainability

`analytics/` derives datasets from events, traces and capability metadata. It will support capability growth charts, capability genealogy graphs, task-to-capability lineage, model performance, validation/rollback statistics and evolution history.

The UI visualizes these datasets; the UI is not the system of record.

## 9. Testing separation

Layer-local tests live with each layer. Cross-layer, integration, system, scenario, baseline and benchmark tests live under `testing/`. Research evaluation remains reproducible and separate from production runtime code.

## 10. Security and governance boundary

User secrets, API keys and runtime project data are configuration/runtime concerns and must never be hard-coded or committed. Self-modification is proposed through the Evolution layer and cannot bypass Governance and Validation.

## 11. Thesis distinction

A conventional coding agent is primarily `Task → Model → Tools → Tests`.

SPS-CA adds persistent experience, strategy learning, adaptation, capability generation, capability lineage, governance, validation and an evolution feedback loop. The prototype should measure whether those additions improve repeat-task performance and capability reuse compared with baselines.
