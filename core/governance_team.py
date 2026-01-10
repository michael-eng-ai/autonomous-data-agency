"""
Governance and Compliance Team Module

Este módulo implementa o Time de Governança e Compliance da Autonomous Data Agency,
responsável por garantir conformidade com LGPD, qualidade de dados, auditoria e
rastreabilidade.

Times e Agentes:
1. Mestre de Governança - Consolida e valida compliance geral
2. Especialista LGPD - Verifica conformidade com a Lei Geral de Proteção de Dados
3. Data Steward - Qualidade, catalogação e glossário de dados
4. Auditor de Dados - Lineage, rastreabilidade e auditoria

Funcionalidades:
- Classificação de dados sensíveis (PII)
- Validação de consentimento
- Políticas de retenção e exclusão
- Anonimização e pseudonimização
- Data Lineage e auditoria
- Relatórios de impacto (DPIA)
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re


class DataClassification(Enum):
    """Classificação de sensibilidade dos dados."""
    PUBLIC = "public"                    # Dados públicos
    INTERNAL = "internal"                # Uso interno
    CONFIDENTIAL = "confidential"        # Confidencial
    RESTRICTED = "restricted"            # Restrito (PII)
    HIGHLY_RESTRICTED = "highly_restricted"  # Altamente restrito (dados sensíveis LGPD)


class PIIType(Enum):
    """Tipos de dados pessoais identificáveis (PII)."""
    NAME = "name"
    CPF = "cpf"
    RG = "rg"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    BIRTH_DATE = "birth_date"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    IP_ADDRESS = "ip_address"
    COOKIE = "cookie"


class LegalBasis(Enum):
    """Bases legais para tratamento de dados (LGPD Art. 7)."""
    CONSENT = "consent"                          # Consentimento do titular
    LEGAL_OBLIGATION = "legal_obligation"        # Obrigação legal
    PUBLIC_POLICY = "public_policy"              # Políticas públicas
    RESEARCH = "research"                        # Estudos e pesquisas
    CONTRACT = "contract"                        # Execução de contrato
    LEGAL_PROCESS = "legal_process"              # Processo judicial
    LIFE_PROTECTION = "life_protection"          # Proteção da vida
    HEALTH_PROTECTION = "health_protection"      # Tutela da saúde
    LEGITIMATE_INTEREST = "legitimate_interest"  # Interesse legítimo
    CREDIT_PROTECTION = "credit_protection"      # Proteção ao crédito


class DataSubjectRight(Enum):
    """Direitos do titular dos dados (LGPD Art. 18)."""
    ACCESS = "access"                    # Confirmação e acesso
    CORRECTION = "correction"            # Correção de dados
    ANONYMIZATION = "anonymization"      # Anonimização
    PORTABILITY = "portability"          # Portabilidade
    DELETION = "deletion"                # Eliminação
    INFORMATION = "information"          # Informação sobre compartilhamento
    REVOKE_CONSENT = "revoke_consent"    # Revogação do consentimento
    OPPOSITION = "opposition"            # Oposição ao tratamento


@dataclass
class PIIDetection:
    """Resultado da detecção de PII em um campo."""
    field_name: str
    pii_type: PIIType
    confidence: float
    sample_value: Optional[str] = None
    recommendation: str = ""


@dataclass
class ConsentRecord:
    """Registro de consentimento do titular."""
    id: str
    data_subject_id: str
    purpose: str
    legal_basis: LegalBasis
    granted_at: str
    expires_at: Optional[str] = None
    revoked_at: Optional[str] = None
    scope: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class DataLineageRecord:
    """Registro de linhagem de dados."""
    id: str
    data_asset: str
    source_system: str
    transformations: List[str]
    destination_system: str
    created_at: str
    created_by: str
    purpose: str
    retention_period_days: int
    classification: DataClassification


@dataclass
class DPIAReport:
    """Relatório de Impacto à Proteção de Dados (DPIA)."""
    id: str
    project_name: str
    created_at: str
    data_types: List[PIIType]
    legal_bases: List[LegalBasis]
    risks: List[Dict[str, Any]]
    mitigations: List[Dict[str, Any]]
    overall_risk_level: str
    recommendation: str
    approved: bool = False
    approved_by: Optional[str] = None


@dataclass
class GovernanceValidation:
    """Resultado da validação de governança."""
    is_compliant: bool
    compliance_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    required_actions: List[str]
    lgpd_status: str
    data_quality_score: float
    lineage_complete: bool


class LGPDValidator:
    """
    Validador de conformidade com a LGPD.
    
    Verifica se o tratamento de dados está em conformidade com a
    Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018).
    """
    
    # Padrões regex para detecção de PII
    PII_PATTERNS = {
        PIIType.CPF: r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
        PIIType.EMAIL: r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        PIIType.PHONE: r'(\+55\s?)?(\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}',
        PIIType.RG: r'\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]',
        PIIType.IP_ADDRESS: r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
    }
    
    # Palavras-chave para detecção de campos PII
    PII_KEYWORDS = {
        PIIType.NAME: ['nome', 'name', 'primeiro_nome', 'sobrenome', 'full_name'],
        PIIType.CPF: ['cpf', 'documento', 'doc_number'],
        PIIType.EMAIL: ['email', 'e-mail', 'correio'],
        PIIType.PHONE: ['telefone', 'phone', 'celular', 'mobile', 'whatsapp'],
        PIIType.ADDRESS: ['endereco', 'address', 'rua', 'cep', 'cidade', 'bairro'],
        PIIType.BIRTH_DATE: ['nascimento', 'birth', 'data_nasc', 'idade', 'age'],
        PIIType.FINANCIAL: ['salario', 'renda', 'conta', 'cartao', 'credit'],
        PIIType.HEALTH: ['saude', 'health', 'doenca', 'medicamento', 'alergia'],
    }
    
    def __init__(self):
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.lineage_records: Dict[str, DataLineageRecord] = {}
        self.dpia_reports: Dict[str, DPIAReport] = {}
    
    def detect_pii_in_schema(self, schema: Dict[str, Any]) -> List[PIIDetection]:
        """
        Detecta campos PII em um schema de dados.
        
        Args:
            schema: Dicionário com nome do campo e tipo/exemplo
            
        Returns:
            Lista de detecções de PII
        """
        detections = []
        
        for field_name, field_info in schema.items():
            field_lower = field_name.lower()
            
            # Verifica por palavras-chave
            for pii_type, keywords in self.PII_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in field_lower:
                        detections.append(PIIDetection(
                            field_name=field_name,
                            pii_type=pii_type,
                            confidence=0.9,
                            recommendation=self._get_pii_recommendation(pii_type)
                        ))
                        break
            
            # Verifica por padrões regex se houver valor de exemplo
            if isinstance(field_info, dict) and 'example' in field_info:
                example = str(field_info['example'])
                for pii_type, pattern in self.PII_PATTERNS.items():
                    if re.search(pattern, example):
                        # Evita duplicatas
                        if not any(d.field_name == field_name and d.pii_type == pii_type for d in detections):
                            detections.append(PIIDetection(
                                field_name=field_name,
                                pii_type=pii_type,
                                confidence=0.95,
                                sample_value=example[:20] + "...",
                                recommendation=self._get_pii_recommendation(pii_type)
                            ))
        
        return detections
    
    def _get_pii_recommendation(self, pii_type: PIIType) -> str:
        """Retorna recomendação de tratamento para tipo de PII."""
        recommendations = {
            PIIType.CPF: "Criptografar em repouso, mascarar em logs, hash para analytics",
            PIIType.EMAIL: "Criptografar, obter consentimento para marketing",
            PIIType.PHONE: "Criptografar, usar apenas para finalidade declarada",
            PIIType.NAME: "Pseudonimizar quando possível, controlar acesso",
            PIIType.ADDRESS: "Criptografar, agregar para analytics (cidade/estado)",
            PIIType.BIRTH_DATE: "Converter para faixa etária quando possível",
            PIIType.FINANCIAL: "Criptografia forte, acesso restrito, auditoria completa",
            PIIType.HEALTH: "Dados sensíveis - requer consentimento específico, criptografia forte",
            PIIType.BIOMETRIC: "Dados sensíveis - consentimento específico obrigatório",
            PIIType.LOCATION: "Agregar/generalizar, consentimento para rastreamento",
            PIIType.IP_ADDRESS: "Anonimizar após período de retenção",
            PIIType.RG: "Criptografar, mascarar em exibição",
            PIIType.COOKIE: "Obter consentimento, política de cookies clara",
        }
        return recommendations.get(pii_type, "Avaliar necessidade e aplicar proteção adequada")
    
    def validate_legal_basis(
        self,
        data_types: List[PIIType],
        legal_basis: LegalBasis,
        purpose: str
    ) -> Tuple[bool, List[str]]:
        """
        Valida se a base legal é adequada para os tipos de dados.
        
        Args:
            data_types: Tipos de dados pessoais tratados
            legal_basis: Base legal alegada
            purpose: Finalidade do tratamento
            
        Returns:
            Tupla (é_válido, lista_de_issues)
        """
        issues = []
        
        # Dados sensíveis requerem consentimento específico ou bases específicas
        sensitive_types = {PIIType.HEALTH, PIIType.BIOMETRIC}
        has_sensitive = any(dt in sensitive_types for dt in data_types)
        
        if has_sensitive:
            valid_bases_for_sensitive = {
                LegalBasis.CONSENT,
                LegalBasis.LEGAL_OBLIGATION,
                LegalBasis.HEALTH_PROTECTION,
                LegalBasis.LIFE_PROTECTION
            }
            if legal_basis not in valid_bases_for_sensitive:
                issues.append(
                    f"Dados sensíveis detectados ({[dt.value for dt in data_types if dt in sensitive_types]}). "
                    f"Base legal '{legal_basis.value}' pode não ser adequada. "
                    f"Considere: {[b.value for b in valid_bases_for_sensitive]}"
                )
        
        # Interesse legítimo requer avaliação de impacto
        if legal_basis == LegalBasis.LEGITIMATE_INTEREST:
            issues.append(
                "Base legal 'interesse legítimo' requer teste de balanceamento (LIA) "
                "e pode ser contestada pelo titular. Documente a necessidade."
            )
        
        # Consentimento deve ser específico
        if legal_basis == LegalBasis.CONSENT:
            if len(data_types) > 3:
                issues.append(
                    "Consentimento deve ser específico para cada finalidade. "
                    "Considere separar os consentimentos por tipo de dado."
                )
        
        return len(issues) == 0, issues
    
    def register_consent(
        self,
        data_subject_id: str,
        purpose: str,
        legal_basis: LegalBasis,
        scope: List[str],
        expires_in_days: Optional[int] = 365
    ) -> ConsentRecord:
        """Registra consentimento do titular."""
        consent_id = f"consent_{hashlib.md5(f'{data_subject_id}_{purpose}'.encode()).hexdigest()[:8]}"
        
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        record = ConsentRecord(
            id=consent_id,
            data_subject_id=data_subject_id,
            purpose=purpose,
            legal_basis=legal_basis,
            granted_at=datetime.now().isoformat(),
            expires_at=expires_at,
            scope=scope,
            is_active=True
        )
        
        self.consent_records[consent_id] = record
        return record
    
    def revoke_consent(self, consent_id: str) -> bool:
        """Revoga um consentimento."""
        if consent_id in self.consent_records:
            self.consent_records[consent_id].is_active = False
            self.consent_records[consent_id].revoked_at = datetime.now().isoformat()
            return True
        return False
    
    def check_consent(self, data_subject_id: str, purpose: str) -> Tuple[bool, Optional[ConsentRecord]]:
        """Verifica se há consentimento válido para uma finalidade."""
        for record in self.consent_records.values():
            if (record.data_subject_id == data_subject_id and 
                record.purpose == purpose and 
                record.is_active):
                # Verifica expiração
                if record.expires_at:
                    if datetime.fromisoformat(record.expires_at) < datetime.now():
                        return False, record
                return True, record
        return False, None
    
    def handle_data_subject_request(
        self,
        data_subject_id: str,
        right: DataSubjectRight,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa solicitação de direito do titular.
        
        Args:
            data_subject_id: ID do titular
            right: Direito sendo exercido
            details: Detalhes adicionais da solicitação
            
        Returns:
            Resposta com ações a serem tomadas
        """
        response = {
            "request_id": f"dsr_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "data_subject_id": data_subject_id,
            "right": right.value,
            "received_at": datetime.now().isoformat(),
            "deadline": (datetime.now() + timedelta(days=15)).isoformat(),
            "actions": [],
            "status": "pending"
        }
        
        if right == DataSubjectRight.ACCESS:
            response["actions"] = [
                "Gerar relatório de todos os dados do titular",
                "Incluir finalidades de tratamento",
                "Incluir período de retenção",
                "Incluir compartilhamentos realizados"
            ]
        
        elif right == DataSubjectRight.DELETION:
            response["actions"] = [
                "Identificar todos os sistemas com dados do titular",
                "Verificar obrigações legais de retenção",
                "Executar exclusão onde permitido",
                "Anonimizar onde exclusão não for possível",
                "Notificar terceiros que receberam os dados"
            ]
        
        elif right == DataSubjectRight.PORTABILITY:
            response["actions"] = [
                "Extrair dados em formato estruturado (JSON/CSV)",
                "Incluir apenas dados fornecidos pelo titular",
                "Disponibilizar para download ou transferência"
            ]
        
        elif right == DataSubjectRight.CORRECTION:
            response["actions"] = [
                "Identificar dados a serem corrigidos",
                "Atualizar em todos os sistemas",
                "Manter log de alterações",
                "Notificar terceiros sobre correção"
            ]
        
        elif right == DataSubjectRight.REVOKE_CONSENT:
            # Revoga todos os consentimentos do titular
            revoked = []
            for consent_id, record in self.consent_records.items():
                if record.data_subject_id == data_subject_id and record.is_active:
                    self.revoke_consent(consent_id)
                    revoked.append(consent_id)
            response["actions"] = [
                f"Consentimentos revogados: {len(revoked)}",
                "Interromper tratamentos baseados em consentimento",
                "Manter dados necessários por obrigação legal"
            ]
        
        return response
    
    def generate_dpia(
        self,
        project_name: str,
        data_types: List[PIIType],
        legal_bases: List[LegalBasis],
        processing_activities: List[str]
    ) -> DPIAReport:
        """
        Gera Relatório de Impacto à Proteção de Dados (DPIA).
        
        Args:
            project_name: Nome do projeto
            data_types: Tipos de dados tratados
            legal_bases: Bases legais utilizadas
            processing_activities: Atividades de tratamento
            
        Returns:
            Relatório DPIA
        """
        risks = []
        mitigations = []
        
        # Avalia riscos por tipo de dado
        sensitive_types = {PIIType.HEALTH, PIIType.BIOMETRIC, PIIType.FINANCIAL}
        high_risk_types = {PIIType.CPF, PIIType.LOCATION}
        
        for dt in data_types:
            if dt in sensitive_types:
                risks.append({
                    "type": "high",
                    "category": "sensitive_data",
                    "description": f"Tratamento de dados sensíveis: {dt.value}",
                    "impact": "Alto impacto em caso de vazamento"
                })
                mitigations.append({
                    "risk": f"sensitive_data_{dt.value}",
                    "measure": "Criptografia forte, acesso restrito, auditoria completa",
                    "priority": "critical"
                })
            elif dt in high_risk_types:
                risks.append({
                    "type": "medium",
                    "category": "pii_data",
                    "description": f"Tratamento de PII de alto risco: {dt.value}",
                    "impact": "Risco de identificação direta"
                })
                mitigations.append({
                    "risk": f"pii_{dt.value}",
                    "measure": "Pseudonimização, hash para analytics, mascaramento",
                    "priority": "high"
                })
        
        # Avalia riscos por atividade
        risky_activities = ['profiling', 'automated_decision', 'large_scale', 'cross_border']
        for activity in processing_activities:
            if any(ra in activity.lower() for ra in risky_activities):
                risks.append({
                    "type": "medium",
                    "category": "processing_activity",
                    "description": f"Atividade de risco: {activity}",
                    "impact": "Pode requerer consentimento específico"
                })
        
        # Calcula nível geral de risco
        high_risks = len([r for r in risks if r['type'] == 'high'])
        medium_risks = len([r for r in risks if r['type'] == 'medium'])
        
        if high_risks >= 2:
            overall_risk = "ALTO"
            recommendation = "Requer aprovação do DPO e possível consulta à ANPD"
        elif high_risks >= 1 or medium_risks >= 3:
            overall_risk = "MÉDIO"
            recommendation = "Implementar todas as mitigações antes de iniciar"
        else:
            overall_risk = "BAIXO"
            recommendation = "Prosseguir com mitigações padrão"
        
        report = DPIAReport(
            id=f"dpia_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            project_name=project_name,
            created_at=datetime.now().isoformat(),
            data_types=data_types,
            legal_bases=legal_bases,
            risks=risks,
            mitigations=mitigations,
            overall_risk_level=overall_risk,
            recommendation=recommendation
        )
        
        self.dpia_reports[report.id] = report
        return report


