"""
Task Orchestrator Module

Este módulo implementa o sistema de orquestração de tarefas com:
- Cronograma de execução
- Dependências entre tarefas
- Paralelização de tarefas independentes
- Validação contínua pelo QA
- Validação de negócio pelo PO
"""

from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json


class TaskStatus(Enum):
    """Status de uma tarefa."""
    PENDING = "pending"
    READY = "ready"  # Dependências satisfeitas, pronta para executar
    IN_PROGRESS = "in_progress"
    WAITING_QA = "waiting_qa"
    WAITING_PO = "waiting_po"
    QA_APPROVED = "qa_approved"
    QA_REJECTED = "qa_rejected"
    PO_APPROVED = "po_approved"
    PO_REJECTED = "po_rejected"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Prioridade de uma tarefa."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskType(Enum):
    """Tipo de tarefa."""
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    INFRASTRUCTURE = "infrastructure"
    DATA_PIPELINE = "data_pipeline"
    ML_MODEL = "ml_model"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    REVIEW = "review"


@dataclass
class TaskDependency:
    """Dependência de uma tarefa."""
    task_id: str
    dependency_type: str = "finish_to_start"  # finish_to_start, start_to_start, finish_to_finish
    lag_hours: int = 0  # Tempo de espera após a dependência


@dataclass
class QAValidation:
    """Resultado da validação do QA."""
    validated_by: str
    validated_at: datetime
    is_approved: bool
    test_results: Dict[str, Any]
    issues_found: List[str]
    recommendations: List[str]
    quality_score: float  # 0.0 a 1.0


@dataclass
class POValidation:
    """Resultado da validação do PO."""
    validated_by: str
    validated_at: datetime
    is_approved: bool
    meets_requirements: bool
    acceptance_criteria_met: List[str]
    acceptance_criteria_failed: List[str]
    business_value_score: float  # 0.0 a 1.0
    feedback: str


@dataclass
class Task:
    """Representa uma tarefa no cronograma."""
    id: str
    name: str
    description: str
    task_type: TaskType
    assigned_team: str
    priority: TaskPriority
    estimated_hours: float
    dependencies: List[TaskDependency] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    
    # Datas
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Resultados
    deliverables: List[str] = field(default_factory=list)
    output: Optional[str] = None
    
    # Validações
    qa_validation: Optional[QAValidation] = None
    po_validation: Optional[POValidation] = None
    requires_qa: bool = True
    requires_po: bool = True
    
    # Metadados
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Verifica se a tarefa está pronta para execução."""
        if self.status != TaskStatus.PENDING:
            return False
        
        for dep in self.dependencies:
            if dep.task_id not in completed_tasks:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type.value,
            "assigned_team": self.assigned_team,
            "priority": self.priority.value,
            "status": self.status.value,
            "estimated_hours": self.estimated_hours,
            "dependencies": [d.task_id for d in self.dependencies],
            "deliverables": self.deliverables,
            "requires_qa": self.requires_qa,
            "requires_po": self.requires_po
        }


@dataclass
class ProjectSchedule:
    """Cronograma do projeto."""
    project_id: str
    project_name: str
    tasks: Dict[str, Task] = field(default_factory=dict)
    phases: List[str] = field(default_factory=list)
    
    # Datas do projeto
    start_date: Optional[datetime] = None
    target_end_date: Optional[datetime] = None
    
    # Métricas
    total_estimated_hours: float = 0.0
    completed_hours: float = 0.0
    
    def add_task(self, task: Task) -> None:
        """Adiciona uma tarefa ao cronograma."""
        self.tasks[task.id] = task
        self.total_estimated_hours += task.estimated_hours
    
    def get_ready_tasks(self) -> List[Task]:
        """Retorna tarefas prontas para execução."""
        completed = {tid for tid, t in self.tasks.items() 
                    if t.status == TaskStatus.COMPLETED}
        return [t for t in self.tasks.values() if t.is_ready(completed)]
    
    def get_parallel_tasks(self) -> List[List[Task]]:
        """Agrupa tarefas que podem ser executadas em paralelo."""
        ready_tasks = self.get_ready_tasks()
        
        # Agrupa por prioridade
        priority_groups: Dict[int, List[Task]] = {}
        for task in ready_tasks:
            priority = task.priority.value
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(task)
        
        return [tasks for _, tasks in sorted(priority_groups.items())]
    
    def get_critical_path(self) -> List[Task]:
        """Calcula o caminho crítico do projeto."""
        # Implementação simplificada do caminho crítico
        critical_tasks = []
        
        # Ordena por dependências e duração
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: (len(t.dependencies), -t.estimated_hours)
        )
        
        for task in sorted_tasks:
            if task.priority == TaskPriority.CRITICAL:
                critical_tasks.append(task)
        
        return critical_tasks
    
    def get_progress(self) -> Dict[str, Any]:
        """Retorna o progresso do projeto."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() 
                       if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in self.tasks.values() 
                         if t.status == TaskStatus.IN_PROGRESS)
        blocked = sum(1 for t in self.tasks.values() 
                     if t.status == TaskStatus.BLOCKED)
        
        return {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "blocked": blocked,
            "pending": total - completed - in_progress - blocked,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
            "hours_completed": self.completed_hours,
            "hours_remaining": self.total_estimated_hours - self.completed_hours
        }


