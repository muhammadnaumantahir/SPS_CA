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

## Brain and SPS components

The **Brain is not an SPS layer and is not a capability**. It is a replaceable intelligence service used by the Cognitive layer for request understanding, intent classification, reasoning and planning support. The canonical architecture and supporting subsystem vocabulary live in `layers/architecture.py`.

The major runtime components are:

- **Brain** — replaceable reasoning/model boundary.
- **CognitiveCore** — structured task/code understanding and capability candidate selection.
- **KnowledgeCore** — validated structured context.
- **ExperienceLog** — historical task outcomes and feedback.
- **MetaLearner** — failure-pattern and strategy evidence analysis.
- **Adaptation** — context-dependent runtime parameter adjustment and capability reuse checks.
- **EvolutionEngine** — capability-gap analysis and governed capability generation.
- **Capability Registry** — canonical and generated capability metadata/lineage.
- **Validator** — sandboxed verification boundary.
- **GovernanceGate** — authorization boundary.
- **SoftwareDNA** — non-bypassable constraints and final safety check.
- **ExecutionEngine** — controlled action with snapshot/rollback support.

## Canonical user execution flow

The browser UI and the model-backed scenario runner now share one entry point: `CanonicalSPSPipeline`.

```text
USER
  │
  │ Prompt + code / uploaded file + language
  ▼
CanonicalSPSPipeline
  │
  ├── L1  Software DNA
  │       Hard/soft constraints and safety boundary
  │
  ├── L2  Governance
  │       Authorization context and change policy
  │
  ├── L3  Cognitive + Brain
  │       Understand → classify → reason → plan
  │
  ├── L4  Knowledge
  │       Build and validate structured context
  │
  ├── L5  Experience
  │       Read historical outcomes and reuse evidence
  │
  ├── L6  Meta-Learning
  │       Detect recurring failures / strategy evidence
  │
  ├── L7  Adaptation
  │       Adjust runtime behavior for current context
  │
  ├── L8  Evolution
  │       Reuse capability OR evaluate/generate a capability gap
  │
  ├── L9  Verification & Validation
  │       Sandbox tests and safety checks
  │
  ├── L2  Governance authorization
  │       Approve / reject the concrete change
  │
  ├── L1  Software DNA final check
  │       Final independent pre-execution gate
  │
  └── L10 Execution
          Apply change, record execution state and rollback snapshot

  ▼
Result + modified code + layer trace + Brain metadata + capability provenance
  │
  ▼
Experience / trace / evolution evidence for future turns
```

The architecture is intentionally represented as ten canonical responsibilities. Some control checks are revisited at the point where the concrete change becomes known; those repeated checks are still the same canonical layer, not additional layers.

## One canonical implementation path

`CanonicalSPSPipeline.run_submission()` is presentation-independent. The browser UI invokes it directly, and `evaluation/scenario_runner.py` invokes the same entry point for model-backed experiments. This prevents the dashboard and the research runner from exercising different capability-selection/execution semantics.

The pipeline result exposes a `pipeline` object containing all ten layers, the component responsible for that layer, current status, artifact/evidence, and an explanatory detail. The UI renders this information instead of maintaining a separate layer vocabulary.

## Feedback and capability growth

A scenario's `agree` or `disagree` is feedback evidence. `disagree` does **not** mean immediate capability creation. The evidence is passed to Layer 8, which analyzes recurring patterns and returns a governed decision. Only a `create` decision results in `record_creation()` and a generated capability.

```text
Actual result
     │
     ▼
Expected-result comparison
     │
     ├── agree ───────► Experience evidence
     │
     └── disagree ───► Layer-8 evidence store
                              │
                              ▼
                         analyze pattern
                              │
                     ┌────────┴────────┐
                     │                 │
                   reuse            create
                     │                 │
                     ▼                 ▼
                keep portfolio   generate → test → govern → register
```

Generated capabilities are not considered successful merely because they were created. Their quality is measured through subsequent real usage.

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

The canonical names, purposes and sub-components are defined once in `layers/architecture.py` and should be treated as the authoritative layer vocabulary.

## Self-programming

SPS-CA can use observed failures and capability gaps as evidence for controlled self-programming. The system can diagnose a bounded problem, create a regression case, generate a candidate, check Software DNA and Governance, validate the candidate, and use Layer 10 for controlled execution with rollback support.

Automatic evolution is deny-by-default. Explicitly enabled automation remains bounded by action limits, repository scope, Governance, validation, and rollback safeguards.

For controlled provider-backed self-programming, use `evaluation/live_self_programming.py` with the explicit confirmation flag and a temporary workspace.

## Web application

The browser UI is chat-first. Users can create, search, reopen, continue, and safely delete persistent conversations. Code can be pasted directly into a prompt or the working-code panel. The result view exposes the Brain boundary, selected/generated capability, validation/governance/DNA/execution state, and a ten-layer pipeline view. The Growth and Evolution tabs expose capability lineage and the persisted why/what/when/how evidence.

While Ollama is processing, the chat displays an activity timeline with the current step and elapsed time instead of leaving the interface looking frozen.

## Evaluation

There are two complementary measurements:

1. `testing/test_sps_scenarios.py` — deterministic 500-case routing/language contract (500 parametrized scenarios plus the suite-size assertion).
2. `evaluation/scenario_runner.py --live-evolve` — model-backed execution through the canonical SPS pipeline, expected-result matching, feedback recording, and Layer-8 evolution evidence.

The second measurement is the one that demonstrates the real user-to-execution path used by the UI.

## Documentation

- `docs/ARCHITECTURE.md` — system boundaries and canonical request flow
- `docs/capabilities/CANONICAL_CAPABILITIES.md` — canonical capability contracts
- `docs/master.md` — research overview and SPS model
- `docs/scenarios.md` — evaluation scenarios
- `docs/PIPELINE.md` — request, feedback, learning, and self-programming flow
- `docs/SELF_PROGRAMMING.md` — controlled self-programming design and operating model
- `docs/WEB_UI_GUIDE.md` — browser workspace guide
- `docs/superpowers/specs/2026-09-03-canonical-sps-pipeline-design.md` — canonical pipeline design
- `docs/superpowers/plans/2026-09-03-canonical-sps-pipeline.md` — implementation plan
- `SETUP.md` — local and Colab setup
- `REQUIREMENTS.md` — environment requirements

Runtime conversation and evolution state is not source-controlled.
