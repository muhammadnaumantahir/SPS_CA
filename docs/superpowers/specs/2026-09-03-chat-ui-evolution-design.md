# SPS-CA Chat, Sessions, and Explainable Evolution Design

## Product goal

SPS-CA should behave like a normal modern coding chat: users can start a new conversation, return to old conversations, continue a previous thread, paste code directly into prompts, and see the system's reasoning/evolution evidence without being forced into forms or separate workflows.

## Approved UX

### Chat

The chat workspace is the default view. The left sidebar contains **New Chat**, conversation search, and saved recent chats. Each conversation has its own message history, current code context, filename, detected language, and model. Selecting an old chat reloads the complete saved thread and lets the user continue normally.

The composer accepts natural language and code together. Large code can also be placed in a collapsible code/context drawer. There is no user-selected programming-language control. Before execution, SPS-CA shows an `Auto · <language>` chip representing Brain inference from the code, request, filename, and conversation.

Assistant turns display the response, resulting code, capability used, inferred language, and a concise reasoning summary. Detail actions expose the layer trace, diff, and evolution evidence without cluttering the main conversation.

### Feedback and evolution

Every assistant turn can receive Agree or Disagree. Disagree is recorded as Experience evidence. It is **not** equivalent to "create a capability now". The system evaluates the pattern and chooses one of four decisions:

- `reuse`: an existing capability already covers the pattern;
- `adapt`: an existing capability can be adjusted without creating a new reusable skill;
- `create`: evidence justifies a new reusable capability;
- `defer`: evidence is insufficient or governance blocks creation.

When creation occurs, the user can inspect a creation record containing what was created, why it was created, when it was created, the parent capability, the evidence that triggered it, the Brain's reasoning summary, validation status, and its registry/lineage identity.

### Architecture and capabilities

Architecture exposes the ten canonical layers as an interactive flow, with Brain and supporting capability subsystems shown separately. Capabilities expose searchable cards and a detail view with origin, version, language support, reuse, validation, creation timestamp, failure pattern, trigger evidence, and lineage. Evolution exposes a chronological audit trail of disagreement, analysis, proposals, creation, validation, and reuse events.

## Data model

### Session

```text
id, title, created_at, updated_at
conversation: [{role, content}]
code, filename, detected_language, language_confidence, model
```

### Evolution event

```text
event_id, event_type, timestamp
session_id, turn_id, request
language, language_confidence
previous_capability_id
failure_pattern, evidence_summary
disagreement_count
decision: reuse | adapt | create | defer
reasoning
created_capability_id
validation_status
```

### Capability provenance

Generated capability metadata uses the existing registry format and adds:

```text
extra_metadata.provenance = {
  decision,
  created_at,
  parent_capability_id,
  trigger_event_ids,
  reasoning,
  evidence_summary,
  validation_status,
  source_request
}
```

## Technical boundaries

The Brain stays separate from capabilities and is used by the Cognitive layer. The existing `SpsAssistantService` remains the orchestration boundary. Session persistence is UI/runtime state and lives outside the capability registry. Evolution evidence lives with Layer 8 and feeds the registry only when the decision is `create`. All generated capabilities use the repository's existing `CapabilityContext` and `CapabilityResult` interface.

## Acceptance criteria

1. New Chat creates an isolated empty session.
2. Sent messages are persisted and appear in the sidebar after refresh.
3. Opening an old session restores its messages and working code context.
4. A user can continue an old session with a normal follow-up message.
5. A prompt containing Python/Java/JavaScript/TypeScript/Go/C# code results in automatic language identification without a manual language selection.
6. Language evidence and confidence are visible to the user after the Brain analyzes the turn.
7. Disagreement always creates an evidence record and a reasoning decision; it does not blindly create a capability.
8. When the decision is `create`, a generated capability is registered with provenance and lineage metadata.
9. The user can inspect why, how, when, and from what evidence a capability was created.
10. Existing architecture and capability concepts remain intact.
11. Runtime session/evolution data is not committed into source-controlled application state.
