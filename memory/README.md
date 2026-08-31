# Runtime Memory and User Data

This boundary stores runtime state separately from SPS-CA implementation code.

- `conversations/` — user/agent chat histories
- `experiences/` — task outcomes and observations
- `memories/` — persisted learned knowledge
- `traces/` — append-oriented execution/event traces

User data must never be committed to Git. The application should support configurable storage roots and export/import for research experiments.