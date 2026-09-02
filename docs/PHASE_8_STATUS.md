# Phase 8 — Target Projects

**Status:** Implemented; CI verification tracked by GitHub Actions.

## Requirements

| ID | Requirement | Status |
|---|---|---|
| R8.1 | Project A (Python/FastAPI) complete and runnable | Implemented |
| R8.2 | Project B (Java/Spring Boot) complete and runnable | Implemented |
| R8.3 | Project C (TypeScript/Express) complete and runnable | Implemented |
| R8.4 | Equivalent features/bugs across all three projects | Implemented |
| R8.5 | Automated project tests included for later coverage/evaluation | Implemented |

## Common benchmark surface

All three projects expose the same core Task API:

- `GET /health`
- `GET /tasks`
- `POST /tasks`
- `GET /tasks/{id}`
- `PUT /tasks/{id}`
- `DELETE /tasks/{id}`

All use an in-memory task store and reject empty titles. Each also contains the same intentionally seeded defect on `GET /tasks/{id}/exists`: it reports true whenever any task exists instead of checking the requested ID. The defect is documented in each project's `known_bug.md`.

## Rationale

The projects are intentionally small and dependency-light. They provide equivalent repair targets without coupling the research evaluation to a large production framework. The seeded defect gives later baseline/evaluation phases a repeatable failure-repair scenario.

## Verification

`.github/workflows/phase8-tests.yml` runs the Python, Java and TypeScript suites and a TypeScript build. A phase should be considered CI-verified only after the corresponding workflow run succeeds.
