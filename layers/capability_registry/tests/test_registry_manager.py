"""
Layer 9 - Tests for CapabilityRegistryManager
"""

import pytest
import json
import tempfile
from pathlib import Path

from layers.capability_registry.registry import CapabilityRegistryManager
from layers.capability_registry.models import (
    CapabilityMetadata,
    CapabilityType,
    CapabilityQuery,
)


@pytest.fixture
def temp_registry_path():
    """Create a temporary directory for test registry files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "registry.json"
        yield str(registry_path)


@pytest.fixture
def registry(temp_registry_path):
    """Create a CapabilityRegistryManager for testing."""
    return CapabilityRegistryManager(registry_path=temp_registry_path)


class TestCapabilityRegistryManager:
    """Tests for CapabilityRegistryManager."""
    
    def test_init_new_registry(self, temp_registry_path):
        """Test initializing a new registry when no file exists."""
        registry = CapabilityRegistryManager(registry_path=temp_registry_path)
        assert len(registry.list_all_capabilities()) == 0
    
    def test_register_capability(self, registry):
        """Test registering a new capability."""
        cap = CapabilityMetadata(
            id="CAP-001",
            name="Simple Bug Detection",
            description="Detect simple bugs",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze_simple_bugs",
            supported_languages=["python", "java"],
            test_coverage=85.0,
        )
        
        result = registry.register(cap)
        assert result == True
        
        registered = registry.get_capability("CAP-001")
        assert registered is not None
        assert registered.name == "Simple Bug Detection"
    
    def test_register_duplicate_capability(self, registry):
        """Test that registering duplicate capability returns False."""
        cap = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
        )
        
        # Register first time
        result1 = registry.register(cap)
        assert result1 == True
        
        # Try to register again
        result2 = registry.register(cap)
        assert result2 == False
    
    def test_get_capability(self, registry):
        """Test retrieving a capability by ID."""
        cap = CapabilityMetadata(
            id="CAP-002",
            name="Syntax Error Fix",
            description="",
            type=CapabilityType.FIX,
            entry_point="fix_syntax",
            supported_languages=["python"],
        )
        registry.register(cap)
        
        retrieved = registry.get_capability("CAP-002")
        assert retrieved is not None
        assert retrieved.name == "Syntax Error Fix"
        
        # Get non-existent capability
        not_found = registry.get_capability("CAP-999")
        assert not_found is None
    
    def test_list_all_capabilities(self, registry):
        """Test listing all registered capabilities."""
        cap1 = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
        )
        cap2 = CapabilityMetadata(
            id="CAP-002",
            name="Syntax Fix",
            description="",
            type=CapabilityType.FIX,
            entry_point="fix",
            supported_languages=["python"],
        )
        
        registry.register(cap1)
        registry.register(cap2)
        
        all_caps = registry.list_all_capabilities()
        assert len(all_caps) == 2
        assert all_caps[0].id == "CAP-001"
        assert all_caps[1].id == "CAP-002"
    
    def test_query_by_type(self, registry):
        """Test querying capabilities by type."""
        cap_analysis = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
        )
        cap_fix = CapabilityMetadata(
            id="CAP-002",
            name="Syntax Fix",
            description="",
            type=CapabilityType.FIX,
            entry_point="fix",
            supported_languages=["python"],
        )
        cap_parsing = CapabilityMetadata(
            id="CAP-009",
            name="Parser",
            description="",
            type=CapabilityType.PARSING,
            entry_point="parse",
            supported_languages=["python"],
        )
        
        registry.register(cap_analysis)
        registry.register(cap_fix)
        registry.register(cap_parsing)
        
        # Query by analysis type
        analysis_caps = registry.query_by_type("analysis")
        assert len(analysis_caps) == 1
        assert analysis_caps[0].id == "CAP-001"
        
        # Query by parsing type
        parsing_caps = registry.query_by_type("parsing")
        assert len(parsing_caps) == 1
        assert parsing_caps[0].id == "CAP-009"
    
    def test_query_by_language(self, registry):
        """Test querying capabilities by language."""
        cap_python = CapabilityMetadata(
            id="CAP-001",
            name="Python Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
        )
        cap_multi = CapabilityMetadata(
            id="CAP-002",
            name="Multi-language Fix",
            description="",
            type=CapabilityType.FIX,
            entry_point="fix",
            supported_languages=["python", "java", "javascript"],
        )
        
        registry.register(cap_python)
        registry.register(cap_multi)
        
        # Query Python capabilities
        python_caps = registry.query_by_language("python")
        assert len(python_caps) == 2
        
        # Query Java capabilities
        java_caps = registry.query_by_language("java")
        assert len(java_caps) == 1
        assert java_caps[0].id == "CAP-002"
        
        # Query JavaScript capabilities
        js_caps = registry.query_by_language("javascript")
        assert len(js_caps) == 1
    
    def test_complex_query(self, registry):
        """Test complex query with multiple filters."""
        cap1 = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="Find bugs easily",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python", "java"],
            test_coverage=85.0,
        )
        cap2 = CapabilityMetadata(
            id="CAP-009",
            name="Universal Parser",
            description="Parse JSON and XML",
            type=CapabilityType.PARSING,
            entry_point="parse",
            supported_languages=["python"],
            test_coverage=100.0,
            generated=True,
        )
        
        registry.register(cap1)
        registry.register(cap2)
        
        # Query generated capabilities only
        query = CapabilityQuery(generated_only=True)
        result = registry.query(query)
        assert result.matched_count == 1
        assert result.capabilities[0].id == "CAP-009"
        
        # Query by language + type
        query = CapabilityQuery(language="python", capability_type="parsing")
        result = registry.query(query)
        assert result.matched_count == 1
        assert result.capabilities[0].id == "CAP-009"
        
        # Query with minimum coverage
        query = CapabilityQuery(min_test_coverage=90.0)
        result = registry.query(query)
        assert result.matched_count == 1
        assert result.capabilities[0].id == "CAP-009"
    
    def test_update_reuse_count(self, registry):
        """Test incrementing reuse count."""
        cap = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
        )
        registry.register(cap)
        
        # Initial reuse count should be 0
        assert registry.get_capability("CAP-001").reuse_count == 0
        
        # Update reuse count
        result = registry.update_reuse_count("CAP-001", increment=1)
        assert result == True
        assert registry.get_capability("CAP-001").reuse_count == 1
        
        # Increment by more than 1
        registry.update_reuse_count("CAP-001", increment=5)
        assert registry.get_capability("CAP-001").reuse_count == 6
        
        # Update non-existent capability
        result = registry.update_reuse_count("CAP-999", increment=1)
        assert result == False
    
    def test_record_usage(self, registry):
        """Test recording capability usage."""
        cap = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
        )
        registry.register(cap)
        
        # Record successful usage
        result = registry.record_usage("CAP-001", success=True, execution_time_ms=250.5)
        assert result == True
        assert registry.get_capability("CAP-001").reuse_count == 1
        
        # Record failed usage (should not increment reuse count)
        registry.record_usage("CAP-001", success=False, execution_time_ms=100.0)
        assert registry.get_capability("CAP-001").reuse_count == 1  # Should still be 1
        
        # Record another successful usage
        registry.record_usage("CAP-001", success=True, execution_time_ms=200.0)
        assert registry.get_capability("CAP-001").reuse_count == 2
    
    def test_persistence(self):
        """Test that registry persists to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "registry.json"
            
            # Create registry and add capability
            registry1 = CapabilityRegistryManager(registry_path=str(registry_path))
            cap = CapabilityMetadata(
                id="CAP-001",
                name="Bug Detection",
                description="",
                type=CapabilityType.ANALYSIS,
                entry_point="analyze",
                supported_languages=["python"],
            )
            registry1.register(cap)
            registry1.update_reuse_count("CAP-001", increment=3)
            
            # Load registry in new instance
            registry2 = CapabilityRegistryManager(registry_path=str(registry_path))
            cap_loaded = registry2.get_capability("CAP-001")
            assert cap_loaded is not None
            assert cap_loaded.name == "Bug Detection"
            assert cap_loaded.reuse_count == 3
            
            # Verify JSON file exists and has correct format
            assert registry_path.exists()
            with open(registry_path, 'r') as f:
                data = json.load(f)
            assert len(data["capabilities"]) == 1
            assert data["capabilities"][0]["id"] == "CAP-001"
    
    def test_get_top_capabilities(self, registry):
        """Test getting top capabilities by metric."""
        cap1 = CapabilityMetadata(
            id="CAP-001",
            name="Cap 1",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
            test_coverage=80.0,
        )
        cap2 = CapabilityMetadata(
            id="CAP-002",
            name="Cap 2",
            description="",
            type=CapabilityType.FIX,
            entry_point="fix",
            supported_languages=["python"],
            test_coverage=90.0,
        )
        cap3 = CapabilityMetadata(
            id="CAP-003",
            name="Cap 3",
            description="",
            type=CapabilityType.PARSING,
            entry_point="parse",
            supported_languages=["python"],
            test_coverage=100.0,
        )
        
        registry.register(cap1)
        registry.register(cap2)
        registry.register(cap3)
        
        # Get top by coverage
        registry.update_reuse_count("CAP-003", increment=10)
        registry.update_reuse_count("CAP-002", increment=5)
        
        top_reuse = registry.get_top_capabilities(count=2, by="reuse_count")
        assert len(top_reuse) == 2
        assert top_reuse[0].id == "CAP-003"  # 10 reuses
        assert top_reuse[1].id == "CAP-002"  # 5 reuses
    
    def test_search_capabilities(self, registry):
        """Test searching by name or description."""
        cap1 = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="Find bugs in code",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
        )
        cap2 = CapabilityMetadata(
            id="CAP-002",
            name="Syntax Fix",
            description="Find and fix syntax errors",
            type=CapabilityType.FIX,
            entry_point="fix",
            supported_languages=["python"],
        )
        
        registry.register(cap1)
        registry.register(cap2)
        
        # Search for "bug"
        results = registry.search_capabilities("bug")
        assert len(results) == 1
        assert results[0].id == "CAP-001"
        
        # Search for "find" - appears in both name and description
        results = registry.search_capabilities("find")
        assert len(results) == 2  # Both have "find" in description
    
    def test_deprecate_activate_capability(self, registry):
        """Test deprecating and activating capabilities."""
        cap = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python"],
        )
        registry.register(cap)
        
        # Initially active
        assert registry.get_capability("CAP-001").status == "active"
        
        # Deprecate
        result = registry.deprecate_capability("CAP-001")
        assert result == True
        assert registry.get_capability("CAP-001").status == "deprecated"
        
        # Activate
        result = registry.activate_capability("CAP-001")
        assert result == True
        assert registry.get_capability("CAP-001").status == "active"
    
    def test_get_statistics(self, registry):
        """Test getting registry statistics."""
        cap_seed = CapabilityMetadata(
            id="CAP-001",
            name="Bug Detection",
            description="",
            type=CapabilityType.ANALYSIS,
            entry_point="analyze",
            supported_languages=["python", "java"],
            test_coverage=85.0,
        )
        cap_generated = CapabilityMetadata(
            id="CAP-009",
            name="Parser",
            description="",
            type=CapabilityType.PARSING,
            entry_point="parse",
            supported_languages=["python"],
            test_coverage=100.0,
            generated=True,
        )
        
        registry.register(cap_seed)
        registry.register(cap_generated)
        registry.update_reuse_count("CAP-001", increment=5)
        registry.update_reuse_count("CAP-009", increment=3)
        
        stats = registry.get_statistics()
        
        assert stats["total_capabilities"] == 2
        assert stats["seed_capabilities"] == 1
        assert stats["generated_capabilities"] == 1
        assert stats["total_reuses"] == 8
        assert stats["average_reuse_count"] == 4.0
        assert stats["average_test_coverage"] == 92.5
        assert stats["active_count"] == 2
