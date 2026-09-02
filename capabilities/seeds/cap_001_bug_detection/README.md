# CAP-001 — Simple Bug Detection

Detects a conservative set of high-confidence Python issues using the standard-library AST: bare `except`, mutable default arguments, and equality comparisons against `None`.

## Interface

`run(context: CapabilityContext) -> CapabilityResult`

The capability is analysis-only: findings are returned in `result.findings` and source code is never changed automatically.

## Safety

Syntax errors fail gracefully and unsupported languages return a successful capability result with an explanatory summary.
