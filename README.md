# SPS-CA — Self-Programming Code Assistant

SPS-CA is a self-programming coding assistant built around a ten-layer Self-Programming Software (SPS) architecture. The Brain is replaceable and separate from executable capabilities.

## Capabilities

The system starts with ten intent-specific canonical capabilities:

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

These are intent-specific. A code-change request is routed to the modification capability, while test generation is reserved for explicit test requests.

Generated capabilities use CAP-011 and above and retain their provenance and lineage.

## Brain routing

The Brain infers programming language from the prompt, source, and filename, classifies the user's intent, filters capability eligibility, and then plans the smallest suitable capability set. The result is checked again after model planning so a normal code request cannot accidentally become a test-generation task.

Example:

```text
User: Add input validation to this Python function.

Brain: language=python
       intent=code_modification

Capability: CAP-002 Code Modification
```

## Architecture

SPS-CA has ten canonical layers:

1. Software DNA
2. Governance
3. Cognitive
4. Knowledge
5. Experience
6. Meta-Learning
7. Adaptation
8. Evolution
9. Verification & Validation
10. Execution

The Brain is a separate intelligence service. The web application exposes the architecture, capabilities, conversations, feedback, trace data, and evolution history without changing the canonical layer model.

## Self-programming

SPS-CA can use observed failures and capability gaps as evidence for controlled self-programming. The system can diagnose a bounded problem, create a regression case, generate a candidate, check Software DNA and Governance, validate the candidate, and use Layer 10 for controlled execution with rollback support.

Generated capabilities are not treated as successful simply because they were created. Capability performance is measured from later real usage, so learning evidence remains tied to actual behavior.

Automatic evolution is deny-by-default. Explicitly enabled automation remains bounded by action limits, repository scope, Governance, validation, and rollback safeguards.

For controlled provider-backed self-programming, use `evaluation/live_self_programming.py` with the explicit confirmation flag and a temporary workspace.

## Web application

The browser UI is chat-first. Users can create, search, reopen, continue, and safely delete persistent conversations. Code can be pasted directly into a prompt or the working-code panel. Language detection, selected capabilities, trace information, and feedback are shown with each turn.

While Ollama is processing, the chat displays an activity timeline with the current step and elapsed time instead of leaving the interface looking frozen. The timeline describes the expected request pipeline and stays visibly active until the response returns.

## Documentation

- `docs/ARCHITECTURE.md` — system boundaries and request flow
- `docs/capabilities/CANONICAL_CAPABILITIES.md` — canonical capability contracts
- `docs/master.md` — research overview and SPS model
- `docs/scenarios.md` — evaluation scenarios
- `docs/PIPELINE.md` — request, feedback, learning, and self-programming flow
- `docs/SELF_PROGRAMMING.md` — controlled self-programming design and operating model
- `docs/WEB_UI_GUIDE.md` — browser workspace guide
- `SETUP.md` — local and Colab setup
- `REQUIREMENTS.md` — environment requirements

Runtime conversation and evolution state is not source-controlled.
