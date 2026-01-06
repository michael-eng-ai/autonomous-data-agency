"""
Core Package

Este pacote contém as classes e utilitários fundamentais do framework:
- BaseTeam: Classe base para todos os times de agentes
- AgencyOrchestrator: Orquestrador principal da agência
- Knowledge: Sistema de conhecimento em 3 camadas
- TeamsFactory: Fábrica de times pré-configurados
- HallucinationDetector: Detector de alucinações
- TeamCommunication: Sistema de comunicação entre times
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

# Knowledge system
from .knowledge import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeQuery,
    get_knowledge_base,
    RAGEngine,
    Document,
    SearchResult,
    get_rag_engine,
    ProjectMemory,
    MemoryType,
    MemoryEntry,
    ProjectContext,
    get_project_memory,
    KnowledgeManager,
    get_knowledge_manager
)

# Teams Factory
from .teams_factory import (
    TeamsFactory,
    TeamType,
    TeamConfig,
    AgentConfig as FactoryAgentConfig,
    get_teams_factory,
    TEAM_CONFIGS
)

# Hallucination Detector
from .hallucination_detector import (
    HallucinationDetector,
    HallucinationSeverity,
    HallucinationType,
    HallucinationIssue,
    ValidationResult as HallucinationValidationResult,
    get_hallucination_detector
)

# Team Communication
from .team_communication import (
    TeamCommunicationHub,
    MessageBus,
    TeamMessage,
    MessageType,
    MessagePriority,
    MessageStatus,
    CollaborationRequest,
    TeamContext,
    get_communication_hub
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
    # Knowledge Base
    "KnowledgeBase",
    "KnowledgeItem",
    "KnowledgeQuery",
    "get_knowledge_base",
    # RAG Engine
    "RAGEngine",
    "Document",
    "SearchResult",
    "get_rag_engine",
    # Project Memory
    "ProjectMemory",
    "MemoryType",
    "MemoryEntry",
    "ProjectContext",
    "get_project_memory",
    # Knowledge Manager
    "KnowledgeManager",
    "get_knowledge_manager",
    # Teams Factory
    "TeamsFactory",
    "TeamType",
    "TeamConfig",
    "FactoryAgentConfig",
    "get_teams_factory",
    "TEAM_CONFIGS",
    # Hallucination Detector
    "HallucinationDetector",
    "HallucinationSeverity",
    "HallucinationType",
    "HallucinationIssue",
    "HallucinationValidationResult",
    "get_hallucination_detector",
    # Team Communication
    "TeamCommunicationHub",
    "MessageBus",
    "TeamMessage",
    "MessageType",
    "MessagePriority",
    "MessageStatus",
    "CollaborationRequest",
    "TeamContext",
    "get_communication_hub",
]
