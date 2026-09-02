"""Legacy compatibility shim for older SPS-CA integrations.

New code should import :mod:`ui.sps_service` directly.
"""

from .sps_service import SPSAnalysisResult, SPSScenarioService

SupervisorAnalysisResult = SPSAnalysisResult
SupervisorScenarioService = SPSScenarioService

__all__ = ["SPSAnalysisResult", "SPSScenarioService", "SupervisorAnalysisResult", "SupervisorScenarioService"]
