"""
Hallucination Detector Module

Este módulo implementa um sistema robusto de detecção de alucinações
para validar respostas dos agentes de IA.

Técnicas utilizadas:
1. Verificação contra Knowledge Base
2. Consistência entre múltiplas respostas
3. Detecção de afirmações sem fundamentação
4. Validação de fatos técnicos
5. Análise de confiança
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class HallucinationSeverity(Enum):
    """Severidade da alucinação detectada."""
    NONE = "none"           # Sem alucinação
    LOW = "low"             # Alucinação menor (imprecisão)
    MEDIUM = "medium"       # Alucinação moderada (informação questionável)
    HIGH = "high"           # Alucinação grave (informação incorreta)
    CRITICAL = "critical"   # Alucinação crítica (contradição direta)


class HallucinationType(Enum):
    """Tipos de alucinação."""
    FACTUAL_ERROR = "factual_error"           # Erro factual
    UNSUPPORTED_CLAIM = "unsupported_claim"   # Afirmação sem suporte
    CONTRADICTION = "contradiction"            # Contradição com KB
    INCONSISTENCY = "inconsistency"           # Inconsistência entre respostas
    OVERCONFIDENCE = "overconfidence"         # Excesso de confiança
    FABRICATION = "fabrication"               # Informação fabricada
    OUTDATED_INFO = "outdated_info"           # Informação desatualizada


@dataclass
class HallucinationIssue:
    """Representa um problema de alucinação detectado."""
    issue_type: HallucinationType
    severity: HallucinationSeverity
    description: str
    source_text: str
    suggested_correction: Optional[str] = None
    confidence: float = 0.0  # Confiança na detecção (0-1)


@dataclass
class ValidationResult:
    """Resultado da validação de uma resposta."""
    is_valid: bool
    overall_score: float  # 0-1, onde 1 é totalmente válido
    issues: List[HallucinationIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_claims: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "is_valid": self.is_valid,
            "overall_score": self.overall_score,
            "issues_count": len(self.issues),
            "issues": [
                {
                    "type": issue.issue_type.value,
                    "severity": issue.severity.value,
                    "description": issue.description,
                    "confidence": issue.confidence
                }
                for issue in self.issues
            ],
            "warnings": self.warnings,
            "validated_claims_count": len(self.validated_claims),
            "timestamp": self.timestamp
        }


class HallucinationDetector:
    """
    Detector de alucinações para respostas de agentes de IA.
    
    Utiliza múltiplas técnicas para identificar informações
    potencialmente incorretas ou fabricadas.
    """
    
    def __init__(self):
        """Inicializa o detector."""
        self.knowledge_base = None
        self.rag_engine = None
        
        # Padrões de linguagem que indicam incerteza ou fabricação
        self.uncertainty_patterns = [
            r"provavelmente",
            r"talvez",
            r"possivelmente",
            r"acredito que",
            r"penso que",
            r"não tenho certeza",
            r"pode ser que",
            r"geralmente",
            r"normalmente",
        ]
        
        self.overconfidence_patterns = [
            r"com certeza absoluta",
            r"sem dúvida alguma",
            r"é impossível",
            r"sempre funciona",
            r"nunca falha",
            r"garantido",
            r"100% certo",
        ]
        
        self.fabrication_indicators = [
            r"segundo estudos recentes",  # Sem citar fonte
            r"pesquisas mostram",          # Sem citar fonte
            r"especialistas dizem",        # Sem citar fonte
            r"é amplamente conhecido",     # Vago
            r"todos sabem que",            # Generalização
        ]
        
        # Termos técnicos conhecidos para validação
        self.valid_tech_terms = {
            "data_engineering": [
                "airflow", "dbt", "spark", "kafka", "postgresql", "mysql",
                "etl", "elt", "data warehouse", "data lake", "lakehouse",
                "pipeline", "dag", "orchestration", "batch", "streaming",
                "delta lake", "iceberg", "hudi", "parquet", "avro"
            ],
            "data_science": [
                "machine learning", "deep learning", "neural network",
                "regression", "classification", "clustering", "nlp",
                "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
                "feature engineering", "model training", "hyperparameter",
                "cross-validation", "overfitting", "underfitting"
            ],
            "devops": [
                "kubernetes", "docker", "terraform", "ansible", "jenkins",
                "github actions", "ci/cd", "gitops", "helm", "argocd",
                "prometheus", "grafana", "elk", "observability", "sre",
                "infrastructure as code", "container", "microservices"
            ],
            "qa": [
                "pytest", "unittest", "selenium", "cypress", "jest",
                "test automation", "unit test", "integration test",
                "e2e test", "load test", "stress test", "tdd", "bdd",
                "great expectations", "data quality", "validation"
            ]
        }
    
    def set_knowledge_base(self, kb) -> None:
        """Define a knowledge base para validação."""
        self.knowledge_base = kb
    
    def set_rag_engine(self, rag) -> None:
        """Define o RAG engine para validação."""
        self.rag_engine = rag
    
    def validate_response(
        self,
        response: str,
        domain: str,
        context: Optional[str] = None,
        other_responses: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Valida uma resposta de agente.
        
        Args:
            response: Texto da resposta a validar
            domain: Domínio técnico (data_engineering, devops, etc.)
            context: Contexto adicional (knowledge base, etc.)
            other_responses: Outras respostas para verificar consistência
        
        Returns:
            ValidationResult com detalhes da validação
        """
        issues = []
        warnings = []
        validated_claims = []
        
        # 1. Verificar padrões de incerteza
        uncertainty_issues = self._check_uncertainty_patterns(response)
        warnings.extend(uncertainty_issues)
        
        # 2. Verificar excesso de confiança
        overconfidence_issues = self._check_overconfidence(response)
        issues.extend(overconfidence_issues)
        
        # 3. Verificar indicadores de fabricação
        fabrication_issues = self._check_fabrication_indicators(response)
        issues.extend(fabrication_issues)
        
        # 4. Validar termos técnicos
        tech_validation = self._validate_technical_terms(response, domain)
        validated_claims.extend(tech_validation["valid"])
        issues.extend(tech_validation["issues"])
        
        # 5. Verificar contra Knowledge Base
        if self.knowledge_base and context:
            kb_issues = self._check_against_knowledge_base(response, domain, context)
            issues.extend(kb_issues["issues"])
            validated_claims.extend(kb_issues["validated"])
        
        # 6. Verificar consistência entre respostas
        if other_responses:
            consistency_issues = self._check_consistency(response, other_responses)
            issues.extend(consistency_issues)
        
        # 7. Verificar afirmações numéricas
        numeric_issues = self._validate_numeric_claims(response)
        issues.extend(numeric_issues)
        
        # Calcular score geral
        overall_score = self._calculate_overall_score(issues, validated_claims)
        
        # Determinar se é válido
        critical_issues = [i for i in issues if i.severity in [HallucinationSeverity.HIGH, HallucinationSeverity.CRITICAL]]
        is_valid = len(critical_issues) == 0 and overall_score >= 0.6
        
        return ValidationResult(
            is_valid=is_valid,
            overall_score=overall_score,
            issues=issues,
            warnings=warnings,
            validated_claims=validated_claims
        )
    
    def _check_uncertainty_patterns(self, text: str) -> List[str]:
        """Verifica padrões de incerteza no texto."""
        warnings = []
        text_lower = text.lower()
        
        for pattern in self.uncertainty_patterns:
            if re.search(pattern, text_lower):
                warnings.append(f"Linguagem de incerteza detectada: '{pattern}'")
        
        return warnings
    
    def _check_overconfidence(self, text: str) -> List[HallucinationIssue]:
        """Verifica excesso de confiança."""
        issues = []
        text_lower = text.lower()
        
        for pattern in self.overconfidence_patterns:
            match = re.search(pattern, text_lower)
            if match:
                issues.append(HallucinationIssue(
                    issue_type=HallucinationType.OVERCONFIDENCE,
                    severity=HallucinationSeverity.MEDIUM,
                    description=f"Afirmação com excesso de confiança: '{pattern}'",
                    source_text=match.group(),
                    suggested_correction="Usar linguagem mais moderada",
                    confidence=0.8
                ))
        
        return issues
    
    def _check_fabrication_indicators(self, text: str) -> List[HallucinationIssue]:
        """Verifica indicadores de informação fabricada."""
        issues = []
        text_lower = text.lower()
        
        for pattern in self.fabrication_indicators:
            match = re.search(pattern, text_lower)
            if match:
                issues.append(HallucinationIssue(
                    issue_type=HallucinationType.UNSUPPORTED_CLAIM,
                    severity=HallucinationSeverity.MEDIUM,
                    description=f"Afirmação sem fonte específica: '{pattern}'",
                    source_text=match.group(),
                    suggested_correction="Citar fonte específica ou remover afirmação",
                    confidence=0.7
                ))
        
        return issues
    
    def _validate_technical_terms(self, text: str, domain: str) -> Dict[str, Any]:
        """Valida termos técnicos mencionados."""
        result = {"valid": [], "issues": []}
        text_lower = text.lower()
        
        # Obtém termos válidos para o domínio
        valid_terms = self.valid_tech_terms.get(domain, [])
        
        # Adiciona termos de domínios relacionados
        for d, terms in self.valid_tech_terms.items():
            if d != domain:
                valid_terms.extend(terms[:10])  # Adiciona alguns termos de outros domínios
        
        # Verifica termos mencionados
        for term in valid_terms:
            if term in text_lower:
                result["valid"].append(f"Termo técnico válido: {term}")
        
        # Procura por possíveis termos inventados (palavras técnicas não reconhecidas)
        # Isso é uma heurística simples - em produção seria mais sofisticado
        tech_pattern = r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b'  # CamelCase
        potential_terms = re.findall(tech_pattern, text)
        
        for term in potential_terms:
            term_lower = term.lower()
            if term_lower not in valid_terms and len(term) > 5:
                # Pode ser um termo inventado ou desconhecido
                result["issues"].append(HallucinationIssue(
                    issue_type=HallucinationType.FABRICATION,
                    severity=HallucinationSeverity.LOW,
                    description=f"Termo técnico não reconhecido: '{term}'",
                    source_text=term,
                    suggested_correction="Verificar se o termo existe ou explicar",
                    confidence=0.5
                ))
        
        return result
    
    def _check_against_knowledge_base(
        self,
        text: str,
        domain: str,
        context: str
    ) -> Dict[str, Any]:
        """Verifica resposta contra a Knowledge Base."""
        result = {"issues": [], "validated": []}
        
        if not self.knowledge_base:
            return result
        
        # Obtém práticas do domínio
        try:
            practices = self.knowledge_base.get_best_practices(domain)
            if not practices:
                return result
            
            text_lower = text.lower()
            
            # Verifica anti-patterns
            if "anti_patterns" in practices:
                for ap in practices["anti_patterns"]:
                    ap_name = ap.get("name", "").lower()
                    ap_desc = ap.get("description", "").lower()
                    
                    # Se a resposta sugere algo que é um anti-pattern
                    if ap_name in text_lower:
                        result["issues"].append(HallucinationIssue(
                            issue_type=HallucinationType.CONTRADICTION,
                            severity=HallucinationSeverity.HIGH,
                            description=f"Resposta sugere anti-pattern: '{ap.get('name')}'",
                            source_text=ap_name,
                            suggested_correction=f"Evitar: {ap.get('description', '')}",
                            confidence=0.85
                        ))
            
            # Verifica princípios
            if "principles" in practices:
                for principle in practices["principles"]:
                    p_name = principle.get("name", "").lower()
                    if p_name in text_lower:
                        result["validated"].append(f"Alinhado com princípio: {principle.get('name')}")
            
            # Verifica ferramentas recomendadas
            if "tools" in practices:
                for tool in practices.get("tools", []):
                    tool_name = tool.get("name", "").lower() if isinstance(tool, dict) else str(tool).lower()
                    if tool_name in text_lower:
                        result["validated"].append(f"Ferramenta recomendada: {tool_name}")
        
        except Exception as e:
            # Se houver erro, não bloqueia a validação
            pass
        
        return result
    
    def _check_consistency(
        self,
        response: str,
        other_responses: List[str]
    ) -> List[HallucinationIssue]:
        """Verifica consistência entre múltiplas respostas."""
        issues = []
        
        # Extrai tecnologias mencionadas em cada resposta
        def extract_technologies(text: str) -> set:
            all_terms = []
            for terms in self.valid_tech_terms.values():
                all_terms.extend(terms)
            
            text_lower = text.lower()
            return {term for term in all_terms if term in text_lower}
        
        response_techs = extract_technologies(response)
        
        # Verifica se há tecnologias conflitantes
        conflicting_pairs = [
            ("mysql", "postgresql"),  # Não são conflitantes, mas diferentes escolhas
            ("batch", "streaming"),   # Abordagens diferentes
            ("monolith", "microservices"),
        ]
        
        for other in other_responses:
            other_techs = extract_technologies(other)
            
            # Verifica se há escolhas muito diferentes
            common = response_techs & other_techs
            only_in_response = response_techs - other_techs
            only_in_other = other_techs - response_techs
            
            # Se houver muita divergência, pode indicar inconsistência
            if len(only_in_response) > 5 and len(only_in_other) > 5 and len(common) < 2:
                issues.append(HallucinationIssue(
                    issue_type=HallucinationType.INCONSISTENCY,
                    severity=HallucinationSeverity.LOW,
                    description="Alta divergência entre respostas dos agentes",
                    source_text=f"Tecnologias únicas: {only_in_response}",
                    suggested_correction="Consolidar e justificar escolhas",
                    confidence=0.6
                ))
        
        return issues
    
    def _validate_numeric_claims(self, text: str) -> List[HallucinationIssue]:
        """Valida afirmações numéricas."""
        issues = []
        
        # Procura por afirmações numéricas extremas
        extreme_patterns = [
            (r"(\d{3,})%", "Porcentagem muito alta"),
            (r"(\d+)\s*vezes\s*mais\s*rápido", "Afirmação de performance"),
            (r"reduz\s*(\d{2,})%", "Afirmação de redução"),
            (r"aumenta\s*(\d{2,})%", "Afirmação de aumento"),
        ]
        
        for pattern, description in extreme_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    value = int(match)
                    if value > 1000:  # Valores muito altos são suspeitos
                        issues.append(HallucinationIssue(
                            issue_type=HallucinationType.UNSUPPORTED_CLAIM,
                            severity=HallucinationSeverity.MEDIUM,
                            description=f"{description} com valor extremo: {value}",
                            source_text=match,
                            suggested_correction="Verificar fonte do dado numérico",
                            confidence=0.7
                        ))
                except ValueError:
                    pass
        
        return issues
    
    def _calculate_overall_score(
        self,
        issues: List[HallucinationIssue],
        validated_claims: List[str]
    ) -> float:
        """Calcula o score geral de validação."""
        
        # Pesos por severidade
        severity_weights = {
            HallucinationSeverity.NONE: 0,
            HallucinationSeverity.LOW: 0.1,
            HallucinationSeverity.MEDIUM: 0.25,
            HallucinationSeverity.HIGH: 0.5,
            HallucinationSeverity.CRITICAL: 1.0,
        }
        
        # Calcula penalidade por issues
        total_penalty = sum(
            severity_weights.get(issue.severity, 0) * issue.confidence
            for issue in issues
        )
        
        # Bônus por claims validados
        validation_bonus = min(len(validated_claims) * 0.05, 0.3)
        
        # Score base
        base_score = 1.0
        
        # Score final
        final_score = max(0, min(1, base_score - total_penalty + validation_bonus))
        
        return round(final_score, 2)
    
    def generate_report(self, result: ValidationResult) -> str:
        """Gera um relatório legível da validação."""
        lines = [
            "=" * 60,
            "  RELATÓRIO DE VALIDAÇÃO ANTI-ALUCINAÇÃO",
            "=" * 60,
            "",
            f"Status: {'✓ VÁLIDO' if result.is_valid else '✗ REQUER REVISÃO'}",
            f"Score Geral: {result.overall_score:.0%}",
            f"Timestamp: {result.timestamp}",
            "",
        ]
        
        if result.issues:
            lines.append("PROBLEMAS DETECTADOS:")
            lines.append("-" * 40)
            for i, issue in enumerate(result.issues, 1):
                lines.append(f"{i}. [{issue.severity.value.upper()}] {issue.issue_type.value}")
                lines.append(f"   Descrição: {issue.description}")
                if issue.suggested_correction:
                    lines.append(f"   Sugestão: {issue.suggested_correction}")
                lines.append(f"   Confiança: {issue.confidence:.0%}")
                lines.append("")
        
        if result.warnings:
            lines.append("AVISOS:")
            lines.append("-" * 40)
            for warning in result.warnings:
                lines.append(f"  ⚠ {warning}")
            lines.append("")
        
        if result.validated_claims:
            lines.append("VALIDAÇÕES POSITIVAS:")
            lines.append("-" * 40)
            for claim in result.validated_claims[:10]:  # Limita a 10
                lines.append(f"  ✓ {claim}")
            if len(result.validated_claims) > 10:
                lines.append(f"  ... e mais {len(result.validated_claims) - 10} validações")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# Singleton do detector
_detector_instance: Optional[HallucinationDetector] = None


def get_hallucination_detector() -> HallucinationDetector:
    """Obtém a instância singleton do detector."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = HallucinationDetector()
    return _detector_instance


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    detector = get_hallucination_detector()
    
    # Texto de teste com alguns problemas
    test_response = """
    Para este projeto, recomendo usar Apache Airflow para orquestração de pipelines.
    
    Segundo estudos recentes, o Airflow é 500% mais rápido que outras ferramentas.
    Com certeza absoluta, esta é a melhor escolha para qualquer cenário.
    
    Também sugiro usar o MegaDataProcessor, uma ferramenta revolucionária para ETL.
    
    O PostgreSQL é uma excelente escolha para o data warehouse, seguindo o princípio
    de Data Quality First.
    """
    
    result = detector.validate_response(
        response=test_response,
        domain="data_engineering",
        context="Projeto de análise de dados"
    )
    
    print(detector.generate_report(result))
