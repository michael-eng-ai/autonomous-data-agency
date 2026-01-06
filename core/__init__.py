"""
Core Package - Autonomous Data Agency v5.0

Este pacote contém as classes e utilitários fundamentais do framework:
- BaseTeam: Classe base para todos os times de agentes
- AgencyOrchestrator: Orquestrador principal da agência
- Knowledge: Sistema de conhecimento em 3 camadas
- TeamsFactory: Fábrica de times pré-configurados
- HallucinationDetector: Detector de alucinações
- TeamCommunication: Sistema de comunicação entre times
- TaskOrchestrator: Orquestrador de tarefas e dependências
- PMOrchestrator: Project Manager como orquestrador central
- ValidationWorkflow: Fluxo de validação QA + PO
- GovernanceTeam: Time de Governança e LGPD (NEW v5.0)
- DataQuality: Validação de qualidade de dados (NEW v5.0)
- ObservabilityTeam: Observabilidade e FinOps (NEW v5.0)
- IntegratedWorkflow: Workflow integrado com governança (NEW v5.0)
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

# Task Orchestrator
from .task_orchestrator import (
    TaskOrchestrator,
    Task,
    TaskStatus,
    TaskPriority,
    TaskType,
    TaskDependency,
    ProjectSchedule,
    get_task_orchestrator
)

# PM Orchestrator
from .pm_orchestrator import (
    PMOrchestrator,
    ProjectPhase as PMProjectPhase,
    RiskLevel,
    Risk,
    Milestone,
    TeamAssignment,
    get_pm_orchestrator
)

# Validation Workflow
from .validation_workflow import (
    ValidationWorkflow,
    QAValidator,
    POValidator,
    ValidationStatus as WorkflowValidationStatus,
    ValidationCategory,
    QAValidationReport,
    POValidationReport,
    get_validation_workflow,
    get_qa_validator,
    get_po_validator
)

# Governance Team (NEW in v5.0)
from .governance_team import (
    GovernanceTeam,
    DataClassification,
    LegalBasis,
    ComplianceStatus,
    DataSubjectRight,
    LGPDChecklist,
    GovernanceReview,
    get_governance_team
)

# Data Quality (NEW in v5.0)
from .data_quality import (
    DataQualityValidator,
    QualityDimension,
    QualityRule,
    QualityViolation,
    QualityReport,
    get_data_quality_validator
)

# Observability Team (NEW in v5.0)
from .observability_team import (
    ObservabilityTeam,
    StructuredLogger,
    MetricsCollector,
    AlertManager,
    CostTracker,
    LogLevel,
    AlertSeverity,
    get_observability_team
)

# Integrated Workflow (NEW in v5.0)
from .integrated_workflow import (
    IntegratedWorkflow,
    WorkflowPhase,
    WorkflowStatus,
    WorkflowCheckpoint,
    IntegratedProject,
    get_integrated_workflow
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
    
    # Task Orchestrator
    "TaskOrchestrator",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskType",
    "TaskDependency",
    "ProjectSchedule",
    "get_task_orchestrator",
    
    # PM Orchestrator
    "PMOrchestrator",
    "PMProjectPhase",
    "RiskLevel",
    "Risk",
    "Milestone",
    "TeamAssignment",
    "get_pm_orchestrator",
    
    # Validation Workflow
    "ValidationWorkflow",
    "QAValidator",
    "POValidator",
    "WorkflowValidationStatus",
    "ValidationCategory",
    "QAValidationReport",
    "POValidationReport",
    "get_validation_workflow",
    "get_qa_validator",
    "get_po_validator",
    
    # Governance Team (NEW in v5.0)
    "GovernanceTeam",
    "DataClassification",
    "LegalBasis",
    "ComplianceStatus",
    "DataSubjectRight",
    "LGPDChecklist",
    "GovernanceReview",
    "get_governance_team",
    
    # Data Quality (NEW in v5.0)
    "DataQualityValidator",
    "QualityDimension",
    "QualityRule",
    "QualityViolation",
    "QualityReport",
    "get_data_quality_validator",
    
    # Observability Team (NEW in v5.0)
    "ObservabilityTeam",
    "StructuredLogger",
    "MetricsCollector",
    "AlertManager",
    "CostTracker",
    "LogLevel",
    "AlertSeverity",
    "get_observability_team",
    
    # Integrated Workflow (NEW in v5.0)
    "IntegratedWorkflow",
    "WorkflowPhase",
    "WorkflowStatus",
    "WorkflowCheckpoint",
    "IntegratedProject",
    "get_integrated_workflow",
]

__version__ = "5.0.0"
