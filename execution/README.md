# Execution Subsystem

Controlled execution services are separate from Layer 10 so the infrastructure can evolve independently.

- `tools/` — typed tool contracts
- `sandbox/` — isolation boundary
- `commands/` — command execution policies
- `processes/` — process lifecycle/state

Layer 10 coordinates execution decisions; governance and validation remain separate gates.