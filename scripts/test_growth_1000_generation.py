from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GENERATOR = REPO / "scripts/generate_growth_1000.py"
SCENARIO_FILE = REPO / "evaluation/scenarios/growth_1000.json"


def main() -> None:
    result = subprocess.run([sys.executable, str(GENERATOR)], cwd=REPO, text=True, capture_output=True, check=False)
    print(result.stdout)
    if result.returncode:
        print(result.stderr)
        raise SystemExit(result.returncode)

    payload = json.loads(SCENARIO_FILE.read_text(encoding="utf-8"))
    scenarios = payload.get("scenarios")
    assert isinstance(scenarios, list) and len(scenarios) == 1000
    assert len({item["id"] for item in scenarios}) == 1000

    types = Counter(item["scenario_type"] for item in scenarios)
    assert types == Counter({"capability_routing": 500, "autonomous_evolution": 500})

    routing = [item for item in scenarios if item["scenario_type"] == "capability_routing"]
    capability_counts = Counter(item["expected"]["capability_id"] for item in routing)
    assert capability_counts == {f"CAP-{i:03d}": 50 for i in range(1, 11)}
    assert all(item["expected"]["status"] == "success" for item in routing)

    evolution = [item for item in scenarios if item["scenario_type"] == "autonomous_evolution"]
    strategy_counts = Counter(item["expected"]["strategy"] for item in evolution)
    assert strategy_counts == Counter({"create": 100, "improve": 100, "adapt": 100, "replan": 100, "compose": 100})
    assert all(item["expected"]["output_required"] is True for item in evolution)
    assert all(item["context"]["evidence"] for item in evolution)

    create_cases = [item for item in evolution if item["expected"]["strategy"] == "create"]
    assert all(item["expected"]["capability_creation_expected"] for item in create_cases)

    print("PASS: 1000 growth scenarios generated and validated")
    print("  canonical routing: 500")
    print("  autonomous evolution: 500")
    print("  create/improve/adapt/replan/compose: 100 each")


if __name__ == "__main__":
    main()
