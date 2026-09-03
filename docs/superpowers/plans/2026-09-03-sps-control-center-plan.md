# SPS-CA Control Center and Safe Chat Deletion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe persistent-chat deletion and a data-driven SPS Overview/control-center dashboard to the existing chat-first web UI.

**Architecture:** Keep `SpsAssistantService`, `SessionStore`, `EvolutionEvidenceStore`, and `architecture_manifest()` as the existing domain boundaries. Add one normalized `/api/dashboard` snapshot for the UI, implement deletion as a guarded sidebar action, and render the dashboard with dependency-free HTML/CSS/SVG in the existing vanilla frontend.

**Tech Stack:** Python 3.11 standard library; existing SPS-CA APIs and JSON runtime state; vanilla HTML/CSS/JavaScript.

**Spec:** `docs/superpowers/specs/2026-09-03-sps-control-center-design.md`

## Global Constraints

- Chat remains the primary workspace.
- Confirmation is mandatory before deleting a conversation.
- Only the requested session ID may be deleted.
- Dashboard counts are derived from live API data, never hard-coded.
- No new frontend dependency is introduced.
- Runtime session/evolution data stays out of source-controlled application state.

---

### Task 1: Dashboard API and regression tests

**Files:**
- Modify: `ui/web_app.py`
- Modify: `ui/tests/test_web_ui.py`
- Create: `ui/tests/test_web_api_contract.py`

**Interfaces:**
- Produce `dashboard_data() -> dict[str, Any]`.
- Produce `GET /api/dashboard` with `metrics`, `architecture`, `capabilities`, `evolution`, and `activity`.

- [ ] Add failing tests asserting metric keys and counts, architecture layer count, capability analytics inputs, evolution timeline ordering, and activity records with empty runtime state.
- [ ] Implement `dashboard_data()` from `sessions.list()`, `capability_directory()`, `evolution.list_events()`, and `architecture_manifest()`.
- [ ] Add `GET /api/dashboard` without changing existing endpoints.
- [ ] Run `python -m pytest ui/tests/test_web_api_contract.py -q` and verify the focused tests pass.
- [ ] Run existing `ui/tests/test_session_store.py` and `ui/tests/test_web_ui.py` and verify no regressions.

### Task 2: Safe chat deletion and chat insights

**Files:**
- Modify: `ui/web/app.js`
- Modify: `ui/web/index.html`
- Modify: `ui/web/styles.css`
- Modify: `ui/tests/test_web_api_contract.py`

**Interfaces:**
- `deleteSession(id)` confirms, calls `DELETE /api/sessions/{id}`, refreshes sidebar, and creates a new chat if the deleted ID was active.
- `renderChatInsights()` renders language, turns, capabilities used, evolution events, and working-code state.

- [ ] Add tests for DELETE success/404 contract and ensure the UI source contains a confirmation gate and active-session fallback path.
- [ ] Add a trash action to every session row that stops row-click propagation and confirms with the conversation title.
- [ ] On successful active deletion, create a new chat and switch to Chat; on non-active deletion, keep the current conversation untouched.
- [ ] Render chat insights from the loaded conversation/session metadata without blocking message submission.
- [ ] Run focused tests and syntax checks.

### Task 3: SPS Overview control center UI

**Files:**
- Modify: `ui/web/index.html`
- Modify: `ui/web/app.js`
- Modify: `ui/web/styles.css`
- Modify: `ui/tests/test_web_api_contract.py`

**Interfaces:**
- `switchView('overview')` loads `/api/dashboard` and renders the Overview.
- Dashboard renderer consumes the normalized snapshot from Task 1.

- [ ] Add Overview as the first secondary navigation item while leaving Chat active by default.
- [ ] Add metrics row: 10 Layers, 10 Core Capabilities, Active Capabilities, Conversations, Evolution Events.
- [ ] Add interactive architecture graph User → Brain → Capability Registry → ten layers → Execution; layer clicks reuse the existing detail drawer.
- [ ] Add capability analytics for Seed vs Generated, active/inactive, reuse counts, and most-used capabilities.
- [ ] Add evolution timeline visualization for disagreement → analysis → reuse/adapt/create/defer → validation.
- [ ] Add compact live activity feed derived from recent sessions/evolution events.
- [ ] Add responsive technical/futuristic styling with subtle connection animation and no flashy effects.
- [ ] Verify dashboard rendering functions with empty and populated API snapshots.

### Task 4: Full verification and repository cleanup

**Files:**
- Modify: `README.md` if the current UI/API documentation omits Overview/deletion behavior.

- [ ] Run `python -m pytest -q` for the full suite.
- [ ] Run `python -m compileall -q brain core capabilities layers ui`.
- [ ] Review the final diff for stale navigation references, accidental runtime JSON, secrets, and API compatibility.
- [ ] Confirm `main` contains the intended commits.
- [ ] Delete only `feature/canonical-capabilities` and `feature/chat-ui-evolution` if the available GitHub mutation surface supports remote ref deletion; otherwise leave refs untouched and report the connector limitation rather than using an unsafe workaround.
