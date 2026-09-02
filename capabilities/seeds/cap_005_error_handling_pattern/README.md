# CAP-005 — Error Handling Pattern

Scans Python ASTs for calls to commonly failure-prone operations such as `open`, numeric conversion, and `loads` that are not inside a `try` block.

The capability reports actionable findings but does not automatically introduce exception handling, avoiding semantic guesses about recovery behavior.