class TaskOrchestrator:
    """
    Orquestrador de tarefas que gerencia o cronograma, dependências e validações.
    """
    
    def __init__(self):
        self.schedules: Dict[str, ProjectSchedule] = {}
        self.task_history: List[Dict[str, Any]] = []
    
    def create_project_schedule(
        self,
        project_id: str,
        project_name: str,
        start_date: Optional[datetime] = None,
        target_end_date: Optional[datetime] = None
    ) -> ProjectSchedule:
        """Cria um novo cronograma de projeto."""
        schedule = ProjectSchedule(
            project_id=project_id,
            project_name=project_name,
            start_date=start_date or datetime.now(),
            target_end_date=target_end_date
        )
        self.schedules[project_id] = schedule
        return schedule
    
    def create_task(
        self,
        project_id: str,
        name: str,
        description: str,
        task_type: TaskType,
        assigned_team: str,
        estimated_hours: float,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: List[str] = None,
        requires_qa: bool = True,
        requires_po: bool = True,
        deliverables: List[str] = None,
        tags: List[str] = None
    ) -> Task:
        """Cria uma nova tarefa."""
        if project_id not in self.schedules:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # Converte dependências para objetos
        deps = []
        if dependencies:
            for dep_id in dependencies:
                deps.append(TaskDependency(task_id=dep_id))
        
        task = Task(
            id=task_id,
            name=name,
            description=description,
            task_type=task_type,
            assigned_team=assigned_team,
            priority=priority,
            estimated_hours=estimated_hours,
            dependencies=deps,
            requires_qa=requires_qa,
            requires_po=requires_po,
            deliverables=deliverables or [],
            tags=tags or []
        )
        
        self.schedules[project_id].add_task(task)
        
        self._log_event("task_created", {
            "project_id": project_id,
            "task_id": task_id,
            "name": name,
            "assigned_team": assigned_team
        })
        
        return task
    
    def start_task(self, project_id: str, task_id: str) -> Task:
        """Inicia a execução de uma tarefa."""
        task = self._get_task(project_id, task_id)
        
        if task.status not in [TaskStatus.PENDING, TaskStatus.READY]:
            raise ValueError(f"Tarefa {task_id} não pode ser iniciada (status: {task.status})")
        
        task.status = TaskStatus.IN_PROGRESS
        task.actual_start = datetime.now()
        
        self._log_event("task_started", {
            "project_id": project_id,
            "task_id": task_id
        })
        
        return task
    
    def complete_task(
        self,
        project_id: str,
        task_id: str,
        output: str,
        deliverables: List[str] = None
    ) -> Task:
        """Marca uma tarefa como concluída e envia para validação."""
        task = self._get_task(project_id, task_id)
        
        if task.status != TaskStatus.IN_PROGRESS:
            raise ValueError(f"Tarefa {task_id} não está em progresso")
        
        task.output = output
        if deliverables:
            task.deliverables.extend(deliverables)
        
        # Determina próximo status baseado nas validações necessárias
        if task.requires_qa:
            task.status = TaskStatus.WAITING_QA
        elif task.requires_po:
            task.status = TaskStatus.WAITING_PO
        else:
            task.status = TaskStatus.COMPLETED
            task.actual_end = datetime.now()
            self.schedules[project_id].completed_hours += task.estimated_hours
        
        self._log_event("task_completed", {
            "project_id": project_id,
            "task_id": task_id,
            "next_status": task.status.value
        })
        
        return task
    
    def qa_validate(
        self,
        project_id: str,
        task_id: str,
        is_approved: bool,
        test_results: Dict[str, Any],
        issues_found: List[str] = None,
        recommendations: List[str] = None,
        quality_score: float = 0.0
    ) -> Task:
        """Validação do QA para uma tarefa."""
        task = self._get_task(project_id, task_id)
        
        if task.status != TaskStatus.WAITING_QA:
            raise ValueError(f"Tarefa {task_id} não está aguardando QA")
        
        task.qa_validation = QAValidation(
            validated_by="QA Team",
            validated_at=datetime.now(),
            is_approved=is_approved,
            test_results=test_results,
            issues_found=issues_found or [],
            recommendations=recommendations or [],
            quality_score=quality_score
        )
        
        if is_approved:
            task.status = TaskStatus.QA_APPROVED
            if task.requires_po:
                task.status = TaskStatus.WAITING_PO
            else:
                task.status = TaskStatus.COMPLETED
                task.actual_end = datetime.now()
                self.schedules[project_id].completed_hours += task.estimated_hours
        else:
            task.status = TaskStatus.QA_REJECTED
        
        self._log_event("qa_validation", {
            "project_id": project_id,
            "task_id": task_id,
            "is_approved": is_approved,
            "quality_score": quality_score
        })
        
        return task
    
    def po_validate(
        self,
        project_id: str,
        task_id: str,
        is_approved: bool,
        meets_requirements: bool,
        acceptance_criteria_met: List[str] = None,
        acceptance_criteria_failed: List[str] = None,
        business_value_score: float = 0.0,
        feedback: str = ""
    ) -> Task:
        """Validação do PO para uma tarefa."""
        task = self._get_task(project_id, task_id)
        
        if task.status not in [TaskStatus.WAITING_PO, TaskStatus.QA_APPROVED]:
            raise ValueError(f"Tarefa {task_id} não está aguardando validação do PO")
        
        task.po_validation = POValidation(
            validated_by="PO Team",
            validated_at=datetime.now(),
            is_approved=is_approved,
            meets_requirements=meets_requirements,
            acceptance_criteria_met=acceptance_criteria_met or [],
            acceptance_criteria_failed=acceptance_criteria_failed or [],
            business_value_score=business_value_score,
            feedback=feedback
        )
        
        if is_approved:
            task.status = TaskStatus.COMPLETED
            task.actual_end = datetime.now()
            self.schedules[project_id].completed_hours += task.estimated_hours
        else:
            task.status = TaskStatus.PO_REJECTED
        
        self._log_event("po_validation", {
            "project_id": project_id,
            "task_id": task_id,
            "is_approved": is_approved,
            "meets_requirements": meets_requirements
        })
        
        return task
    
    def reject_task(self, project_id: str, task_id: str, reason: str) -> Task:
        """Rejeita uma tarefa e a envia de volta para retrabalho."""
        task = self._get_task(project_id, task_id)
        
        task.status = TaskStatus.IN_PROGRESS
        task.metadata["rejection_reason"] = reason
        task.metadata["rejection_count"] = task.metadata.get("rejection_count", 0) + 1
        
        self._log_event("task_rejected", {
            "project_id": project_id,
            "task_id": task_id,
            "reason": reason
        })
        
        return task
    
    def block_task(self, project_id: str, task_id: str, reason: str) -> Task:
        """Bloqueia uma tarefa."""
        task = self._get_task(project_id, task_id)
        task.status = TaskStatus.BLOCKED
        task.metadata["block_reason"] = reason
        
        self._log_event("task_blocked", {
            "project_id": project_id,
            "task_id": task_id,
            "reason": reason
        })
        
        return task
    
    def generate_execution_plan(self, project_id: str) -> Dict[str, Any]:
        """
        Gera um plano de execução otimizado para o projeto.
        Identifica tarefas paralelas e sequenciais.
        """
        if project_id not in self.schedules:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        schedule = self.schedules[project_id]
        
        # Calcula níveis de execução (tarefas no mesmo nível podem ser paralelas)
        levels: Dict[int, List[Task]] = {}
        task_levels: Dict[str, int] = {}
        
        # Primeira passada: tarefas sem dependências
        for task in schedule.tasks.values():
            if not task.dependencies:
                task_levels[task.id] = 0
                if 0 not in levels:
                    levels[0] = []
                levels[0].append(task)
        
        # Iterativamente calcula níveis para tarefas com dependências
        changed = True
        while changed:
            changed = False
            for task in schedule.tasks.values():
                if task.id in task_levels:
                    continue
                
                # Verifica se todas as dependências têm nível calculado
                dep_levels = []
                all_deps_calculated = True
                for dep in task.dependencies:
                    if dep.task_id in task_levels:
                        dep_levels.append(task_levels[dep.task_id])
                    else:
                        all_deps_calculated = False
                        break
                
                if all_deps_calculated and dep_levels:
                    level = max(dep_levels) + 1
                    task_levels[task.id] = level
                    if level not in levels:
                        levels[level] = []
                    levels[level].append(task)
                    changed = True
        
        # Gera o plano de execução
        execution_plan = {
            "project_id": project_id,
            "project_name": schedule.project_name,
            "total_tasks": len(schedule.tasks),
            "total_estimated_hours": schedule.total_estimated_hours,
            "execution_levels": [],
            "critical_path": [t.to_dict() for t in schedule.get_critical_path()],
            "progress": schedule.get_progress()
        }
        
        for level in sorted(levels.keys()):
            level_tasks = levels[level]
            execution_plan["execution_levels"].append({
                "level": level,
                "can_parallelize": len(level_tasks) > 1,
                "tasks": [t.to_dict() for t in level_tasks],
                "total_hours": sum(t.estimated_hours for t in level_tasks),
                "teams_involved": list(set(t.assigned_team for t in level_tasks))
            })
        
        return execution_plan
    
    def get_team_workload(self, project_id: str) -> Dict[str, Any]:
        """Retorna a carga de trabalho por time."""
        if project_id not in self.schedules:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        schedule = self.schedules[project_id]
        workload: Dict[str, Dict[str, Any]] = {}
        
        for task in schedule.tasks.values():
            team = task.assigned_team
            if team not in workload:
                workload[team] = {
                    "total_tasks": 0,
                    "total_hours": 0,
                    "completed_tasks": 0,
                    "in_progress_tasks": 0,
                    "pending_tasks": 0,
                    "tasks": []
                }
            
            workload[team]["total_tasks"] += 1
            workload[team]["total_hours"] += task.estimated_hours
            workload[team]["tasks"].append(task.to_dict())
            
            if task.status == TaskStatus.COMPLETED:
                workload[team]["completed_tasks"] += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                workload[team]["in_progress_tasks"] += 1
            else:
                workload[team]["pending_tasks"] += 1
        
        return workload
    
    def get_validation_queue(self, project_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna a fila de validações pendentes."""
        if project_id not in self.schedules:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        schedule = self.schedules[project_id]
        
        qa_queue = []
        po_queue = []
        
        for task in schedule.tasks.values():
            if task.status == TaskStatus.WAITING_QA:
                qa_queue.append(task.to_dict())
            elif task.status in [TaskStatus.WAITING_PO, TaskStatus.QA_APPROVED]:
                po_queue.append(task.to_dict())
        
        return {
            "qa_queue": qa_queue,
            "po_queue": po_queue,
            "total_pending_validations": len(qa_queue) + len(po_queue)
        }
    
    def _get_task(self, project_id: str, task_id: str) -> Task:
        """Obtém uma tarefa."""
        if project_id not in self.schedules:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        schedule = self.schedules[project_id]
        if task_id not in schedule.tasks:
            raise ValueError(f"Tarefa {task_id} não encontrada")
        
        return schedule.tasks[task_id]
    
    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Registra um evento no histórico."""
        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        })


