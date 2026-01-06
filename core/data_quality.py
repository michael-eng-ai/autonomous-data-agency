"""
Data Quality Module

Este módulo implementa um sistema completo de validação e monitoramento
de qualidade de dados para a Autonomous Data Agency.

Dimensões de Qualidade:
1. Completude - Dados não nulos
2. Consistência - Dados seguem regras de negócio
3. Precisão - Dados corretos e válidos
4. Unicidade - Sem duplicatas indevidas
5. Atualidade - Dados atualizados
6. Validade - Dados no formato esperado

Funcionalidades:
- Validação automática de schemas
- Regras de qualidade configuráveis
- Métricas e scores de qualidade
- Alertas de anomalias
- Relatórios de qualidade
"""

import re
import json
import statistics
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class QualityDimension(Enum):
    """Dimensões de qualidade de dados."""
    COMPLETENESS = "completeness"      # Dados não nulos
    CONSISTENCY = "consistency"        # Segue regras de negócio
    ACCURACY = "accuracy"              # Dados corretos
    UNIQUENESS = "uniqueness"          # Sem duplicatas
    TIMELINESS = "timeliness"          # Dados atualizados
    VALIDITY = "validity"              # Formato válido


class RuleSeverity(Enum):
    """Severidade das regras de qualidade."""
    INFO = "info"           # Informativo
    WARNING = "warning"     # Alerta
    ERROR = "error"         # Erro
    CRITICAL = "critical"   # Crítico - bloqueia processamento


class RuleType(Enum):
    """Tipos de regras de qualidade."""
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    FORMAT = "format"
    RANGE = "range"
    ENUM = "enum"
    REGEX = "regex"
    CUSTOM = "custom"
    REFERENTIAL = "referential"
    STATISTICAL = "statistical"
    FRESHNESS = "freshness"


@dataclass
class QualityRule:
    """Definição de uma regra de qualidade."""
    id: str
    name: str
    description: str
    rule_type: RuleType
    dimension: QualityDimension
    severity: RuleSeverity
    field: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type.value,
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "field": self.field,
            "parameters": self.parameters,
            "enabled": self.enabled
        }


@dataclass
class RuleViolation:
    """Violação de uma regra de qualidade."""
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    dimension: QualityDimension
    field: Optional[str]
    message: str
    affected_records: int
    sample_values: List[Any] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QualityScore:
    """Score de qualidade por dimensão."""
    dimension: QualityDimension
    score: float  # 0.0 a 1.0
    total_checks: int
    passed_checks: int
    failed_checks: int
    violations: List[RuleViolation] = field(default_factory=list)


@dataclass
class QualityReport:
    """Relatório completo de qualidade."""
    asset_name: str
    generated_at: str
    record_count: int
    overall_score: float
    dimension_scores: Dict[str, QualityScore]
    violations: List[RuleViolation]
    recommendations: List[str]
    passed: bool
    blocking_violations: int


