"""
Teams Package

Este pacote contém todos os times de agentes especializados.
Cada time segue a arquitetura:
- 1 Agente Mestre (validador/consolidador)
- 2 Agentes Operacionais (cada um com LLM diferente)

Times Disponíveis:
- Product Owner: Requisitos e escopo
- Project Manager: Planejamento e gestão
- Data Engineering: Arquitetura e pipelines
- Data Science: ML e MLOps
- Data Analytics: Análises e dashboards
- DevOps: Infraestrutura e CI/CD
- QA: Testes e qualidade
"""

from .product_owner import ProductOwnerTeam, get_product_owner_team
from .project_manager import ProjectManagerTeam, get_project_manager_team
from .data_engineering import DataEngineeringTeam, get_data_engineering_team
from .data_science import DataScienceTeam, get_data_science_team
from .data_analytics import DataAnalyticsTeam, get_data_analytics_team
from .devops import DevOpsTeam, get_devops_team
from .qa import QATeam, get_qa_team

__all__ = [
    # Product Owner
    "ProductOwnerTeam",
    "get_product_owner_team",
    # Project Manager
    "ProjectManagerTeam",
    "get_project_manager_team",
    # Data Engineering
    "DataEngineeringTeam",
    "get_data_engineering_team",
    # Data Science
    "DataScienceTeam",
    "get_data_science_team",
    # Data Analytics
    "DataAnalyticsTeam",
    "get_data_analytics_team",
    # DevOps
    "DevOpsTeam",
    "get_devops_team",
    # QA
    "QATeam",
    "get_qa_team",
]


def get_all_teams():
    """Retorna instâncias de todos os times disponíveis."""
    return {
        "product_owner": get_product_owner_team(),
        "project_manager": get_project_manager_team(),
        "data_engineering": get_data_engineering_team(),
        "data_science": get_data_science_team(),
        "data_analytics": get_data_analytics_team(),
        "devops": get_devops_team(),
        "qa": get_qa_team(),
    }
