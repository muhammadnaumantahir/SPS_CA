"""Deprecated compatibility import for the SPS-CA scenario service.

Use :mod:`ui.sps_service` for all new code. This shim remains temporarily so
older integrations do not fail during the naming cleanup.
"""

from .sps_service import SPSAnalysisResult, SPSScenarioService

# Backward-compatible aliases for existing callers.
SupervisorAnalysisResult = SPSAnalysisResult
SupervisorScenarioService = SPSScenarioService

__all__ = [
    "SPSAnalysisResult",
    "SPSScenarioService",
    "SupervisorAnalysisResult",
    "SupervisorScenarioService",
]
