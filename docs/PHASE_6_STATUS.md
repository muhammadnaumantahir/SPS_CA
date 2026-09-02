# Phase 6 — Initial Capability Implementation

Status: **Implemented; CI verification pending**

## Scope

Phase 6 implements CAP-001 through CAP-008 as standalone capabilities using the shared `CapabilityContext` / `CapabilityResult` contract. The master plan requires each seed capability to have a capability module, tests, metadata, and documentation.

## Capability matrix

| ID | Capability | Behavior | Safe automatic change |
|---|---|---|---|
| CAP-001 | Simple Bug Detection | AST-based detection of high-confidence Python bug patterns | No |
| CAP-002 | Syntax Error Fix | Repairs recognized missing-colon syntax errors and reparses the result | Yes, narrowly |
| CAP-003 | Unit Test Generation | Generates executable pytest smoke tests when inputs/behavior are statically inferable | Yes, generated artifact |
| CAP-004 | Loop Optimization | Detects append-loop candidates and rewrites only identity append loops | Yes, narrowly |
| CAP-005 | Error Handling Pattern | Detects risky calls outside `try` blocks | No |
| CAP-006 | Unused Variable Removal | Detects unused assignments and removes literal-only assignments when requested | Yes, narrowly |
| CAP-007 | Type Annotation Addition | Infers parameter types from literal defaults and adds annotations when requested | Yes, narrowly |
| CAP-008 | Documentation Generation | Generates conservative docstring stubs from symbol/signature information | Yes, generated artifact |

## Registry

`capabilities/registry.json` now indexes CAP-001 through CAP-009. CAP-001–CAP-008 are seed capabilities; CAP-009 remains the Phase-4 generated capability.

## Safety boundary

The seed capabilities remain deliberately conservative. They do not invent semantics for ambiguous code. Transformations require either strong static evidence or `parameters["apply"] = true` where documented.

## Tests

`capabilities/tests/test_seed_capabilities.py` was expanded to assert executable generation/transformation behavior for the Phase-6 capabilities.

A GitHub Actions workflow was added at `.github/workflows/phase6-tests.yml` to run the seed suite. At the time this document was written, the repository's Actions API reported no workflow runs, so remote CI execution could not be independently confirmed.

## Acceptance state

- R6.1–R6.6: implementation, metadata, tests, registry registration, and per-capability documentation are present.
- Coverage >80%: **not claimed until an actual coverage run is available**.
- Phase-6 completion tag: **not created by the available GitHub connector**.