# Singleton do orquestrador
_orchestrator_instance: Optional[TaskOrchestrator] = None


def get_task_orchestrator() -> TaskOrchestrator:
    """Obtém a instância singleton do orquestrador de tarefas."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = TaskOrchestrator()
    return _orchestrator_instance


# ============================================================================
# FUNÇÕES DE CONVENIÊNCIA PARA O PM
# ============================================================================

def create_standard_data_project_schedule(
    project_id: str,
    project_name: str,
    requirements: str
) -> Dict[str, Any]:
    """
    Cria um cronograma padrão para um projeto de dados.
    
    Fluxo:
    1. Arquitetura (decisões estratégicas)
    2. Data Engineering + DevOps (podem ser paralelos após arquitetura)
    3. Data Science (após Data Engineering)
    4. QA (valida cada entrega)
    5. PO (valida valor de negócio)
    """
    orchestrator = get_task_orchestrator()
    
    # Cria o cronograma
    schedule = orchestrator.create_project_schedule(
        project_id=project_id,
        project_name=project_name
    )
    
    # FASE 1: Arquitetura (sem dependências - primeira a executar)
    arch_task = orchestrator.create_task(
        project_id=project_id,
        name="Definição de Arquitetura",
        description="Definir arquitetura de solução, escolha de tecnologias, estimativa de custos e plano de escalabilidade",
        task_type=TaskType.ARCHITECTURE,
        assigned_team="architecture",
        estimated_hours=16,
        priority=TaskPriority.CRITICAL,
        requires_qa=True,
        requires_po=True,
        deliverables=[
            "Documento de Arquitetura",
            "Diagrama de Componentes",
            "Estimativa de Custos",
            "Plano de Escalabilidade"
        ],
        tags=["arquitetura", "estratégico"]
    )
    
    # FASE 2A: Infraestrutura (depende de arquitetura)
    infra_task = orchestrator.create_task(
        project_id=project_id,
        name="Provisionamento de Infraestrutura",
        description="Provisionar infraestrutura cloud conforme arquitetura definida",
        task_type=TaskType.INFRASTRUCTURE,
        assigned_team="devops",
        estimated_hours=24,
        priority=TaskPriority.HIGH,
        dependencies=[arch_task.id],
        requires_qa=True,
        requires_po=False,
        deliverables=[
            "Infraestrutura provisionada",
            "Scripts IaC (Terraform)",
            "Documentação de deploy"
        ],
        tags=["infraestrutura", "devops"]
    )
    
    # FASE 2B: Design do Data Pipeline (depende de arquitetura, paralelo com infra)
    pipeline_design_task = orchestrator.create_task(
        project_id=project_id,
        name="Design do Data Pipeline",
        description="Projetar pipelines de dados, modelagem e fluxos de ETL/ELT",
        task_type=TaskType.DATA_PIPELINE,
        assigned_team="data_engineering",
        estimated_hours=16,
        priority=TaskPriority.HIGH,
        dependencies=[arch_task.id],
        requires_qa=True,
        requires_po=True,
        deliverables=[
            "Modelo de dados",
            "Diagrama de pipelines",
            "Especificação técnica"
        ],
        tags=["dados", "pipeline", "design"]
    )
    
    # FASE 3: Implementação do Pipeline (depende de infra e design)
    pipeline_impl_task = orchestrator.create_task(
        project_id=project_id,
        name="Implementação do Data Pipeline",
        description="Implementar pipelines de dados conforme design aprovado",
        task_type=TaskType.DATA_PIPELINE,
        assigned_team="data_engineering",
        estimated_hours=40,
        priority=TaskPriority.HIGH,
        dependencies=[infra_task.id, pipeline_design_task.id],
        requires_qa=True,
        requires_po=True,
        deliverables=[
            "Pipelines implementados",
            "Testes de integração",
            "Documentação técnica"
        ],
        tags=["dados", "pipeline", "implementação"]
    )
    
    # FASE 4: Modelos de ML (depende do pipeline)
    ml_task = orchestrator.create_task(
        project_id=project_id,
        name="Desenvolvimento de Modelos de ML",
        description="Desenvolver e treinar modelos de machine learning",
        task_type=TaskType.ML_MODEL,
        assigned_team="data_science",
        estimated_hours=32,
        priority=TaskPriority.MEDIUM,
        dependencies=[pipeline_impl_task.id],
        requires_qa=True,
        requires_po=True,
        deliverables=[
            "Modelos treinados",
            "Métricas de performance",
            "API de inferência"
        ],
        tags=["ml", "modelo", "ciência de dados"]
    )
    
    # FASE 5: Deploy e Monitoramento (depende de ML)
    deploy_task = orchestrator.create_task(
        project_id=project_id,
        name="Deploy e Configuração de Monitoramento",
        description="Deploy da solução completa e configuração de monitoramento",
        task_type=TaskType.DEPLOYMENT,
        assigned_team="devops",
        estimated_hours=16,
        priority=TaskPriority.HIGH,
        dependencies=[ml_task.id],
        requires_qa=True,
        requires_po=True,
        deliverables=[
            "Solução em produção",
            "Dashboards de monitoramento",
            "Alertas configurados"
        ],
        tags=["deploy", "monitoramento", "produção"]
    )
    
    # Gera o plano de execução
    execution_plan = orchestrator.generate_execution_plan(project_id)
    
    return execution_plan


if __name__ == "__main__":
    # Demo do orquestrador
    print("\n" + "=" * 60)
    print("  DEMO: Task Orchestrator")
    print("=" * 60)
    
    # Cria um projeto de exemplo
    plan = create_standard_data_project_schedule(
        project_id="demo_001",
        project_name="Sistema de Análise de Clientes",
        requirements="Bot de análise de clientes com recomendações"
    )
    
    print(f"\n📋 Projeto: {plan['project_name']}")
    print(f"   Total de tarefas: {plan['total_tasks']}")
    print(f"   Horas estimadas: {plan['total_estimated_hours']}")
    
    print("\n📊 Níveis de Execução:")
    for level in plan["execution_levels"]:
        parallel_str = "✓ Paralelo" if level["can_parallelize"] else "→ Sequencial"
        print(f"\n   Nível {level['level']} ({parallel_str}):")
        print(f"   Times: {', '.join(level['teams_involved'])}")
        print(f"   Horas: {level['total_hours']}")
        for task in level["tasks"]:
            print(f"      - {task['name']} ({task['assigned_team']})")
    
    print("\n" + "=" * 60)
