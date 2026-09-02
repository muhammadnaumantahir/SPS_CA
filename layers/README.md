# SPS-CA Layers

The public SPS-CA architecture has **ten layers**. Use these names in the UI, documentation, experiments and trace output:

1. **Software DNA layer** — identity, invariants and constraints.
2. **Governance layer** — policy, risk and approval/rejection.
3. **Cognitive core** — prompt analysis, reasoning, planning and code context.
4. **Knowledge core** — structured code/capability/system knowledge.
5. **Experience core** — persistent outcomes, failures, successes and lessons.
6. **Meta-learning core** — learns which strategies work under which conditions.
7. **Adaptation core** — adjusts strategies and capability composition.
8. **Evolution core** — develops/improves reusable SPS capabilities.
9. **Verification & Validation** — correctness, tests, sandbox and evidence.
10. **Execution layer** — controlled application of approved operations.

## Brain boundary

The **Brain is separate from these ten layers**. It is a replaceable AI intelligence service, initially backed by Ollama through `models/`. It supports the Cognitive core with prompt understanding, reasoning, planning, code generation and debugging. It may also support Meta-learning, Adaptation and Evolution reasoning.

The Brain is **not** `CAP-001`, is not assigned a `CAP-NNN` identifier, and is not counted as layer 11.

## Capability boundary

Capabilities are executable SPS skills under `capabilities/`. They are selected/composed by the SPS process and may be seeded or generated. The Capability Registry and Capability Lineage are supporting subsystems, not additional architectural layers.

`layers/architecture.py` is the canonical machine-readable vocabulary for the ten public layer names.
