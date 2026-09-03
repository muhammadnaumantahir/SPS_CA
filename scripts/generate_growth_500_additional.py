from pathlib import Path
import json

OUT = Path("evaluation/scenarios/growth_500_additional.json")
CODE = {
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
TEMPLATES = {
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
DOMAINS = ["payments", "inventory", "customer profiles", "file processing", "reporting", "notifications", "authentication", "analytics", "scheduling", "data import"]
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
scenarios = []
for capability_id, (intent, template) in TEMPLATES.items():
    for domain in DOMAINS:
        for feature_index, feature in enumerate(FEATURES[capability_id]):
            number = len(scenarios) + 1
            feedback = "disagree" if feature_index == 4 else "agree"
            scenarios.append({
                "id": f"additional-{number:03d}",
                "request": template.format(domain=domain, feature=feature),
                "code": CODE[intent],
                "language": "python",
                "filename": "main.py",
                "expected": {"intent": intent, "capability_id": capability_id, "status": "success", "output_required": intent in {"code_generation", "code_modification", "bug_fixing", "test_generation"}},
                "feedback": feedback,
            })
assert len(scenarios) == 500
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"suite_id": "sps-ca-growth-500-additional", "description": "500 additional executable scenarios: 50 per canonical capability, varied by domain and concern, with repeated feedback evidence for Layer-8 growth decisions.", "scenarios": scenarios}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"generated {OUT} with {len(scenarios)} scenarios")
