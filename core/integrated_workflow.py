"""
Integrated Workflow Module

Este módulo integra todos os times e sistemas da Autonomous Data Agency
em um workflow completo e coeso.

Fluxo de Trabalho:
1. Cliente → PO (requisitos)
2. PO → PM (planejamento)
3. PM → Arquitetura (decisões técnicas)
4. Arquitetura → Governança (validação LGPD/compliance)
5. Governança → Times de Execução (paralelo)
6. Execução → QA (validação técnica + qualidade de dados)
7. QA → PO (validação de negócio)
8. Observabilidade monitora todo o processo

Funcionalidades:
- Orquestração completa do workflow
- Validação de governança em cada etapa
- Monitoramento de qualidade de dados
- Logging e métricas centralizados
- Gestão de custos integrada
"""

import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Imports dos módulos internos
from .governance_team import (
    GovernanceTeam,
    get_governance_team,
    ComplianceStatus
)
from .data_quality import (
    DataQualityValidator,
    get_data_quality_validator,
    QualityReport
)
from .observability_team import (
    ObservabilityTeam,
    get_observability_team
)
from .pm_orchestrator import (
    PMOrchestrator,
    get_pm_orchestrator,
    TaskStatus
)
from .validation_workflow import (
    ValidationWorkflow,
    get_validation_workflow
)
from .team_communication import (
    TeamCommunicationHub,
    get_communication_hub
)


class WorkflowPhase(Enum):
    """Fases do workflow integrado."""
    REQUIREMENTS = "requirements"           # PO coleta requisitos
    PLANNING = "planning"                   # PM cria cronograma
    ARCHITECTURE = "architecture"           # Arquitetura define solução
    GOVERNANCE_REVIEW = "governance_review" # Governança valida compliance
    EXECUTION = "execution"                 # Times executam
    QA_VALIDATION = "qa_validation"         # QA valida qualidade
    PO_VALIDATION = "po_validation"         # PO valida negócio
    COMPLETED = "completed"                 # Projeto concluído


