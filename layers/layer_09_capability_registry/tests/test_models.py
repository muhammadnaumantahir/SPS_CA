"""
Layer 9 - Tests for data models (CapabilityMetadata, CapabilityQuery, etc.)
"""

import pytest
from datetime import datetime
from layers.layer_09_capability_registry.models import (
    CapabilityMetadata,
    CapabilityType,
    CapabilityLanguage,
    CapabilityQuery,
    CapabilityQueryResult,
    CapabilityReusageRecord,
    CapabilityRegistry,
)


class TestCapabilityMetadata:
    """Tests for CapabilityMetadata dataclass."""
    
    def test_create_seed_capability(self):
        """Test creating a seed (non-generated) capability."""
        cap = CapabilityMetadata(
            id="CAP-001",
            name="Simple Bug Detection",
            description="Detect obvious bugs like unused variables",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze_simple_bugs",
            supported_languages=["python", "java", "javascript"],
            version="1.0.0",
            test_coverage=85.0,
            status="active",
        )
        
        assert cap.id == "CAP-001"
        assert cap.name == "Simple Bug Detection"
        assert cap.generated == False
        assert cap.reuse_count == 0
        assert cap.test_coverage == 85.0
    
    def test_create_generated_capability(self):
        """Test creating a generated capability."""
        cap = CapabilityMetadata(
            id="CAP-009",
            name="Universal Parser",
            description="Parse JSON, XML, CSV files",
            type=CapabilityType.PARSING,
            entry_point="universal_parser",
            supported_languages=["python"],
            generated=True,
            origin="capability_evolution",
            failure_pattern="Parse error",
            trigger_tasks=["task_010", "task_015", "task_020"],
            test_coverage=100.0,
        )
        
        assert cap.generated == True
        assert cap.origin == "capability_evolution"
        assert cap.failure_pattern == "Parse error"
        assert len(cap.trigger_tasks) == 3
        assert cap.test_coverage == 100.0
    
    def test_capability_to_dict(self):
        """Test converting capability to dictionary."""
        cap = CapabilityMetadata(
            id="CAP-002",
            name="Syntax Error Fix",
            description="Fix common syntax errors",
            type=CapabilityType.FIX,
            entry_point="fix_syntax_errors",
            supported_languages=["python", "java"],
            version="1.0.0",
            test_coverage=88.5,
        )
        
        cap_dict = cap.to_dict()
        
        assert cap_dict["id"] == "CAP-002"
        assert cap_dict["name"] == "Syntax Error Fix"
        assert cap_dict["type"] == "fix"  # Enum converted to value
        assert cap_dict["test_coverage"] == 88.5
        assert isinstance(cap_dict["created_date"], str)  # Should be ISO format
    
    def test_capability_from_dict(self):
        """Test creating capability from dictionary."""
        data = {
            "id": "CAP-003",
            "name": "Test Generation",
            "description": "Generate unit tests",
            "type": "generation",
            "entry_point": "generate_unit_tests",
            "supported_languages": ["python", "java"],
            "version": "1.0.0",
            "test_coverage": 90.0,
            "generated": False,
        }
        
        cap = CapabilityMetadata.from_dict(data)
        
        assert cap.id == "CAP-003"
        assert cap.name == "Test Generation"
        assert cap.type == CapabilityType.GENERATION
        assert cap.test_coverage == 90.0
    
    def test_capability_round_trip(self):
        """Test converting to dict and back."""
        original = CapabilityMetadata(
            id="CAP-005",
            name="Error Handling",
            description="Add try-catch blocks",
            type=CapabilityType.TRANSFORMATION,
            entry_point="add_error_handling",
            supported_languages=["python", "java", "javascript"],
            version="1.0.0",
            test_coverage=92.0,
            status="active",
        )
        
        cap_dict = original.to_dict()
        restored = CapabilityMetadata.from_dict(cap_dict)
        
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.type == original.type
        assert restored.test_coverage == original.test_coverage


class TestCapabilityQuery:
    """Tests for CapabilityQuery dataclass."""
    
    def test_query_by_id(self):
        """Test creating a query by capability ID."""
        query = CapabilityQuery(capability_id="CAP-001")
        assert query.capability_id == "CAP-001"
        assert query.generated_only == False
        assert query.sort_by == "id"
    
    def test_query_by_type_and_language(self):
        """Test creating a query by type and language."""
        query = CapabilityQuery(
            capability_type="parsing",
            language="python",
        )
        assert query.capability_type == "parsing"
        assert query.language == "python"
    
    def test_query_generated_only(self):
        """Test querying only generated capabilities."""
        query = CapabilityQuery(generated_only=True)
        assert query.generated_only == True
        assert query.seed_only == False
    
    def test_query_sorting(self):
        """Test query with sorting."""
        query = CapabilityQuery(
            sort_by="reuse_count",
            sort_order="desc",
        )
        assert query.sort_by == "reuse_count"
        assert query.sort_order == "desc"
    
    def test_query_to_dict(self):
        """Test converting query to dictionary."""
        query = CapabilityQuery(
            capability_type="bug_detection",
            language="java",
            sort_by="test_coverage",
        )
        query_dict = query.to_dict()
        
        assert query_dict["capability_type"] == "bug_detection"
        assert query_dict["language"] == "java"
        assert query_dict["sort_by"] == "test_coverage"


