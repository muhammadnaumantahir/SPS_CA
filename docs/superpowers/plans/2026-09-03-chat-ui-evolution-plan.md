# SPS-CA Chat UI + Explainable Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make SPS-CA feel like a normal persistent chat application while exposing Brain-based language detection, explainable capability evolution, and auditable capability lineage.

**Architecture:** Keep `SpsAssistantService` as the single execution path. Add a lightweight persistent conversation store behind `/api/sessions`, a Brain language-inference contract, and an Evolution evidence/proposal layer that records the reason for capability creation. Replace the presentation layer with a responsive chat-first UI while preserving Architecture and Capabilities data from the existing APIs.

**Tech Stack:** Python standard library HTTP server and JSON persistence; existing SPS-CA Brain/Ollama service; vanilla HTML/CSS/JavaScript.

**Spec:** `docs/superpowers/specs/2026-09-03-chat-ui-evolution-design.md`

## Global Constraints

- Chat is the primary workspace; Architecture, Capabilities, Evolution, and Guide remain discoverable.
- New chats are separate sessions and old sessions remain reopenable.
- Language is inferred from the prompt/code by the Brain; the user does not choose a language for execution.
- Disagreement is evidence for reasoning, not an unconditional command to create a capability.
- Capability creation requires an explicit evolution decision and records why/when/how/what was created.
- Existing Brain/capability/layer boundaries remain intact.

---

### Task 1: Persistent Chat Sessions

**Files:**
- Create: `ui/session_store.py`
- Modify: `ui/web_app.py`
- Test: `ui/tests/test_session_store.py`

**Interfaces:**
- `SessionStore.create(title="New chat") -> dict`
- `SessionStore.list() -> list[dict]`
- `SessionStore.get(session_id) -> dict | None`
- `SessionStore.save(session_id, conversation, code, filename, language, model) -> dict`
- `SessionStore.delete(session_id) -> bool`

- [ ] Add JSON-backed session persistence under `runtime/sessions.json` so runtime chat data is not mixed into source-controlled capability state.
- [ ] Add GET `/api/sessions` and GET `/api/sessions/{id}` plus POST `/api/sessions` and PUT `/api/sessions/{id}`.
- [ ] Make `/api/chat` accept `session_id`; when present, save the updated conversation and current code after a successful turn.
- [ ] Preserve recent conversation when reopening a chat; do not reuse one session's messages in another session.
- [ ] Write focused tests for create/list/get/save/delete and malformed/corrupt storage recovery.

---

### Task 2: Brain-Based Language Detection

**Files:**
- Modify: `brain/brain.py`
- Modify: `core/assistant_service.py`
- Test: `brain/tests/test_language_detection.py`

**Interfaces:**
- `Brain.detect_language(code: str, request: str, filename: str = "") -> tuple[str, float, str]`

- [ ] Add deterministic high-confidence heuristics for common languages first, using code syntax and filename as evidence.
- [ ] Add prompt wording to the Brain plan contract that the inferred language comes from the actual prompt/code and is not user-selected.
- [ ] Return detected language and confidence in `BrainPlan` and `AssistantTurn`.
- [ ] Use the detected language for Knowledge, Adaptation, capability execution, and UI display.
- [ ] Keep an `auto` fallback and never invent a language outside the supported SPS vocabulary.

---

### Task 3: Explainable Disagreement + Capability Evolution Evidence

**Files:**
- Create: `layers/layer_08_evolution/evolution_evidence.py`
- Modify: `ui/web_app.py`
- Modify: `layers/architecture.py`
- Test: `layers/layer_08_evolution/tests/test_evolution_evidence.py`

**Interfaces:**
- `EvolutionEvidenceStore.record_disagreement(...) -> dict`
- `EvolutionEvidenceStore.analyze(...) -> dict`
- `EvolutionEvidenceStore.record_creation(...) -> dict`
- `EvolutionEvidenceStore.list_events(limit=100) -> list[dict]`
- `EvolutionEvidenceStore.get_capability_lineage(capability_id) -> dict`

- [ ] Record the original request, detected language, previous capability, disagreement count, evidence references, timestamp, and Brain reasoning.
- [ ] Decide among `reuse`, `adapt`, `create`, or `defer` using evidence rather than automatically creating after a single disagreement.
- [ ] On `create`, register a real generated capability metadata object through the existing registry manager and write a generated executable entry point that follows the existing `CapabilityContext -> CapabilityResult` contract.
- [ ] Record parent capability, trigger events, creation reasoning, validation state, and timestamps in capability `extra_metadata` / lineage.
- [ ] Expose `/api/evolution`, `/api/evolution/{capability_id}`, and return an `evolution` object from feedback responses.

---

### Task 4: ChatGPT/Claude-Style UI

**Files:**
- Replace: `ui/web/index.html`
- Replace: `ui/web/app.js`
- Replace: `ui/web/styles.css`

**Interfaces:**
- Session sidebar actions call the session APIs from Task 1.
- Chat send includes `session_id`, request, inline/shared code, and model.
- Feedback buttons call `/api/feedback` and render the returned evolution decision/evidence.

- [ ] Make chat the default and visually dominant view.
- [ ] Add a persistent left conversation sidebar with New Chat, search, recent sessions, and selected-session state.
- [ ] Remove the manual language selector; show `Auto · Python` (or inferred result) after analysis.
- [ ] Let users paste code directly into the chat composer; retain a collapsible code/context drawer for larger code.
- [ ] Render assistant code, explanation, capability used, detected language, and reasoning summary inside the conversation.
- [ ] Add Disagree -> Evolution analysis UI with Create/Adapt/Reuse/Defer decision and the reason.
- [ ] Add Architecture, Capabilities, and Evolution pages with detail drawers/cards showing flow and lineage.
- [ ] Ensure responsive desktop/tablet/mobile layouts and keyboard-friendly chat submission.

---

### Task 5: Documentation + Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/PIPELINE.md`
- Create: `ui/tests/test_web_api_contract.py`

- [ ] Document session persistence, auto language detection, and explainable evolution.
- [ ] Add API contract tests for sessions, chat metadata, feedback evolution, and lineage payloads.
- [ ] Run the full Python test suite and targeted UI/API tests.
- [ ] Run syntax compilation for all changed Python files.
- [ ] Review the final diff for secrets, runtime data leakage, broken imports, and stale UI references.
