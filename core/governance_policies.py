"""
Governance Policies Module

Módulo para gerenciamento de políticas de governança de dados.
Carrega políticas de arquivos YAML e valida conformidade.

Inspirado no projeto ABInBev Case, adaptado para o framework de agentes.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

__all__ = [
    "GovernancePolicies",
    "AccessPolicy",
    "RetentionPolicy",
    "DataClassification",
    "DataOwnership",
    "PolicyValidationResult",
    "get_governance_policies",
]


class DataClassificationLevel(Enum):
    """Níveis de classificação de dados."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"
    SENSITIVE = "sensitive"


class DataLayer(Enum):
    """Camadas de dados."""
    LANDING = "landing"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    CONSUMPTION = "consumption"
    AGGREGATION = "aggregation"
    CONTROL = "control"


@dataclass
class AccessPolicy:
    """Política de acesso a uma camada."""
    layer: DataLayer
    description: str
    read_roles: List[str]
    write_roles: List[str]
    admin_roles: List[str] = field(default_factory=lambda: ["admin"])


@dataclass
class RetentionPolicy:
    """Política de retenção de dados."""
    layer: DataLayer
    retention_days: int
    archive_after_days: int
    description: str
    delete_after_archive: bool = False


@dataclass
class DataOwnership:
    """Propriedade de dados."""
    layer: DataLayer
    team: str
    contact: str
    business_owner: Optional[str] = None
    data_steward: Optional[str] = None


