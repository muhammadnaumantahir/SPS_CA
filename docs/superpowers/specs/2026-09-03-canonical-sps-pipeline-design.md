# Canonical SPS Execution Pipeline Design

## Goal

Make the SPS-CA user workflow, model-backed scenario runner, and research documentation describe and exercise one canonical ten-layer SPS execution path.

## Design

The canonical entry point is the existing `SPSExecutionService.run_submission()` used by the browser UI. The scenario runner will call the same service rather than the older conversational-only path. `SPSScenarioService` remains responsible for analysis, capability search, and Layer-8 growth; `SPSExecutionService` remains responsible for controlled validation, governance, DNA, sandbox preparation, and execution.

The ten layers remain authoritative in `layers/architecture.py`. The UI must consume that manifest rather than maintaining a second layer list.

Each execution result will expose a `pipeline` object containing the canonical ten layers, component names, stage/status, and the major artifact produced at that boundary. The trace must distinguish an executed layer from a downstream layer that was not reached because an earlier gate blocked the request.

The Brain is explicitly represented as a replaceable supporting intelligence service inside the Cognitive layer. It is not a layer and is never registered as a capability.

## Canonical flow

User input -> Software DNA context -> Governance context -> Cognitive/Brain analysis -> Knowledge snapshot -> Experience evidence -> Meta-Learning decision -> Adaptation -> Evolution/capability selection or creation -> Validation -> Governance authorization -> final DNA check -> controlled Execution -> persisted Experience/trace.

The architecture documentation may group preparatory and control stages for readability, but the runtime trace must use the canonical layer numbers from `layers/architecture.py`.

## Evolution semantics

A user `disagree` is evidence. It is persisted and analyzed by Layer 8. Capability creation occurs only when the evolution evidence policy returns a `create` decision. Repeated disagreement is not itself sufficient unless the policy threshold is met.

## UI behavior

The user-facing result shows:

- Brain/provider/model and reasoning summary.
- Selected or generated capability and provenance.
- Ten numbered SPS layers with live status and component.
- Validation, governance, DNA, execution and rollback outcomes.
- Scenario/evolution trace with enough information to answer why, what, when and how.

## Compatibility

No new SPS layer is introduced. Capability IDs remain separate from the Brain. Existing generated capability lineage remains intact.
