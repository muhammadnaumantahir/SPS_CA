# SPS-CA Control Center and Safe Chat Deletion Design

## Goal
Extend the existing chat-first SPS-CA web application with safe conversation deletion and an interactive SPS control-center dashboard, while preserving the existing Brain, capability, evolution, and session boundaries.

## Current baseline
`main` already contains persistent JSON-backed sessions, `DELETE /api/sessions/<id>`, automatic language detection, interactive Architecture/Capabilities/Evolution views, and explainable disagreement/evolution APIs. The remaining work is presentation and coverage: expose deletion safely in the sidebar, add a first-class Overview dashboard, and add regression tests for the new data/UI contracts.

## UX

### Conversation deletion
Each sidebar conversation row exposes a small trash action. Clicking it must stop propagation, ask for explicit confirmation containing the conversation title, and only then call `DELETE /api/sessions/<id>`. A successful delete removes the row immediately. If the deleted session is active, the client creates a fresh New chat and switches to Chat. A failed delete leaves the existing session untouched and reports the error.

### SPS Overview
Add an Overview/Control Center view without replacing Chat as the primary workspace. The Overview contains:

- metrics: 10 Layers, 10 Core Capabilities, Active Capabilities, Conversations, Evolution Events;
- architecture graph: User → Brain → Capability Registry → ten connected layers → Execution;
- capability analytics: Seed vs Generated, reuse counts, active/inactive state, most-used capabilities;
- evolution activity: chronological disagreement → analysis → reuse/adapt/create/defer → validation flow;
- live activity feed built from recent evolution events and recent session activity.

The graphs use lightweight inline SVG/CSS/HTML and no new frontend dependency. Clicking architecture nodes opens their existing detail drawer. Clicking capabilities opens existing capability provenance/lineage detail. The dashboard is data-driven from existing APIs rather than hard-coded counts.

### Chat insights
The Chat view gains a compact session summary below the conversation: detected language, turn count, capabilities used in the loaded conversation, evolution events, and working-code state. It is informational and must not interfere with message submission.

## Backend/data contract
Add `GET /api/dashboard` returning a normalized snapshot:

```text
metrics: {layers, core_capabilities, active_capabilities, conversations, evolution_events}
architecture: architecture_manifest()
capabilities: capability_directory()
evolution: recent events
activity: normalized recent session/evolution activity
```

The dashboard helper must tolerate empty runtime state and preserve deterministic ordering. Existing `/api/sessions`, `/api/architecture`, `/api/capabilities`, and `/api/evolution` remain backwards compatible.

## Safety and regression requirements

- Only the requested session ID is deleted.
- Deleting a nonexistent session returns HTTP 404.
- Confirmation is mandatory for UI deletion; no row click may trigger deletion.
- Runtime JSON remains outside source-controlled application state.
- Existing chat/session behavior, language detection, feedback/evolution, Architecture, Capabilities, and Evolution views remain functional.
- Tests cover session deletion, active-session fallback, nonexistent deletion, sidebar list consistency, dashboard metric shape, architecture data, capability analytics data, evolution timeline data, and existing chat/session regressions.

## Git cleanup
Delete only the already-merged remote branches `feature/canonical-capabilities` and `feature/chat-ui-evolution`; keep `main`. If the connected GitHub mutation surface cannot delete remote refs, do not substitute a destructive workaround; report that limitation explicitly.
