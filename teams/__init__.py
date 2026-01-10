"""
Teams Package

Este pacote contém todos os times de agentes especializados.
Cada time segue a arquitetura:
- 1 Agente Mestre (validador/consolidador)
- 2-3 Agentes Operacionais (cada um com LLM diferente)

Times Disponíveis:
==================

GESTÃO E PLANEJAMENTO:
- Product Owner: Requisitos e escopo
- Project Manager: Planejamento e gestão
- Architecture: Decisões arquiteturais

DESENVOLVIMENTO:
- Frontend: Interfaces web e SPAs
- Backend: APIs e serviços
- Mobile: Apps iOS, Android, Cross-platform
- Fullstack: Desenvolvimento end-to-end
- Database: Modelagem e administração de BDs

DADOS E ANALYTICS:
- Data Engineering: Arquitetura e pipelines
- Data Science: ML e MLOps
- Data Analytics: Análises e dashboards

QUALIDADE E OPERAÇÕES:
- DevOps: Infraestrutura e CI/CD
- QA: Testes e qualidade
- Security: Segurança e compliance
- UX/UI: Design de experiência e interface
"""

# Gestão e Planejamento
from .product_owner import ProductOwnerTeam, get_product_owner_team
from .project_manager import ProjectManagerTeam, get_project_manager_team
from .architecture import ArchitectureTeam, get_architecture_team

# Desenvolvimento
from .frontend import FrontendTeam, get_frontend_team
from .backend import BackendTeam, get_backend_team
from .mobile import MobileTeam, get_mobile_team
from .fullstack import FullstackTeam, get_fullstack_team
from .database import DatabaseTeam, get_database_team

# Dados e Analytics
from .data_engineering import DataEngineeringTeam, get_data_engineering_team
from .data_science import DataScienceTeam, get_data_science_team
from .data_analytics import DataAnalyticsTeam, get_data_analytics_team

# Qualidade e Operações
from .devops import DevOpsTeam, get_devops_team
from .qa import QATeam, get_qa_team
from .security import SecurityTeam, get_security_team
from .ux_ui import UXUITeam, get_uxui_team

__all__ = [
    # Gestão e Planejamento
    "ProductOwnerTeam", "get_product_owner_team",
    "ProjectManagerTeam", "get_project_manager_team",
    "ArchitectureTeam", "get_architecture_team",
    # Desenvolvimento
    "FrontendTeam", "get_frontend_team",
    "BackendTeam", "get_backend_team",
    "MobileTeam", "get_mobile_team",
    "FullstackTeam", "get_fullstack_team",
    "DatabaseTeam", "get_database_team",
    # Dados e Analytics
    "DataEngineeringTeam", "get_data_engineering_team",
    "DataScienceTeam", "get_data_science_team",
    "DataAnalyticsTeam", "get_data_analytics_team",
    # Qualidade e Operações
    "DevOpsTeam", "get_devops_team",
    "QATeam", "get_qa_team",
    "SecurityTeam", "get_security_team",
    "UXUITeam", "get_uxui_team",
]


def get_all_teams():
    """Retorna instâncias de todos os times disponíveis."""
    return {
        # Gestão
        "product_owner": get_product_owner_team(),
        "project_manager": get_project_manager_team(),
        "architecture": get_architecture_team(),
        # Desenvolvimento
        "frontend": get_frontend_team(),
        "backend": get_backend_team(),
        "mobile": get_mobile_team(),
        "fullstack": get_fullstack_team(),
        "database": get_database_team(),
        # Dados
        "data_engineering": get_data_engineering_team(),
        "data_science": get_data_science_team(),
        "data_analytics": get_data_analytics_team(),
        # Operações
        "devops": get_devops_team(),
        "qa": get_qa_team(),
        "security": get_security_team(),
        "ux_ui": get_uxui_team(),
    }


def get_team_by_name(team_name: str):
    """Retorna um time específico pelo nome."""
    teams = get_all_teams()
    return teams.get(team_name.lower().replace(" ", "_"))


def list_available_teams():
    """Lista todos os times disponíveis com suas descrições."""
    teams_info = {
        "product_owner": "Requisitos, user stories e priorização",
        "project_manager": "Planejamento, cronograma e riscos",
        "architecture": "Decisões arquiteturais e padrões técnicos",
        "frontend": "Interfaces web, SPAs e React/Vue",
        "backend": "APIs, serviços e lógica de negócio",
        "mobile": "Apps iOS, Android e cross-platform",
        "fullstack": "Desenvolvimento web end-to-end",
        "database": "Modelagem e administração de bancos",
        "data_engineering": "Pipelines ETL/ELT e arquitetura de dados",
        "data_science": "Machine Learning e MLOps",
        "data_analytics": "Dashboards, métricas e insights",
        "devops": "Infraestrutura, CI/CD e cloud",
        "qa": "Testes, qualidade e validação",
        "security": "Segurança, LGPD e compliance",
        "ux_ui": "Design de experiência e interface",
    }
    return teams_info
