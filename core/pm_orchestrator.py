"""
PM Orchestrator Module

Este módulo implementa o Project Manager como orquestrador central que:
- Cria e gerencia cronogramas de projeto
- Define dependências entre tarefas
- Identifica tarefas paralelas
- Coordena a execução entre times
- Monitora progresso e riscos
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

from .task_orchestrator import (
    TaskOrchestrator,
    TaskStatus,
    TaskPriority,
    TaskType,
    Task,
    ProjectSchedule,
    get_task_orchestrator
)


class ProjectPhase(Enum):
    """Fases de um projeto de dados."""
    INITIATION = "initiation"
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    CLOSURE = "closure"


class RiskLevel(Enum):
    """Nível de risco."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Risk:
    """Representa um risco do projeto."""
    id: str
    description: str
    level: RiskLevel
    probability: float  # 0.0 a 1.0
    impact: float  # 0.0 a 1.0
    mitigation: str
    owner: str
    status: str = "open"  # open, mitigated, closed


@dataclass
class Milestone:
    """Representa um marco do projeto."""
    id: str
    name: str
    description: str
    target_date: datetime
    deliverables: List[str]
    dependencies: List[str]  # IDs de tarefas que devem estar completas
    status: str = "pending"  # pending, achieved, missed


@dataclass
class TeamAssignment:
    """Atribuição de time a uma fase."""
    team_name: str
    phase: ProjectPhase
    tasks: List[str]
    estimated_hours: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class PMOrchestrator:
    """
    Project Manager Orchestrator - Coordena todo o fluxo do projeto.
    
    Responsabilidades:
    1. Criar cronograma baseado nos requisitos
    2. Definir ordem de execução (arquitetura primeiro)
    3. Identificar tarefas paralelas
    4. Coordenar handoffs entre times
    5. Monitorar progresso e riscos
    6. Garantir que QA e PO validem cada entrega
    """
    
    def __init__(self):
        self.task_orchestrator = get_task_orchestrator()
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.risks: Dict[str, List[Risk]] = {}
        self.milestones: Dict[str, List[Milestone]] = {}
    
    def create_project(
        self,
        project_id: str,
        project_name: str,
        description: str,
        client_requirements: str,
        target_end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Cria um novo projeto e gera o cronograma inicial.
        """
        # Cria o cronograma no task orchestrator
        schedule = self.task_orchestrator.create_project_schedule(
            project_id=project_id,
            project_name=project_name,
            target_end_date=target_end_date
        )
        
        # Armazena metadados do projeto
        self.projects[project_id] = {
            "id": project_id,
            "name": project_name,
            "description": description,
            "client_requirements": client_requirements,
            "created_at": datetime.now().isoformat(),
            "current_phase": ProjectPhase.INITIATION.value,
            "status": "active"
        }
        
        # Inicializa riscos e milestones
        self.risks[project_id] = []
        self.milestones[project_id] = []
        
        return self.projects[project_id]
    
    def analyze_requirements_and_create_schedule(
        self,
        project_id: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analisa os requisitos e cria um cronograma otimizado.
        
        O PM segue esta ordem:
        1. Arquitetura (sempre primeiro - decisões estratégicas)
        2. Infraestrutura + Design de Dados (podem ser paralelos)
        3. Implementação (depende de infra e design)
        4. ML/Analytics (depende de dados)
        5. Testes e Deploy
        
        Cada entrega passa por:
        - QA (validação técnica)
        - PO (validação de negócio)
        """
        
        if project_id not in self.projects:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        # Extrai informações dos requisitos
        has_ml = requirements.get("has_ml", False)
        has_streaming = requirements.get("has_streaming", False)
        has_analytics = requirements.get("has_analytics", True)
        data_volume = requirements.get("data_volume", "medium")
        team_size = requirements.get("team_size", 3)
        
        # Calcula estimativas baseadas no escopo
        base_hours = self._calculate_base_hours(data_volume, team_size)
        
        tasks_created = []
        
        # ========== FASE 1: ARQUITETURA (CRÍTICO - SEMPRE PRIMEIRO) ==========
        arch_task = self.task_orchestrator.create_task(
            project_id=project_id,
            name="Definição de Arquitetura de Solução",
            description="""
            Definir arquitetura completa incluindo:
            - Escolha de tecnologias e cloud provider
            - Estimativa de custos (mensal e anual)
            - Plano de escalabilidade
            - Estratégia de portabilidade e migração
            - Requisitos de segurança e compliance
            - Diagrama de componentes e integrações
            """,
            task_type=TaskType.ARCHITECTURE,
            assigned_team="architecture",
            estimated_hours=base_hours["architecture"],
            priority=TaskPriority.CRITICAL,
            requires_qa=True,
            requires_po=True,
            deliverables=[
                "Documento de Arquitetura (ADR)",
                "Diagrama de Componentes",
                "Estimativa de Custos",
                "Plano de Escalabilidade",
                "Análise de Riscos Técnicos"
            ],
            tags=["arquitetura", "estratégico", "fase1"]
        )
        tasks_created.append(arch_task)
        
        # ========== FASE 2A: INFRAESTRUTURA (após arquitetura) ==========
        infra_task = self.task_orchestrator.create_task(
            project_id=project_id,
            name="Provisionamento de Infraestrutura",
            description="""
            Provisionar infraestrutura conforme arquitetura aprovada:
            - Configurar ambiente cloud
            - Implementar IaC (Terraform/Pulumi)
            - Configurar networking e segurança
            - Setup de CI/CD
            - Configurar monitoramento base
            """,
            task_type=TaskType.INFRASTRUCTURE,
            assigned_team="devops",
            estimated_hours=base_hours["infrastructure"],
            priority=TaskPriority.HIGH,
            dependencies=[arch_task.id],
            requires_qa=True,
            requires_po=False,  # Infra não precisa validação de negócio
            deliverables=[
                "Infraestrutura provisionada",
                "Scripts IaC versionados",
                "Pipeline CI/CD configurado",
                "Documentação de deploy"
            ],
            tags=["infraestrutura", "devops", "fase2"]
        )
        tasks_created.append(infra_task)
        
        # ========== FASE 2B: DESIGN DE DADOS (paralelo com infra) ==========
        data_design_task = self.task_orchestrator.create_task(
            project_id=project_id,
            name="Design de Modelo de Dados e Pipelines",
            description="""
            Projetar modelo de dados e pipelines:
            - Modelagem dimensional/relacional
            - Design de pipelines ETL/ELT
            - Definição de schemas e contratos
            - Estratégia de qualidade de dados
            - Documentação de linhagem
            """,
            task_type=TaskType.DATA_PIPELINE,
            assigned_team="data_engineering",
            estimated_hours=base_hours["data_design"],
            priority=TaskPriority.HIGH,
            dependencies=[arch_task.id],  # Só depende de arquitetura, paralelo com infra
            requires_qa=True,
            requires_po=True,
            deliverables=[
                "Modelo de dados documentado",
                "Diagrama de pipelines",
                "Contratos de dados (schemas)",
                "Estratégia de data quality"
            ],
            tags=["dados", "design", "fase2"]
        )
        tasks_created.append(data_design_task)
        
        # ========== FASE 3: IMPLEMENTAÇÃO DE PIPELINES ==========
        pipeline_impl_task = self.task_orchestrator.create_task(
            project_id=project_id,
            name="Implementação de Data Pipelines",
            description="""
            Implementar pipelines de dados:
            - Desenvolver jobs de ingestão
            - Implementar transformações
            - Configurar orquestração (Airflow/Dagster)
            - Implementar testes de dados
            - Configurar monitoramento de pipelines
            """,
            task_type=TaskType.DATA_PIPELINE,
            assigned_team="data_engineering",
            estimated_hours=base_hours["pipeline_impl"],
            priority=TaskPriority.HIGH,
            dependencies=[infra_task.id, data_design_task.id],  # Precisa de infra E design
            requires_qa=True,
            requires_po=True,
            deliverables=[
                "Pipelines implementados e testados",
                "Documentação técnica",
                "Testes automatizados",
                "Runbooks operacionais"
            ],
            tags=["dados", "implementação", "fase3"]
        )
        tasks_created.append(pipeline_impl_task)
        
        # ========== FASE 4: ML/ANALYTICS (condicional) ==========
        if has_ml:
            ml_task = self.task_orchestrator.create_task(
                project_id=project_id,
                name="Desenvolvimento de Modelos de ML",
                description="""
                Desenvolver e treinar modelos de ML:
                - Feature engineering
                - Treinamento e validação de modelos
                - Otimização de hiperparâmetros
                - Setup de MLOps (MLflow/Kubeflow)
                - API de inferência
                """,
                task_type=TaskType.ML_MODEL,
                assigned_team="data_science",
                estimated_hours=base_hours["ml"],
                priority=TaskPriority.MEDIUM,
                dependencies=[pipeline_impl_task.id],
                requires_qa=True,
                requires_po=True,
                deliverables=[
                    "Modelos treinados e versionados",
                    "Métricas de performance",
                    "API de inferência",
                    "Documentação de features"
                ],
                tags=["ml", "modelo", "fase4"]
            )
            tasks_created.append(ml_task)
            last_impl_task = ml_task
        else:
            last_impl_task = pipeline_impl_task
        
        if has_analytics:
            analytics_task = self.task_orchestrator.create_task(
                project_id=project_id,
                name="Desenvolvimento de Analytics e Dashboards",
                description="""
                Criar camada de analytics:
                - Desenvolver queries analíticas
                - Criar dashboards e relatórios
                - Implementar KPIs e métricas
                - Configurar alertas de negócio
                """,
                task_type=TaskType.DEVELOPMENT,
                assigned_team="data_analytics",
                estimated_hours=base_hours["analytics"],
                priority=TaskPriority.MEDIUM,
                dependencies=[pipeline_impl_task.id],  # Paralelo com ML se houver
                requires_qa=True,
                requires_po=True,
                deliverables=[
                    "Dashboards implementados",
                    "Relatórios automatizados",
                    "Documentação de métricas"
                ],
                tags=["analytics", "dashboards", "fase4"]
            )
            tasks_created.append(analytics_task)
            if not has_ml:
                last_impl_task = analytics_task
        
        # ========== FASE 5: TESTES INTEGRADOS ==========
        integration_test_task = self.task_orchestrator.create_task(
            project_id=project_id,
            name="Testes Integrados e Validação",
            description="""
            Executar testes integrados:
            - Testes end-to-end
            - Testes de performance
            - Validação de data quality
            - Testes de segurança
            - User acceptance testing (UAT)
            """,
            task_type=TaskType.TESTING,
            assigned_team="qa",
            estimated_hours=base_hours["testing"],
            priority=TaskPriority.HIGH,
            dependencies=[last_impl_task.id],
            requires_qa=False,  # É o próprio QA executando
            requires_po=True,
            deliverables=[
                "Relatório de testes",
                "Evidências de qualidade",
                "Lista de issues resolvidos",
                "Sign-off de UAT"
            ],
            tags=["testes", "qualidade", "fase5"]
        )
        tasks_created.append(integration_test_task)
        
        # ========== FASE 6: DEPLOY PRODUÇÃO ==========
        deploy_task = self.task_orchestrator.create_task(
            project_id=project_id,
            name="Deploy em Produção",
            description="""
            Deploy da solução em produção:
            - Executar runbook de deploy
            - Configurar monitoramento de produção
            - Ativar alertas
            - Validar smoke tests
            - Handover para operações
            """,
            task_type=TaskType.DEPLOYMENT,
            assigned_team="devops",
            estimated_hours=base_hours["deploy"],
            priority=TaskPriority.CRITICAL,
            dependencies=[integration_test_task.id],
            requires_qa=True,
            requires_po=True,
            deliverables=[
                "Solução em produção",
                "Monitoramento ativo",
                "Documentação operacional",
                "Plano de rollback testado"
            ],
            tags=["deploy", "produção", "fase6"]
        )
        tasks_created.append(deploy_task)
        
        # Gera o plano de execução
        execution_plan = self.task_orchestrator.generate_execution_plan(project_id)
        
        # Adiciona informações do PM
        execution_plan["pm_analysis"] = {
            "total_phases": 6,
            "parallel_opportunities": self._identify_parallel_opportunities(tasks_created),
            "critical_path_tasks": [t.name for t in tasks_created if t.priority == TaskPriority.CRITICAL],
            "validation_checkpoints": len([t for t in tasks_created if t.requires_qa or t.requires_po]),
            "estimated_duration_weeks": self._estimate_duration_weeks(execution_plan["total_estimated_hours"], team_size)
        }
        
        return execution_plan
    
    def _calculate_base_hours(self, data_volume: str, team_size: int) -> Dict[str, float]:
        """Calcula horas base por tipo de tarefa."""
        multiplier = {
            "small": 0.5,
            "medium": 1.0,
            "large": 2.0,
            "enterprise": 3.0
        }.get(data_volume, 1.0)
        
        return {
            "architecture": 16 * multiplier,
            "infrastructure": 24 * multiplier,
            "data_design": 16 * multiplier,
            "pipeline_impl": 40 * multiplier,
            "ml": 32 * multiplier,
            "analytics": 24 * multiplier,
            "testing": 16 * multiplier,
            "deploy": 8 * multiplier
        }
    
    def _identify_parallel_opportunities(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Identifica oportunidades de paralelização."""
        opportunities = []
        
        # Agrupa tarefas por dependências
        dep_groups: Dict[str, List[Task]] = {}
        for task in tasks:
            dep_key = ",".join(sorted([d.task_id for d in task.dependencies])) if task.dependencies else "none"
            if dep_key not in dep_groups:
                dep_groups[dep_key] = []
            dep_groups[dep_key].append(task)
        
        for dep_key, group_tasks in dep_groups.items():
            if len(group_tasks) > 1:
                opportunities.append({
                    "tasks": [t.name for t in group_tasks],
                    "teams": list(set(t.assigned_team for t in group_tasks)),
                    "can_parallelize": True,
                    "dependency": dep_key if dep_key != "none" else "Sem dependências"
                })
        
        return opportunities
    
    def _estimate_duration_weeks(self, total_hours: float, team_size: int) -> float:
        """Estima duração em semanas."""
        hours_per_week = 40 * team_size * 0.7  # 70% de eficiência
        return round(total_hours / hours_per_week, 1)
    
    def add_risk(
        self,
        project_id: str,
        description: str,
        level: RiskLevel,
        probability: float,
        impact: float,
        mitigation: str,
        owner: str
    ) -> Risk:
        """Adiciona um risco ao projeto."""
        if project_id not in self.risks:
            self.risks[project_id] = []
        
        risk = Risk(
            id=f"risk_{len(self.risks[project_id]) + 1:03d}",
            description=description,
            level=level,
            probability=probability,
            impact=impact,
            mitigation=mitigation,
            owner=owner
        )
        
        self.risks[project_id].append(risk)
        return risk
    
    def add_milestone(
        self,
        project_id: str,
        name: str,
        description: str,
        target_date: datetime,
        deliverables: List[str],
        dependencies: List[str]
    ) -> Milestone:
        """Adiciona um milestone ao projeto."""
        if project_id not in self.milestones:
            self.milestones[project_id] = []
        
        milestone = Milestone(
            id=f"ms_{len(self.milestones[project_id]) + 1:03d}",
            name=name,
            description=description,
            target_date=target_date,
            deliverables=deliverables,
            dependencies=dependencies
        )
        
        self.milestones[project_id].append(milestone)
        return milestone
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Retorna o status completo do projeto."""
        if project_id not in self.projects:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        schedule = self.task_orchestrator.schedules.get(project_id)
        progress = schedule.get_progress() if schedule else {}
        
        validation_queue = self.task_orchestrator.get_validation_queue(project_id)
        team_workload = self.task_orchestrator.get_team_workload(project_id)
        
        return {
            "project": self.projects[project_id],
            "progress": progress,
            "validation_queue": validation_queue,
            "team_workload": team_workload,
            "risks": [
                {
                    "id": r.id,
                    "description": r.description,
                    "level": r.level.value,
                    "status": r.status
                }
                for r in self.risks.get(project_id, [])
            ],
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "target_date": m.target_date.isoformat(),
                    "status": m.status
                }
                for m in self.milestones.get(project_id, [])
            ],
            "next_actions": self._get_next_actions(project_id)
        }
    
    def _get_next_actions(self, project_id: str) -> List[Dict[str, Any]]:
        """Identifica as próximas ações necessárias."""
        actions = []
        
        schedule = self.task_orchestrator.schedules.get(project_id)
        if not schedule:
            return actions
        
        # Tarefas prontas para iniciar
        ready_tasks = schedule.get_ready_tasks()
        for task in ready_tasks[:3]:  # Top 3
            actions.append({
                "type": "start_task",
                "task_id": task.id,
                "task_name": task.name,
                "assigned_team": task.assigned_team,
                "priority": task.priority.value
            })
        
        # Validações pendentes
        validation_queue = self.task_orchestrator.get_validation_queue(project_id)
        for task in validation_queue.get("qa_queue", [])[:2]:
            actions.append({
                "type": "qa_validation",
                "task_id": task["id"],
                "task_name": task["name"],
                "assigned_team": "qa"
            })
        
        for task in validation_queue.get("po_queue", [])[:2]:
            actions.append({
                "type": "po_validation",
                "task_id": task["id"],
                "task_name": task["name"],
                "assigned_team": "product_owner"
            })
        
        return actions
    
    def generate_gantt_data(self, project_id: str) -> Dict[str, Any]:
        """Gera dados para visualização de Gantt."""
        if project_id not in self.projects:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        schedule = self.task_orchestrator.schedules.get(project_id)
        if not schedule:
            return {"tasks": [], "dependencies": []}
        
        gantt_tasks = []
        dependencies = []
        
        # Calcula datas baseado em ordem de execução
        execution_plan = self.task_orchestrator.generate_execution_plan(project_id)
        current_date = datetime.now()
        
        for level_data in execution_plan["execution_levels"]:
            level_start = current_date
            max_duration = 0
            
            for task_data in level_data["tasks"]:
                task = schedule.tasks[task_data["id"]]
                duration_days = int(task.estimated_hours / 8)  # 8 horas por dia
                
                gantt_tasks.append({
                    "id": task.id,
                    "name": task.name,
                    "team": task.assigned_team,
                    "start": level_start.isoformat(),
                    "end": (level_start + timedelta(days=duration_days)).isoformat(),
                    "duration_days": duration_days,
                    "status": task.status.value,
                    "priority": task.priority.value
                })
                
                # Adiciona dependências
                for dep in task.dependencies:
                    dependencies.append({
                        "from": dep.task_id,
                        "to": task.id
                    })
                
                max_duration = max(max_duration, duration_days)
            
            current_date = level_start + timedelta(days=max_duration + 1)
        
        return {
            "tasks": gantt_tasks,
            "dependencies": dependencies,
            "total_duration_days": (current_date - datetime.now()).days
        }


