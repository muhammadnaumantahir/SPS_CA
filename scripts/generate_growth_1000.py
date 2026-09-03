from pathlib import Path
import json

OUT = Path("evaluation/scenarios/growth_1000.json")

CANONICAL_CODE = {
    "code_generation": "",
    "code_modification": "def calculate(value):\n    return value * 2\n",
    "analysis": "def process(items):\n    return [x * 2 for x in items]\n",
    "bug_diagnosis": "def divide(a, b):\n    return a / b\n",
    "bug_fixing": "def divide(a, b):\n    return a / b\n",
    "refactoring": "def build_name(first, last):\n    name = first + ' ' + last\n    return name.strip()\n",
    "test_generation": "def add(a, b):\n    return a + b\n",
    "documentation": "def add(a, b):\n    return a + b\n",
    "validation": "def add(a, b):\n    return a + b\n",
    "project_operations": "",
}

CANONICAL_TEMPLATES = {
    "CAP-001": ("code_generation", "Create a Python function for {domain} that supports {feature}."),
    "CAP-002": ("code_modification", "Modify this Python function to add {feature} for {domain} while preserving its existing behavior."),
    "CAP-003": ("analysis", "Analyze this Python code for {domain}, focusing on {feature}."),
    "CAP-004": ("bug_diagnosis", "Diagnose the {feature} problem in this Python code for {domain} and explain the root cause."),
    "CAP-005": ("bug_fixing", "Fix the {feature} problem in this Python code for {domain} and return the corrected source."),
    "CAP-006": ("refactoring", "Refactor this Python code for {domain} to improve {feature} without changing public behavior."),
    "CAP-007": ("test_generation", "Generate Python tests for {domain} covering {feature}."),
    "CAP-008": ("documentation", "Document this Python function for {domain} with a {feature}."),
    "CAP-009": ("validation", "Validate this Python code for {domain}, focusing on {feature}."),
    "CAP-010": ("project_operations", "Perform the project operation to support {feature} in the {domain} project."),
}

DOMAINS = [
    "payments", "inventory", "customer profiles", "file processing", "reporting",
    "notifications", "authentication", "analytics", "scheduling", "data import",
]

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

EVOLUTION_DOMAINS = DOMAINS

EVOLUTION_VARIANTS = {
    "create": [
        ("CSV schema inference", "The current capability catalog cannot infer column types from inconsistent CSV files.", "Build a reusable Python capability that infers CSV schemas from sampled rows."),
        ("log redaction", "Existing logging capabilities do not consistently redact secrets and personal identifiers before persistence.", "Create a reusable Python capability that redacts configured sensitive fields before logging."),
        ("rate-limit analysis", "The current catalog can modify code but lacks a reusable capability for estimating API rate-limit pressure from call patterns.", "Create a reusable Python capability that analyzes request traces and estimates rate-limit pressure."),
        ("dependency graphing", "No existing capability builds a dependency graph from Python imports and reports cycles.", "Create a reusable Python capability that builds an import dependency graph and identifies cycles."),
        ("config migration", "The system lacks a capability for transforming legacy configuration keys into a new schema while reporting unmapped keys.", "Create a reusable Python capability that migrates legacy configuration dictionaries to a target schema."),
    ],
    "improve": [
        ("faster schema inspection", "An existing generated schema-inspection capability works but is too slow on large samples.", "Improve the existing schema-inspection capability to reduce runtime while preserving its public behavior."),
        ("stronger input checks", "An existing generated validation capability accepts ambiguous numeric strings that should be rejected.", "Improve the existing validation capability so its input checks are stricter without breaking valid inputs."),
        ("better diagnostics", "An existing generated diagnosis capability produces useful findings but weak root-cause evidence.", "Improve the existing diagnosis capability to produce more precise evidence and failure explanations."),
        ("lower memory usage", "An existing generated parser loads all records into memory even when streaming is possible.", "Improve the existing parser capability to support bounded memory usage."),
        ("clearer errors", "An existing generated conversion capability returns vague error messages for malformed records.", "Improve the existing conversion capability with actionable error reporting."),
    ],
    "adapt": [
        ("streaming input", "The current approach assumes an in-memory list, but production input now arrives as an iterator.", "Adapt the execution approach so the capability can process iterators without materializing the full dataset."),
        ("schema drift", "Input fields can change between deployments and the previous fixed-schema approach now fails.", "Adapt the approach to tolerate documented schema drift while preserving required fields."),
        ("large payloads", "The current strategy times out on very large payloads even though the same transformation is valid in chunks.", "Adapt execution to use chunked processing for large payloads."),
        ("partial failures", "The current all-or-nothing approach stops useful work when a small subset of records is malformed.", "Adapt the approach to isolate malformed records and continue safely."),
        ("missing dependency", "The preferred library is unavailable in the target runtime, so the current implementation cannot execute.", "Adapt the implementation to use available standard-library primitives while preserving behavior."),
    ],
    "replan": [
        ("failed first fix", "The attempted bug fix passed static checks but the defect remains under the failing scenario.", "Replan from the current code and observations using evidence from the failed attempt."),
        ("validator rejection", "The planned change was rejected by governance because its side effects exceeded the allowed risk.", "Replan with a lower-risk implementation that satisfies the original goal."),
        ("capability unavailable", "The selected capability is inactive and no longer eligible for the target language.", "Replan using another eligible capability or identify a capability gap."),
        ("wrong assumption", "Execution evidence contradicts a key assumption made by the first plan.", "Discard the invalid assumption and produce a new evidence-based plan."),
        ("incomplete result", "The first task succeeded but the overall user goal is not yet satisfied.", "Replan the remaining work rather than declaring success."),
    ],
    "compose": [
        ("analysis then fix", "The user needs diagnosis and repair as two dependent actions, and the repair depends on analysis findings.", "Compose analysis and bug-fixing capabilities into an ordered dependency chain."),
        ("generate then validate", "The user needs new source and then an explicit validation step.", "Compose code generation and validation into an ordered chain."),
        ("modify then review", "The user asks for a code change followed by an explicit correctness review.", "Compose code modification and validation as separate ordered actions."),
        ("fix then document", "The user wants an existing bug repaired and the resulting behavior documented.", "Compose bug fixing and documentation into a dependency-aware chain."),
        ("reuse multiple skills", "The goal can be satisfied by combining two existing capabilities without creating anything new.", "Compose the smallest set of existing capabilities that together satisfy the goal."),
    ],
}

