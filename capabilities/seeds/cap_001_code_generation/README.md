# CAP-001 — Code Generation

Creates new source code from an explicit natural-language requirement.

**Allowed intent:** `code_generation`.

**Not responsible for:** tests, bug diagnosis, bug fixing, or generic code review.

The capability may receive an empty working source. It returns the complete requested source and does not create tests unless the request explicitly includes them.
