"""
Layer 9: Capability Registry Manager

Implements the CapabilityRegistry class that manages all capabilities (seed + generated),
tracks reuse, handles queries, and persists state to capabilities/registry.json.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import time

from .models import (
    CapabilityMetadata,
    CapabilityQuery,
    CapabilityQueryResult,
    CapabilityReusageRecord,
    CapabilityRegistry as CapabilityRegistryData,
    CapabilityType,
    CapabilityLanguage,
)

logger = logging.getLogger(__name__)


class CapabilityRegistryManager:
    """
    Manages the capability registry — registration, querying, reuse tracking, and persistence.
    
    Responsibilities:
    - Register new capabilities (seed or generated)
    - Query capabilities by type, language, name, status
    - Track capability reuse and update reuse counts
    - Persist registry to JSON
    - Load registry from JSON
    """
    
    def __init__(self, registry_path: str = "capabilities/registry.json"):
        """
        Initialize the registry manager.
        
        Args:
            registry_path: Path to capabilities/registry.json
        """
        self.registry_path = Path(registry_path)
        self.registry_data: CapabilityRegistryData = CapabilityRegistryData()
        self.capabilities_by_id: Dict[str, CapabilityMetadata] = {}
        self._load_from_disk()
    
    def _load_from_disk(self) -> None:
        """Load registry from JSON file if it exists."""
        if not self.registry_path.exists():
            logger.info(f"Registry file {self.registry_path} does not exist yet")
            self.registry_data = CapabilityRegistryData()
            self.capabilities_by_id = {}
            return
        
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
            self.registry_data = CapabilityRegistryData.from_dict(data)
            # Build fast lookup by ID
            self.capabilities_by_id = {cap.id: cap for cap in self.registry_data.capabilities}
            logger.info(f"Loaded {len(self.registry_data.capabilities)} capabilities from {self.registry_path}")
        except Exception as e:
            logger.error(f"Failed to load registry from {self.registry_path}: {e}")
            self.registry_data = CapabilityRegistryData()
            self.capabilities_by_id = {}
    
    def _save_to_disk(self) -> None:
        """Persist registry to JSON file."""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            self.registry_data.last_updated = datetime.utcnow().isoformat()
            with open(self.registry_path, 'w') as f:
                json.dump(self.registry_data.to_dict(), f, indent=2)
            logger.info(f"Saved {len(self.registry_data.capabilities)} capabilities to {self.registry_path}")
        except Exception as e:
            logger.error(f"Failed to save registry to {self.registry_path}: {e}")
            raise
    
    def register(self, capability: CapabilityMetadata) -> bool:
        """
        Register a new capability in the registry.
        
        Args:
            capability: CapabilityMetadata object to register
            
        Returns:
            True if registered successfully, False if capability already exists
        """
        if capability.id in self.capabilities_by_id:
            logger.warning(f"Capability {capability.id} already registered")
            return False
        
        self.registry_data.capabilities.append(capability)
        self.capabilities_by_id[capability.id] = capability
        self._save_to_disk()
        logger.info(f"Registered capability {capability.id}: {capability.name}")
        return True
    
    def get_capability(self, capability_id: str) -> Optional[CapabilityMetadata]:
        """
        Retrieve a capability by ID.
        
        Args:
            capability_id: Capability ID (e.g., "CAP-001")
            
        Returns:
            CapabilityMetadata if found, None otherwise
        """
        return self.capabilities_by_id.get(capability_id)
    
    def list_all_capabilities(self) -> List[CapabilityMetadata]:
        """Return all registered capabilities."""
        return self.registry_data.capabilities.copy()
    
    def query_by_type(self, task_type: str) -> List[CapabilityMetadata]:
        """
        Find all capabilities matching a task type.
        
        Args:
            task_type: Type string (e.g., "parsing", "bug_detection", "analysis")
            
        Returns:
            List of matching CapabilityMetadata objects
        """
        return [
            cap for cap in self.registry_data.capabilities
            if cap.type.value == task_type or cap.type == task_type
        ]
    
    def query_by_language(self, language: str) -> List[CapabilityMetadata]:
        """
        Find all capabilities supporting a specific language.
        
        Args:
            language: Language name (e.g., "python", "java", "javascript")
            
        Returns:
            List of matching CapabilityMetadata objects
        """
        return [
            cap for cap in self.registry_data.capabilities
            if language.lower() in [lang.lower() for lang in cap.supported_languages]
        ]
    
    def query(self, query: CapabilityQuery) -> CapabilityQueryResult:
        """
        Execute a complex query on the capability registry.
        
        Args:
            query: CapabilityQuery object with search criteria
            
        Returns:
            CapabilityQueryResult with matched capabilities
        """
        start_time = time.time()
        matches = self.registry_data.capabilities.copy()
        
        # Filter by ID
        if query.capability_id:
            matches = [c for c in matches if c.id == query.capability_id]
        
        # Filter by type
        if query.capability_type:
            matches = [c for c in matches if c.type.value == query.capability_type or c.type == query.capability_type]
        
        # Filter by language
        if query.language:
            language_lower = query.language.lower()
            matches = [
                c for c in matches
                if language_lower in [lang.lower() for lang in c.supported_languages]
            ]
        
        # Filter by name substring
        if query.name_contains:
            name_lower = query.name_contains.lower()
            matches = [c for c in matches if name_lower in c.name.lower()]
        
        # Filter generated vs seed
        if query.generated_only:
            matches = [c for c in matches if c.generated]
        if query.seed_only:
            matches = [c for c in matches if not c.generated]
        
        # Filter by status
        if query.status:
            matches = [c for c in matches if c.status == query.status]
        
        # Filter by minimum test coverage
        if query.min_test_coverage > 0:
            matches = [c for c in matches if c.test_coverage >= query.min_test_coverage]
        
        # Sort
        sort_key_map = {
            "id": lambda c: c.id,
            "reuse_count": lambda c: c.reuse_count,
            "test_coverage": lambda c: c.test_coverage,
            "created_date": lambda c: c.created_date,
            "name": lambda c: c.name,
        }
        
        sort_func = sort_key_map.get(query.sort_by, lambda c: c.id)
        reverse = query.sort_order == "desc"
        matches.sort(key=sort_func, reverse=reverse)
        
        query_time_ms = (time.time() - start_time) * 1000
        
        return CapabilityQueryResult(
            matched_count=len(matches),
            capabilities=matches,
            query_time_ms=query_time_ms,
        )
    
    def update_reuse_count(self, capability_id: str, increment: int = 1) -> bool:
        """
        Increment the reuse count for a capability and record usage.
        
        Args:
            capability_id: Capability ID (e.g., "CAP-001")
            increment: Amount to increment by (default 1)
            
        Returns:
            True if updated successfully, False if capability not found
        """
        capability = self.capabilities_by_id.get(capability_id)
        if not capability:
            logger.warning(f"Capability {capability_id} not found")
            return False
        
        capability.reuse_count += increment
        capability.last_modified = datetime.utcnow().isoformat()
        
        # Record usage
        usage_record = CapabilityReusageRecord(
            capability_id=capability_id,
            success=True,
        )
        self.registry_data.usage_history.append(usage_record)
        
        self._save_to_disk()
        logger.info(f"Updated reuse count for {capability_id}: now {capability.reuse_count}")
        return True
    
    def record_usage(self, capability_id: str, success: bool = True, execution_time_ms: float = 0.0, notes: str = "") -> bool:
        """
        Record a capability usage event.
        
        Args:
            capability_id: Capability ID
            success: Whether the capability execution was successful
            execution_time_ms: How long execution took (milliseconds)
            notes: Optional notes about the usage
            
        Returns:
            True if recorded successfully
        """
        if capability_id not in self.capabilities_by_id:
            logger.warning(f"Capability {capability_id} not found")
            return False
        
        usage_record = CapabilityReusageRecord(
            capability_id=capability_id,
            success=success,
            execution_time_ms=execution_time_ms,
            notes=notes,
        )
        self.registry_data.usage_history.append(usage_record)
        
        # Also update reuse count if successful
        if success:
            self.capabilities_by_id[capability_id].reuse_count += 1
            self.capabilities_by_id[capability_id].last_modified = datetime.utcnow().isoformat()
        
        self._save_to_disk()
        return True
    
    def get_top_capabilities(self, count: int = 5, by: str = "reuse_count") -> List[CapabilityMetadata]:
        """
        Get the top N capabilities by some metric.
        
        Args:
            count: How many to return
            by: Metric to sort by ("reuse_count", "test_coverage", "created_date")
            
        Returns:
            List of top capabilities
        """
        query = CapabilityQuery(sort_by=by, sort_order="desc")
        result = self.query(query)
        return result.capabilities[:count]
    
    def search_capabilities(self, search_text: str) -> List[CapabilityMetadata]:
        """
        Search capabilities by name or description.
        
        Args:
            search_text: Text to search for
            
        Returns:
            List of matching capabilities
        """
        search_lower = search_text.lower()
        return [
            cap for cap in self.registry_data.capabilities
            if search_lower in cap.name.lower() or search_lower in cap.description.lower()
        ]
    
    def get_capabilities_by_status(self, status: str) -> List[CapabilityMetadata]:
        """
        Get all capabilities with a specific status.
        
        Args:
            status: Status value (e.g., "active", "deprecated", "experimental")
            
        Returns:
            List of capabilities with that status
        """
        return [cap for cap in self.registry_data.capabilities if cap.status == status]
    
    def deprecate_capability(self, capability_id: str) -> bool:
        """
        Mark a capability as deprecated.
        
        Args:
            capability_id: Capability to deprecate
            
        Returns:
            True if successful
        """
        capability = self.capabilities_by_id.get(capability_id)
        if not capability:
            return False
        
        capability.status = "deprecated"
        capability.last_modified = datetime.utcnow().isoformat()
        self._save_to_disk()
        logger.info(f"Deprecated capability {capability_id}")
        return True
    
    def activate_capability(self, capability_id: str) -> bool:
        """
        Mark a capability as active.
        
        Args:
            capability_id: Capability to activate
            
        Returns:
            True if successful
        """
        capability = self.capabilities_by_id.get(capability_id)
        if not capability:
            return False
        
        capability.status = "active"
        capability.last_modified = datetime.utcnow().isoformat()
        self._save_to_disk()
        logger.info(f"Activated capability {capability_id}")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the capability registry.
        
        Returns:
            Dictionary with stats (total capabilities, generated count, avg reuse count, etc.)
        """
        capabilities = self.registry_data.capabilities
        generated = [c for c in capabilities if c.generated]
        seed = [c for c in capabilities if not c.generated]
        
        total_reuses = sum(c.reuse_count for c in capabilities)
        avg_reuse = total_reuses / len(capabilities) if capabilities else 0
        avg_coverage = sum(c.test_coverage for c in capabilities) / len(capabilities) if capabilities else 0
        
        return {
            "total_capabilities": len(capabilities),
            "seed_capabilities": len(seed),
            "generated_capabilities": len(generated),
            "total_reuses": total_reuses,
            "average_reuse_count": avg_reuse,
            "average_test_coverage": avg_coverage,
            "unique_languages": len(set(lang for c in capabilities for lang in c.supported_languages)),
            "capability_types": list(set(c.type.value for c in capabilities)),
            "active_count": len([c for c in capabilities if c.status == "active"]),
            "deprecated_count": len([c for c in capabilities if c.status == "deprecated"]),
        }
