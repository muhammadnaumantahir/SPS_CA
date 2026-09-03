# SPS-CA Self-Programming

SPS-CA can improve its own capability population and repair bounded internal defects while preserving the ten canonical layers and their responsibilities.

## Core loop

```text
Failure or capability gap
        ↓
Layer 08 Evolution diagnosis
        ↓
Evidence and regression case
        ↓
Candidate generation
        ↓
Software DNA check
        ↓
Governance decision
        ↓
Verification & Validation
        ↓
Layer 10 snapshot / execute / rollback
        ↓
Promote only when the change is valid
        ↓
Observe later real usage
        ↓
Experience + Meta-Learning
```

The model proposes. The SPS control path decides what is allowed, validates the proposed change, and controls mutation.

## Controlled repair

Internal repair is limited to a diagnosed file scope, a small number of candidate attempts, and a bounded number of edited files. Protected areas include Software DNA, Governance, audit and trace stores, regression records, snapshots, and runtime control state.

The candidate must stay inside the repository. Python candidates are syntax-checked before execution. Validation, Governance, sandbox, and rollback boundaries are required before a self-change can be executed.

Transient model, provider, or network failures are not treated as source defects. A slow Ollama response must not trigger autonomous source mutation.

## Capability growth

When repeated evidence shows that the current capability set cannot handle a useful task, Layer 08 can turn that gap into a `CapabilityPlan`. The controlled Evolution engine generates a capability, validates it, registers it only after the required checks, and preserves its provenance.

Generated capabilities use IDs beginning at `CAP-011`. The ten canonical capabilities remain protected and are never replaced by an automatically generated capability merely because a generated option exists.

## Learning from real behavior

Capability creation does not count as a successful capability use. Only subsequent real task outcomes become capability-performance evidence.

Layer 06 uses that evidence conservatively to recommend future routing changes, compare compatible alternatives, and identify generated capabilities that should eventually be retired. Retirement preserves history and is subject to Governance.

## Automatic evolution

Automatic Evolution is deny-by-default. The execution authority can be explicitly enabled for controlled environments and is still bounded by action limits and the same Evolution safety gates.

The provider-backed runner in `evaluation/live_self_programming.py` uses a temporary workspace and requires explicit confirmation. Its purpose is to demonstrate the complete real-provider path without silently changing the user's working repository.

## Runtime behavior

A successful source self-repair can request a controlled same-process restart when the application was launched through `ui/web_app.py`, allowing repaired Python modules to take effect. Restart can be disabled with `SPS_CA_DISABLE_RESTART=1`.

## Evidence and audit

Every meaningful self-programming decision should remain explainable through the stored trigger, evidence, candidate, validation result, Governance decision, execution outcome, and later real-use evidence.

This keeps self-programming observable and reversible instead of turning model output directly into uncontrolled source mutation.
