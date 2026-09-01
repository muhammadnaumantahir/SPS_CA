# CAP-009 — Universal Parser

## Origin

Phase 4 evolution trial. Generated from three repeated parsing failures:
`task_010`, `task_015`, and `task_020`.

## Purpose

Provide a reusable parser that normalizes JSON, XML, CSV, and simple YAML input
into Python values.

## Entry points

- `universal_parser(data, format)` — direct parser API.
- `run(context)` — SPS-CA capability contract.

## Validation

The capability must pass its sandbox test suite with more than 80% coverage
before registration/promotion.

## Lineage

- Capability ID: `CAP-009`
- Version: `1.0.0`
- Origin: `phase_4_evolution_trial`
- Trigger: `repeated_parsing_failures`
- Trigger tasks: `task_010`, `task_015`, `task_020`
