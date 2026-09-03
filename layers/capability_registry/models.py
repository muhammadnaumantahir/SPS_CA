from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
class CapabilityType(str,Enum):
    ANALYSIS="analysis"; BUG_DETECTION="bug_detection"; FIX="fix"; GENERATION="generation"; OPTIMIZATION="optimization"; VALIDATION="validation"; PARSING="parsing"; TRANSFORMATION="transformation"; REFACTORING="refactoring"; MODIFICATION="modification"; TESTING="testing"; DOCUMENTATION="documentation"; PROJECT_OPERATIONS="project_operations"; UNKNOWN="unknown"
class CapabilityLanguage(str,Enum):
    PYTHON="python"; JAVA="java"; JAVASCRIPT="javascript"; TYPESCRIPT="typescript"; GO="go"; CSHARP="csharp"; CPP="cpp"; RUST="rust"
@dataclass
class CapabilityMetadata:
    id:str; name:str; description:str; type:CapabilityType; entry_point:str; supported_languages:List[str]; version:str="1.0.0"; created_date:str=field(default_factory=lambda:datetime.utcnow().isoformat()); last_modified:str=field(default_factory=lambda:datetime.utcnow().isoformat()); generated:bool=False; origin:Optional[str]=None; failure_pattern:Optional[str]=None; trigger_tasks:List[str]=field(default_factory=list); reuse_count:int=0; test_coverage:float=0.0; documentation_path:str=""; metadata_path:str=""; status:str="active"; extra_metadata:Dict[str,Any]=field(default_factory=dict); canonical:bool=False; intent_class:str="unknown"; allowed_intents:List[str]=field(default_factory=list); forbidden_intents:List[str]=field(default_factory=list); risk_level:str="medium"; side_effects:List[str]=field(default_factory=list)
    def to_dict(self):
        return {"id":self.id,"name":self.name,"description":self.description,"type":self.type.value if isinstance(self.type,Enum) else self.type,"entry_point":self.entry_point,"supported_languages":self.supported_languages,"version":self.version,"created_date":self.created_date,"last_modified":self.last_modified,"generated":self.generated,"origin":self.origin,"failure_pattern":self.failure_pattern,"trigger_tasks":self.trigger_tasks,"reuse_count":self.reuse_count,"test_coverage":self.test_coverage,"documentation_path":self.documentation_path,"metadata_path":self.metadata_path,"status":self.status,"extra_metadata":self.extra_metadata,"canonical":self.canonical,"intent_class":self.intent_class,"allowed_intents":self.allowed_intents,"forbidden_intents":self.forbidden_intents,"risk_level":self.risk_level,"side_effects":self.side_effects}
    @staticmethod
    def from_dict(data):
        extra=data.get("extra_metadata",{}) or {}
        return CapabilityMetadata(id=data.get("id",""),name=data.get("name",""),description=data.get("description",""),type=CapabilityType(data.get("type","unknown")) if isinstance(data.get("type"),str) else CapabilityType.UNKNOWN,entry_point=data.get("entry_point",""),supported_languages=data.get("supported_languages",data.get("target_languages",[])),version=data.get("version","1.0.0"),created_date=data.get("created_date",datetime.utcnow().isoformat()),last_modified=data.get("last_modified",datetime.utcnow().isoformat()),generated=bool(data.get("generated",False)),origin=data.get("origin"),failure_pattern=data.get("failure_pattern"),trigger_tasks=list(data.get("trigger_tasks",[])),reuse_count=int(data.get("reuse_count",0) or 0),test_coverage=float(data.get("test_coverage") or 0.0),documentation_path=data.get("documentation_path",""),metadata_path=data.get("metadata_path",""),status=data.get("status","active"),extra_metadata=extra,canonical=bool(data.get("canonical",extra.get("canonical",False))),intent_class=data.get("intent_class",extra.get("intent_class","unknown")),allowed_intents=list(data.get("allowed_intents",extra.get("allowed_intents",[]))),forbidden_intents=list(data.get("forbidden_intents",extra.get("forbidden_intents",[]))),risk_level=data.get("risk_level",extra.get("risk_level","medium")),side_effects=list(data.get("side_effects",extra.get("side_effects",[]))))
@dataclass
class CapabilityQuery:
    capability_id:Optional[str]=None; capability_type:Optional[str]=None; language:Optional[str]=None; name_contains:Optional[str]=None; generated_only:bool=False; seed_only:bool=False; status:Optional[str]=None; min_test_coverage:float=0.0; sort_by:str="id"; sort_order:str="asc"
    def to_dict(self): return asdict(self)
@dataclass
class CapabilityQueryResult:
    matched_count:int; capabilities:List[CapabilityMetadata]=field(default_factory=list); query_time_ms:float=0.0
    def to_dict(self): return {"matched_count":self.matched_count,"capabilities":[c.to_dict() for c in self.capabilities],"query_time_ms":self.query_time_ms}
@dataclass
class CapabilityReusageRecord:
    capability_id:str; timestamp:str=field(default_factory=lambda:datetime.utcnow().isoformat()); task_id:str=""; success:bool=True; execution_time_ms:float=0.0; notes:str=""
@dataclass
class CapabilityRegistry:
    version:str="1.0.0"; last_updated:str=field(default_factory=lambda:datetime.utcnow().isoformat()); capabilities:List[CapabilityMetadata]=field(default_factory=list); usage_history:List[CapabilityReusageRecord]=field(default_factory=list)
    def to_dict(self): return {"version":self.version,"last_updated":self.last_updated,"capabilities":[c.to_dict() for c in self.capabilities],"usage_history":[asdict(u) for u in self.usage_history]}
    @staticmethod
    def from_dict(data): return CapabilityRegistry(version=data.get("version","1.0.0"),last_updated=data.get("last_updated",datetime.utcnow().isoformat()),capabilities=[CapabilityMetadata.from_dict(c) for c in data.get("capabilities",[])],usage_history=[CapabilityReusageRecord(**u) for u in data.get("usage_history",[])])
