"""
Core Package - Autonomous Data Agency v6.0

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
- GovernanceTeam: Time de Governança e LGPD
- DataQuality: Validação de qualidade de dados
- ObservabilityTeam: Observabilidade e FinOps
- IntegratedWorkflow: Workflow integrado com governança
- QuarantineManager: Gestão de dados inválidos (NEW v6.0)
- ProcessControl: Rastreabilidade de execuções (NEW v6.0)
- GovernancePolicies: Políticas de governança em YAML (NEW v6.0)
- DataCatalog: Catálogo de dados com OpenMetadata (NEW v6.0)
- LineageTracker: Rastreamento de linhagem de dados (NEW v6.0)
- BusinessGlossary: Glossário de negócio padronizado (NEW v6.0)
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

# Governance Team
from .governance_team import (
    GovernanceTeam,
    DataClassification,
    LegalBasis,
    DataSubjectRight,
    PIIType,
    LGPDValidator,
    GovernanceValidation,
    get_governance_team
)

# Data Quality
from .data_quality import (
    DataQualityValidator,
    QualityDimension,
    QualityRule,
    RuleViolation,
    QualityReport,
    RuleSeverity,
    get_data_quality_validator
)

# Observability Team
from .observability_team import (
    ObservabilityTeam,
    StructuredLogger,
    MetricsCollector,
    AlertManager,
    CostTracker,
    AlertSeverity,
    MetricType,
    get_observability_team
)

# Integrated Workflow
from .integrated_workflow import (
    IntegratedWorkflow,
    WorkflowPhase,
    WorkflowStatus,
    WorkflowCheckpoint,
    IntegratedProject,
    get_integrated_workflow
)

# Quarantine Manager (NEW in v6.0)
from .quarantine_manager import (
    QuarantineManager,
    QuarantineRecord,
    QuarantineReason,
    QuarantineStatus,
    QuarantineStats,
    get_quarantine_manager
)

# Process Control (NEW in v6.0)
from .process_control import (
    ProcessControl,
    ProcessExecution,
    ExecutionStatus,
    ExecutionStep,
    StepStatus,
    ExecutionMetrics,
    get_process_control
)

# Governance Policies (NEW in v6.0)
from .governance_policies import (
    GovernancePolicies,
    AccessPolicy,
    RetentionPolicy,
    DataClassificationLevel,
    QualityThreshold,
    LGPDConfig,
    AuditConfig,
    get_governance_policies
)

# Data Catalog (NEW in v6.0)
from .data_catalog import (
    DataCatalog,
    TableMetadata,
    ColumnMetadata,
    DataAsset,
    AssetType,
    get_data_catalog
)

# Lineage Tracker (NEW in v6.0)
from .lineage_tracker import (
    LineageTracker,
    LineageNode,
    LineageEdge,
    TransformationType,
    ImpactAnalysis,
    get_lineage_tracker
)

# Business Glossary (NEW in v6.0)
from .business_glossary import (
    BusinessGlossary,
    GlossaryTerm,
    TermRelationship,
    TermStatus,
    get_business_glossary
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
    
    # Governance Team
    "GovernanceTeam",
    "DataClassification",
    "LegalBasis",
    "DataSubjectRight",
    "PIIType",
    "LGPDValidator",
    "GovernanceValidation",
    "get_governance_team",
    
    # Data Quality
    "DataQualityValidator",
    "QualityDimension",
    "QualityRule",
    "RuleViolation",
    "QualityReport",
    "RuleSeverity",
    "get_data_quality_validator",
    
    # Observability Team
    "ObservabilityTeam",
    "StructuredLogger",
    "MetricsCollector",
    "AlertManager",
    "CostTracker",
    "MetricType",
    "AlertSeverity",
    "get_observability_team",
    
    # Integrated Workflow
    "IntegratedWorkflow",
    "WorkflowPhase",
    "WorkflowStatus",
    "WorkflowCheckpoint",
    "IntegratedProject",
    "get_integrated_workflow",
    
    # Quarantine Manager (NEW in v6.0)
    "QuarantineManager",
    "QuarantineRecord",
    "QuarantineReason",
    "QuarantineStatus",
    "QuarantineStats",
    "get_quarantine_manager",
    
    # Process Control (NEW in v6.0)
    "ProcessControl",
    "ProcessExecution",
    "ExecutionStatus",
    "ExecutionStep",
    "StepStatus",
    "ExecutionMetrics",
    "get_process_control",
    
    # Governance Policies (NEW in v6.0)
    "GovernancePolicies",
    "AccessPolicy",
    "RetentionPolicy",
    "DataClassificationLevel",
    "QualityThreshold",
    "LGPDConfig",
    "AuditConfig",
    "get_governance_policies",
    
    # Data Catalog (NEW in v6.0)
    "DataCatalog",
    "TableMetadata",
    "ColumnMetadata",
    "DataAsset",
    "AssetType",
    "get_data_catalog",
    
    # Lineage Tracker (NEW in v6.0)
    "LineageTracker",
    "LineageNode",
    "LineageEdge",
    "TransformationType",
    "ImpactAnalysis",
    "get_lineage_tracker",
    
    # Business Glossary (NEW in v6.0)
    "BusinessGlossary",
    "GlossaryTerm",
    "TermRelationship",
    "TermStatus",
    "get_business_glossary",
]

__version__ = "6.0.0"