class DataSteward:
    """
    Data Steward - Responsável pela qualidade e catalogação de dados.
    """
    
    def __init__(self):
        self.data_catalog: Dict[str, Dict[str, Any]] = {}
        self.glossary: Dict[str, str] = {}
        self.quality_rules: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_data_asset(
        self,
        asset_name: str,
        description: str,
        schema: Dict[str, Any],
        owner: str,
        classification: DataClassification,
        retention_days: int,
        pii_fields: List[str] = None
    ) -> Dict[str, Any]:
        """Registra um ativo de dados no catálogo."""
        asset = {
            "name": asset_name,
            "description": description,
            "schema": schema,
            "owner": owner,
            "classification": classification.value,
            "retention_days": retention_days,
            "pii_fields": pii_fields or [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "quality_score": None,
            "lineage": []
        }
        self.data_catalog[asset_name] = asset
        return asset
    
    def add_glossary_term(self, term: str, definition: str) -> None:
        """Adiciona termo ao glossário de negócio."""
        self.glossary[term.lower()] = definition
    
    def define_quality_rules(
        self,
        asset_name: str,
        rules: List[Dict[str, Any]]
    ) -> None:
        """
        Define regras de qualidade para um ativo.
        
        Exemplo de regra:
        {
            "field": "email",
            "rule": "format",
            "pattern": "email",
            "severity": "error"
        }
        """
        self.quality_rules[asset_name] = rules
    
    def validate_data_quality(
        self,
        asset_name: str,
        sample_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Valida qualidade dos dados contra as regras definidas.
        
        Returns:
            Relatório de qualidade
        """
        rules = self.quality_rules.get(asset_name, [])
        
        results = {
            "asset": asset_name,
            "sample_size": len(sample_data),
            "validated_at": datetime.now().isoformat(),
            "overall_score": 1.0,
            "dimensions": {
                "completeness": {"score": 1.0, "issues": []},
                "consistency": {"score": 1.0, "issues": []},
                "accuracy": {"score": 1.0, "issues": []},
                "timeliness": {"score": 1.0, "issues": []},
                "uniqueness": {"score": 1.0, "issues": []}
            },
            "rule_results": []
        }
        
        if not sample_data:
            return results
        
        # Verifica completude
        total_fields = len(sample_data[0].keys()) * len(sample_data)
        null_count = sum(
            1 for row in sample_data 
            for v in row.values() 
            if v is None or v == ""
        )
        completeness = 1 - (null_count / total_fields) if total_fields > 0 else 1
        results["dimensions"]["completeness"]["score"] = completeness
        
        # Verifica unicidade (duplicatas)
        unique_rows = len(set(str(row) for row in sample_data))
        uniqueness = unique_rows / len(sample_data) if sample_data else 1
        results["dimensions"]["uniqueness"]["score"] = uniqueness
        
        # Aplica regras específicas
        for rule in rules:
            rule_result = self._apply_rule(rule, sample_data)
            results["rule_results"].append(rule_result)
        
        # Calcula score geral
        dimension_scores = [d["score"] for d in results["dimensions"].values()]
        results["overall_score"] = sum(dimension_scores) / len(dimension_scores)
        
        return results
    
    def _apply_rule(
        self,
        rule: Dict[str, Any],
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aplica uma regra de qualidade aos dados."""
        field = rule.get("field")
        rule_type = rule.get("rule")
        
        result = {
            "rule": rule,
            "passed": True,
            "violations": 0,
            "details": []
        }
        
        for i, row in enumerate(data):
            value = row.get(field)
            
            if rule_type == "not_null" and (value is None or value == ""):
                result["violations"] += 1
                result["details"].append(f"Row {i}: {field} is null")
            
            elif rule_type == "format":
                pattern = rule.get("pattern")
                if pattern == "email" and value:
                    if not re.match(r'[^@]+@[^@]+\.[^@]+', str(value)):
                        result["violations"] += 1
                elif pattern == "cpf" and value:
                    if not re.match(r'\d{11}', str(value).replace(".", "").replace("-", "")):
                        result["violations"] += 1
            
            elif rule_type == "range":
                min_val = rule.get("min")
                max_val = rule.get("max")
                if value is not None:
                    if min_val is not None and value < min_val:
                        result["violations"] += 1
                    if max_val is not None and value > max_val:
                        result["violations"] += 1
        
        result["passed"] = result["violations"] == 0
        return result


class DataAuditor:
    """
    Auditor de Dados - Responsável por lineage e rastreabilidade.
    """
    
    def __init__(self):
        self.lineage_graph: Dict[str, List[str]] = {}  # source -> [destinations]
        self.audit_log: List[Dict[str, Any]] = []
        self.access_log: List[Dict[str, Any]] = []
    
    def register_lineage(
        self,
        source: str,
        destination: str,
        transformation: str,
        created_by: str
    ) -> Dict[str, Any]:
        """Registra linhagem de dados."""
        if source not in self.lineage_graph:
            self.lineage_graph[source] = []
        
        lineage_record = {
            "id": f"lineage_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "source": source,
            "destination": destination,
            "transformation": transformation,
            "created_by": created_by,
            "created_at": datetime.now().isoformat()
        }
        
        self.lineage_graph[source].append(destination)
        self.audit_log.append({
            "action": "lineage_registered",
            "details": lineage_record,
            "timestamp": datetime.now().isoformat()
        })
        
        return lineage_record
    
    def trace_lineage(self, asset_name: str, direction: str = "downstream") -> List[str]:
        """
        Rastreia linhagem de um ativo.
        
        Args:
            asset_name: Nome do ativo
            direction: "downstream" (para onde vai) ou "upstream" (de onde vem)
            
        Returns:
            Lista de ativos relacionados
        """
        result = []
        visited = set()
        
        def traverse(current):
            if current in visited:
                return
            visited.add(current)
            
            if direction == "downstream":
                destinations = self.lineage_graph.get(current, [])
                for dest in destinations:
                    result.append(dest)
                    traverse(dest)
            else:  # upstream
                for source, destinations in self.lineage_graph.items():
                    if current in destinations:
                        result.append(source)
                        traverse(source)
        
        traverse(asset_name)
        return result
    
    def log_access(
        self,
        user: str,
        asset: str,
        action: str,
        purpose: str,
        records_affected: int = 0
    ) -> None:
        """Registra acesso a dados."""
        self.access_log.append({
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "asset": asset,
            "action": action,
            "purpose": purpose,
            "records_affected": records_affected
        })
    
    def generate_audit_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        asset: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera relatório de auditoria."""
        filtered_logs = self.access_log
        
        if asset:
            filtered_logs = [l for l in filtered_logs if l["asset"] == asset]
        
        if start_date:
            filtered_logs = [l for l in filtered_logs if l["timestamp"] >= start_date]
        
        if end_date:
            filtered_logs = [l for l in filtered_logs if l["timestamp"] <= end_date]
        
        # Agrupa por usuário
        by_user = {}
        for log in filtered_logs:
            user = log["user"]
            if user not in by_user:
                by_user[user] = {"count": 0, "actions": []}
            by_user[user]["count"] += 1
            by_user[user]["actions"].append(log["action"])
        
        return {
            "report_generated_at": datetime.now().isoformat(),
            "period": {"start": start_date, "end": end_date},
            "asset_filter": asset,
            "total_accesses": len(filtered_logs),
            "unique_users": len(by_user),
            "by_user": by_user,
            "logs": filtered_logs[-100:]  # Últimos 100
        }


class GovernanceTeam:
    """
    Time de Governança e Compliance.
    
    Coordena todos os aspectos de governança de dados, incluindo
    LGPD, qualidade, catalogação e auditoria.
    """
    
    def __init__(self):
        self.lgpd_validator = LGPDValidator()
        self.data_steward = DataSteward()
        self.data_auditor = DataAuditor()
    
    def validate_project(
        self,
        project_name: str,
        schema: Dict[str, Any],
        legal_basis: LegalBasis,
        purpose: str,
        processing_activities: List[str]
    ) -> GovernanceValidation:
        """
        Valida um projeto sob a perspectiva de governança.
        
        Args:
            project_name: Nome do projeto
            schema: Schema dos dados
            legal_basis: Base legal
            purpose: Finalidade
            processing_activities: Atividades de tratamento
            
        Returns:
            Resultado da validação
        """
        issues = []
        recommendations = []
        required_actions = []
        
        # 1. Detecta PII
        pii_detections = self.lgpd_validator.detect_pii_in_schema(schema)
        data_types = list(set(d.pii_type for d in pii_detections))
        
        if pii_detections:
            for detection in pii_detections:
                recommendations.append(
                    f"Campo '{detection.field_name}' ({detection.pii_type.value}): "
                    f"{detection.recommendation}"
                )
        
        # 2. Valida base legal
        is_valid_basis, basis_issues = self.lgpd_validator.validate_legal_basis(
            data_types, legal_basis, purpose
        )
        if not is_valid_basis:
            issues.extend([{"type": "legal_basis", "message": i} for i in basis_issues])
        
        # 3. Gera DPIA se necessário
        sensitive_types = {PIIType.HEALTH, PIIType.BIOMETRIC, PIIType.FINANCIAL}
        if any(dt in sensitive_types for dt in data_types):
            dpia = self.lgpd_validator.generate_dpia(
                project_name, data_types, [legal_basis], processing_activities
            )
            required_actions.append(f"DPIA gerado (ID: {dpia.id}). Risco: {dpia.overall_risk_level}")
            if dpia.overall_risk_level == "ALTO":
                required_actions.append("Requer aprovação do DPO antes de prosseguir")
        
        # 4. Calcula scores
        compliance_score = 1.0
        if issues:
            compliance_score -= 0.2 * len(issues)
        compliance_score = max(0, compliance_score)
        
        # 5. Determina status LGPD
        if compliance_score >= 0.8:
            lgpd_status = "CONFORME"
        elif compliance_score >= 0.5:
            lgpd_status = "PARCIALMENTE CONFORME"
        else:
            lgpd_status = "NÃO CONFORME"
        
        return GovernanceValidation(
            is_compliant=compliance_score >= 0.8,
            compliance_score=compliance_score,
            issues=issues,
            recommendations=recommendations,
            required_actions=required_actions,
            lgpd_status=lgpd_status,
            data_quality_score=1.0,  # Será calculado quando houver dados
            lineage_complete=False
        )
    
    def get_governance_summary(self) -> Dict[str, Any]:
        """Retorna resumo do estado de governança."""
        return {
            "total_consents": len(self.lgpd_validator.consent_records),
            "active_consents": len([c for c in self.lgpd_validator.consent_records.values() if c.is_active]),
            "dpia_reports": len(self.lgpd_validator.dpia_reports),
            "cataloged_assets": len(self.data_steward.data_catalog),
            "glossary_terms": len(self.data_steward.glossary),
            "lineage_connections": sum(len(v) for v in self.data_auditor.lineage_graph.values()),
            "audit_entries": len(self.data_auditor.audit_log)
        }


# Singleton
_governance_team: Optional[GovernanceTeam] = None


def get_governance_team() -> GovernanceTeam:
    """Retorna instância singleton do GovernanceTeam."""
    global _governance_team
    if _governance_team is None:
        _governance_team = GovernanceTeam()
    return _governance_team