@dataclass
class PolicyValidationResult:
    """Resultado de validação de política."""
    is_valid: bool
    policy_type: str
    violations: List[str]
    warnings: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class GovernancePolicies:
    """
    Gerencia políticas de governança de dados.
    
    Funcionalidades:
    - Carrega políticas de arquivos YAML
    - Valida acesso por role
    - Valida retenção de dados
    - Classifica dados automaticamente
    - Gerencia ownership
    
    Uso:
        policies = GovernancePolicies()
        policies.load_from_yaml("governance_policies.yaml")
        
        # Validar acesso
        can_read = policies.can_access("silver", "data_analyst", "read")
        
        # Obter política de retenção
        retention = policies.get_retention_policy("bronze")
        
        # Classificar dados
        classification = policies.classify_data(["cpf", "email", "nome"])
    """
    
    # Padrões de dados sensíveis para classificação automática
    SENSITIVE_PATTERNS = {
        DataClassificationLevel.PII: [
            "cpf", "rg", "cnh", "passport", "ssn", "social_security",
            "email", "telefone", "phone", "celular", "mobile",
            "endereco", "address", "cep", "zip_code", "postal_code",
            "nome", "name", "sobrenome", "surname", "full_name",
            "data_nascimento", "birth_date", "birthdate", "dob",
            "ip_address", "mac_address", "device_id"
        ],
        DataClassificationLevel.SENSITIVE: [
            "salario", "salary", "income", "renda",
            "senha", "password", "secret", "token", "api_key",
            "cartao", "card", "credit_card", "cvv", "expiry",
            "conta", "account", "bank", "banco", "agencia",
            "saude", "health", "medical", "diagnosis", "prescription"
        ],
        DataClassificationLevel.CONFIDENTIAL: [
            "margem", "margin", "lucro", "profit", "cost", "custo",
            "estrategia", "strategy", "forecast", "previsao",
            "contrato", "contract", "agreement", "nda"
        ]
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de políticas.
        
        Args:
            config_path: Caminho para arquivo YAML de configuração
        """
        self.config_path = config_path
        
        # Políticas
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        self.data_ownership: Dict[str, DataOwnership] = {}
        self.table_classifications: Dict[str, DataClassificationLevel] = {}
        self.business_glossary: Dict[str, Dict[str, Any]] = {}
        
        # Configurações de qualidade
        self.quality_thresholds: Dict[str, float] = {
            "completeness": 0.95,
            "uniqueness": 1.0,
            "validity": 0.98,
            "freshness_hours": 24
        }
        
        # Alertas
        self.alert_config: Dict[str, Any] = {}
        
        # Carrega configuração se fornecida
        if config_path and os.path.exists(config_path):
            self.load_from_yaml(config_path)
        else:
            self._load_defaults()
    
    def _load_defaults(self):
        """Carrega políticas padrão."""
        # Políticas de acesso padrão
        default_layers = [
            ("landing", "Arquivos brutos - Acesso restrito", ["data_engineer"], ["data_engineer"]),
            ("bronze", "Dados brutos em Delta - Acesso restrito", ["data_engineer", "data_scientist"], ["data_engineer"]),
            ("silver", "Dados limpos - Acesso para analistas", ["data_engineer", "data_scientist", "data_analyst"], ["data_engineer"]),
            ("gold", "Dados de negócio - Acesso amplo", ["data_engineer", "data_scientist", "data_analyst", "business_user"], ["data_engineer"]),
            ("consumption", "Modelo dimensional - Acesso para BI", ["data_engineer", "data_scientist", "data_analyst", "business_user", "bi_developer"], ["data_engineer"])
        ]
        
        for layer, desc, read_roles, write_roles in default_layers:
            self.access_policies[layer] = AccessPolicy(
                layer=DataLayer(layer),
                description=desc,
                read_roles=read_roles,
                write_roles=write_roles
            )
        
        # Políticas de retenção padrão
        default_retention = [
            ("landing", 90, 30, "Arquivos brutos mantidos por 90 dias"),
            ("bronze", 365, 180, "Dados históricos mantidos por 1 ano"),
            ("silver", 730, 365, "Dados limpos mantidos por 2 anos"),
            ("gold", 1095, 730, "Dados de negócio mantidos por 3 anos"),
            ("consumption", 1095, 730, "Modelo dimensional mantido por 3 anos"),
            ("control", 365, 180, "Logs de controle mantidos por 1 ano")
        ]
        
        for layer, retention, archive, desc in default_retention:
            self.retention_policies[layer] = RetentionPolicy(
                layer=DataLayer(layer),
                retention_days=retention,
                archive_after_days=archive,
                description=desc
            )
    
    def load_from_yaml(self, yaml_path: str) -> bool:
        """
        Carrega políticas de um arquivo YAML.
        
        Args:
            yaml_path: Caminho para o arquivo YAML
            
        Returns:
            True se carregado com sucesso
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Carrega políticas de acesso
            if "access_policies" in config:
                for layer, policy in config["access_policies"].items():
                    self.access_policies[layer] = AccessPolicy(
                        layer=DataLayer(layer),
                        description=policy.get("description", ""),
                        read_roles=[r["role"] for r in policy.get("read", [])],
                        write_roles=[r["role"] for r in policy.get("write", [])]
                    )
            
            # Carrega políticas de retenção
            if "retention_policies" in config:
                for layer, policy in config["retention_policies"].items():
                    self.retention_policies[layer] = RetentionPolicy(
                        layer=DataLayer(layer),
                        retention_days=policy.get("retention_days", 365),
                        archive_after_days=policy.get("archive_after_days", 180),
                        description=policy.get("description", "")
                    )
            
            # Carrega classificações de tabelas
            if "data_classification" in config:
                classifications = config["data_classification"]
                if "table_classifications" in classifications:
                    for table, level in classifications["table_classifications"].items():
                        self.table_classifications[table] = DataClassificationLevel(level.lower())
            
            # Carrega thresholds de qualidade
            if "data_quality_policies" in config:
                dq = config["data_quality_policies"]
                if "thresholds" in dq:
                    for key, value in dq["thresholds"].items():
                        if isinstance(value, dict) and "min" in value:
                            self.quality_thresholds[key] = value["min"]
                        elif isinstance(value, dict) and "max_hours" in value:
                            self.quality_thresholds["freshness_hours"] = value["max_hours"]
            
            # Carrega glossário de negócio
            if "business_glossary" in config:
                glossary = config["business_glossary"]
                if "terms" in glossary:
                    for term in glossary["terms"]:
                        self.business_glossary[term["term"]] = {
                            "definition": term.get("definition", ""),
                            "synonyms": term.get("synonyms", []),
                            "related_columns": term.get("related_columns", []),
                            "values": term.get("values", {})
                        }
            
            # Carrega ownership
            if "data_ownership" in config:
                ownership = config["data_ownership"]
                if "stewards" in ownership:
                    for layer, steward in ownership["stewards"].items():
                        self.data_ownership[layer] = DataOwnership(
                            layer=DataLayer(layer),
                            team=steward.get("team", ""),
                            contact=steward.get("contact", ""),
                            business_owner=steward.get("business_owner")
                        )
            
            # Carrega configuração de alertas
            if "data_quality_policies" in config:
                dq = config["data_quality_policies"]
                if "alerting" in dq:
                    self.alert_config = dq["alerting"]
            
            print(f"[GOVERNANCE] Políticas carregadas de: {yaml_path}")
            return True
            
        except Exception as e:
            print(f"[GOVERNANCE] Erro ao carregar políticas: {e}")
            self._load_defaults()
            return False
    
    def save_to_yaml(self, yaml_path: str) -> bool:
        """
        Salva políticas em um arquivo YAML.
        
        Args:
            yaml_path: Caminho para o arquivo YAML
            
        Returns:
            True se salvo com sucesso
        """
        try:
            config = {
                "access_policies": {},
                "retention_policies": {},
                "data_classification": {
                    "levels": [
                        {"name": level.value.upper(), "description": f"Dados {level.value}"}
                        for level in DataClassificationLevel
                    ],
                    "table_classifications": {
                        table: level.value.upper()
                        for table, level in self.table_classifications.items()
                    }
                },
                "data_quality_policies": {
                    "thresholds": self.quality_thresholds,
                    "alerting": self.alert_config
                },
                "business_glossary": {
                    "terms": [
                        {"term": term, **data}
                        for term, data in self.business_glossary.items()
                    ]
                },
                "data_ownership": {
                    "stewards": {}
                }
            }
            
            # Converte políticas de acesso
            for layer, policy in self.access_policies.items():
                config["access_policies"][layer] = {
                    "description": policy.description,
                    "read": [{"role": r} for r in policy.read_roles],
                    "write": [{"role": r} for r in policy.write_roles]
                }
            
            # Converte políticas de retenção
            for layer, policy in self.retention_policies.items():
                config["retention_policies"][layer] = {
                    "retention_days": policy.retention_days,
                    "archive_after_days": policy.archive_after_days,
                    "description": policy.description
                }
            
            # Converte ownership
            for layer, ownership in self.data_ownership.items():
                config["data_ownership"]["stewards"][layer] = {
                    "team": ownership.team,
                    "contact": ownership.contact,
                    "business_owner": ownership.business_owner
                }
            
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"[GOVERNANCE] Políticas salvas em: {yaml_path}")
            return True
            
        except Exception as e:
            print(f"[GOVERNANCE] Erro ao salvar políticas: {e}")
            return False
    
    def can_access(
        self,
        layer: str,
        role: str,
        access_type: str = "read"
    ) -> bool:
        """
        Verifica se um role pode acessar uma camada.
        
        Args:
            layer: Camada de dados
            role: Role do usuário
            access_type: Tipo de acesso (read, write, admin)
            
        Returns:
            True se pode acessar
        """
        if layer not in self.access_policies:
            return False
        
        policy = self.access_policies[layer]
        
        if access_type == "read":
            return role in policy.read_roles or role in policy.admin_roles
        elif access_type == "write":
            return role in policy.write_roles or role in policy.admin_roles
        elif access_type == "admin":
            return role in policy.admin_roles
        
        return False
    
    def get_retention_policy(self, layer: str) -> Optional[RetentionPolicy]:
        """
        Retorna política de retenção de uma camada.
        
        Args:
            layer: Camada de dados
            
        Returns:
            RetentionPolicy ou None
        """
        return self.retention_policies.get(layer)
    
    def classify_data(
        self,
        columns: List[str],
        sample_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, DataClassificationLevel]:
        """
        Classifica dados automaticamente baseado em nomes de colunas.
        
        Args:
            columns: Lista de nomes de colunas
            sample_data: Amostra de dados (opcional)
            
        Returns:
            Dicionário com classificação de cada coluna
        """
        classifications = {}
        
        for column in columns:
            col_lower = column.lower()
            classified = False
            
            # Verifica padrões sensíveis
            for level, patterns in self.SENSITIVE_PATTERNS.items():
                for pattern in patterns:
                    if pattern in col_lower:
                        classifications[column] = level
                        classified = True
                        break
                if classified:
                    break
            
            # Se não classificado, assume INTERNAL
            if not classified:
                classifications[column] = DataClassificationLevel.INTERNAL
        
        return classifications
    
    def get_highest_classification(
        self,
        columns: List[str]
    ) -> DataClassificationLevel:
        """
        Retorna a classificação mais alta de um conjunto de colunas.
        
        Args:
            columns: Lista de nomes de colunas
            
        Returns:
            Classificação mais alta
        """
        classifications = self.classify_data(columns)
        
        # Ordem de prioridade
        priority = [
            DataClassificationLevel.RESTRICTED,
            DataClassificationLevel.PII,
            DataClassificationLevel.SENSITIVE,
            DataClassificationLevel.CONFIDENTIAL,
            DataClassificationLevel.INTERNAL,
            DataClassificationLevel.PUBLIC
        ]
        
        for level in priority:
            if level in classifications.values():
                return level
        
        return DataClassificationLevel.INTERNAL
    
    def validate_access_request(
        self,
        layer: str,
        role: str,
        access_type: str,
        columns: Optional[List[str]] = None
    ) -> PolicyValidationResult:
        """
        Valida uma requisição de acesso.
        
        Args:
            layer: Camada de dados
            role: Role do usuário
            access_type: Tipo de acesso
            columns: Colunas sendo acessadas (opcional)
            
        Returns:
            PolicyValidationResult
        """
        violations = []
        warnings = []
        recommendations = []
        
        # Verifica acesso à camada
        if not self.can_access(layer, role, access_type):
            violations.append(
                f"Role '{role}' não tem permissão de '{access_type}' na camada '{layer}'"
            )
        
        # Verifica classificação das colunas
        if columns:
            classifications = self.classify_data(columns)
            
            for col, level in classifications.items():
                if level in [DataClassificationLevel.PII, DataClassificationLevel.SENSITIVE]:
                    if role not in ["admin", "data_engineer", "security"]:
                        warnings.append(
                            f"Coluna '{col}' contém dados {level.value} - requer aprovação adicional"
                        )
                        recommendations.append(
                            f"Considere mascarar ou anonimizar a coluna '{col}'"
                        )
        
        is_valid = len(violations) == 0
        
        return PolicyValidationResult(
            is_valid=is_valid,
            policy_type="access",
            violations=violations,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def get_quality_threshold(self, metric: str) -> float:
        """
        Retorna threshold de qualidade para uma métrica.
        
        Args:
            metric: Nome da métrica
            
        Returns:
            Valor do threshold
        """
        return self.quality_thresholds.get(metric, 0.95)
    
    def get_term_definition(self, term: str) -> Optional[Dict[str, Any]]:
        """
        Retorna definição de um termo do glossário.
        
        Args:
            term: Termo a buscar
            
        Returns:
            Definição ou None
        """
        # Busca exata
        if term in self.business_glossary:
            return self.business_glossary[term]
        
        # Busca por sinônimo
        for t, data in self.business_glossary.items():
            if term in data.get("synonyms", []):
                return data
        
        return None
    
    def get_data_owner(self, layer: str) -> Optional[DataOwnership]:
        """
        Retorna o owner de uma camada de dados.
        
        Args:
            layer: Camada de dados
            
        Returns:
            DataOwnership ou None
        """
        return self.data_ownership.get(layer)
    
    def add_table_classification(
        self,
        table_name: str,
        classification: DataClassificationLevel
    ):
        """
        Adiciona classificação para uma tabela.
        
        Args:
            table_name: Nome da tabela
            classification: Nível de classificação
        """
        self.table_classifications[table_name] = classification
    
    def get_table_classification(
        self,
        table_name: str
    ) -> DataClassificationLevel:
        """
        Retorna classificação de uma tabela.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Classificação (INTERNAL se não definida)
        """
        return self.table_classifications.get(
            table_name,
            DataClassificationLevel.INTERNAL
        )
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Gera relatório de compliance.
        
        Returns:
            Relatório de compliance
        """
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_layers": len(self.access_policies),
                "total_tables_classified": len(self.table_classifications),
                "total_glossary_terms": len(self.business_glossary),
                "retention_policies_defined": len(self.retention_policies),
                "owners_defined": len(self.data_ownership)
            },
            "access_policies": {
                layer: {
                    "read_roles": policy.read_roles,
                    "write_roles": policy.write_roles
                }
                for layer, policy in self.access_policies.items()
            },
            "retention_policies": {
                layer: {
                    "retention_days": policy.retention_days,
                    "archive_after_days": policy.archive_after_days
                }
                for layer, policy in self.retention_policies.items()
            },
            "data_classifications": {
                table: level.value
                for table, level in self.table_classifications.items()
            },
            "quality_thresholds": self.quality_thresholds
        }


# Singleton para acesso global
_governance_policies: Optional[GovernancePolicies] = None


def get_governance_policies(config_path: Optional[str] = None) -> GovernancePolicies:
    """
    Retorna instância singleton do GovernancePolicies.
    
    Args:
        config_path: Caminho para arquivo YAML de configuração
        
    Returns:
        GovernancePolicies instance
    """
    global _governance_policies
    
    if _governance_policies is None:
        _governance_policies = GovernancePolicies(config_path)
    
    return _governance_policies
