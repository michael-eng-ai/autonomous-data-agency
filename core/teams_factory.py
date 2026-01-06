"""
Teams Factory Module

Este módulo fornece uma fábrica para criar times de agentes
pré-configurados para diferentes domínios.

Cada time possui:
- 1 Agente Mestre (supervisor/validador)
- 2-3 Agentes Operacionais (com LLMs diferentes)
- Conhecimento específico do domínio
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TeamType(Enum):
    """Tipos de times disponíveis."""
    PRODUCT_OWNER = "product_owner"
    PROJECT_MANAGER = "project_manager"
    DATA_ENGINEERING = "data_engineering"
    DATA_SCIENCE = "data_science"
    DATA_ANALYTICS = "data_analytics"
    DEVOPS = "devops"
    QA = "qa"
    SECURITY = "security"
    ARCHITECTURE = "architecture"


@dataclass
class AgentConfig:
    """Configuração de um agente."""
    name: str
    role: str
    llm_model: str
    specialization: str
    system_prompt_additions: str = ""


@dataclass
class TeamConfig:
    """Configuração de um time."""
    team_type: TeamType
    name: str
    domain: str
    description: str
    master_config: AgentConfig
    operational_agents: List[AgentConfig]
    collaboration_topics: List[str]  # Tópicos que este time pode ajudar outros


# ============================================================================
# CONFIGURAÇÕES DOS TIMES
# ============================================================================

TEAM_CONFIGS: Dict[TeamType, TeamConfig] = {
    
    # ==================== PRODUCT OWNER ====================
    TeamType.PRODUCT_OWNER: TeamConfig(
        team_type=TeamType.PRODUCT_OWNER,
        name="Product Owner Team",
        domain="product_owner",
        description="Responsável por definir requisitos, priorizar backlog e garantir valor de negócio",
        master_config=AgentConfig(
            name="PO Master",
            role="Product Owner Líder",
            llm_model="gpt-4.1-mini",
            specialization="Consolidação de requisitos e priorização estratégica"
        ),
        operational_agents=[
            AgentConfig(
                name="Analista de Requisitos",
                role="Especialista em elicitação e documentação de requisitos",
                llm_model="gpt-4.1-mini",
                specialization="User stories, critérios de aceitação, BDD"
            ),
            AgentConfig(
                name="Analista de Negócios",
                role="Especialista em análise de valor e ROI",
                llm_model="gpt-4.1-nano",
                specialization="Business cases, métricas de sucesso, KPIs"
            ),
            AgentConfig(
                name="UX Researcher",
                role="Especialista em experiência do usuário",
                llm_model="gemini-2.5-flash",
                specialization="Personas, jornadas do usuário, usabilidade"
            )
        ],
        collaboration_topics=["requisitos", "priorização", "valor_negócio", "user_stories"]
    ),
    
    # ==================== PROJECT MANAGER ====================
    TeamType.PROJECT_MANAGER: TeamConfig(
        team_type=TeamType.PROJECT_MANAGER,
        name="Project Manager Team",
        domain="project_manager",
        description="Responsável por planejamento, cronograma, riscos e entregas",
        master_config=AgentConfig(
            name="PM Master",
            role="Project Manager Líder",
            llm_model="gpt-4.1-mini",
            specialization="Consolidação de planos e gestão de riscos"
        ),
        operational_agents=[
            AgentConfig(
                name="Planejador de Projeto",
                role="Especialista em cronogramas e WBS",
                llm_model="gpt-4.1-mini",
                specialization="Gantt, milestones, dependências, caminho crítico"
            ),
            AgentConfig(
                name="Gestor de Riscos",
                role="Especialista em identificação e mitigação de riscos",
                llm_model="gpt-4.1-nano",
                specialization="Matriz de riscos, planos de contingência"
            ),
            AgentConfig(
                name="Scrum Master",
                role="Especialista em metodologias ágeis",
                llm_model="gemini-2.5-flash",
                specialization="Sprints, retrospectivas, velocity, burndown"
            )
        ],
        collaboration_topics=["cronograma", "riscos", "entregas", "sprints", "recursos"]
    ),
    
    # ==================== DATA ENGINEERING ====================
    TeamType.DATA_ENGINEERING: TeamConfig(
        team_type=TeamType.DATA_ENGINEERING,
        name="Data Engineering Team",
        domain="data_engineering",
        description="Responsável por pipelines de dados, ETL/ELT, e infraestrutura de dados",
        master_config=AgentConfig(
            name="Data Engineering Master",
            role="Engenheiro de Dados Líder",
            llm_model="gpt-4.1-mini",
            specialization="Arquitetura de dados e validação de pipelines"
        ),
        operational_agents=[
            AgentConfig(
                name="Arquiteto de Dados",
                role="Especialista em arquitetura e modelagem de dados",
                llm_model="gpt-4.1-mini",
                specialization="Data warehouse, data lake, modelagem dimensional"
            ),
            AgentConfig(
                name="Engenheiro de ETL",
                role="Especialista em pipelines de extração e transformação",
                llm_model="gpt-4.1-nano",
                specialization="Airflow, dbt, Spark, qualidade de dados"
            ),
            AgentConfig(
                name="Especialista em Streaming",
                role="Especialista em processamento em tempo real",
                llm_model="gemini-2.5-flash",
                specialization="Kafka, Flink, CDC, event-driven architecture"
            )
        ],
        collaboration_topics=["pipelines", "dados", "etl", "data_warehouse", "streaming"]
    ),
    
    # ==================== DATA SCIENCE ====================
    TeamType.DATA_SCIENCE: TeamConfig(
        team_type=TeamType.DATA_SCIENCE,
        name="Data Science Team",
        domain="data_science",
        description="Responsável por modelos de ML, análises preditivas e MLOps",
        master_config=AgentConfig(
            name="Data Science Master",
            role="Cientista de Dados Líder",
            llm_model="gpt-4.1-mini",
            specialization="Validação de modelos e metodologia científica"
        ),
        operational_agents=[
            AgentConfig(
                name="Cientista de Dados",
                role="Especialista em modelagem estatística e ML",
                llm_model="gpt-4.1-mini",
                specialization="Regressão, classificação, clustering, feature engineering"
            ),
            AgentConfig(
                name="Engenheiro de ML",
                role="Especialista em MLOps e produtização de modelos",
                llm_model="gpt-4.1-nano",
                specialization="MLflow, Kubeflow, model serving, A/B testing"
            ),
            AgentConfig(
                name="Especialista em Deep Learning",
                role="Especialista em redes neurais e NLP",
                llm_model="gemini-2.5-flash",
                specialization="Transformers, CNN, RNN, embeddings, LLMs"
            )
        ],
        collaboration_topics=["machine_learning", "modelos", "previsão", "mlops", "features"]
    ),
    
    # ==================== DATA ANALYTICS ====================
    TeamType.DATA_ANALYTICS: TeamConfig(
        team_type=TeamType.DATA_ANALYTICS,
        name="Data Analytics Team",
        domain="data_analytics",
        description="Responsável por análises, dashboards e insights de negócio",
        master_config=AgentConfig(
            name="Analytics Master",
            role="Analista de Dados Líder",
            llm_model="gpt-4.1-mini",
            specialization="Validação de análises e storytelling com dados"
        ),
        operational_agents=[
            AgentConfig(
                name="Analista de Dados",
                role="Especialista em análise exploratória e SQL",
                llm_model="gpt-4.1-mini",
                specialization="SQL avançado, análise estatística, segmentação"
            ),
            AgentConfig(
                name="Especialista em Visualização",
                role="Especialista em dashboards e data viz",
                llm_model="gpt-4.1-nano",
                specialization="Tableau, Power BI, Metabase, design de dashboards"
            ),
            AgentConfig(
                name="Business Intelligence Analyst",
                role="Especialista em métricas de negócio",
                llm_model="gemini-2.5-flash",
                specialization="KPIs, OKRs, análise de cohort, funil de conversão"
            )
        ],
        collaboration_topics=["dashboards", "métricas", "kpis", "visualização", "insights"]
    ),
    
    # ==================== DEVOPS ====================
    TeamType.DEVOPS: TeamConfig(
        team_type=TeamType.DEVOPS,
        name="DevOps Team",
        domain="devops",
        description="Responsável por infraestrutura, CI/CD, e operações",
        master_config=AgentConfig(
            name="DevOps Master",
            role="Engenheiro DevOps Líder",
            llm_model="gpt-4.1-mini",
            specialization="Arquitetura de infraestrutura e automação"
        ),
        operational_agents=[
            AgentConfig(
                name="Engenheiro de Infraestrutura",
                role="Especialista em cloud e IaC",
                llm_model="gpt-4.1-mini",
                specialization="AWS, GCP, Terraform, Kubernetes, Docker"
            ),
            AgentConfig(
                name="Especialista em CI/CD",
                role="Especialista em pipelines de deploy",
                llm_model="gpt-4.1-nano",
                specialization="GitHub Actions, Jenkins, ArgoCD, GitOps"
            ),
            AgentConfig(
                name="SRE - Site Reliability Engineer",
                role="Especialista em confiabilidade e observabilidade",
                llm_model="gemini-2.5-flash",
                specialization="Prometheus, Grafana, alertas, SLOs, incident response"
            )
        ],
        collaboration_topics=["infraestrutura", "deploy", "kubernetes", "monitoramento", "cloud"]
    ),
    
    # ==================== QA ====================
    TeamType.QA: TeamConfig(
        team_type=TeamType.QA,
        name="QA Team",
        domain="qa",
        description="Responsável por qualidade, testes e validação",
        master_config=AgentConfig(
            name="QA Master",
            role="QA Lead",
            llm_model="gpt-4.1-mini",
            specialization="Estratégia de testes e garantia de qualidade"
        ),
        operational_agents=[
            AgentConfig(
                name="Engenheiro de Testes",
                role="Especialista em automação de testes",
                llm_model="gpt-4.1-mini",
                specialization="Pytest, Selenium, testes unitários, integração"
            ),
            AgentConfig(
                name="Especialista em Data Quality",
                role="Especialista em qualidade de dados",
                llm_model="gpt-4.1-nano",
                specialization="Great Expectations, dbt tests, validação de schema"
            ),
            AgentConfig(
                name="Performance Tester",
                role="Especialista em testes de performance",
                llm_model="gemini-2.5-flash",
                specialization="Load testing, stress testing, benchmarking"
            )
        ],
        collaboration_topics=["testes", "qualidade", "validação", "data_quality", "performance"]
    ),
    
    # ==================== SECURITY ====================
    TeamType.SECURITY: TeamConfig(
        team_type=TeamType.SECURITY,
        name="Security Team",
        domain="security",
        description="Responsável por segurança, compliance e proteção de dados",
        master_config=AgentConfig(
            name="Security Master",
            role="Security Lead",
            llm_model="gpt-4.1-mini",
            specialization="Arquitetura de segurança e compliance"
        ),
        operational_agents=[
            AgentConfig(
                name="Engenheiro de Segurança",
                role="Especialista em segurança de aplicações",
                llm_model="gpt-4.1-mini",
                specialization="OWASP, criptografia, autenticação, autorização"
            ),
            AgentConfig(
                name="Especialista em Compliance",
                role="Especialista em regulamentações",
                llm_model="gpt-4.1-nano",
                specialization="LGPD, GDPR, SOC2, ISO 27001"
            ),
            AgentConfig(
                name="Data Privacy Officer",
                role="Especialista em privacidade de dados",
                llm_model="gemini-2.5-flash",
                specialization="Anonimização, pseudonimização, consentimento"
            )
        ],
        collaboration_topics=["segurança", "lgpd", "compliance", "criptografia", "privacidade"]
    ),
    
    # ==================== ARCHITECTURE ====================
    TeamType.ARCHITECTURE: TeamConfig(
        team_type=TeamType.ARCHITECTURE,
        name="Architecture Team",
        domain="architecture",
        description="Responsável por decisões arquiteturais e padrões técnicos",
        master_config=AgentConfig(
            name="Architecture Master",
            role="Arquiteto de Soluções Líder",
            llm_model="gpt-4.1-mini",
            specialization="Decisões arquiteturais e trade-offs"
        ),
        operational_agents=[
            AgentConfig(
                name="Arquiteto de Soluções",
                role="Especialista em arquitetura de sistemas",
                llm_model="gpt-4.1-mini",
                specialization="Microservices, event-driven, CQRS, DDD"
            ),
            AgentConfig(
                name="Arquiteto de Dados",
                role="Especialista em arquitetura de dados",
                llm_model="gpt-4.1-nano",
                specialization="Data mesh, data fabric, lakehouse"
            ),
            AgentConfig(
                name="Arquiteto Cloud",
                role="Especialista em arquitetura cloud-native",
                llm_model="gemini-2.5-flash",
                specialization="Well-architected framework, multi-cloud, serverless"
            )
        ],
        collaboration_topics=["arquitetura", "padrões", "decisões_técnicas", "trade_offs"]
    ),
}


class TeamsFactory:
    """
    Fábrica para criar times de agentes pré-configurados.
    """
    
    @staticmethod
    def get_team_config(team_type: TeamType) -> TeamConfig:
        """Obtém a configuração de um time."""
        if team_type not in TEAM_CONFIGS:
            raise ValueError(f"Team type {team_type} não configurado")
        return TEAM_CONFIGS[team_type]
    
    @staticmethod
    def list_available_teams() -> List[Dict[str, Any]]:
        """Lista todos os times disponíveis."""
        return [
            {
                "type": config.team_type.value,
                "name": config.name,
                "description": config.description,
                "agents_count": len(config.operational_agents) + 1,  # +1 para o master
                "collaboration_topics": config.collaboration_topics
            }
            for config in TEAM_CONFIGS.values()
        ]
    
    @staticmethod
    def get_teams_for_topic(topic: str) -> List[TeamType]:
        """Encontra times que podem ajudar com um tópico específico."""
        matching_teams = []
        topic_lower = topic.lower()
        
        for team_type, config in TEAM_CONFIGS.items():
            for collab_topic in config.collaboration_topics:
                if topic_lower in collab_topic.lower() or collab_topic.lower() in topic_lower:
                    matching_teams.append(team_type)
                    break
        
        return matching_teams
    
    @staticmethod
    def get_all_team_types() -> List[TeamType]:
        """Retorna todos os tipos de time disponíveis."""
        return list(TEAM_CONFIGS.keys())


# Singleton da fábrica
_factory_instance: Optional[TeamsFactory] = None


def get_teams_factory() -> TeamsFactory:
    """Obtém a instância singleton da fábrica de times."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = TeamsFactory()
    return _factory_instance


# ============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================================================

def list_teams() -> None:
    """Imprime a lista de times disponíveis."""
    factory = get_teams_factory()
    teams = factory.list_available_teams()
    
    print("\n" + "=" * 60)
    print("  TIMES DISPONÍVEIS NA AUTONOMOUS DATA AGENCY")
    print("=" * 60)
    
    for team in teams:
        print(f"\n📋 {team['name']}")
        print(f"   Tipo: {team['type']}")
        print(f"   Descrição: {team['description']}")
        print(f"   Agentes: {team['agents_count']} (1 Master + {team['agents_count']-1} Operacionais)")
        print(f"   Tópicos: {', '.join(team['collaboration_topics'])}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    list_teams()