class DataQualityValidator:
    """
    Validador de qualidade de dados.
    
    Aplica regras de qualidade a datasets e gera relatórios.
    """
    
    # Padrões comuns de validação
    PATTERNS = {
        "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "cpf": r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$',
        "cnpj": r'^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$',
        "phone_br": r'^(\+55\s?)?(\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}$',
        "cep": r'^\d{5}-?\d{3}$',
        "date_iso": r'^\d{4}-\d{2}-\d{2}$',
        "datetime_iso": r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
        "uuid": r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        "url": r'^https?://[^\s/$.?#].[^\s]*$',
    }
    
    def __init__(self):
        self.rules: Dict[str, List[QualityRule]] = {}  # asset_name -> rules
        self.custom_validators: Dict[str, Callable] = {}
        self.history: List[QualityReport] = []
        self.thresholds = {
            "minimum_overall_score": 0.8,
            "minimum_dimension_score": 0.7,
            "max_null_percentage": 0.1,
            "max_duplicate_percentage": 0.05
        }
    
    def add_rule(self, asset_name: str, rule: QualityRule) -> None:
        """Adiciona uma regra de qualidade para um ativo."""
        if asset_name not in self.rules:
            self.rules[asset_name] = []
        self.rules[asset_name].append(rule)
    
    def add_standard_rules(self, asset_name: str, schema: Dict[str, Any]) -> List[QualityRule]:
        """
        Adiciona regras padrão baseadas no schema.
        
        Args:
            asset_name: Nome do ativo
            schema: Schema com campos e tipos
            
        Returns:
            Lista de regras criadas
        """
        rules_created = []
        
        for field_name, field_info in schema.items():
            field_type = field_info.get("type", "string") if isinstance(field_info, dict) else "string"
            nullable = field_info.get("nullable", True) if isinstance(field_info, dict) else True
            
            # Regra de não nulo para campos obrigatórios
            if not nullable:
                rule = QualityRule(
                    id=f"{asset_name}_{field_name}_not_null",
                    name=f"{field_name} não pode ser nulo",
                    description=f"Campo {field_name} é obrigatório",
                    rule_type=RuleType.NOT_NULL,
                    dimension=QualityDimension.COMPLETENESS,
                    severity=RuleSeverity.ERROR,
                    field=field_name
                )
                self.add_rule(asset_name, rule)
                rules_created.append(rule)
            
            # Regras de formato baseadas no nome do campo
            field_lower = field_name.lower()
            
            if "email" in field_lower:
                rule = QualityRule(
                    id=f"{asset_name}_{field_name}_email_format",
                    name=f"{field_name} deve ser email válido",
                    description=f"Campo {field_name} deve seguir formato de email",
                    rule_type=RuleType.FORMAT,
                    dimension=QualityDimension.VALIDITY,
                    severity=RuleSeverity.ERROR,
                    field=field_name,
                    parameters={"pattern": "email"}
                )
                self.add_rule(asset_name, rule)
                rules_created.append(rule)
            
            elif "cpf" in field_lower:
                rule = QualityRule(
                    id=f"{asset_name}_{field_name}_cpf_format",
                    name=f"{field_name} deve ser CPF válido",
                    description=f"Campo {field_name} deve seguir formato de CPF",
                    rule_type=RuleType.FORMAT,
                    dimension=QualityDimension.VALIDITY,
                    severity=RuleSeverity.ERROR,
                    field=field_name,
                    parameters={"pattern": "cpf"}
                )
                self.add_rule(asset_name, rule)
                rules_created.append(rule)
            
            elif "phone" in field_lower or "telefone" in field_lower or "celular" in field_lower:
                rule = QualityRule(
                    id=f"{asset_name}_{field_name}_phone_format",
                    name=f"{field_name} deve ser telefone válido",
                    description=f"Campo {field_name} deve seguir formato de telefone",
                    rule_type=RuleType.FORMAT,
                    dimension=QualityDimension.VALIDITY,
                    severity=RuleSeverity.WARNING,
                    field=field_name,
                    parameters={"pattern": "phone_br"}
                )
                self.add_rule(asset_name, rule)
                rules_created.append(rule)
            
            elif "cep" in field_lower:
                rule = QualityRule(
                    id=f"{asset_name}_{field_name}_cep_format",
                    name=f"{field_name} deve ser CEP válido",
                    description=f"Campo {field_name} deve seguir formato de CEP",
                    rule_type=RuleType.FORMAT,
                    dimension=QualityDimension.VALIDITY,
                    severity=RuleSeverity.WARNING,
                    field=field_name,
                    parameters={"pattern": "cep"}
                )
                self.add_rule(asset_name, rule)
                rules_created.append(rule)
            
            # Regras de range para campos numéricos
            if field_type in ["int", "integer", "float", "number"]:
                if "idade" in field_lower or "age" in field_lower:
                    rule = QualityRule(
                        id=f"{asset_name}_{field_name}_age_range",
                        name=f"{field_name} deve estar em range válido",
                        description=f"Campo {field_name} deve estar entre 0 e 150",
                        rule_type=RuleType.RANGE,
                        dimension=QualityDimension.ACCURACY,
                        severity=RuleSeverity.ERROR,
                        field=field_name,
                        parameters={"min": 0, "max": 150}
                    )
                    self.add_rule(asset_name, rule)
                    rules_created.append(rule)
                
                elif "preco" in field_lower or "price" in field_lower or "valor" in field_lower:
                    rule = QualityRule(
                        id=f"{asset_name}_{field_name}_price_range",
                        name=f"{field_name} deve ser positivo",
                        description=f"Campo {field_name} deve ser maior ou igual a 0",
                        rule_type=RuleType.RANGE,
                        dimension=QualityDimension.ACCURACY,
                        severity=RuleSeverity.ERROR,
                        field=field_name,
                        parameters={"min": 0}
                    )
                    self.add_rule(asset_name, rule)
                    rules_created.append(rule)
        
        return rules_created
    
    def validate(
        self,
        asset_name: str,
        data: List[Dict[str, Any]],
        fail_fast: bool = False
    ) -> QualityReport:
        """
        Valida um dataset contra as regras definidas.
        
        Args:
            asset_name: Nome do ativo
            data: Lista de registros
            fail_fast: Se True, para na primeira violação crítica
            
        Returns:
            Relatório de qualidade
        """
        rules = self.rules.get(asset_name, [])
        violations = []
        dimension_results = defaultdict(lambda: {"passed": 0, "failed": 0, "violations": []})
        
        if not data:
            return QualityReport(
                asset_name=asset_name,
                generated_at=datetime.now().isoformat(),
                record_count=0,
                overall_score=1.0,
                dimension_scores={},
                violations=[],
                recommendations=["Nenhum dado para validar"],
                passed=True,
                blocking_violations=0
            )
        
        # Aplica cada regra
        for rule in rules:
            if not rule.enabled:
                continue
            
            violation = self._apply_rule(rule, data)
            
            if violation:
                violations.append(violation)
                dimension_results[rule.dimension.value]["failed"] += 1
                dimension_results[rule.dimension.value]["violations"].append(violation)
                
                if fail_fast and rule.severity == RuleSeverity.CRITICAL:
                    break
            else:
                dimension_results[rule.dimension.value]["passed"] += 1
        
        # Adiciona verificações padrão de qualidade
        self._check_completeness(data, dimension_results, violations)
        self._check_uniqueness(data, dimension_results, violations)
        
        # Calcula scores por dimensão
        dimension_scores = {}
        for dim in QualityDimension:
            results = dimension_results[dim.value]
            total = results["passed"] + results["failed"]
            score = results["passed"] / total if total > 0 else 1.0
            
            dimension_scores[dim.value] = QualityScore(
                dimension=dim,
                score=score,
                total_checks=total,
                passed_checks=results["passed"],
                failed_checks=results["failed"],
                violations=results["violations"]
            )
        
        # Calcula score geral
        if dimension_scores:
            overall_score = statistics.mean([ds.score for ds in dimension_scores.values()])
        else:
            overall_score = 1.0
        
        # Conta violações bloqueantes
        blocking = len([v for v in violations if v.severity in [RuleSeverity.CRITICAL, RuleSeverity.ERROR]])
        
        # Gera recomendações
        recommendations = self._generate_recommendations(violations, dimension_scores)
        
        report = QualityReport(
            asset_name=asset_name,
            generated_at=datetime.now().isoformat(),
            record_count=len(data),
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            violations=violations,
            recommendations=recommendations,
            passed=overall_score >= self.thresholds["minimum_overall_score"] and blocking == 0,
            blocking_violations=blocking
        )
        
        self.history.append(report)
        return report
    
    def _apply_rule(self, rule: QualityRule, data: List[Dict[str, Any]]) -> Optional[RuleViolation]:
        """Aplica uma regra específica aos dados."""
        affected = 0
        samples = []
        
        if rule.rule_type == RuleType.NOT_NULL:
            for row in data:
                value = row.get(rule.field)
                if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
                    affected += 1
                    if len(samples) < 5:
                        samples.append({"row": row, "value": value})
        
        elif rule.rule_type == RuleType.FORMAT:
            pattern_name = rule.parameters.get("pattern")
            pattern = self.PATTERNS.get(pattern_name) or rule.parameters.get("regex")
            
            if pattern:
                for row in data:
                    value = row.get(rule.field)
                    if value is not None and value != "":
                        if not re.match(pattern, str(value)):
                            affected += 1
                            if len(samples) < 5:
                                samples.append({"value": value})
        
        elif rule.rule_type == RuleType.RANGE:
            min_val = rule.parameters.get("min")
            max_val = rule.parameters.get("max")
            
            for row in data:
                value = row.get(rule.field)
                if value is not None:
                    try:
                        num_value = float(value)
                        if min_val is not None and num_value < min_val:
                            affected += 1
                            if len(samples) < 5:
                                samples.append({"value": value, "issue": f"< {min_val}"})
                        elif max_val is not None and num_value > max_val:
                            affected += 1
                            if len(samples) < 5:
                                samples.append({"value": value, "issue": f"> {max_val}"})
                    except (ValueError, TypeError):
                        affected += 1
        
        elif rule.rule_type == RuleType.ENUM:
            allowed_values = set(rule.parameters.get("values", []))
            
            for row in data:
                value = row.get(rule.field)
                if value is not None and value not in allowed_values:
                    affected += 1
                    if len(samples) < 5:
                        samples.append({"value": value})
        
        elif rule.rule_type == RuleType.UNIQUE:
            values = [row.get(rule.field) for row in data if row.get(rule.field) is not None]
            duplicates = len(values) - len(set(values))
            if duplicates > 0:
                affected = duplicates
                # Encontra valores duplicados
                seen = set()
                for v in values:
                    if v in seen and len(samples) < 5:
                        samples.append({"duplicate_value": v})
                    seen.add(v)
        
        if affected > 0:
            return RuleViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                dimension=rule.dimension,
                field=rule.field,
                message=f"{affected} registros violam a regra '{rule.name}'",
                affected_records=affected,
                sample_values=samples
            )
        
        return None
    
    def _check_completeness(
        self,
        data: List[Dict[str, Any]],
        results: Dict,
        violations: List[RuleViolation]
    ) -> None:
        """Verifica completude geral dos dados."""
        if not data:
            return
        
        total_fields = len(data[0].keys()) * len(data)
        null_count = sum(
            1 for row in data 
            for v in row.values() 
            if v is None or v == ""
        )
        
        null_percentage = null_count / total_fields if total_fields > 0 else 0
        
        if null_percentage > self.thresholds["max_null_percentage"]:
            violation = RuleViolation(
                rule_id="completeness_check",
                rule_name="Verificação de Completude",
                severity=RuleSeverity.WARNING,
                dimension=QualityDimension.COMPLETENESS,
                field=None,
                message=f"{null_percentage:.1%} dos campos estão nulos (limite: {self.thresholds['max_null_percentage']:.1%})",
                affected_records=null_count
            )
            violations.append(violation)
            results[QualityDimension.COMPLETENESS.value]["failed"] += 1
            results[QualityDimension.COMPLETENESS.value]["violations"].append(violation)
        else:
            results[QualityDimension.COMPLETENESS.value]["passed"] += 1
    
    def _check_uniqueness(
        self,
        data: List[Dict[str, Any]],
        results: Dict,
        violations: List[RuleViolation]
    ) -> None:
        """Verifica duplicatas nos dados."""
        if not data:
            return
        
        # Verifica duplicatas de registros completos
        str_rows = [json.dumps(row, sort_keys=True, default=str) for row in data]
        unique_rows = len(set(str_rows))
        duplicate_count = len(data) - unique_rows
        
        duplicate_percentage = duplicate_count / len(data) if data else 0
        
        if duplicate_percentage > self.thresholds["max_duplicate_percentage"]:
            violation = RuleViolation(
                rule_id="uniqueness_check",
                rule_name="Verificação de Unicidade",
                severity=RuleSeverity.WARNING,
                dimension=QualityDimension.UNIQUENESS,
                field=None,
                message=f"{duplicate_percentage:.1%} dos registros são duplicados (limite: {self.thresholds['max_duplicate_percentage']:.1%})",
                affected_records=duplicate_count
            )
            violations.append(violation)
            results[QualityDimension.UNIQUENESS.value]["failed"] += 1
            results[QualityDimension.UNIQUENESS.value]["violations"].append(violation)
        else:
            results[QualityDimension.UNIQUENESS.value]["passed"] += 1
    
    def _generate_recommendations(
        self,
        violations: List[RuleViolation],
        dimension_scores: Dict[str, QualityScore]
    ) -> List[str]:
        """Gera recomendações baseadas nas violações."""
        recommendations = []
        
        # Recomendações por dimensão com score baixo
        for dim_name, score in dimension_scores.items():
            if score.score < self.thresholds["minimum_dimension_score"]:
                if dim_name == QualityDimension.COMPLETENESS.value:
                    recommendations.append(
                        "Completude baixa: Revisar campos obrigatórios e implementar validação na entrada"
                    )
                elif dim_name == QualityDimension.VALIDITY.value:
                    recommendations.append(
                        "Validade baixa: Implementar máscaras de entrada e validação de formato"
                    )
                elif dim_name == QualityDimension.UNIQUENESS.value:
                    recommendations.append(
                        "Unicidade baixa: Implementar deduplicação e verificar processo de ingestão"
                    )
                elif dim_name == QualityDimension.ACCURACY.value:
                    recommendations.append(
                        "Precisão baixa: Revisar regras de negócio e validar dados na origem"
                    )
        
        # Recomendações por violações críticas
        critical_violations = [v for v in violations if v.severity == RuleSeverity.CRITICAL]
        if critical_violations:
            recommendations.append(
                f"URGENTE: {len(critical_violations)} violações críticas requerem ação imediata"
            )
        
        # Recomendações por campo específico
        field_violations = defaultdict(int)
        for v in violations:
            if v.field:
                field_violations[v.field] += v.affected_records
        
        worst_fields = sorted(field_violations.items(), key=lambda x: x[1], reverse=True)[:3]
        for field, count in worst_fields:
            recommendations.append(
                f"Campo '{field}' tem {count} problemas de qualidade - priorizar correção"
            )
        
        return recommendations


