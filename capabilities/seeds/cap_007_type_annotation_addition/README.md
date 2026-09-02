# CAP-007 — Type Annotation Addition

Finds missing Python parameter annotations and safely adds annotations when a literal default provides reliable type evidence (`int`, `float`, `str`, or `bool`).

Use `parameters['apply'] = true` to return modified source. Parameters without inferable types are reported without guessing.