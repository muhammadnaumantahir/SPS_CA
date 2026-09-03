# SPS-CA Testing

Testing is separated from production implementation.

## Scenario suite

`test_sps_500_scenarios.py` is the single pytest entry point for scenario-level coverage. It expands `evaluation/scenarios/growth_500.json` into exactly **500 parametrized test cases** and validates language detection plus intent classification for every case.

The full model-backed scenario runner remains available through `evaluation/scenario_runner.py` for end-to-end/research runs.

## Code tests

Implementation and subsystem tests remain separate and are kept close to the code they verify under `core/`, `brain/`, `capabilities/`, `layers/`, `runtime/`, and `ui/`.

Layer-specific tests remain beside their layer under `layers/`.
