# SPS-CA

SPS-CA is a self-programming coding assistant prototype organized around ten canonical SPS layers plus a separate Brain.

## Canonical architecture

1. Software DNA Core
2. Governance Core
3. Cognitive core
4. Knowledge core
5. Experience core
6. Meta-learning core
7. Adaptation core
8. Evolution core
9. Verification & Validation Core
10. Execution Core

The authoritative mapping, purposes, and implemented sub-components live in [`layers/architecture.py`](layers/architecture.py). The ten names are immutable architectural vocabulary.

## Sub-components

The layer packages now use explicit `*_core` directory names. Their sub-components correspond to implemented modules/classes: DNA policies and contracts, governance gates and risk assessment, cognitive reasoning and project analysis, knowledge snapshots and validation, experience logging and long-term learning, meta-learning/evaluation/strategy optimization, adaptation records, controlled evolution and SPS Growth Decision, validation/sandbox execution, and the execution engine.

## SPS Growth Decision

Layer 8 does not turn disagreement directly into a new capability. Evidence flows through Experience → Meta-learning → Brain/Cognitive reasoning → **SPS Growth Decision**, which can choose `reuse`, `adapt`, `compose`, `improve`, `create`, or `defer`.

## Brain boundary

The SPS-CA Brain is a separate replaceable model service. It is not a layer, not Layer 11, and not a capability.

See `docs/ARCHITECTURE.md` and `docs/PIPELINE.md` for the complete flow and `testing/README.md` for verification commands.
