# Persistent Execution Experience Design

## Goal
Make execution history a first-class Layer 5 Experience sub-component shared by Web UI, CLI, and scenario evaluation so SPS remembers what it attempted, which capability it used, whether it succeeded/failed, and what feedback/evidence followed.

## Constraints
- Do not rename, add, remove, or reorder the canonical ten SPS layers.
- The Brain remains outside the ten-layer count.
- Extend existing Layer 5 Experience components; new files are sub-components of that layer.
- Scenario testing and Web UI must use the same experience recording contract.
- Disagreement remains evidence, not an automatic CREATE trigger.

## Design
1. Extend the Layer 5 `Task` model with execution provenance (`source`, `scenario_id`, `run_id`, `feedback`) and optional result metadata.
2. Add a small Layer 5 `ExecutionExperienceStore` sub-component that records completed attempts into the existing append-only ExperienceLog and can retrieve relevant historical attempts.
3. Instantiate the store from SPS execution services using a persistent default path under `experience/logs/`, so Web UI and scenario runs converge on the same memory.
4. Feed historical capability outcomes and scenario evidence into Layer 8 growth reasoning. Existing experience can lower capability fitness and increase recurrence/creation need; it does not bypass the growth decision.
5. Make `record_creation()` reject any analysis whose explicit growth decision is not `create`, preventing false-positive capability registration.
6. Make the 500 autonomous-evolution scenarios executable evidence cases: their declared context/evidence becomes input to the real Layer 8 decision rather than merely an assertion field.
7. Preserve existing trace/evolution ledgers; the new Experience memory is the durable task-outcome memory that can be consumed by later reasoning.

## Acceptance Criteria
- A Web UI execution persists a Layer 5 experience record containing request, capability, outcome, source and timestamp.
- A scenario execution persists the same shape with `source=scenario` and its scenario/run identifiers.
- Reloading a new `ExperienceLog` instance exposes prior executions.
- Historical failures/successes can be queried per capability and used by growth reasoning.
- `record_creation()` cannot create a capability from a `reuse`, `adapt`, `improve`, `compose`, or `defer` analysis.
- At least one supplied scenario can drive a genuine `create` decision from evidence, followed by registration and future reuse in an isolated test.
- Existing 1000-case suite remains exactly 1000 cases and uses `growth.json`.
- All repository tests relevant to these changes pass in CI.
