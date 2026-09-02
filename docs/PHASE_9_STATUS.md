# Phase 9 — Baseline Agent Implementation

**Status:** Implemented; CI verification tracked by GitHub Actions.

## Purpose

Phase 9 isolates the SPS-CA framework contribution by comparing it with two same-model internal baselines. The master plan defines Baseline A as a naive LLM and Baseline B as a tool-augmented coding agent without learning or capability generation.

## R9.1 — Baseline A

`baselines/baseline_a_naive_llm.py` implements `BaselineA_NaiveLLM` with the shared `process_request(user_request, project_context, project)` contract. It sends the request and project context directly to the supplied LLM and performs no tool calls, learning, adaptation, or capability generation.

## R9.2 — Baseline B

`baselines/baseline_b_coding_agent.py` implements `BaselineB_CodingAgent`. Its registry provides `analyze_code`, `syntax_check`, and `run_tests` tool boundaries before the LLM call. It deliberately has no capability registry, learning loop, or self-modification.

## R9.3 — Same local LLM

`baselines/local_llm.py` creates the baseline callable through the existing provider-neutral `LLMInterface`. The default model is `qwen2.5-coder:7b`, matching the master plan's experimental baseline model.

## R9.4 — Common interface

Both baselines return `BaselineResult` objects from `baselines/runner.py`. The record contains baseline ID, request, project, model, response, tool calls, retries, duration and test outcome fields, giving Phase 10 a common measurement surface.

## R9.5 — Execution framework

`evaluation/baselines/experiment_runner.py` loads JSON scenarios and executes the same scenarios through both baselines. Results are stored as JSONL via `ResultStore`. A smoke scenario set covers Python, Java and TypeScript target projects.

## Planned evaluation scale

The master plan calls for 25 scenarios × 3 projects for each of Baseline A, Baseline B and SPS-CA, totaling 225 executions.

## Verification

`.github/workflows/phase9-tests.yml` runs the baseline unit tests on Python 3.11. Phase 9 should only be tagged complete after that workflow succeeds. The Ollama-backed experiment runner is intentionally not invoked in CI because CI does not provide the local Ollama service/model; the real-model runs belong to the controlled Phase 10 experiment environment.
