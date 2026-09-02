# SPS-CA UI

## Conversational web interface

Run:

```bash
python ui/web_app.py
```

Then open `http://127.0.0.1:8080`.

The top page is a coding-assistant chat. A session keeps:

- the current working source;
- recent user/assistant messages;
- Brain reasoning and selected capabilities;
- latest code diff and trace.

A user can provide feedback in a later message without restarting the task. For example:

```text
User: Add input validation.
SPS-CA: Done.
User: Also reject negative values.
SPS-CA: [reasons over the current code + prior turn]
User: Now add tests.
SPS-CA: [selects the testing capability]
```

The browser calls `/api/chat`, and the backend delegates the turn to `core/assistant_service.py`. The service builds Knowledge and Experience context, asks the separate Brain for a plan, executes active capabilities, returns the new working source, and records the turn as Experience evidence.

The UI also exposes the ten-layer architecture, optional sub-components, Brain boundary, capability registry, capability results, code/diff/trace and layer status. The UI is not the decision-maker.

## CLI

```bash
python ui/cli_interface.py
```

The CLI supports project loading, architecture inspection, Brain status, capability registry inspection, experience history and natural-language coding requests.

## Design boundary

```text
UI
 ↓
core/assistant_service.py
 ↓
Cognitive Layer ↔ Brain
 ↓
Knowledge / Experience / Meta-learning / Adaptation / Evolution context
 ↓
Capabilities
 ↓
Verification & Validation Layer
 ↓
Governance
 ↓
Execution
```

The browser does not silently mutate a user's local filesystem. Controlled project mutation remains an Execution-layer responsibility.
