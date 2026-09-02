# CAP-001 — Prompt Processing

CAP-001 is the mandatory first stage of every user coding request.

It sends the request, target code, language and the active capability catalog to the local Ollama model. Ollama acts as the SPS-CA reasoning brain and returns an ordered JSON plan of capability IDs. The pipeline validates those IDs against an allowlist before any downstream capability runs.