class WorkflowStatus(Enum):
    """Status do workflow."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowCheckpoint:
    """Checkpoint do workflow para auditoria."""
    phase: WorkflowPhase
    status: WorkflowStatus
    timestamp: str
    details: Dict[str, Any]
    approved_by: Optional[str] = None
    blocked_reason: Optional[str] = None


@dataclass
class IntegratedProject:
    """Projeto integrado com todos os metadados."""
    id: str
    name: str
    description: str
    client: str
    created_at: str
    current_phase: WorkflowPhase
    status: WorkflowStatus
    checkpoints: List[WorkflowCheckpoint] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    governance_approval: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    quality_reports: List[Dict[str, Any]] = field(default_factory=list)
    validations: List[Dict[str, Any]] = field(default_factory=list)
    cost_estimate: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "client": self.client,
            "created_at": self.created_at,
            "current_phase": self.current_phase.value,
            "status": self.status.value,
            "checkpoints": [
                {
                    "phase": cp.phase.value,
                    "status": cp.status.value,
                    "timestamp": cp.timestamp,
                    "details": cp.details,
                    "approved_by": cp.approved_by,
                    "blocked_reason": cp.blocked_reason
                }
                for cp in self.checkpoints
            ],
            "requirements": self.requirements,
            "architecture": self.architecture,
            "governance_approval": self.governance_approval,
            "tasks_count": len(self.tasks),
            "quality_reports_count": len(self.quality_reports),
            "validations_count": len(self.validations),
            "cost_estimate": self.cost_estimate
        }


class IntegratedWorkflow:
    """
    Workflow integrado da Autonomous Data Agency.
    
    Coordena todos os times e sistemas em um fluxo coeso.
    """
    
    def __init__(self):
        # Inicializa todos os componentes
        self.governance = get_governance_team()
        self.quality = get_data_quality_validator()
        self.observability = get_observability_team()
        self.pm = get_pm_orchestrator()
        self.validation = get_validation_workflow()
        self.communication = get_communication_hub()
        
        # Estado
        self.projects: Dict[str, IntegratedProject] = {}
        self._project_counter = 0
        
        # Callbacks para notificações
        self.phase_callbacks: Dict[WorkflowPhase, List[Callable]] = {
            phase: [] for phase in WorkflowPhase
        }
    
    def _generate_project_id(self) -> str:
        """Gera ID único para projeto."""
        self._project_counter += 1
        return f"proj_{datetime.now().strftime('%Y%m%d')}_{self._project_counter:04d}"
    
    def _log_action(
        self,
        project_id: str,
        action: str,
        details: Dict[str, Any],
        success: bool = True
    ) -> None:
        """Registra ação no sistema de observabilidade."""
        self.observability.logger.log(
            level="INFO" if success else "ERROR",
            component="integrated_workflow",
            action=action,
            message=f"Projeto {project_id}: {action}",
            context={"project_id": project_id, **details}
        )
        
        self.observability.metrics.increment("workflow_actions_total")
    
    def _add_checkpoint(
        self,
        project: IntegratedProject,
        phase: WorkflowPhase,
        status: WorkflowStatus,
        details: Dict[str, Any],
        approved_by: str = None,
        blocked_reason: str = None
    ) -> None:
        """Adiciona checkpoint ao projeto."""
        checkpoint = WorkflowCheckpoint(
            phase=phase,
            status=status,
            timestamp=datetime.now().isoformat(),
            details=details,
            approved_by=approved_by,
            blocked_reason=blocked_reason
        )
        project.checkpoints.append(checkpoint)
        project.current_phase = phase
        project.status = status
    
    def create_project(
        self,
        name: str,
        description: str,
        client: str,
        initial_requirements: Dict[str, Any] = None
    ) -> IntegratedProject:
        """
        Cria um novo projeto integrado.
        
        Args:
            name: Nome do projeto
            description: Descrição
            client: Nome do cliente
            initial_requirements: Requisitos iniciais (opcional)
            
        Returns:
            Projeto criado
        """
        project_id = self._generate_project_id()
        
        project = IntegratedProject(
            id=project_id,
            name=name,
            description=description,
            client=client,
            created_at=datetime.now().isoformat(),
            current_phase=WorkflowPhase.REQUIREMENTS,
            status=WorkflowStatus.IN_PROGRESS,
            requirements=initial_requirements or {}
        )
        
        self.projects[project_id] = project
        
        # Registra no sistema de observabilidade
        self._log_action(
            project_id,
            "project_created",
            {"name": name, "client": client}
        )
        
        # Adiciona checkpoint inicial
        self._add_checkpoint(
            project,
            WorkflowPhase.REQUIREMENTS,
            WorkflowStatus.IN_PROGRESS,
            {"message": "Projeto iniciado, coletando requisitos"}
        )
        
        return project
    
    def submit_requirements(
        self,
        project_id: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submete requisitos do projeto (fase PO).
        
        Args:
            project_id: ID do projeto
            requirements: Requisitos coletados
            
        Returns:
            Resultado da submissão
        """
        project = self.projects.get(project_id)
        if not project:
            return {"success": False, "error": "Projeto não encontrado"}
        
        project.requirements = requirements
        
        # Análise inicial de governança nos requisitos
        governance_check = self._check_requirements_governance(requirements)
        
        if not governance_check["compliant"]:
            self._add_checkpoint(
                project,
                WorkflowPhase.REQUIREMENTS,
                WorkflowStatus.BLOCKED,
                {"governance_issues": governance_check["issues"]},
                blocked_reason="Requisitos não conformes com LGPD/Governança"
            )
            return {
                "success": False,
                "phase": "requirements",
                "blocked": True,
                "governance_issues": governance_check["issues"],
                "recommendations": governance_check["recommendations"]
            }
        
        # Avança para planejamento
        self._add_checkpoint(
            project,
            WorkflowPhase.PLANNING,
            WorkflowStatus.IN_PROGRESS,
            {"requirements_approved": True, "governance_check": "passed"}
        )
        
        self._log_action(
            project_id,
            "requirements_submitted",
            {"requirements_count": len(requirements)}
        )
        
        return {
            "success": True,
            "phase": "planning",
            "message": "Requisitos aprovados, avançando para planejamento"
        }
    
    def _check_requirements_governance(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verifica governança nos requisitos."""
        issues = []
        recommendations = []
        
        # Verifica se há coleta de dados pessoais
        data_fields = requirements.get("data_fields", [])
        personal_data_fields = []
        sensitive_data_fields = []
        
        sensitive_keywords = ["cpf", "cnpj", "saude", "health", "biometri", "genetic"]
        personal_keywords = ["nome", "name", "email", "telefone", "phone", "endereco", "address"]
        
        for field in data_fields:
            field_lower = field.lower() if isinstance(field, str) else str(field).lower()
            
            if any(kw in field_lower for kw in sensitive_keywords):
                sensitive_data_fields.append(field)
            elif any(kw in field_lower for kw in personal_keywords):
                personal_data_fields.append(field)
        
        # Verifica base legal
        if personal_data_fields or sensitive_data_fields:
            legal_basis = requirements.get("legal_basis")
            if not legal_basis:
                issues.append({
                    "type": "missing_legal_basis",
                    "severity": "critical",
                    "message": "Base legal não definida para tratamento de dados pessoais",
                    "affected_fields": personal_data_fields + sensitive_data_fields
                })
                recommendations.append(
                    "Definir base legal (consentimento, contrato, obrigação legal, etc.) "
                    "para cada tipo de dado pessoal coletado"
                )
        
        # Verifica dados sensíveis
        if sensitive_data_fields:
            consent_mechanism = requirements.get("consent_mechanism")
            if not consent_mechanism:
                issues.append({
                    "type": "missing_consent_for_sensitive",
                    "severity": "critical",
                    "message": "Dados sensíveis requerem consentimento específico",
                    "affected_fields": sensitive_data_fields
                })
                recommendations.append(
                    "Implementar mecanismo de consentimento específico e destacado "
                    "para dados sensíveis conforme Art. 11 da LGPD"
                )
        
        # Verifica período de retenção
        if personal_data_fields and not requirements.get("retention_period"):
            issues.append({
                "type": "missing_retention_period",
                "severity": "warning",
                "message": "Período de retenção não definido para dados pessoais"
            })
            recommendations.append(
                "Definir período de retenção para cada categoria de dado pessoal"
            )
        
        # Verifica canal para direitos do titular
        if personal_data_fields and not requirements.get("data_subject_rights_channel"):
            issues.append({
                "type": "missing_rights_channel",
                "severity": "warning",
                "message": "Canal para exercício de direitos do titular não definido"
            })
            recommendations.append(
                "Disponibilizar canal para que titulares exerçam seus direitos "
                "(acesso, correção, exclusão, portabilidade)"
            )
        
        # Determina se está compliant
        critical_issues = [i for i in issues if i.get("severity") == "critical"]
        compliant = len(critical_issues) == 0
        
        return {
            "compliant": compliant,
            "issues": issues,
            "recommendations": recommendations,
            "personal_data_detected": personal_data_fields,
            "sensitive_data_detected": sensitive_data_fields
        }
    
    def submit_architecture(
        self,
        project_id: str,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submete arquitetura do projeto.
        
        Args:
            project_id: ID do projeto
            architecture: Decisões arquiteturais
            
        Returns:
            Resultado da submissão
        """
        project = self.projects.get(project_id)
        if not project:
            return {"success": False, "error": "Projeto não encontrado"}
        
        project.architecture = architecture
        
        # Análise de governança na arquitetura
        governance_review = self.governance.review_architecture(architecture)
        
        # Estimativa de custos
        cost_estimate = self.observability.costs.estimate_project_cost({
            "duration_days": architecture.get("timeline_days", 30),
            "llm_calls_per_day": architecture.get("estimated_llm_calls", 100),
            "avg_tokens_per_call": 2000,
            "storage_gb": architecture.get("storage_estimate_gb", 10),
            "compute_hours_per_day": 8
        })
        
        project.cost_estimate = cost_estimate
        
        if not governance_review["approved"]:
            self._add_checkpoint(
                project,
                WorkflowPhase.ARCHITECTURE,
                WorkflowStatus.BLOCKED,
                {
                    "governance_review": governance_review,
                    "cost_estimate": cost_estimate
                },
                blocked_reason="Arquitetura não aprovada pela governança"
            )
            return {
                "success": False,
                "phase": "architecture",
                "blocked": True,
                "governance_review": governance_review,
                "cost_estimate": cost_estimate
            }
        
        # Avança para revisão de governança completa
        self._add_checkpoint(
            project,
            WorkflowPhase.GOVERNANCE_REVIEW,
            WorkflowStatus.IN_PROGRESS,
            {
                "architecture_approved": True,
                "cost_estimate": cost_estimate
            }
        )
        
        self._log_action(
            project_id,
            "architecture_submitted",
            {"components": list(architecture.keys())}
        )
        
        return {
            "success": True,
            "phase": "governance_review",
            "governance_review": governance_review,
            "cost_estimate": cost_estimate,
            "message": "Arquitetura aprovada, avançando para revisão de governança"
        }
    
    def complete_governance_review(
        self,
        project_id: str,
        dpia_required: bool = False,
        dpia_result: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Completa revisão de governança.
        
        Args:
            project_id: ID do projeto
            dpia_required: Se DPIA é necessário
            dpia_result: Resultado do DPIA (se aplicável)
            
        Returns:
            Resultado da revisão
        """
        project = self.projects.get(project_id)
        if not project:
            return {"success": False, "error": "Projeto não encontrado"}
        
        # Executa revisão completa de governança
        full_review = self.governance.full_project_review(
            project_name=project.name,
            requirements=project.requirements,
            architecture=project.architecture,
            dpia_result=dpia_result
        )
        
        project.governance_approval = full_review
        
        if full_review["status"] != ComplianceStatus.COMPLIANT.value:
            self._add_checkpoint(
                project,
                WorkflowPhase.GOVERNANCE_REVIEW,
                WorkflowStatus.BLOCKED,
                {"governance_review": full_review},
                blocked_reason=f"Governança: {full_review.get('blocking_issues', 'Issues encontrados')}"
            )
            return {
                "success": False,
                "phase": "governance_review",
                "blocked": True,
                "review": full_review
            }
        
        # Avança para execução
        self._add_checkpoint(
            project,
            WorkflowPhase.EXECUTION,
            WorkflowStatus.IN_PROGRESS,
            {"governance_approved": True, "approval_date": datetime.now().isoformat()}
        )
        
        self._log_action(
            project_id,
            "governance_approved",
            {"status": full_review["status"]}
        )
        
        return {
            "success": True,
            "phase": "execution",
            "review": full_review,
            "message": "Governança aprovada, iniciando execução"
        }
    
    def submit_deliverable(
        self,
        project_id: str,
        deliverable_name: str,
        deliverable_type: str,
        data_sample: List[Dict[str, Any]] = None,
        schema: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Submete uma entrega para validação.
        
        Args:
            project_id: ID do projeto
            deliverable_name: Nome da entrega
            deliverable_type: Tipo (pipeline, model, api, etc.)
            data_sample: Amostra de dados para validação de qualidade
            schema: Schema dos dados
            
        Returns:
            Resultado da validação
        """
        project = self.projects.get(project_id)
        if not project:
            return {"success": False, "error": "Projeto não encontrado"}
        
        result = {
            "deliverable": deliverable_name,
            "type": deliverable_type,
            "validations": {}
        }
        
        # Validação de qualidade de dados (se aplicável)
        if data_sample:
            # Adiciona regras padrão baseadas no schema
            if schema:
                self.quality.add_standard_rules(deliverable_name, schema)
            
            quality_report = self.quality.validate(deliverable_name, data_sample)
            
            result["validations"]["data_quality"] = {
                "passed": quality_report.passed,
                "overall_score": quality_report.overall_score,
                "violations_count": len(quality_report.violations),
                "blocking_violations": quality_report.blocking_violations,
                "recommendations": quality_report.recommendations
            }
            
            project.quality_reports.append({
                "deliverable": deliverable_name,
                "report": result["validations"]["data_quality"],
                "timestamp": datetime.now().isoformat()
            })
            
            if not quality_report.passed:
                result["success"] = False
                result["blocked_by"] = "data_quality"
                return result
        
        # Validação de governança na entrega
        governance_check = self.governance.validate_deliverable(
            deliverable_name=deliverable_name,
            deliverable_type=deliverable_type,
            has_personal_data=bool(data_sample),
            encryption_enabled=True,  # Assume que está habilitado
            access_control_enabled=True
        )
        
        result["validations"]["governance"] = governance_check
        
        if not governance_check.get("approved", False):
            result["success"] = False
            result["blocked_by"] = "governance"
            return result
        
        # Registra métricas
        self.observability.metrics.increment("deliverables_submitted_total")
        
        self._log_action(
            project_id,
            "deliverable_submitted",
            {"name": deliverable_name, "type": deliverable_type}
        )
        
        result["success"] = True
        result["message"] = "Entrega validada com sucesso"
        
        return result
    
    def complete_qa_validation(
        self,
        project_id: str,
        qa_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Completa validação de QA.
        
        Args:
            project_id: ID do projeto
            qa_results: Resultados dos testes de QA
            
        Returns:
            Resultado da validação
        """
        project = self.projects.get(project_id)
        if not project:
            return {"success": False, "error": "Projeto não encontrado"}
        
        # Valida através do workflow de validação
        validation_result = self.validation.submit_for_qa_validation(
            project_id=project_id,
            deliverable="complete_project",
            test_results=qa_results
        )
        
        project.validations.append({
            "type": "qa",
            "result": validation_result,
            "timestamp": datetime.now().isoformat()
        })
        
        if not validation_result.get("approved", False):
            self._add_checkpoint(
                project,
                WorkflowPhase.QA_VALIDATION,
                WorkflowStatus.BLOCKED,
                {"qa_result": validation_result},
                blocked_reason="QA não aprovado"
            )
            return {
                "success": False,
                "phase": "qa_validation",
                "blocked": True,
                "result": validation_result
            }
        
        # Avança para validação do PO
        self._add_checkpoint(
            project,
            WorkflowPhase.PO_VALIDATION,
            WorkflowStatus.IN_PROGRESS,
            {"qa_approved": True}
        )
        
        self._log_action(
            project_id,
            "qa_validation_completed",
            {"approved": True}
        )
        
        return {
            "success": True,
            "phase": "po_validation",
            "result": validation_result,
            "message": "QA aprovado, avançando para validação do PO"
        }
    
    def complete_po_validation(
        self,
        project_id: str,
        po_approval: bool,
        feedback: str = None
    ) -> Dict[str, Any]:
        """
        Completa validação do PO (validação de negócio).
        
        Args:
            project_id: ID do projeto
            po_approval: Se o PO aprovou
            feedback: Feedback do PO
            
        Returns:
            Resultado da validação
        """
        project = self.projects.get(project_id)
        if not project:
            return {"success": False, "error": "Projeto não encontrado"}
        
        validation_result = {
            "approved": po_approval,
            "feedback": feedback,
            "validated_at": datetime.now().isoformat()
        }
        
        project.validations.append({
            "type": "po",
            "result": validation_result,
            "timestamp": datetime.now().isoformat()
        })
        
        if not po_approval:
            self._add_checkpoint(
                project,
                WorkflowPhase.PO_VALIDATION,
                WorkflowStatus.BLOCKED,
                {"po_result": validation_result},
                blocked_reason=f"PO não aprovou: {feedback}"
            )
            return {
                "success": False,
                "phase": "po_validation",
                "blocked": True,
                "result": validation_result
            }
        
        # Projeto concluído!
        self._add_checkpoint(
            project,
            WorkflowPhase.COMPLETED,
            WorkflowStatus.COMPLETED,
            {
                "po_approved": True,
                "completed_at": datetime.now().isoformat()
            },
            approved_by="PO"
        )
        
        project.status = WorkflowStatus.COMPLETED
        
        self._log_action(
            project_id,
            "project_completed",
            {"total_checkpoints": len(project.checkpoints)}
        )
        
        # Gera relatório final
        final_report = self.generate_project_report(project_id)
        
        return {
            "success": True,
            "phase": "completed",
            "message": "Projeto concluído com sucesso!",
            "final_report": final_report
        }
    
    def generate_project_report(self, project_id: str) -> Dict[str, Any]:
        """
        Gera relatório completo do projeto.
        
        Args:
            project_id: ID do projeto
            
        Returns:
            Relatório completo
        """
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Projeto não encontrado"}
        
        # Calcula métricas
        total_duration = None
        if project.checkpoints:
            start = project.checkpoints[0].timestamp
            end = project.checkpoints[-1].timestamp
            # Simplificado - em produção calcular diferença real
            total_duration = f"{start} até {end}"
        
        # Conta validações
        qa_validations = [v for v in project.validations if v["type"] == "qa"]
        po_validations = [v for v in project.validations if v["type"] == "po"]
        
        return {
            "project_id": project.id,
            "name": project.name,
            "client": project.client,
            "status": project.status.value,
            "duration": total_duration,
            "summary": {
                "total_checkpoints": len(project.checkpoints),
                "phases_completed": len([
                    cp for cp in project.checkpoints 
                    if cp.status == WorkflowStatus.COMPLETED
                ]),
                "quality_reports": len(project.quality_reports),
                "qa_validations": len(qa_validations),
                "po_validations": len(po_validations)
            },
            "governance": {
                "approved": project.governance_approval.get("status") == ComplianceStatus.COMPLIANT.value,
                "lgpd_compliant": project.governance_approval.get("lgpd_compliant", False),
                "data_classification": project.governance_approval.get("data_classification")
            },
            "quality": {
                "average_score": sum(
                    r["report"]["overall_score"] 
                    for r in project.quality_reports
                ) / len(project.quality_reports) if project.quality_reports else None,
                "reports_count": len(project.quality_reports)
            },
            "cost": project.cost_estimate,
            "timeline": [
                {
                    "phase": cp.phase.value,
                    "status": cp.status.value,
                    "timestamp": cp.timestamp
                }
                for cp in project.checkpoints
            ]
        }
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Retorna status atual do projeto."""
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Projeto não encontrado"}
        
        return {
            "project_id": project.id,
            "name": project.name,
            "current_phase": project.current_phase.value,
            "status": project.status.value,
            "last_checkpoint": project.checkpoints[-1].details if project.checkpoints else None
        }
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard geral de todos os projetos."""
        projects_by_status = {}
        for status in WorkflowStatus:
            projects_by_status[status.value] = len([
                p for p in self.projects.values() 
                if p.status == status
            ])
        
        projects_by_phase = {}
        for phase in WorkflowPhase:
            projects_by_phase[phase.value] = len([
                p for p in self.projects.values() 
                if p.current_phase == phase and p.status == WorkflowStatus.IN_PROGRESS
            ])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_projects": len(self.projects),
            "by_status": projects_by_status,
            "by_phase": projects_by_phase,
            "observability": self.observability.get_dashboard_data(),
            "recent_projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "phase": p.current_phase.value,
                    "status": p.status.value
                }
                for p in sorted(
                    self.projects.values(),
                    key=lambda x: x.created_at,
                    reverse=True
                )[:10]
            ]
        }


# Singleton
_integrated_workflow: Optional[IntegratedWorkflow] = None


def get_integrated_workflow() -> IntegratedWorkflow:
    """Retorna instância singleton do IntegratedWorkflow."""
    global _integrated_workflow
    if _integrated_workflow is None:
        _integrated_workflow = IntegratedWorkflow()
    return _integrated_workflow