class DataQualityMonitor:
    """
    Monitor de qualidade de dados.
    
    Monitora tendências e detecta anomalias na qualidade.
    """
    
    def __init__(self, validator: DataQualityValidator):
        self.validator = validator
        self.baselines: Dict[str, Dict[str, float]] = {}  # asset -> dimension -> baseline_score
        self.alerts: List[Dict[str, Any]] = []
    
    def set_baseline(self, asset_name: str, dimension_scores: Dict[str, float]) -> None:
        """Define baseline de qualidade para um ativo."""
        self.baselines[asset_name] = dimension_scores
    
    def check_for_anomalies(
        self,
        asset_name: str,
        current_report: QualityReport,
        threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Verifica anomalias comparando com baseline.
        
        Args:
            asset_name: Nome do ativo
            current_report: Relatório atual
            threshold: Variação máxima permitida
            
        Returns:
            Lista de anomalias detectadas
        """
        anomalies = []
        baseline = self.baselines.get(asset_name, {})
        
        if not baseline:
            return anomalies
        
        for dim_name, score in current_report.dimension_scores.items():
            baseline_score = baseline.get(dim_name, 1.0)
            variation = baseline_score - score.score
            
            if variation > threshold:
                anomaly = {
                    "type": "quality_degradation",
                    "asset": asset_name,
                    "dimension": dim_name,
                    "baseline": baseline_score,
                    "current": score.score,
                    "variation": variation,
                    "severity": "high" if variation > 0.2 else "medium",
                    "detected_at": datetime.now().isoformat()
                }
                anomalies.append(anomaly)
                self.alerts.append(anomaly)
        
        return anomalies
    
    def get_trend(self, asset_name: str, last_n: int = 10) -> Dict[str, Any]:
        """
        Analisa tendência de qualidade.
        
        Args:
            asset_name: Nome do ativo
            last_n: Número de relatórios a considerar
            
        Returns:
            Análise de tendência
        """
        relevant_reports = [
            r for r in self.validator.history 
            if r.asset_name == asset_name
        ][-last_n:]
        
        if len(relevant_reports) < 2:
            return {"status": "insufficient_data", "reports_count": len(relevant_reports)}
        
        scores = [r.overall_score for r in relevant_reports]
        
        # Calcula tendência (regressão linear simples)
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(scores)
        
        numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        if slope > 0.01:
            trend = "improving"
        elif slope < -0.01:
            trend = "degrading"
        else:
            trend = "stable"
        
        return {
            "status": "analyzed",
            "reports_count": len(relevant_reports),
            "current_score": scores[-1],
            "average_score": y_mean,
            "min_score": min(scores),
            "max_score": max(scores),
            "trend": trend,
            "slope": slope
        }


# Singleton
_data_quality_validator: Optional[DataQualityValidator] = None
_data_quality_monitor: Optional[DataQualityMonitor] = None


def get_data_quality_validator() -> DataQualityValidator:
    """Retorna instância singleton do DataQualityValidator."""
    global _data_quality_validator
    if _data_quality_validator is None:
        _data_quality_validator = DataQualityValidator()
    return _data_quality_validator


def get_data_quality_monitor() -> DataQualityMonitor:
    """Retorna instância singleton do DataQualityMonitor."""
    global _data_quality_monitor
    if _data_quality_monitor is None:
        _data_quality_monitor = DataQualityMonitor(get_data_quality_validator())
    return _data_quality_monitor
