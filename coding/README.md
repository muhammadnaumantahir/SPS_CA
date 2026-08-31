# Coding Subsystem

Coding is separate from the SPS layers and provides repository intelligence and code manipulation services.

Planned boundaries:

- `repository/` — project discovery, indexing and dependency metadata
- `code_analysis/` — AST/symbol/search analysis
- `context/` — context assembly for model calls
- `generation/` — code-generation coordination
- `modification/` — controlled file/patch changes
- `git/` — local version-control operations

The subsystem serves the layers through explicit interfaces and does not own SPS learning or governance decisions.