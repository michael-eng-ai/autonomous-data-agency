"""
Project Manager Module

Gerencia o ciclo de vida completo de projetos:
- Criação e listagem de projetos
- Tracking de status (iniciado, em andamento, concluído)
- Histórico de atividades
- Preparação para push ao GitHub
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from core.project_generator import get_project_generator, ProjectType


class ProjectStatus(Enum):
    """Status possíveis de um projeto."""
    INITIATED = "initiated"        # Projeto criado, aguardando análise
    ANALYZING = "analyzing"        # PO/PM analisando requisitos
    PLANNING = "planning"          # Criando plano de projeto
    GENERATING = "generating"      # Gerando código/artefatos
    IN_PROGRESS = "in_progress"    # Em desenvolvimento pelos times
    REVIEW = "review"              # Em revisão/validação
    COMPLETED = "completed"        # Concluído
    DELIVERED = "delivered"        # Entregue ao cliente
    CANCELLED = "cancelled"        # Cancelado


@dataclass
class ProjectActivity:
    """Registro de atividade do projeto."""
    timestamp: str
    action: str
    team: Optional[str]
    details: str


@dataclass
class ProjectInfo:
    """Informações completas de um projeto."""
    project_id: str
    name: str
    description: str
    project_type: str
    status: ProjectStatus
    created_at: str
    updated_at: str
    path: str
    teams_involved: List[str]
    activities: List[ProjectActivity]
    github_url: Optional[str] = None


class ProjectManager:
    """
    Gerenciador central de projetos.
    
    Mantém registro de todos os projetos, seus status e histórico.
    """
    
    PROJECTS_INDEX_FILE = "projects_index.json"
    
    def __init__(self, base_path: str = "projects"):
        """
        Inicializa o gerenciador de projetos.
        
        Args:
            base_path: Caminho base onde os projetos são armazenados
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.base_path / self.PROJECTS_INDEX_FILE
        self.generator = get_project_generator(base_path)
        
        # Carrega índice de projetos
        self._projects_index: Dict[str, ProjectInfo] = {}
        self._load_index()
    
    def _load_index(self):
        """Carrega o índice de projetos do disco."""
        if self.index_path.exists():
            try:
                data = json.loads(self.index_path.read_text(encoding='utf-8'))
                for proj_id, proj_data in data.items():
                    # Converte status string para enum
                    proj_data['status'] = ProjectStatus(proj_data['status'])
                    # Converte activities
                    proj_data['activities'] = [
                        ProjectActivity(**act) for act in proj_data.get('activities', [])
                    ]
                    self._projects_index[proj_id] = ProjectInfo(**proj_data)
            except Exception as e:
                print(f"Erro ao carregar índice de projetos: {e}")
                self._projects_index = {}
        
        # Sincroniza com projetos no disco que podem não estar no índice
        self._sync_with_disk()
    
    def _sync_with_disk(self):
        """Sincroniza o índice com projetos existentes no disco."""
        disk_projects = self.generator.list_projects()
        
        for proj in disk_projects:
            if proj['project_id'] not in self._projects_index:
                # Projeto existe no disco mas não no índice
                self._projects_index[proj['project_id']] = ProjectInfo(
                    project_id=proj['project_id'],
                    name=proj['project_name'],
                    description="",
                    project_type=proj['project_type'],
                    status=ProjectStatus(proj['status']),
                    created_at=proj['created_at'],
                    updated_at=proj['created_at'],
                    path=proj['path'],
                    teams_involved=[],
                    activities=[],
                    github_url=None
                )
        
        self._save_index()
    
    def _save_index(self):
        """Salva o índice de projetos no disco."""
        data = {}
        for proj_id, proj_info in self._projects_index.items():
            proj_dict = {
                'project_id': proj_info.project_id,
                'name': proj_info.name,
                'description': proj_info.description,
                'project_type': proj_info.project_type,
                'status': proj_info.status.value,
                'created_at': proj_info.created_at,
                'updated_at': proj_info.updated_at,
                'path': proj_info.path,
                'teams_involved': proj_info.teams_involved,
                'activities': [asdict(act) for act in proj_info.activities],
                'github_url': proj_info.github_url
            }
            data[proj_id] = proj_dict
        
        self.index_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def create_project(
        self,
        name: str,
        description: str,
        project_type: str = "fullstack"
    ) -> ProjectInfo:
        """
        Cria um novo projeto.
        
        Args:
            name: Nome do projeto
            description: Descrição/requisitos do cliente
            project_type: Tipo do projeto
            
        Returns:
            Informações do projeto criado
        """
        # Gera ID único
        project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Mapeia tipo de projeto
        type_mapping = {
            "web_app": ProjectType.WEB_APP,
            "api_only": ProjectType.API_ONLY,
            "data_pipeline": ProjectType.DATA_PIPELINE,
            "ml_project": ProjectType.ML_PROJECT,
            "mobile_app": ProjectType.MOBILE_APP,
            "fullstack": ProjectType.FULLSTACK,
            "microservices": ProjectType.MICROSERVICES
        }
        pt = type_mapping.get(project_type, ProjectType.FULLSTACK)
        
        # Cria estrutura do projeto via generator
        project_structure = self.generator.create_project(
            project_id=project_id,
            project_name=name,
            project_type=pt,
            client_request=description
        )
        
        # Cria registro no índice
        now = datetime.now().isoformat()
        project_info = ProjectInfo(
            project_id=project_id,
            name=name,
            description=description,
            project_type=project_type,
            status=ProjectStatus.INITIATED,
            created_at=now,
            updated_at=now,
            path=project_structure.root_path,
            teams_involved=[],
            activities=[
                ProjectActivity(
                    timestamp=now,
                    action="project_created",
                    team=None,
                    details=f"Projeto '{name}' criado com tipo {project_type}"
                )
            ],
            github_url=None
        )
        
        self._projects_index[project_id] = project_info
        self._save_index()
        
        return project_info
    
    def get_project(self, project_id: str) -> Optional[ProjectInfo]:
        """Obtém informações de um projeto pelo ID."""
        return self._projects_index.get(project_id)
    
    def update_status(self, project_id: str, new_status: ProjectStatus, details: str = ""):
        """
        Atualiza o status de um projeto.
        
        Args:
            project_id: ID do projeto
            new_status: Novo status
            details: Detalhes da atualização
        """
        if project_id not in self._projects_index:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        project = self._projects_index[project_id]
        old_status = project.status
        project.status = new_status
        project.updated_at = datetime.now().isoformat()
        
        project.activities.append(ProjectActivity(
            timestamp=project.updated_at,
            action="status_change",
            team=None,
            details=f"Status alterado de {old_status.value} para {new_status.value}. {details}"
        ))
        
        self._save_index()
    
    def add_activity(
        self,
        project_id: str,
        action: str,
        team: Optional[str],
        details: str
    ):
        """
        Adiciona uma atividade ao histórico do projeto.
        
        Args:
            project_id: ID do projeto
            action: Tipo da ação
            team: Time responsável (se aplicável)
            details: Detalhes da atividade
        """
        if project_id not in self._projects_index:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        project = self._projects_index[project_id]
        project.updated_at = datetime.now().isoformat()
        
        project.activities.append(ProjectActivity(
            timestamp=project.updated_at,
            action=action,
            team=team,
            details=details
        ))
        
        if team and team not in project.teams_involved:
            project.teams_involved.append(team)
        
        self._save_index()
    
    def list_projects(
        self,
        status_filter: Optional[ProjectStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista todos os projetos.
        
        Args:
            status_filter: Filtrar por status específico
            
        Returns:
            Lista de projetos com informações básicas
        """
        projects = []
        
        for proj_id, proj_info in self._projects_index.items():
            if status_filter and proj_info.status != status_filter:
                continue
            
            projects.append({
                "project_id": proj_info.project_id,
                "name": proj_info.name,
                "description": proj_info.description[:100] + "..." if len(proj_info.description) > 100 else proj_info.description,
                "project_type": proj_info.project_type,
                "status": proj_info.status.value,
                "created_at": proj_info.created_at,
                "updated_at": proj_info.updated_at,
                "teams_involved": proj_info.teams_involved,
                "github_url": proj_info.github_url
            })
        
        # Ordena por data de criação (mais recente primeiro)
        projects.sort(key=lambda x: x['created_at'], reverse=True)
        
        return projects
    
    def get_projects_summary(self) -> Dict[str, Any]:
        """Retorna um resumo estatístico dos projetos."""
        status_counts = {status.value: 0 for status in ProjectStatus}
        
        for proj_info in self._projects_index.values():
            status_counts[proj_info.status.value] += 1
        
        return {
            "total": len(self._projects_index),
            "by_status": status_counts,
            "active": status_counts[ProjectStatus.IN_PROGRESS.value] + 
                     status_counts[ProjectStatus.ANALYZING.value] +
                     status_counts[ProjectStatus.PLANNING.value] +
                     status_counts[ProjectStatus.REVIEW.value],
            "completed": status_counts[ProjectStatus.COMPLETED.value] +
                        status_counts[ProjectStatus.DELIVERED.value]
        }
    
    def prepare_for_github(self, project_id: str) -> str:
        """
        Prepara um projeto para ser enviado ao GitHub.
        Inicializa git no projeto se necessário.
        
        Args:
            project_id: ID do projeto
            
        Returns:
            Caminho do projeto preparado
        """
        if project_id not in self._projects_index:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        project = self._projects_index[project_id]
        project_path = Path(project.path)
        
        # Verifica se já tem .git
        git_path = project_path / ".git"
        if not git_path.exists():
            # Inicializa repositório git
            subprocess.run(
                ["git", "init"],
                cwd=project_path,
                capture_output=True
            )
            
            # Cria .gitignore se não existir
            gitignore_path = project_path / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = """# Dependencies
node_modules/
venv/
.venv/
__pycache__/
*.pyc

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# Build
dist/
build/

# Logs
*.log

# OS
.DS_Store
"""
                gitignore_path.write_text(gitignore_content)
            
            # Add e commit inicial
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit - Generated by Autonomous Data Agency"],
                cwd=project_path,
                capture_output=True
            )
        
        self.add_activity(
            project_id,
            "github_prepared",
            None,
            "Projeto preparado para GitHub (git init realizado)"
        )
        
        return str(project_path)
    
    def set_github_url(self, project_id: str, github_url: str):
        """
        Define a URL do GitHub para um projeto.
        
        Args:
            project_id: ID do projeto
            github_url: URL do repositório no GitHub
        """
        if project_id not in self._projects_index:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        project = self._projects_index[project_id]
        project.github_url = github_url
        project.updated_at = datetime.now().isoformat()
        
        project.activities.append(ProjectActivity(
            timestamp=project.updated_at,
            action="github_linked",
            team=None,
            details=f"Projeto linkado ao GitHub: {github_url}"
        ))
        
        self._save_index()
    
    def get_project_details(self, project_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de um projeto.
        
        Args:
            project_id: ID do projeto
            
        Returns:
            Dicionário com todos os detalhes do projeto
        """
        if project_id not in self._projects_index:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        project = self._projects_index[project_id]
        project_path = Path(project.path)
        
        # Lista arquivos do projeto
        files = []
        if project_path.exists():
            for root, dirs, filenames in os.walk(project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                for filename in filenames:
                    if not filename.startswith('.'):
                        full_path = Path(root) / filename
                        rel_path = full_path.relative_to(project_path)
                        files.append({
                            "path": str(rel_path),
                            "size": full_path.stat().st_size
                        })
        
        return {
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "project_type": project.project_type,
            "status": project.status.value,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "path": project.path,
            "teams_involved": project.teams_involved,
            "activities": [asdict(act) for act in project.activities],
            "github_url": project.github_url,
            "files": files,
            "files_count": len(files)
        }


# Singleton instance
_manager_instance: Optional[ProjectManager] = None


def get_project_manager(base_path: str = "projects") -> ProjectManager:
    """Factory function para obter o gerenciador de projetos (Singleton)."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ProjectManager(base_path)
    return _manager_instance


if __name__ == "__main__":
    # Teste do gerenciador
    manager = get_project_manager()
    
    # Cria um projeto de teste
    project = manager.create_project(
        name="Sistema de E-commerce",
        description="Preciso de uma loja virtual com carrinho de compras, pagamentos e gestão de estoque",
        project_type="fullstack"
    )
    
    print(f"\n✅ Projeto criado: {project.name}")
    print(f"   ID: {project.project_id}")
    print(f"   Status: {project.status.value}")
    print(f"   Path: {project.path}")
    
    # Lista projetos
    print("\n📋 Projetos existentes:")
    for p in manager.list_projects():
        print(f"   [{p['status']}] {p['project_id']} - {p['name']}")
    
    # Resumo
    summary = manager.get_projects_summary()
    print(f"\n📊 Resumo:")
    print(f"   Total: {summary['total']}")
    print(f"   Ativos: {summary['active']}")
    print(f"   Concluídos: {summary['completed']}")
