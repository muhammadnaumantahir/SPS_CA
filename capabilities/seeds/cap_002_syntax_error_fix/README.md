# CAP-002 — Syntax Error Fix

Repairs a narrow class of common Python syntax errors: missing `:` on block headers such as `def`, `if`, `for`, `while`, `class`, and `try`.

## Interface

`run(context: CapabilityContext) -> CapabilityResult`

On a recognized error, `modified_code` contains the repaired source. The candidate is reparsed before being returned.

## Safety

Unrecognized syntax errors are reported instead of guessed at. Valid source is returned unchanged.