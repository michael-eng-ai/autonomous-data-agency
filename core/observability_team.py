"""
Observability and FinOps Team Module

Este módulo implementa o Time de Observabilidade e FinOps da Autonomous Data Agency,
responsável por monitoramento, logging, alertas e gestão de custos.

Times e Agentes:
1. Mestre de Observabilidade - Consolida métricas e alertas
2. Engenheiro de Monitoramento - Configura dashboards e alertas
3. Especialista em Custos (FinOps) - Otimização e previsão de custos
4. Analista de Performance - Identifica gargalos e otimizações

Funcionalidades:
- Logging estruturado de decisões dos agentes
- Métricas de performance dos pipelines
- Alertas e notificações
- Dashboards de saúde do sistema
- Estimativa e otimização de custos
- Relatórios de consumo
"""

import json
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import threading


class MetricType(Enum):
    """Tipos de métricas."""
    COUNTER = "counter"       # Contagem (sempre incrementa)
    GAUGE = "gauge"           # Valor atual (pode subir/descer)
    HISTOGRAM = "histogram"   # Distribuição de valores
    TIMER = "timer"           # Duração de operações


class AlertSeverity(Enum):
    """Severidade dos alertas."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Status dos alertas."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class CostCategory(Enum):
    """Categorias de custo."""
    COMPUTE = "compute"           # Processamento
    STORAGE = "storage"           # Armazenamento
    NETWORK = "network"           # Rede/transferência
    LLM_API = "llm_api"           # APIs de LLM
    DATABASE = "database"         # Banco de dados
    MONITORING = "monitoring"     # Monitoramento
    OTHER = "other"               # Outros


@dataclass
class LogEntry:
    """Entrada de log estruturado."""
    timestamp: str
    level: str
    component: str
    action: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "component": self.component,
            "action": self.action,
            "message": self.message,
            "context": self.context,
            "duration_ms": self.duration_ms,
            "trace_id": self.trace_id
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class Metric:
    """Definição de uma métrica."""
    name: str
    type: MetricType
    description: str
    unit: str
    labels: Dict[str, str] = field(default_factory=dict)
    value: float = 0.0
    values: List[float] = field(default_factory=list)  # Para histograma
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Alert:
    """Definição de um alerta."""
    id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    source: str
    metric_name: Optional[str] = None
    threshold: Optional[float] = None
    current_value: Optional[float] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "source": self.source,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "created_at": self.created_at,
            "acknowledged_at": self.acknowledged_at,
            "resolved_at": self.resolved_at
        }


@dataclass
class CostRecord:
    """Registro de custo."""
    id: str
    category: CostCategory
    service: str
    description: str
    amount: float
    currency: str = "USD"
    period_start: str = ""
    period_end: str = ""
    project: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "service": self.service,
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "project": self.project,
            "tags": self.tags
        }


@dataclass
class AlertRule:
    """Regra para disparo de alertas."""
    id: str
    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq", "gte", "lte"
    threshold: float
    severity: AlertSeverity
    duration_seconds: int = 0  # Tempo que condição deve persistir
    enabled: bool = True


class StructuredLogger:
    """
    Logger estruturado para a agência.
    
    Registra todas as ações dos agentes de forma estruturada
    para análise e auditoria.
    """
    
    def __init__(self, max_entries: int = 10000):
        self.entries: List[LogEntry] = []
        self.max_entries = max_entries
        self._lock = threading.Lock()
        self.callbacks: List[Callable[[LogEntry], None]] = []
    
    def log(
        self,
        level: str,
        component: str,
        action: str,
        message: str,
        context: Dict[str, Any] = None,
        duration_ms: float = None,
        trace_id: str = None
    ) -> LogEntry:
        """Registra uma entrada de log."""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.upper(),
            component=component,
            action=action,
            message=message,
            context=context or {},
            duration_ms=duration_ms,
            trace_id=trace_id
        )
        
        with self._lock:
            self.entries.append(entry)
            
            # Mantém limite de entradas
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[-self.max_entries:]
        
        # Notifica callbacks
        for callback in self.callbacks:
            try:
                callback(entry)
            except Exception:
                pass
        
        return entry
    
    def info(self, component: str, action: str, message: str, **kwargs) -> LogEntry:
        return self.log("INFO", component, action, message, **kwargs)
    
    def warning(self, component: str, action: str, message: str, **kwargs) -> LogEntry:
        return self.log("WARNING", component, action, message, **kwargs)
    
    def error(self, component: str, action: str, message: str, **kwargs) -> LogEntry:
        return self.log("ERROR", component, action, message, **kwargs)
    
    def debug(self, component: str, action: str, message: str, **kwargs) -> LogEntry:
        return self.log("DEBUG", component, action, message, **kwargs)
    
    def add_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """Adiciona callback para novos logs."""
        self.callbacks.append(callback)
    
    def query(
        self,
        level: str = None,
        component: str = None,
        action: str = None,
        start_time: str = None,
        end_time: str = None,
        limit: int = 100
    ) -> List[LogEntry]:
        """Consulta logs com filtros."""
        results = self.entries.copy()
        
        if level:
            results = [e for e in results if e.level == level.upper()]
        
        if component:
            results = [e for e in results if component.lower() in e.component.lower()]
        
        if action:
            results = [e for e in results if action.lower() in e.action.lower()]
        
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
        
        return results[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos logs."""
        if not self.entries:
            return {"total": 0}
        
        by_level = defaultdict(int)
        by_component = defaultdict(int)
        
        for entry in self.entries:
            by_level[entry.level] += 1
            by_component[entry.component] += 1
        
        return {
            "total": len(self.entries),
            "by_level": dict(by_level),
            "by_component": dict(by_component),
            "oldest": self.entries[0].timestamp,
            "newest": self.entries[-1].timestamp
        }


