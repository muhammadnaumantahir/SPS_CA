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

## 1000-case growth + evolution proof

The repository includes an optimized 1000-case suite: 490 routing cases, 500 evolution-strategy contract cases, and 10 executable evolution-proof lifecycle cases. The proof cases verify persistent disagreement evidence → evolution analysis → actual `capability_created` evidence → generated capability registration → later-request discovery → reuse-count persistence. The scenario generator is `scripts/generate_growth_1000.py`, and the single pytest entry point is `testing/test_sps_scenarios.py`.

For Colab, open `notebooks/SPS_CA_optimized_1000_evolution.ipynb`. It contains one cell that executes the complete 1000-case suite and a separate evidence-summary cell.

## Brain boundary

The SPS-CA Brain is a separate replaceable model service. It is not a layer, not Layer 11, and not a capability.

See `docs/ARCHITECTURE.md` and `docs/PIPELINE.md` for the complete flow and `testing/README.md` for verification commands.
