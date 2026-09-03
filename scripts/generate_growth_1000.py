from pathlib import Path
import json
from itertools import product

OUT = Path("evaluation/scenarios/growth_1000.json")
DOMAINS = ["payments", "inventory", "customer profiles", "file processing", "reporting", "notifications", "authentication", "analytics", "scheduling", "data import"]
CANONICAL = {
    "CAP-001": ("code_generation", "Create a Python function for {domain} that supports {feature}.", ""),
    "CAP-002": ("code_modification", "Modify this Python function to add {feature} for {domain} while preserving its existing behavior.", "def calculate(value):\n    return value * 2\n"),
    "CAP-003": ("analysis", "Analyze this Python code for {domain}, focusing on {feature}.", "def process(items):\n    return [x * 2 for x in items]\n"),
    "CAP-004": ("bug_diagnosis", "Diagnose the {feature} problem in this Python code for {domain} and explain the root cause.", "def divide(a, b):\n    return a / b\n"),
    "CAP-005": ("bug_fixing", "Fix the {feature} problem in this Python code for {domain} and return the corrected source.", "def divide(a, b):\n    return a / b\n"),
    "CAP-006": ("refactoring", "Refactor this Python code for {domain} to improve {feature} without changing public behavior.", "def build_name(first, last):\n    return (first + ' ' + last).strip()\n"),
    "CAP-007": ("test_generation", "Generate Python tests for {domain} covering {feature}.", "def add(a, b):\n    return a + b\n"),
    "CAP-008": ("documentation", "Document this Python function for {domain} with a {feature}.", "def add(a, b):\n    return a + b\n"),
    "CAP-009": ("validation", "Validate this Python code for {domain}, focusing on {feature}.", "def add(a, b):\n    return a + b\n"),
    "CAP-010": ("project_operations", "Perform the project operation to support {feature} in the {domain} project.", ""),
}
FEATURES = {
    "CAP-001": ["validation", "logging", "caching", "pagination", "error handling"],
    "CAP-002": ["input validation", "structured logging", "type annotations", "retry handling", "configuration support"],
    "CAP-003": ["time complexity", "space complexity", "edge cases", "error propagation", "performance"],
    "CAP-004": ["division-by-zero risk", "type errors", "boundary failures", "state corruption", "race conditions"],
    "CAP-005": ["division-by-zero bug", "type errors", "boundary failures", "state corruption", "race conditions"],
    "CAP-006": ["readability", "performance", "maintainability", "lower coupling", "lower complexity"],
    "CAP-007": ["typical inputs", "edge cases", "exceptions", "boundary values", "regression behavior"],
    "CAP-008": ["docstring", "usage example", "parameter reference", "error-handling note", "API reference"],
    "CAP-009": ["syntax correctness", "type consistency", "security risks", "resource cleanup", "production readiness"],
    "CAP-010": ["tests directory", "README", "CI configuration", "configuration directory", "documentation"],
}
EVOLUTION_VARIANTS = {
    "create": [
        ("CSV schema inference", "Infer column types from inconsistent CSV samples.", "Build a reusable capability for sampled CSV schema inference."),
        ("log redaction", "Sensitive values are inconsistently redacted before logging.", "Create a reusable capability that redacts configured sensitive fields."),
        ("rate-limit analysis", "No reusable capability estimates rate-limit pressure from traces.", "Create a capability that estimates rate-limit pressure from request traces."),
        ("dependency graphing", "No capability builds a Python import graph and detects cycles.", "Create a capability that builds an import dependency graph and finds cycles."),
        ("config migration", "Legacy configuration keys need migration with unmapped-key reporting.", "Create a capability that migrates configuration dictionaries to a target schema."),
    ],
    "improve": [
        ("faster schema inspection", "Existing generated schema inspection is slow on large samples.", "Improve schema inspection while preserving public behavior."),
        ("stronger input checks", "Existing generated validation accepts ambiguous numeric strings.", "Improve validation so ambiguous inputs are rejected without breaking valid inputs."),
        ("better diagnostics", "Existing diagnosis produces findings but weak root-cause evidence.", "Improve diagnosis with stronger evidence and explanations."),
        ("lower memory usage", "Existing parser materializes all records when streaming is possible.", "Improve the parser for bounded memory usage."),
        ("clearer errors", "Existing conversion errors are vague for malformed records.", "Improve error reporting with actionable diagnostics."),
    ],
    "adapt": [
        ("streaming input", "Production input now arrives as an iterator instead of a list.", "Adapt processing to handle iterators without materializing the dataset."),
        ("schema drift", "Input fields change between deployments and fixed-schema logic fails.", "Adapt the approach to tolerate documented schema drift."),
        ("large payloads", "Very large payloads time out even though the work can be chunked.", "Adapt execution to use chunked processing."),
        ("partial failures", "A small number of malformed records stops useful work.", "Adapt execution to isolate malformed records and continue safely."),
        ("missing dependency", "A preferred library is unavailable in the target runtime.", "Adapt the implementation to available standard-library primitives."),
    ],
    "replan": [
        ("failed first fix", "The first fix passed static checks but the defect remains.", "Replan from current code and evidence from the failed attempt."),
        ("validator rejection", "The planned change exceeded the permitted governance risk.", "Replan with a lower-risk implementation that still satisfies the goal."),
        ("capability unavailable", "The selected capability is inactive or ineligible for the target language.", "Replan with another eligible capability or identify a genuine gap."),
        ("wrong assumption", "Execution evidence contradicts a key assumption in the original plan.", "Discard the invalid assumption and build an evidence-based plan."),
        ("incomplete result", "A first task succeeded but the overall goal remains incomplete.", "Replan the remaining work instead of declaring success."),
    ],
    "compose": [
        ("analysis then fix", "Diagnosis must inform a dependent repair action.", "Compose analysis and bug-fixing capabilities as an ordered dependency chain."),
        ("generate then validate", "New source must be followed by an explicit validation action.", "Compose generation and validation as an ordered chain."),
        ("modify then review", "A code change must be followed by an explicit correctness review.", "Compose modification and validation as separate ordered actions."),
        ("fix then document", "The repaired behavior must also be documented.", "Compose bug fixing and documentation as a dependency-aware chain."),
        ("reuse multiple skills", "The goal can be satisfied by two existing capabilities.", "Compose the smallest existing capability set that satisfies the goal."),
    ],
}