# Singleton do PM Orchestrator
_pm_instance: Optional[PMOrchestrator] = None


def get_pm_orchestrator() -> PMOrchestrator:
    """Obtém a instância singleton do PM Orchestrator."""
    global _pm_instance
    if _pm_instance is None:
        _pm_instance = PMOrchestrator()
    return _pm_instance


if __name__ == "__main__":
    # Demo do PM Orchestrator
    print("\n" + "=" * 60)
    print("  DEMO: PM Orchestrator")
    print("=" * 60)
    
    pm = get_pm_orchestrator()
    
    # Cria um projeto
    project = pm.create_project(
        project_id="demo_pm_001",
        project_name="Sistema de Análise de Clientes",
        description="Bot de análise com recomendações",
        client_requirements="Análise de clientes, recomendações, WhatsApp"
    )
    
    print(f"\n📋 Projeto criado: {project['name']}")
    
    # Gera cronograma
    requirements = {
        "has_ml": True,
        "has_streaming": False,
        "has_analytics": True,
        "data_volume": "medium",
        "team_size": 3
    }
    
    plan = pm.analyze_requirements_and_create_schedule("demo_pm_001", requirements)
    
    print(f"\n📊 Cronograma gerado:")
    print(f"   Total de tarefas: {plan['total_tasks']}")
    print(f"   Horas estimadas: {plan['total_estimated_hours']}")
    print(f"   Duração estimada: {plan['pm_analysis']['estimated_duration_weeks']} semanas")
    
    print("\n📈 Níveis de Execução:")
    for level in plan["execution_levels"]:
        parallel = "✓ Paralelo" if level["can_parallelize"] else "→ Sequencial"
        print(f"\n   Nível {level['level']} ({parallel}):")
        for task in level["tasks"]:
            print(f"      [{task['assigned_team']}] {task['name']}")
    
    print("\n🔄 Oportunidades de Paralelização:")
    for opp in plan["pm_analysis"]["parallel_opportunities"]:
        print(f"   - {', '.join(opp['tasks'])}")
        print(f"     Times: {', '.join(opp['teams'])}")
    
    print("\n" + "=" * 60)