class TestCapabilityQueryResult:
    """Tests for CapabilityQueryResult dataclass."""
    
    def test_empty_result(self):
        """Test an empty query result."""
        result = CapabilityQueryResult(matched_count=0)
        assert result.matched_count == 0
        assert len(result.capabilities) == 0
    
    def test_result_with_capabilities(self):
        """Test a result with matched capabilities."""
        cap1 = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="detect_bugs",
            supported_languages=["python"],
        )
        cap2 = CapabilityMetadata(
            id="CAP-009",
            name="Parser",
            description="",
            type=CapabilityType.PARSING,
            entry_point="parse",
            supported_languages=["python"],
        )
        
        result = CapabilityQueryResult(
            matched_count=2,
            capabilities=[cap1, cap2],
            query_time_ms=5.2,
        )
        
        assert result.matched_count == 2
        assert len(result.capabilities) == 2
        assert result.capabilities[0].id == "CAP-001"
        assert result.query_time_ms == 5.2


class TestCapabilityReusageRecord:
    """Tests for CapabilityReusageRecord dataclass."""
    
    def test_create_usage_record(self):
        """Test creating a usage record."""
        record = CapabilityReusageRecord(
            capability_id="CAP-001",
            success=True,
            execution_time_ms=250.5,
            notes="Fixed syntax error in utils.py",
        )
        
        assert record.capability_id == "CAP-001"
        assert record.success == True
        assert record.execution_time_ms == 250.5
        assert record.notes == "Fixed syntax error in utils.py"
        assert record.timestamp is not None


class TestCapabilityRegistry:
    """Tests for CapabilityRegistry (data model, not manager)."""
    
    def test_create_empty_registry(self):
        """Test creating an empty registry."""
        registry = CapabilityRegistry()
        assert registry.version == "1.0.0"
        assert len(registry.capabilities) == 0
        assert len(registry.usage_history) == 0
    
    def test_registry_with_capabilities(self):
        """Test registry with some capabilities."""
        cap = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="detect",
            supported_languages=["python"],
        )
        
        registry = CapabilityRegistry(
            capabilities=[cap],
            usage_history=[],
        )
        
        assert len(registry.capabilities) == 1
        assert registry.capabilities[0].id == "CAP-001"
    
    def test_registry_to_dict(self):
        """Test converting registry to dictionary."""
        cap = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="detect",
            supported_languages=["python"],
        )
        
        registry = CapabilityRegistry(capabilities=[cap])
        registry_dict = registry.to_dict()
        
        assert registry_dict["version"] == "1.0.0"
        assert len(registry_dict["capabilities"]) == 1
        assert registry_dict["capabilities"][0]["id"] == "CAP-001"
    
    def test_registry_from_dict(self):
        """Test creating registry from dictionary."""
        data = {
            "version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat(),
            "capabilities": [
                {
                    "id": "CAP-001",
                    "name": "Bug Detection",
                    "description": "Detect bugs",
                    "type": "analysis",
                    "entry_point": "detect",
                    "supported_languages": ["python"],
                    "version": "1.0.0",
                    "created_date": datetime.utcnow().isoformat(),
                    "last_modified": datetime.utcnow().isoformat(),
                    "generated": False,
                    "origin": None,
                    "failure_pattern": None,
                    "trigger_tasks": [],
                    "reuse_count": 5,
                    "test_coverage": 88.0,
                    "documentation_path": "",
                    "metadata_path": "",
                    "status": "active",
                    "extra_metadata": {},
                }
            ],
            "usage_history": [],
        }
        
        registry = CapabilityRegistry.from_dict(data)
        
        assert len(registry.capabilities) == 1
        assert registry.capabilities[0].id == "CAP-001"
        assert registry.capabilities[0].reuse_count == 5
    
    def test_registry_round_trip(self):
        """Test converting registry to dict and back."""
        cap1 = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="detect",
            supported_languages=["python"],
        )
        cap2 = CapabilityMetadata(
            id="CAP-009",
            name="Parser",
            description="",
            type=CapabilityType.PARSING,
            entry_point="parse",
            supported_languages=["python"],
            generated=True,
        )
        
        original = CapabilityRegistry(capabilities=[cap1, cap2])
        registry_dict = original.to_dict()
        restored = CapabilityRegistry.from_dict(registry_dict)
        
        assert len(restored.capabilities) == 2
        assert restored.capabilities[0].id == "CAP-001"
        assert restored.capabilities[1].generated == True
