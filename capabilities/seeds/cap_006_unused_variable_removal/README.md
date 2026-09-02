# CAP-006 — Unused Variable Removal

Finds simple unused assignments inside Python functions. With `parameters['apply'] = true`, literal-only assignments can be removed safely.

Calls and other potentially side-effecting right-hand sides are never removed automatically.