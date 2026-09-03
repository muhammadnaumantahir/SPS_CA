from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from layers.capability_registry.models import CapabilityType
from layers.capability_registry.registry import CapabilityRegistryManager

ROOT = Path(__file__).resolve().parents[2]
EVENTS_PATH = ROOT / "runtime" / "evolution_events.json"


class EvolutionEvidenceStore:
    """Persistent evidence ledger for explainable Layer-8 decisions."""
    def __init__(self,path:str|Path=EVENTS_PATH,registry_path:str|Path=ROOT/"capabilities"/"registry.json")->None:
        self.path=Path(path); self.registry=CapabilityRegistryManager(str(registry_path))
    def _load(self):
        if not self.path.exists(): return []
        try:
            data=json.loads(self.path.read_text(encoding="utf-8")); return data if isinstance(data,list) else []
        except (OSError,json.JSONDecodeError): return []
    def _save(self,events):
        self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps(events,indent=2,ensure_ascii=False),encoding="utf-8")
    @staticmethod
    def _now(): return datetime.now(timezone.utc).isoformat()
    @staticmethod
    def _next_id(events): return f"EVOL-{len(events)+1:05d}"
    def record_disagreement(self,*,session_id,turn_id,request,language,language_confidence,previous_capability_id,code=""):
        events=self._load(); same_cap=[e for e in events if e.get("event_type")=="disagreement" and e.get("previous_capability_id")==previous_capability_id]; count=len(same_cap)+1
        evidence={"event_id":self._next_id(events),"event_type":"disagreement","timestamp":self._now(),"session_id":session_id,"turn_id":turn_id,"request":request,"language":language,"language_confidence":language_confidence,"previous_capability_id":previous_capability_id,"disagreement_count":count,"failure_pattern":self._failure_pattern(request,code),"evidence_summary":self._evidence_summary(previous_capability_id,count)}
        events.append(evidence); self._save(events); return evidence
    def analyze(self,event):
        count=int(event.get("disagreement_count") or 0); parent=event.get("previous_capability_id") or ""
        if not parent: decision="defer"; reasoning="No previous capability was identified, so the system cannot establish a reusable capability gap safely."
        elif count>=3: decision="create"; reasoning=f"Repeated evidence shows {count} disagreements for {parent}; the existing capability is not reliably covering this pattern, so a new reusable capability is justified."
        elif count==2: decision="adapt"; reasoning=f"Two disagreements indicate a capability gap, but the evidence is not yet strong enough to create a new capability. Adaptation of {parent} is preferred first."
        else: decision="defer"; reasoning=f"Only one disagreement is available for {parent}; preserve the evidence and avoid capability proliferation until the pattern repeats."
        result=dict(event); result.update({"decision":decision,"reasoning":reasoning,"validation_status":"pending" if decision=="create" else "not_applicable"}); events=self._load(); result["event_type"]="evolution_analysis"; result["event_id"]=self._next_id(events); result["timestamp"]=self._now(); events.append(result); self._save(events); return result
    def record_creation(self,analysis):
        events=self._load(); existing=[int(c.id.split("-")[-1]) for c in self.registry.list_all_capabilities() if c.id.startswith("CAP-") and c.id.split("-")[-1].isdigit()]; next_num=max([10,*existing])+1; cap_id=f"CAP-{next_num:03d}"
        parent=analysis.get("previous_capability_id") or None; name=self._capability_name(analysis.get("request",""),parent,cap_id)
        provenance={"decision":"create","created_at":self._now(),"parent_capability_id":parent,"trigger_event_ids":[analysis.get("event_id","")],"reasoning":analysis.get("reasoning",""),"evidence_summary":analysis.get("evidence_summary",""),"validation_status":"registered","source_request":analysis.get("request","")}
        metadata={"id":cap_id,"name":name,"description":f"Generated reusable skill for the repeated pattern: {analysis.get('failure_pattern','observed user requirement')}","type":CapabilityType.MODIFICATION.value,"entry_point":"capabilities.generated.evolved_runtime.run","supported_languages":[analysis.get("language") or "python"],"version":"1.0.0","created_date":self._now(),"last_modified":self._now(),"generated":True,"origin":"capability_evolution","failure_pattern":analysis.get("failure_pattern"),"trigger_tasks":[str(analysis.get("session_id",""))],"reuse_count":0,"test_coverage":0.0,"status":"active","canonical":False,"extra_metadata":{"provenance":provenance,"tags":["evolved","explainable"]}}
        self.registry.register_from_dict(metadata); creation=dict(analysis); creation.update({"event_type":"capability_created","event_id":self._next_id(events),"timestamp":self._now(),"created_capability_id":cap_id,"validation_status":"registered","capability_name":name}); events.append(creation); self._save(events); return creation
    def list_events(self,limit=100): return self._load()[-max(1,limit):][::-1]
    def get_capability_lineage(self,capability_id):
        capability=self.registry.get_capability(capability_id); events=self._load(); related=[e for e in events if e.get("created_capability_id")==capability_id]; provenance=((capability.extra_metadata or {}).get("provenance") if capability else None) or {}
        return {"capability":capability.to_dict() if capability else None,"provenance":provenance,"events":related,"parent":provenance.get("parent_capability_id")}
    @staticmethod
    def _failure_pattern(request,code):
        text=f"{request} {code}".lower(); keywords=[("parameter","parameterized test/behavior pattern"),("async","asynchronous code pattern"),("validation","input validation pattern"),("type","type-handling pattern"),("exception","exception-handling pattern"),("test","test-generation pattern")]
        for token,label in keywords:
            if token in text: return label
        return "repeated unmet user requirement"
    @staticmethod
    def _evidence_summary(capability_id,count): return f"{count} disagreement(s) associated with {capability_id or 'no capability'} were observed; evidence is accumulated before structural evolution."
    @staticmethod
    def _capability_name(request,parent,cap_id):
        words=[w.strip(".,:;!?\"'") for w in request.split() if w.strip()]; title=" ".join(words[:5]).title() if words else "Evolved Coding Skill"; return f"{title} ({cap_id})"
