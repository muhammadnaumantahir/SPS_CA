# Capability Guide

## Source of truth

`capabilities/registry.json` is the persistent capability catalogue. `capabilities/canonical.py` defines the canonical ten-capability vocabulary, while `capabilities/canonical_runtime.py` provides the executable dispatch for those ten IDs.

The Brain is outside this registry boundary.

## Canonical capabilities

| ID | Capability | Intent |
|---|---|---|
| CAP-001 | Code Generation | code_generation |
| CAP-002 | Code Modification | code_modification |
| CAP-003 | Code Explanation & Analysis | analysis |
| CAP-004 | Bug Detection & Diagnosis | bug_diagnosis |
| CAP-005 | Bug Fixing | bug_fixing |
| CAP-006 | Refactoring & Optimization | refactoring |
| CAP-007 | Test Generation | test_generation |
| CAP-008 | Documentation Generation | documentation |
| CAP-009 | Code Validation & Review | validation |
| CAP-010 | Project/File Operations | project_operations |

## Naming rules

Capability folders must not reuse numeric prefixes for unrelated behaviors. Canonical capabilities use their stable `CAP-xxx` identity. Retired compatibility implementations use descriptive semantic names so the repository cannot contain ambiguous folders such as two `cap_001_*` directories.

Generated capabilities use `capabilities/generated/` and receive a unique registry ID. Their provenance, tests, governance result and lifecycle status must be recorded.

## Reuse, adaptation and evolution

Capability selection is reasoning-driven. A matching name is not enough: SPS considers intent, language, risk, evidence, test coverage, prior reuse and environmental constraints.

The allowed growth strategies are:

- `reuse`: an existing capability is fit for the task.
- `adapt`: an existing capability needs controlled environmental adaptation.
- `improve`: an existing capability needs a governed improvement.
- `compose`: multiple capabilities together satisfy the task.
- `create`: evidence demonstrates a genuine reusable capability gap.
- `defer`: available evidence is insufficient or governance blocks mutation.

## Capability creation evidence

A new capability should have a traceable trigger and demonstrate that existing capabilities could not safely satisfy the requirement. The normal lifecycle is candidate design → generated source → generated tests → Software DNA validation → Governance approval → registration → later discovery/reuse.

## Registry invariants

Capability IDs are unique. Entry points must resolve to executable callables. Retired seeds are ignored by discovery. Generated capabilities remain distinct from built-in seeds. Reuse updates persistent usage history.
