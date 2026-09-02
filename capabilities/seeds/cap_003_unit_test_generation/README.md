# CAP-003 — Unit Test Generation

Generates executable pytest smoke tests for simple top-level Python functions when safe representative inputs can be inferred from defaults or basic annotations.

## Interface

`run(context: CapabilityContext) -> CapabilityResult`

Generated tests are returned in `modified_code` and findings identify generated or unsupported cases.

## Safety

The generator does not invent behavior for complex or ambiguous signatures. It fails safely when no executable test can be inferred.