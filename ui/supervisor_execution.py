"""Deprecated compatibility import for the SPS-CA execution service.

Use :mod:`ui.sps_execution` for all new code. This shim remains temporarily so
older integrations do not fail during the naming cleanup.
"""

from .sps_execution import SPSExecutionService

# Backward-compatible alias for existing callers.
SupervisorExecutionService = SPSExecutionService

__all__ = ["SPSExecutionService", "SupervisorExecutionService"]