class MetricsCollector:
    """
    Coletor de métricas do sistema.
    
    Coleta e armazena métricas de performance, uso e saúde.
    """
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self._lock = threading.Lock()
    
    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str,
        unit: str,
        labels: Dict[str, str] = None
    ) -> Metric:
        """Registra uma nova métrica."""
        metric = Metric(
            name=name,
            type=metric_type,
            description=description,
            unit=unit,
            labels=labels or {}
        )
        
        with self._lock:
            self.metrics[name] = metric
        
        return metric
    
    def increment(self, name: str, value: float = 1.0, labels: Dict[str, str] = None) -> None:
        """Incrementa um counter."""
        with self._lock:
            if name in self.metrics:
                self.metrics[name].value += value
                self.metrics[name].last_updated = datetime.now().isoformat()
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Define valor de um gauge."""
        with self._lock:
            if name in self.metrics:
                self.metrics[name].value = value
                self.metrics[name].last_updated = datetime.now().isoformat()
    
    def observe(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Observa um valor para histograma."""
        with self._lock:
            if name in self.metrics:
                self.metrics[name].values.append(value)
                self.metrics[name].last_updated = datetime.now().isoformat()
                
                # Mantém últimos 1000 valores
                if len(self.metrics[name].values) > 1000:
                    self.metrics[name].values = self.metrics[name].values[-1000:]
    
    def record_timer(self, name: str, duration_ms: float, labels: Dict[str, str] = None) -> None:
        """Registra duração de uma operação."""
        self.observe(name, duration_ms, labels)
    
    def get_metric(self, name: str) -> Optional[Dict[str, Any]]:
        """Retorna uma métrica com estatísticas."""
        metric = self.metrics.get(name)
        if not metric:
            return None
        
        result = {
            "name": metric.name,
            "type": metric.type.value,
            "description": metric.description,
            "unit": metric.unit,
            "labels": metric.labels,
            "last_updated": metric.last_updated
        }
        
        if metric.type in [MetricType.COUNTER, MetricType.GAUGE]:
            result["value"] = metric.value
        
        elif metric.type in [MetricType.HISTOGRAM, MetricType.TIMER]:
            if metric.values:
                result["count"] = len(metric.values)
                result["sum"] = sum(metric.values)
                result["avg"] = statistics.mean(metric.values)
                result["min"] = min(metric.values)
                result["max"] = max(metric.values)
                result["p50"] = statistics.median(metric.values)
                if len(metric.values) >= 10:
                    sorted_values = sorted(metric.values)
                    p95_idx = int(len(sorted_values) * 0.95)
                    p99_idx = int(len(sorted_values) * 0.99)
                    result["p95"] = sorted_values[p95_idx]
                    result["p99"] = sorted_values[p99_idx]
        
        return result
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Retorna todas as métricas."""
        return {name: self.get_metric(name) for name in self.metrics}


class AlertManager:
    """
    Gerenciador de alertas.
    
    Monitora métricas e dispara alertas baseado em regras.
    """
    
    def __init__(self, metrics_collector: MetricsCollector, logger: StructuredLogger):
        self.metrics = metrics_collector
        self.logger = logger
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self._alert_counter = 0
    
    def add_rule(self, rule: AlertRule) -> None:
        """Adiciona regra de alerta."""
        self.rules[rule.id] = rule
    
    def _generate_alert_id(self) -> str:
        """Gera ID único para alerta."""
        self._alert_counter += 1
        return f"alert_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._alert_counter}"
    
    def check_rules(self) -> List[Alert]:
        """Verifica todas as regras e dispara alertas."""
        new_alerts = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            metric = self.metrics.get_metric(rule.metric_name)
            if not metric:
                continue
            
            value = metric.get("value") or metric.get("avg")
            if value is None:
                continue
            
            triggered = False
            
            if rule.condition == "gt" and value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and value < rule.threshold:
                triggered = True
            elif rule.condition == "gte" and value >= rule.threshold:
                triggered = True
            elif rule.condition == "lte" and value <= rule.threshold:
                triggered = True
            elif rule.condition == "eq" and value == rule.threshold:
                triggered = True
            
            if triggered:
                # Verifica se já existe alerta ativo para esta regra
                existing = next(
                    (a for a in self.alerts.values() 
                     if a.metric_name == rule.metric_name and a.status == AlertStatus.ACTIVE),
                    None
                )
                
                if not existing:
                    alert = Alert(
                        id=self._generate_alert_id(),
                        name=rule.name,
                        severity=rule.severity,
                        status=AlertStatus.ACTIVE,
                        message=f"{rule.metric_name} {rule.condition} {rule.threshold} (atual: {value})",
                        source="alert_manager",
                        metric_name=rule.metric_name,
                        threshold=rule.threshold,
                        current_value=value
                    )
                    
                    self.alerts[alert.id] = alert
                    self.alert_history.append(alert)
                    new_alerts.append(alert)
                    
                    self.logger.warning(
                        "AlertManager",
                        "alert_triggered",
                        f"Alerta disparado: {rule.name}",
                        context=alert.to_dict()
                    )
        
        return new_alerts
    
    def acknowledge(self, alert_id: str, user: str) -> bool:
        """Reconhece um alerta."""
        if alert_id in self.alerts:
            self.alerts[alert_id].status = AlertStatus.ACKNOWLEDGED
            self.alerts[alert_id].acknowledged_at = datetime.now().isoformat()
            self.alerts[alert_id].acknowledged_by = user
            return True
        return False
    
    def resolve(self, alert_id: str) -> bool:
        """Resolve um alerta."""
        if alert_id in self.alerts:
            self.alerts[alert_id].status = AlertStatus.RESOLVED
            self.alerts[alert_id].resolved_at = datetime.now().isoformat()
            return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Retorna alertas ativos."""
        return [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos alertas."""
        active = [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
        
        by_severity = defaultdict(int)
        for alert in active:
            by_severity[alert.severity.value] += 1
        
        return {
            "total_active": len(active),
            "by_severity": dict(by_severity),
            "total_history": len(self.alert_history)
        }


class CostTracker:
    """
    Rastreador de custos (FinOps).
    
    Monitora, estima e otimiza custos de infraestrutura e APIs.
    """
    
    # Estimativas de custo por serviço (USD)
    COST_ESTIMATES = {
        # LLM APIs (por 1M tokens)
        "gpt-4.1-mini": {"input": 0.15, "output": 0.60},
        "gpt-4.1-nano": {"input": 0.075, "output": 0.30},
        "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
        
        # Cloud (por hora)
        "aws_ec2_t3_medium": 0.0416,
        "aws_ec2_t3_large": 0.0832,
        "aws_rds_t3_medium": 0.068,
        "aws_s3_storage_gb": 0.023,  # por GB/mês
        "aws_s3_requests_1k": 0.0004,  # por 1000 requests
        
        # Outros
        "chromadb_local": 0.0,  # Gratuito
        "postgresql_local": 0.0,  # Gratuito
    }
    
    def __init__(self):
        self.records: List[CostRecord] = []
        self.budgets: Dict[str, float] = {}  # category -> budget
        self.usage: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._record_counter = 0
    
    def _generate_record_id(self) -> str:
        """Gera ID único para registro."""
        self._record_counter += 1
        return f"cost_{datetime.now().strftime('%Y%m%d')}_{self._record_counter}"
    
    def set_budget(self, category: CostCategory, amount: float) -> None:
        """Define orçamento para uma categoria."""
        self.budgets[category.value] = amount
    
    def record_usage(
        self,
        category: CostCategory,
        service: str,
        quantity: float,
        unit: str,
        project: str = None
    ) -> CostRecord:
        """
        Registra uso de um serviço.
        
        Args:
            category: Categoria de custo
            service: Nome do serviço
            quantity: Quantidade usada
            unit: Unidade (tokens, hours, GB, etc.)
            project: Projeto associado
            
        Returns:
            Registro de custo
        """
        # Calcula custo estimado
        estimate = self.COST_ESTIMATES.get(service, {})
        
        if isinstance(estimate, dict):
            # Para LLMs, assume 50% input, 50% output
            cost = quantity * (estimate.get("input", 0) + estimate.get("output", 0)) / 2 / 1_000_000
        else:
            cost = quantity * estimate
        
        record = CostRecord(
            id=self._generate_record_id(),
            category=category,
            service=service,
            description=f"{quantity} {unit} de {service}",
            amount=cost,
            period_start=datetime.now().isoformat(),
            period_end=datetime.now().isoformat(),
            project=project
        )
        
        self.records.append(record)
        self.usage[category.value][service] += cost
        
        return record
    
    def record_llm_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        project: str = None
    ) -> CostRecord:
        """Registra uso de API de LLM."""
        estimate = self.COST_ESTIMATES.get(model, {"input": 0.15, "output": 0.60})
        
        cost = (input_tokens * estimate["input"] + output_tokens * estimate["output"]) / 1_000_000
        
        record = CostRecord(
            id=self._generate_record_id(),
            category=CostCategory.LLM_API,
            service=model,
            description=f"{input_tokens} input + {output_tokens} output tokens",
            amount=cost,
            period_start=datetime.now().isoformat(),
            period_end=datetime.now().isoformat(),
            project=project,
            tags={"input_tokens": str(input_tokens), "output_tokens": str(output_tokens)}
        )
        
        self.records.append(record)
        self.usage[CostCategory.LLM_API.value][model] += cost
        
        return record
    
    def estimate_project_cost(
        self,
        project_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estima custo de um projeto.
        
        Args:
            project_config: Configuração do projeto com:
                - duration_days: Duração em dias
                - llm_calls_per_day: Chamadas de LLM por dia
                - avg_tokens_per_call: Tokens médios por chamada
                - storage_gb: Armazenamento necessário
                - compute_hours_per_day: Horas de computação por dia
                
        Returns:
            Estimativa detalhada de custos
        """
        duration = project_config.get("duration_days", 30)
        llm_calls = project_config.get("llm_calls_per_day", 100)
        tokens_per_call = project_config.get("avg_tokens_per_call", 2000)
        storage_gb = project_config.get("storage_gb", 10)
        compute_hours = project_config.get("compute_hours_per_day", 8)
        
        # Custo de LLM (assume mix de modelos)
        total_tokens = duration * llm_calls * tokens_per_call
        llm_cost = total_tokens * 0.0003 / 1000  # Média dos modelos
        
        # Custo de storage
        storage_cost = storage_gb * self.COST_ESTIMATES["aws_s3_storage_gb"]
        
        # Custo de compute
        compute_cost = duration * compute_hours * self.COST_ESTIMATES["aws_ec2_t3_medium"]
        
        # Custo de database
        db_cost = duration * 24 * self.COST_ESTIMATES["aws_rds_t3_medium"] * 0.5  # 50% uptime
        
        total = llm_cost + storage_cost + compute_cost + db_cost
        
        return {
            "duration_days": duration,
            "breakdown": {
                "llm_api": {"amount": llm_cost, "percentage": llm_cost / total * 100},
                "storage": {"amount": storage_cost, "percentage": storage_cost / total * 100},
                "compute": {"amount": compute_cost, "percentage": compute_cost / total * 100},
                "database": {"amount": db_cost, "percentage": db_cost / total * 100}
            },
            "total_estimated": total,
            "monthly_estimated": total / duration * 30,
            "recommendations": self._generate_cost_recommendations(
                llm_cost, storage_cost, compute_cost, db_cost
            )
        }
    
    def _generate_cost_recommendations(
        self,
        llm_cost: float,
        storage_cost: float,
        compute_cost: float,
        db_cost: float
    ) -> List[str]:
        """Gera recomendações de otimização de custos."""
        recommendations = []
        total = llm_cost + storage_cost + compute_cost + db_cost
        
        if llm_cost / total > 0.5:
            recommendations.append(
                "LLM representa >50% do custo. Considere: "
                "1) Usar modelos menores para tarefas simples, "
                "2) Implementar cache de respostas, "
                "3) Otimizar prompts para reduzir tokens"
            )
        
        if compute_cost / total > 0.3:
            recommendations.append(
                "Compute representa >30% do custo. Considere: "
                "1) Usar instâncias spot/preemptible, "
                "2) Implementar auto-scaling, "
                "3) Usar serverless para cargas variáveis"
            )
        
        if storage_cost > 50:
            recommendations.append(
                "Storage acima de $50/mês. Considere: "
                "1) Implementar lifecycle policies, "
                "2) Usar compressão, "
                "3) Mover dados antigos para Glacier"
            )
        
        if not recommendations:
            recommendations.append("Custos estão bem distribuídos. Continue monitorando.")
        
        return recommendations
    
    def get_cost_summary(
        self,
        period_days: int = 30,
        group_by: str = "category"
    ) -> Dict[str, Any]:
        """
        Retorna resumo de custos.
        
        Args:
            period_days: Período em dias
            group_by: Agrupar por "category" ou "service"
            
        Returns:
            Resumo de custos
        """
        cutoff = (datetime.now() - timedelta(days=period_days)).isoformat()
        
        recent_records = [r for r in self.records if r.period_start >= cutoff]
        
        total = sum(r.amount for r in recent_records)
        
        grouped = defaultdict(float)
        for record in recent_records:
            key = record.category.value if group_by == "category" else record.service
            grouped[key] += record.amount
        
        # Verifica budgets
        budget_status = {}
        for category, budget in self.budgets.items():
            spent = grouped.get(category, 0)
            budget_status[category] = {
                "budget": budget,
                "spent": spent,
                "remaining": budget - spent,
                "percentage_used": (spent / budget * 100) if budget > 0 else 0
            }
        
        return {
            "period_days": period_days,
            "total_cost": total,
            "by_group": dict(grouped),
            "budget_status": budget_status,
            "record_count": len(recent_records)
        }
    
    def check_budget_alerts(self) -> List[Dict[str, Any]]:
        """Verifica se algum orçamento foi excedido."""
        alerts = []
        
        for category, budget in self.budgets.items():
            spent = self.usage.get(category, {})
            total_spent = sum(spent.values())
            
            if total_spent > budget:
                alerts.append({
                    "type": "budget_exceeded",
                    "category": category,
                    "budget": budget,
                    "spent": total_spent,
                    "overage": total_spent - budget,
                    "severity": "critical"
                })
            elif total_spent > budget * 0.8:
                alerts.append({
                    "type": "budget_warning",
                    "category": category,
                    "budget": budget,
                    "spent": total_spent,
                    "percentage": total_spent / budget * 100,
                    "severity": "warning"
                })
        
        return alerts


class ObservabilityTeam:
    """
    Time de Observabilidade e FinOps.
    
    Coordena logging, métricas, alertas e gestão de custos.
    """
    
    def __init__(self):
        self.logger = StructuredLogger()
        self.metrics = MetricsCollector()
        self.alerts = AlertManager(self.metrics, self.logger)
        self.costs = CostTracker()
        
        # Registra métricas padrão
        self._setup_default_metrics()
        self._setup_default_alerts()
    
    def _setup_default_metrics(self) -> None:
        """Configura métricas padrão."""
        # Métricas de agentes
        self.metrics.register_metric(
            "agent_requests_total",
            MetricType.COUNTER,
            "Total de requisições aos agentes",
            "requests"
        )
        
        self.metrics.register_metric(
            "agent_response_time_ms",
            MetricType.HISTOGRAM,
            "Tempo de resposta dos agentes",
            "milliseconds"
        )
        
        self.metrics.register_metric(
            "agent_errors_total",
            MetricType.COUNTER,
            "Total de erros dos agentes",
            "errors"
        )
        
        # Métricas de LLM
        self.metrics.register_metric(
            "llm_tokens_total",
            MetricType.COUNTER,
            "Total de tokens consumidos",
            "tokens"
        )
        
        self.metrics.register_metric(
            "llm_cost_total",
            MetricType.COUNTER,
            "Custo total de LLM",
            "USD"
        )
        
        # Métricas de qualidade
        self.metrics.register_metric(
            "data_quality_score",
            MetricType.GAUGE,
            "Score de qualidade de dados",
            "percentage"
        )
        
        # Métricas de sistema
        self.metrics.register_metric(
            "active_projects",
            MetricType.GAUGE,
            "Projetos ativos",
            "projects"
        )
    
    def _setup_default_alerts(self) -> None:
        """Configura alertas padrão."""
        # Alerta de erro alto
        self.alerts.add_rule(AlertRule(
            id="high_error_rate",
            name="Taxa de Erro Alta",
            metric_name="agent_errors_total",
            condition="gt",
            threshold=10,
            severity=AlertSeverity.ERROR
        ))
        
        # Alerta de latência
        self.alerts.add_rule(AlertRule(
            id="high_latency",
            name="Latência Alta",
            metric_name="agent_response_time_ms",
            condition="gt",
            threshold=5000,
            severity=AlertSeverity.WARNING
        ))
        
        # Alerta de qualidade
        self.alerts.add_rule(AlertRule(
            id="low_quality",
            name="Qualidade de Dados Baixa",
            metric_name="data_quality_score",
            condition="lt",
            threshold=0.7,
            severity=AlertSeverity.WARNING
        ))
    
    def record_agent_action(
        self,
        agent_name: str,
        action: str,
        duration_ms: float,
        success: bool,
        tokens_used: int = 0,
        model: str = None,
        context: Dict[str, Any] = None
    ) -> None:
        """
        Registra ação de um agente.
        
        Atualiza logs, métricas e custos automaticamente.
        """
        # Log
        level = "INFO" if success else "ERROR"
        self.logger.log(
            level=level,
            component=f"agent.{agent_name}",
            action=action,
            message=f"Ação {'concluída' if success else 'falhou'}: {action}",
            context=context or {},
            duration_ms=duration_ms
        )
        
        # Métricas
        self.metrics.increment("agent_requests_total")
        self.metrics.record_timer("agent_response_time_ms", duration_ms)
        
        if not success:
            self.metrics.increment("agent_errors_total")
        
        if tokens_used > 0:
            self.metrics.increment("llm_tokens_total", tokens_used)
            
            # Custo
            if model:
                self.costs.record_llm_usage(
                    model=model,
                    input_tokens=int(tokens_used * 0.4),
                    output_tokens=int(tokens_used * 0.6)
                )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para dashboard de observabilidade."""
        return {
            "timestamp": datetime.now().isoformat(),
            "logs": self.logger.get_summary(),
            "metrics": {
                "agent_requests": self.metrics.get_metric("agent_requests_total"),
                "agent_response_time": self.metrics.get_metric("agent_response_time_ms"),
                "agent_errors": self.metrics.get_metric("agent_errors_total"),
                "llm_tokens": self.metrics.get_metric("llm_tokens_total"),
                "data_quality": self.metrics.get_metric("data_quality_score")
            },
            "alerts": self.alerts.get_alert_summary(),
            "active_alerts": [a.to_dict() for a in self.alerts.get_active_alerts()],
            "costs": self.costs.get_cost_summary(period_days=30)
        }
    
    def generate_report(self, period_days: int = 7) -> Dict[str, Any]:
        """Gera relatório de observabilidade."""
        cutoff = (datetime.now() - timedelta(days=period_days)).isoformat()
        
        logs = self.logger.query(start_time=cutoff, limit=10000)
        
        errors = [l for l in logs if l.level == "ERROR"]
        warnings = [l for l in logs if l.level == "WARNING"]
        
        return {
            "report_generated_at": datetime.now().isoformat(),
            "period_days": period_days,
            "summary": {
                "total_logs": len(logs),
                "errors": len(errors),
                "warnings": len(warnings),
                "error_rate": len(errors) / len(logs) * 100 if logs else 0
            },
            "top_errors": self._get_top_items(errors, "action", 5),
            "top_components": self._get_top_items(logs, "component", 10),
            "metrics_summary": self.metrics.get_all_metrics(),
            "cost_summary": self.costs.get_cost_summary(period_days),
            "alert_summary": self.alerts.get_alert_summary()
        }
    
    def _get_top_items(
        self,
        items: List[LogEntry],
        field: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Retorna itens mais frequentes."""
        counts = defaultdict(int)
        for item in items:
            value = getattr(item, field, "unknown")
            counts[value] += 1
        
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{"name": k, "count": v} for k, v in sorted_items[:limit]]


# Singleton
_observability_team: Optional[ObservabilityTeam] = None


def get_observability_team() -> ObservabilityTeam:
    """Retorna instância singleton do ObservabilityTeam."""
    global _observability_team
    if _observability_team is None:
        _observability_team = ObservabilityTeam()
    return _observability_team