EVOLUTION_STRATEGIES = ["create", "improve", "adapt", "replan", "compose"]


def canonical_scenarios():
    scenarios = []
    for capability_id, (intent, template) in CANONICAL_TEMPLATES.items():
        for domain in DOMAINS:
            for feature_index, feature in enumerate(FEATURES[capability_id]):
                number = len(scenarios) + 1
                feedback = "disagree" if feature_index == 4 else "agree"
                scenarios.append({
                    "id": f"additional-{number:03d}",
                    "scenario_type": "capability_routing",
                    "request": template.format(domain=domain, feature=feature),
                    "code": CANONICAL_CODE[intent],
                    "language": "python",
                    "filename": "main.py",
                    "expected": {"intent": intent, "capability_id": capability_id, "status": "success", "output_required": intent in {"code_generation", "code_modification", "bug_fixing", "test_generation"}},
                    "feedback": feedback,
                })
    return scenarios


def evolution_scenarios():
    scenarios = []
    local = 0
    for strategy in EVOLUTION_STRATEGIES:
        for domain in EVOLUTION_DOMAINS:
            for variant_index, (gap_name, evidence, action) in enumerate(EVOLUTION_VARIANTS[strategy]):
                local += 1
                request = {
                    "create": f"The existing catalog cannot satisfy this requirement for {domain}: {gap_name}. {action}",
                    "improve": f"For {domain}, an existing generated capability has this weakness: {gap_name}. {action}",
                    "adapt": f"For {domain}, execution evidence shows this environmental mismatch: {gap_name}. {action}",
                    "replan": f"For {domain}, the current attempt is not sufficient. {gap_name}. {action}",
                    "compose": f"For {domain}, the goal explicitly requires coordinated work. {gap_name}. {action}",
                }[strategy]
                scenarios.append({
                    "id": f"evolution-{local:03d}",
                    "scenario_type": "autonomous_evolution",
                    "request": request,
                    "code": "def process(value):\n    return value\n",
                    "language": "python",
                    "filename": "main.py",
                    "context": {
                        "domain": domain,
                        "gap_name": gap_name,
                        "evidence": evidence,
                        "available_capabilities": [f"CAP-{i:03d}" for i in range(1, 11)],
                        "generated_capabilities": [],
                    },
                    "expected": {
                        "strategy": strategy,
                        "evolution_required": strategy in {"create", "improve", "adapt", "replan"},
                        "capability_creation_expected": strategy == "create",
                        "capability_mutation_expected": strategy == "improve",
                        "execution_adaptation_expected": strategy == "adapt",
                        "replanning_expected": strategy == "replan",
                        "composition_expected": strategy == "compose",
                        "status": "success",
                        "output_required": True,
                    },
                    "feedback": "disagree" if variant_index == 4 else "agree",
                })
    assert len(scenarios) == 500
    return scenarios


scenarios = canonical_scenarios()
scenarios.extend(evolution_scenarios())
assert len(scenarios) == 1000
assert sum(s["scenario_type"] == "capability_routing" for s in scenarios) == 500
assert sum(s["scenario_type"] == "autonomous_evolution" for s in scenarios) == 500

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    "suite_id": "sps-ca-growth-1000",
    "description": "1000 growth scenarios: 500 canonical capability-routing cases plus 500 autonomous Brain evolution cases covering capability creation, improvement, adaptation, replanning, and composition.",
    "scenarios": scenarios,
}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"generated {OUT} with {len(scenarios)} scenarios")
