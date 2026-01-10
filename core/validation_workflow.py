"""
Validation Workflow Module

Este módulo implementa o fluxo de validação contínua:
- QA: Valida qualidade técnica de cada entrega
- PO: Valida se a entrega atende aos requisitos de negócio

Cada entrega passa por este fluxo antes de ser considerada completa.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class ValidationStatus(Enum):
    """Status de validação."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class ValidationCategory(Enum):
    """Categorias de validação."""
    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DATA_QUALITY = "data_quality"
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    BUSINESS_VALUE = "business_value"
    USER_ACCEPTANCE = "user_acceptance"


@dataclass
class ValidationCriterion:
    """Critério de validação."""
    id: str
    category: ValidationCategory
    description: str
    is_mandatory: bool
    passed: Optional[bool] = None
    notes: str = ""
    evidence: str = ""


@dataclass
class QAValidationReport:
    """Relatório de validação do QA."""
    task_id: str
    task_name: str
    validated_by: str
    validated_at: datetime
    status: ValidationStatus
    criteria: List[ValidationCriterion]
    test_results: Dict[str, Any]
    quality_score: float  # 0.0 a 1.0
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    can_proceed: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "validated_by": self.validated_by,
            "validated_at": self.validated_at.isoformat(),
            "status": self.status.value,
            "quality_score": self.quality_score,
            "issues_count": len(self.issues_found),
            "can_proceed": self.can_proceed,
            "criteria_passed": sum(1 for c in self.criteria if c.passed),
            "criteria_total": len(self.criteria)
        }


@dataclass
class POValidationReport:
    """Relatório de validação do PO."""
    task_id: str
    task_name: str
    validated_by: str
    validated_at: datetime
    status: ValidationStatus
    meets_requirements: bool
    acceptance_criteria: List[Dict[str, Any]]
    business_value_score: float  # 0.0 a 1.0
    user_feedback: str
    stakeholder_approval: bool
    can_release: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "validated_by": self.validated_by,
            "validated_at": self.validated_at.isoformat(),
            "status": self.status.value,
            "meets_requirements": self.meets_requirements,
            "business_value_score": self.business_value_score,
            "can_release": self.can_release,
            "criteria_met": sum(1 for c in self.acceptance_criteria if c.get("met")),
            "criteria_total": len(self.acceptance_criteria)
        }


