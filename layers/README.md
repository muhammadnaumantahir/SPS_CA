# SPS-CA Layers

The ten SPS layers are first-class modules. Each layer owns its implementation, models, interfaces, and layer-local tests.

## Layers

1. Software DNA — immutable constraints and seed rules
2. Cognitive Core — understanding, planning, decomposition, reasoning
3. Experience — structured task/outcome history
4. Meta-Learning — strategy effectiveness learning
5. Adaptation — strategy and parameter adaptation
6. Validation — testing and verification
7. Governance — risk, policy, approval gates
8. Evolution — capability development/self-programming
9. Capability Registry — versions, provenance, dependencies, lineage
10. Execution — controlled tools, processes, snapshots and rollback

Cross-layer orchestration belongs in `core/`; cross-layer tests belong in `testing/`.