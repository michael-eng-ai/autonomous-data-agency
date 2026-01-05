"""
Core Package

Este pacote contém as classes e utilitários fundamentais do framework:
- BaseTeam: Classe base para todos os times de agentes
- AgencyOrchestrator: Orquestrador principal da agência
- Tipos de dados compartilhados
- Utilitários de validação
"""

from .base_team import (
    BaseTeam,
    AgentRole,
    ValidationStatus,
    AgentResponse,
    ValidationResult,
    TeamOutput
)

from .agency_orchestrator import (
    AgencyOrchestrator,
    ProjectPhase,
    ProjectState,
    GlobalValidationResult,
    get_agency_orchestrator
)

__all__ = [
    # Base Team
    "BaseTeam",
    "AgentRole",
    "ValidationStatus",
    "AgentResponse",
    "ValidationResult",
    "TeamOutput",
    # Orchestrator
    "AgencyOrchestrator",
    "ProjectPhase",
    "ProjectState",
    "GlobalValidationResult",
    "get_agency_orchestrator",
]