class QAValidator:
    """
    Validador de QA - Responsável pela validação técnica.
    
    Verifica:
    - Funcionalidade (testes passando)
    - Performance (dentro dos limites)
    - Segurança (sem vulnerabilidades)
    - Qualidade de dados (se aplicável)
    - Qualidade de código (padrões seguidos)
    - Documentação (completa e atualizada)
    """
    
    def __init__(self):
        self.validation_history: List[QAValidationReport] = []
    
    def create_validation_criteria(self, task_type: str) -> List[ValidationCriterion]:
        """Cria critérios de validação baseados no tipo de tarefa."""
        base_criteria = [
            ValidationCriterion(
                id="func_01",
                category=ValidationCategory.FUNCTIONALITY,
                description="Todos os testes unitários passando",
                is_mandatory=True
            ),
            ValidationCriterion(
                id="func_02",
                category=ValidationCategory.FUNCTIONALITY,
                description="Testes de integração executados com sucesso",
                is_mandatory=True
            ),
            ValidationCriterion(
                id="code_01",
                category=ValidationCategory.CODE_QUALITY,
                description="Código segue padrões de estilo definidos",
                is_mandatory=False
            ),
            ValidationCriterion(
                id="code_02",
                category=ValidationCategory.CODE_QUALITY,
                description="Sem code smells críticos",
                is_mandatory=True
            ),
            ValidationCriterion(
                id="doc_01",
                category=ValidationCategory.DOCUMENTATION,
                description="Documentação técnica atualizada",
                is_mandatory=True
            ),
            ValidationCriterion(
                id="sec_01",
                category=ValidationCategory.SECURITY,
                description="Sem vulnerabilidades de segurança conhecidas",
                is_mandatory=True
            )
        ]
        
        # Adiciona critérios específicos por tipo
        if task_type in ["data_pipeline", "etl"]:
            base_criteria.extend([
                ValidationCriterion(
                    id="dq_01",
                    category=ValidationCategory.DATA_QUALITY,
                    description="Validações de schema implementadas",
                    is_mandatory=True
                ),
                ValidationCriterion(
                    id="dq_02",
                    category=ValidationCategory.DATA_QUALITY,
                    description="Testes de qualidade de dados passando",
                    is_mandatory=True
                ),
                ValidationCriterion(
                    id="dq_03",
                    category=ValidationCategory.DATA_QUALITY,
                    description="Linhagem de dados documentada",
                    is_mandatory=False
                )
            ])
        
        if task_type in ["ml_model", "machine_learning"]:
            base_criteria.extend([
                ValidationCriterion(
                    id="ml_01",
                    category=ValidationCategory.FUNCTIONALITY,
                    description="Métricas de modelo dentro do threshold",
                    is_mandatory=True
                ),
                ValidationCriterion(
                    id="ml_02",
                    category=ValidationCategory.FUNCTIONALITY,
                    description="Testes de drift implementados",
                    is_mandatory=False
                ),
                ValidationCriterion(
                    id="ml_03",
                    category=ValidationCategory.DOCUMENTATION,
                    description="Model card documentado",
                    is_mandatory=True
                )
            ])
        
        if task_type in ["infrastructure", "deployment"]:
            base_criteria.extend([
                ValidationCriterion(
                    id="infra_01",
                    category=ValidationCategory.SECURITY,
                    description="Configurações de segurança validadas",
                    is_mandatory=True
                ),
                ValidationCriterion(
                    id="infra_02",
                    category=ValidationCategory.PERFORMANCE,
                    description="Monitoramento e alertas configurados",
                    is_mandatory=True
                ),
                ValidationCriterion(
                    id="infra_03",
                    category=ValidationCategory.DOCUMENTATION,
                    description="Runbooks operacionais documentados",
                    is_mandatory=True
                )
            ])
        
        return base_criteria
    
    def validate(
        self,
        task_id: str,
        task_name: str,
        task_type: str,
        deliverables: List[str],
        test_results: Dict[str, Any],
        code_analysis: Optional[Dict[str, Any]] = None
    ) -> QAValidationReport:
        """
        Executa validação de QA em uma entrega.
        """
        criteria = self.create_validation_criteria(task_type)
        issues_found = []
        recommendations = []
        
        # Simula validação dos critérios
        for criterion in criteria:
            # Em produção, isso seria baseado em resultados reais de testes
            if criterion.category == ValidationCategory.FUNCTIONALITY:
                criterion.passed = test_results.get("all_tests_passed", False)
                if not criterion.passed:
                    issues_found.append({
                        "criterion_id": criterion.id,
                        "severity": "high" if criterion.is_mandatory else "medium",
                        "description": f"Falha em: {criterion.description}"
                    })
            
            elif criterion.category == ValidationCategory.CODE_QUALITY:
                criterion.passed = code_analysis.get("quality_score", 0) > 0.7 if code_analysis else True
                if not criterion.passed:
                    recommendations.append("Melhorar qualidade do código antes do próximo release")
            
            elif criterion.category == ValidationCategory.SECURITY:
                criterion.passed = not test_results.get("security_vulnerabilities", False)
                if not criterion.passed:
                    issues_found.append({
                        "criterion_id": criterion.id,
                        "severity": "critical",
                        "description": "Vulnerabilidades de segurança detectadas"
                    })
            
            elif criterion.category == ValidationCategory.DATA_QUALITY:
                criterion.passed = test_results.get("data_quality_score", 0) > 0.9
                if not criterion.passed:
                    issues_found.append({
                        "criterion_id": criterion.id,
                        "severity": "high",
                        "description": "Problemas de qualidade de dados detectados"
                    })
            
            elif criterion.category == ValidationCategory.DOCUMENTATION:
                criterion.passed = test_results.get("documentation_complete", True)
            
            elif criterion.category == ValidationCategory.PERFORMANCE:
                criterion.passed = test_results.get("performance_ok", True)
            
            else:
                criterion.passed = True
        
        # Calcula score de qualidade
        mandatory_passed = sum(1 for c in criteria if c.is_mandatory and c.passed)
        mandatory_total = sum(1 for c in criteria if c.is_mandatory)
        optional_passed = sum(1 for c in criteria if not c.is_mandatory and c.passed)
        optional_total = sum(1 for c in criteria if not c.is_mandatory)
        
        mandatory_score = mandatory_passed / mandatory_total if mandatory_total > 0 else 1.0
        optional_score = optional_passed / optional_total if optional_total > 0 else 1.0
        
        quality_score = (mandatory_score * 0.8) + (optional_score * 0.2)
        
        # Determina status
        critical_issues = [i for i in issues_found if i.get("severity") == "critical"]
        high_issues = [i for i in issues_found if i.get("severity") == "high"]
        
        if critical_issues:
            status = ValidationStatus.REJECTED
            can_proceed = False
        elif high_issues and mandatory_score < 1.0:
            status = ValidationStatus.NEEDS_REVISION
            can_proceed = False
        elif mandatory_score == 1.0:
            status = ValidationStatus.APPROVED
            can_proceed = True
        else:
            status = ValidationStatus.NEEDS_REVISION
            can_proceed = False
        
        report = QAValidationReport(
            task_id=task_id,
            task_name=task_name,
            validated_by="QA Team",
            validated_at=datetime.now(),
            status=status,
            criteria=criteria,
            test_results=test_results,
            quality_score=quality_score,
            issues_found=issues_found,
            recommendations=recommendations,
            can_proceed=can_proceed
        )
        
        self.validation_history.append(report)
        return report
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Retorna resumo das validações."""
        if not self.validation_history:
            return {"total": 0, "approved": 0, "rejected": 0}
        
        return {
            "total": len(self.validation_history),
            "approved": sum(1 for r in self.validation_history if r.status == ValidationStatus.APPROVED),
            "rejected": sum(1 for r in self.validation_history if r.status == ValidationStatus.REJECTED),
            "needs_revision": sum(1 for r in self.validation_history if r.status == ValidationStatus.NEEDS_REVISION),
            "average_quality_score": sum(r.quality_score for r in self.validation_history) / len(self.validation_history)
        }


class POValidator:
    """
    Validador de PO - Responsável pela validação de negócio.
    
    Verifica:
    - Atendimento aos requisitos do cliente
    - Critérios de aceitação
    - Valor de negócio entregue
    - Feedback do usuário
    - Aprovação de stakeholders
    """
    
    def __init__(self):
        self.validation_history: List[POValidationReport] = []
    
    def create_acceptance_criteria(
        self,
        task_name: str,
        original_requirements: List[str]
    ) -> List[Dict[str, Any]]:
        """Cria critérios de aceitação baseados nos requisitos."""
        criteria = []
        
        for i, req in enumerate(original_requirements):
            criteria.append({
                "id": f"ac_{i+1:02d}",
                "requirement": req,
                "met": None,
                "evidence": "",
                "notes": ""
            })
        
        # Adiciona critérios padrão
        criteria.extend([
            {
                "id": "ac_std_01",
                "requirement": "Funcionalidade atende à necessidade do usuário",
                "met": None,
                "evidence": "",
                "notes": ""
            },
            {
                "id": "ac_std_02",
                "requirement": "Interface/output é intuitivo e utilizável",
                "met": None,
                "evidence": "",
                "notes": ""
            },
            {
                "id": "ac_std_03",
                "requirement": "Documentação de usuário disponível",
                "met": None,
                "evidence": "",
                "notes": ""
            }
        ])
        
        return criteria
    
    def validate(
        self,
        task_id: str,
        task_name: str,
        original_requirements: List[str],
        deliverables: List[str],
        demo_feedback: Optional[str] = None,
        stakeholder_comments: Optional[List[str]] = None
    ) -> POValidationReport:
        """
        Executa validação de PO em uma entrega.
        """
        acceptance_criteria = self.create_acceptance_criteria(task_name, original_requirements)
        
        # Simula validação dos critérios
        # Em produção, isso seria baseado em feedback real do cliente/stakeholders
        criteria_met = 0
        for criterion in acceptance_criteria:
            # Simula avaliação (em produção, seria input do PO)
            criterion["met"] = True  # Assume aprovado para demo
            if criterion["met"]:
                criteria_met += 1
        
        meets_requirements = criteria_met >= len(acceptance_criteria) * 0.8
        
        # Calcula score de valor de negócio
        business_value_score = criteria_met / len(acceptance_criteria) if acceptance_criteria else 0.0
        
        # Determina status
        if business_value_score >= 0.9:
            status = ValidationStatus.APPROVED
            can_release = True
        elif business_value_score >= 0.7:
            status = ValidationStatus.NEEDS_REVISION
            can_release = False
        else:
            status = ValidationStatus.REJECTED
            can_release = False
        
        report = POValidationReport(
            task_id=task_id,
            task_name=task_name,
            validated_by="PO Team",
            validated_at=datetime.now(),
            status=status,
            meets_requirements=meets_requirements,
            acceptance_criteria=acceptance_criteria,
            business_value_score=business_value_score,
            user_feedback=demo_feedback or "Aguardando feedback",
            stakeholder_approval=status == ValidationStatus.APPROVED,
            can_release=can_release
        )
        
        self.validation_history.append(report)
        return report
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Retorna resumo das validações."""
        if not self.validation_history:
            return {"total": 0, "approved": 0, "rejected": 0}
        
        return {
            "total": len(self.validation_history),
            "approved": sum(1 for r in self.validation_history if r.status == ValidationStatus.APPROVED),
            "rejected": sum(1 for r in self.validation_history if r.status == ValidationStatus.REJECTED),
            "needs_revision": sum(1 for r in self.validation_history if r.status == ValidationStatus.NEEDS_REVISION),
            "average_business_value": sum(r.business_value_score for r in self.validation_history) / len(self.validation_history)
        }


