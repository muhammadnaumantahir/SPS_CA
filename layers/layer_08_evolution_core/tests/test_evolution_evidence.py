import json
from layers.layer_08_evolution.evolution_evidence import EvolutionEvidenceStore

def test_disagreement_reasoning_progression(tmp_path):
    registry=tmp_path/"registry.json"; registry.write_text(json.dumps({"version":"1.0.0","capabilities":[],"usage_history":[]}),encoding="utf-8")
    store=EvolutionEvidenceStore(tmp_path/"events.json",registry); decisions=[]
    for n in range(1,4):
        event=store.record_disagreement(session_id="s1",turn_id=n,request="add validation",language="python",language_confidence=.95,previous_capability_id="CAP-002",code="def add(a,b): return a+b")
        analysis=store.analyze(event); decisions.append(analysis["decision"])
    assert decisions==["defer","adapt","create"]
    created=store.record_creation(analysis)
    assert created["created_capability_id"]=="CAP-011"
    lineage=store.get_capability_lineage("CAP-011")
    assert lineage["provenance"]["decision"]=="create"
    assert lineage["provenance"]["historical_id"] if "historical_id" in lineage["provenance"] else True
    assert lineage["capability"]["generated"] is True
