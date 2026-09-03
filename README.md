# SPS-CA — Self-Programming Code Assistant

SPS-CA is a research prototype that wraps a coding assistant in a ten-layer Self-Programming Software (SPS) architecture. The AI Brain is replaceable and separate from executable capabilities.

## Current baseline

The project now starts with exactly ten canonical capabilities:

1. **CAP-001 — Code Generation**
2. **CAP-002 — Code Modification**
3. **CAP-003 — Code Explanation & Analysis**
4. **CAP-004 — Bug Detection & Diagnosis**
5. **CAP-005 — Bug Fixing**
6. **CAP-006 — Refactoring & Optimization**
7. **CAP-007 — Test Generation**
8. **CAP-008 — Documentation Generation**
9. **CAP-009 — Code Validation & Review**
10. **CAP-010 — Project/File Operations**

These are intent-specific. A request to create code is routed to CAP-001, while CAP-007 is reserved for explicit test-generation requests.

## Brain routing

The Brain infers programming language from the prompt/code/filename and classifies the user's intent before selecting a capability. Capability eligibility is enforced both before and after LLM planning, preventing a plain creation request from becoming a test-generation task.

Example:

```text
User: Write Python code to add, subtract, multiply and divide numbers.
      First ask how many numbers.

Brain: language=python
       intent=code_generation

Capability: CAP-001 Code Generation
```

Generated/evolved capabilities begin at **CAP-011+** and preserve provenance and lineage. The earlier generated Parse Error Handler was migrated from historical CAP-010 to CAP-011.

## Architecture

SPS-CA has ten architectural layers: Software DNA, Governance, Cognitive, Knowledge, Experience, Meta-Learning, Adaptation, Evolution, Verification & Validation, and Execution. The Brain is a separate intelligence service. The Architecture view is the single UI surface for exploring these layers and their supporting components.

## Web dashboard

The browser UI is chat-first. Users can create, search, reopen, continue, and safely delete persistent conversations. Code can be pasted directly into a prompt or the collapsible working-code panel, and the UI reports Brain language inference and confidence.

The **Capabilities** view now contains the capability analysis panel, including seed vs generated population, active/inactive counts, reuse counts, and the most-reused capabilities. Individual capabilities remain clickable for provenance and lineage details. Architecture and Evolution remain separate detailed views.

Deleting a conversation requires explicit confirmation. The DELETE session API removes only the requested session; if the active conversation is deleted, the UI immediately creates and opens a fresh chat.

## Documentation

- `docs/ARCHITECTURE.md` — system boundaries and request flow
- `docs/capabilities/CANONICAL_CAPABILITIES.md` — ten capability contracts
- `docs/master.md` — research overview and SPS model
- `docs/scenarios.md` — evaluation scenarios
- `docs/PIPELINE.md` — request/feedback lifecycle
- `docs/superpowers/specs/2026-09-03-sps-control-center-design.md` — UI and deletion design
- `docs/superpowers/plans/2026-09-03-sps-control-center-plan.md` — implementation plan
- `SETUP.md` — local/Colab setup
- `REQUIREMENTS.md` — environment requirements

Runtime session/evolution state is not source-controlled.