class ValidationWorkflow:
    """
    Orquestra o fluxo completo de validação.
    
    Fluxo:
    1. Tarefa concluída pelo time de desenvolvimento
    2. QA valida qualidade técnica
    3. Se aprovado pelo QA, PO valida valor de negócio
    4. Se aprovado pelo PO, tarefa é marcada como completa
    5. Se rejeitado em qualquer etapa, volta para o time com feedback
    """
    
    def __init__(self):
        self.qa_validator = QAValidator()
        self.po_validator = POValidator()
        self.workflow_history: List[Dict[str, Any]] = []
    
    def submit_for_validation(
        self,
        task_id: str,
        task_name: str,
        task_type: str,
        assigned_team: str,
        deliverables: List[str],
        original_requirements: List[str],
        test_results: Dict[str, Any],
        code_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submete uma tarefa para o fluxo de validação completo.
        """
        workflow_result = {
            "task_id": task_id,
            "task_name": task_name,
            "submitted_at": datetime.now().isoformat(),
            "qa_validation": None,
            "po_validation": None,
            "final_status": "pending",
            "can_proceed": False,
            "feedback": []
        }
        
        # Etapa 1: Validação do QA
        print(f"\n🔍 [QA] Iniciando validação técnica de '{task_name}'...")
        qa_report = self.qa_validator.validate(
            task_id=task_id,
            task_name=task_name,
            task_type=task_type,
            deliverables=deliverables,
            test_results=test_results,
            code_analysis=code_analysis
        )
        
        workflow_result["qa_validation"] = qa_report.to_dict()
        
        if not qa_report.can_proceed:
            workflow_result["final_status"] = "qa_rejected"
            workflow_result["feedback"].append({
                "from": "QA",
                "message": f"Validação técnica falhou. Issues: {len(qa_report.issues_found)}",
                "issues": qa_report.issues_found,
                "recommendations": qa_report.recommendations
            })
            print(f"   ❌ QA rejeitou: {len(qa_report.issues_found)} issues encontrados")
            self.workflow_history.append(workflow_result)
            return workflow_result
        
        print(f"   ✅ QA aprovou (Score: {qa_report.quality_score:.1%})")
        
        # Etapa 2: Validação do PO
        print(f"\n📋 [PO] Iniciando validação de negócio de '{task_name}'...")
        po_report = self.po_validator.validate(
            task_id=task_id,
            task_name=task_name,
            original_requirements=original_requirements,
            deliverables=deliverables
        )
        
        workflow_result["po_validation"] = po_report.to_dict()
        
        if not po_report.can_release:
            workflow_result["final_status"] = "po_rejected"
            workflow_result["feedback"].append({
                "from": "PO",
                "message": f"Validação de negócio falhou. Requisitos não atendidos.",
                "criteria_failed": [c for c in po_report.acceptance_criteria if not c.get("met")]
            })
            print(f"   ❌ PO rejeitou: Requisitos não atendidos")
            self.workflow_history.append(workflow_result)
            return workflow_result
        
        print(f"   ✅ PO aprovou (Score: {po_report.business_value_score:.1%})")
        
        # Etapa 3: Aprovação final
        workflow_result["final_status"] = "approved"
        workflow_result["can_proceed"] = True
        workflow_result["feedback"].append({
            "from": "Workflow",
            "message": "Tarefa aprovada por QA e PO. Pronta para próxima fase."
        })
        
        print(f"\n✅ '{task_name}' aprovada e pronta para prosseguir!")
        
        self.workflow_history.append(workflow_result)
        return workflow_result
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Retorna resumo do workflow de validação."""
        if not self.workflow_history:
            return {"total": 0}
        
        return {
            "total_submissions": len(self.workflow_history),
            "approved": sum(1 for w in self.workflow_history if w["final_status"] == "approved"),
            "qa_rejected": sum(1 for w in self.workflow_history if w["final_status"] == "qa_rejected"),
            "po_rejected": sum(1 for w in self.workflow_history if w["final_status"] == "po_rejected"),
            "qa_summary": self.qa_validator.get_validation_summary(),
            "po_summary": self.po_validator.get_validation_summary()
        }


# Singletons
_qa_validator: Optional[QAValidator] = None
_po_validator: Optional[POValidator] = None
_validation_workflow: Optional[ValidationWorkflow] = None


def get_qa_validator() -> QAValidator:
    """Obtém instância singleton do QA Validator."""
    global _qa_validator
    if _qa_validator is None:
        _qa_validator = QAValidator()
    return _qa_validator


def get_po_validator() -> POValidator:
    """Obtém instância singleton do PO Validator."""
    global _po_validator
    if _po_validator is None:
        _po_validator = POValidator()
    return _po_validator


def get_validation_workflow() -> ValidationWorkflow:
    """Obtém instância singleton do Validation Workflow."""
    global _validation_workflow
    if _validation_workflow is None:
        _validation_workflow = ValidationWorkflow()
    return _validation_workflow


if __name__ == "__main__":
    # Demo do Validation Workflow
    print("\n" + "=" * 60)
    print("  DEMO: Validation Workflow (QA + PO)")
    print("=" * 60)
    
    workflow = get_validation_workflow()
    
    # Simula submissão de uma tarefa
    result = workflow.submit_for_validation(
        task_id="task_001",
        task_name="Implementação de Data Pipeline",
        task_type="data_pipeline",
        assigned_team="data_engineering",
        deliverables=["Pipeline ETL", "Testes automatizados", "Documentação"],
        original_requirements=[
            "Ingerir dados de 3 fontes",
            "Transformar para formato dimensional",
            "Carregar no data warehouse"
        ],
        test_results={
            "all_tests_passed": True,
            "data_quality_score": 0.95,
            "documentation_complete": True,
            "security_vulnerabilities": False
        },
        code_analysis={
            "quality_score": 0.85
        }
    )
    
    print("\n📊 Resultado do Workflow:")
    print(f"   Status Final: {result['final_status']}")
    print(f"   Pode Prosseguir: {result['can_proceed']}")
    
    print("\n" + "=" * 60)
