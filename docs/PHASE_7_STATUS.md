# Phase 7 — User Interface & Prompt-Based Interaction

**Status:** Implemented; CI verification pending/available through GitHub Actions.

## Requirements

| ID | Requirement | Status |
|---|---|---|
| R7.1 | CLI interface with prompt-based interaction | Implemented |
| R7.2 | `load`, `show`, `help`, `quit` commands | Implemented |
| R7.3 | User requests routed through Cognitive Core and downstream validation/governance/execution boundaries | Implemented for supported executable capability changes |
| R7.4 | Session history tracked in `ui/session_history.json` | Implemented |
| R7.5 | Response formatting is clear and actionable | Implemented |

## Interface

Entry point:

```bash
python ui/cli_interface.py
```

Commands:

```text
load <project_path>
show project
show registry
show experience
help
quit
```

Natural-language input is passed to the Cognitive Core for analysis and capability selection. When a selected capability produces a code modification, the interface validates it through Layer 6, requests a governance decision through Layer 7, and executes approved changes through Layer 10.

## Session History

The UI stores interaction events as JSON objects containing timestamp, event type, command, and response. The runtime file is intended to remain local/user-specific and should not be treated as SPS source data.

## Scope Boundary

Phase 7 is deliberately a simple prompt-based interface. Dashboards, visualization views, multi-user state, and the full research evaluation UI belong to later phases.

## Verification

The repository includes `.github/workflows/phase7-tests.yml`, which runs the CLI tests and verifies the documented direct entrypoint. Completion should be considered verified only when the corresponding GitHub Actions run is successful.