def canonical_scenarios():
    scenarios = []
    for capability_id, (intent, template, code) in CANONICAL.items():
        for domain, feature in product(DOMAINS, FEATURES[capability_id]):
            n = len(scenarios) + 1
            scenarios.append({"id": f"additional-{n:03d}", "scenario_type": "capability_routing", "request": template.format(domain=domain, feature=feature), "code": code, "language": "python", "filename": "main.py", "expected": {"intent": intent, "capability_id": capability_id, "status": "success", "output_required": intent in {"code_generation", "code_modification", "bug_fixing", "test_generation"}}, "feedback": "disagree" if feature == FEATURES[capability_id][-1] else "agree"})
    assert len(scenarios) == 500
    return scenarios

def evolution_scenarios():
    scenarios = []
    local = 0
    for strategy, variants in EVOLUTION_VARIANTS.items():
        for round_index in range(2):
            for domain, (gap_name, evidence, action) in product(DOMAINS, variants):
                local += 1
                request = {"create": f"The existing catalog cannot satisfy this requirement for {domain}: {gap_name}. {action}", "improve": f"For {domain}, an existing generated capability has this weakness: {gap_name}. {action}", "adapt": f"For {domain}, execution evidence shows this environmental mismatch: {gap_name}. {action}", "replan": f"For {domain}, the current attempt is not sufficient: {gap_name}. {action}", "compose": f"For {domain}, the goal explicitly requires coordinated work: {gap_name}. {action}"}[strategy]
                scenarios.append({"id": f"evolution-{local:03d}", "scenario_type": "autonomous_evolution", "request": f"{request} Variation {round_index + 1}.", "code": "def process(value):\n    return value\n", "language": "python", "filename": "main.py", "context": {"domain": domain, "gap_name": gap_name, "evidence": evidence, "available_capabilities": [f"CAP-{i:03d}" for i in range(1, 11)], "generated_capabilities": []}, "expected": {"strategy": strategy, "evolution_required": strategy in {"create", "improve", "adapt", "replan"}, "capability_creation_expected": strategy == "create", "capability_mutation_expected": strategy == "improve", "execution_adaptation_expected": strategy == "adapt", "replanning_expected": strategy == "replan", "composition_expected": strategy == "compose", "status": "success", "output_required": True}, "feedback": "disagree" if round_index == 1 else "agree"})
    assert len(scenarios) == 500
    return scenarios

scenarios = canonical_scenarios() + evolution_scenarios()
assert len(scenarios) == 1000
assert len({s["id"] for s in scenarios}) == 1000
assert sum(s["scenario_type"] == "capability_routing" for s in scenarios) == 500
assert sum(s["scenario_type"] == "autonomous_evolution" for s in scenarios) == 500

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"suite_id": "sps-ca-growth-1000", "description": "1000 growth scenarios: 500 canonical routing cases plus 500 autonomous Brain evolution cases across create, improve, adapt, replan, and compose strategies.", "scenarios": scenarios}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"generated {OUT} with {len(scenarios)} scenarios")
