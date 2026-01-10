"""
Project Generator Module

Este módulo é responsável por:
- Criar estrutura de pastas para projetos gerados
- Gerar arquivos de código baseado nas especificações dos times
- Empacotar projetos para entrega ao cliente
- Manter versionamento dos projetos

Estrutura de pastas:
/projects/
├── proj_001_sistema_vendas/
│   ├── .gitignore
│   ├── README.md
│   ├── docs/
│   │   ├── requisitos.md (PO)
│   │   ├── plano_projeto.md (PM)
│   │   ├── arquitetura.md (Arquiteto)
│   │   └── especificacoes/
│   ├── src/
│   │   ├── backend/
│   │   ├── frontend/
│   │   └── database/
│   ├── tests/
│   ├── infra/
│   │   ├── docker/
│   │   └── terraform/
│   └── .agency/
│       ├── project_state.json
│       └── execution_log.json
"""

import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class ProjectType(Enum):
    """Tipos de projeto que podem ser gerados."""
    WEB_APP = "web_app"           # Frontend + Backend
    API_ONLY = "api_only"         # Apenas Backend/API
    DATA_PIPELINE = "data_pipeline"  # ETL/Data Engineering
    ML_PROJECT = "ml_project"     # Data Science/ML
    MOBILE_APP = "mobile_app"     # App Mobile
    FULLSTACK = "fullstack"       # Web completo
    MICROSERVICES = "microservices"  # Arquitetura distribuída


@dataclass
class GeneratedFile:
    """Representa um arquivo gerado."""
    path: str
    content: str
    generated_by: str  # Nome do time/agente que gerou
    timestamp: str
    description: str


@dataclass
class ProjectStructure:
    """Estrutura completa de um projeto gerado."""
    project_id: str
    project_name: str
    project_type: ProjectType
    client_request: str
    root_path: str
    files: List[GeneratedFile]
    teams_involved: List[str]
    created_at: str
    status: str  # "generating", "ready", "delivered"


class ProjectGenerator:
    """
    Gerador de projetos da agência.
    
    Responsável por criar a estrutura de arquivos e pastas
    baseado nas especificações dos times de agentes.
    """
    
    PROJECTS_BASE_PATH = "projects"
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Inicializa o gerador de projetos.
        
        Args:
            base_path: Caminho base para os projetos (default: ./projects)
        """
        self.base_path = Path(base_path or self.PROJECTS_BASE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Cache de projetos ativos
        self._active_projects: Dict[str, ProjectStructure] = {}
    
    def create_project(
        self,
        project_id: str,
        project_name: str,
        project_type: ProjectType,
        client_request: str
    ) -> ProjectStructure:
        """
        Cria a estrutura inicial de um novo projeto.
        
        Args:
            project_id: ID único do projeto
            project_name: Nome do projeto
            project_type: Tipo do projeto
            client_request: Solicitação original do cliente
            
        Returns:
            Estrutura do projeto criado
        """
        # Sanitiza o nome para uso em pasta
        safe_name = self._sanitize_folder_name(project_name)
        folder_name = f"{project_id}_{safe_name}"
        project_path = self.base_path / folder_name
        
        # Cria a estrutura de pastas
        self._create_folder_structure(project_path, project_type)
        
        # Cria arquivos base
        base_files = self._create_base_files(
            project_id, project_name, client_request, project_type
        )
        
        # Escreve os arquivos
        for file in base_files:
            full_path = project_path / file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(file.content, encoding='utf-8')
        
        # Cria estrutura do projeto
        project = ProjectStructure(
            project_id=project_id,
            project_name=project_name,
            project_type=project_type,
            client_request=client_request,
            root_path=str(project_path),
            files=base_files,
            teams_involved=[],
            created_at=datetime.now().isoformat(),
            status="generating"
        )
        
        # Salva estado do projeto
        self._save_project_state(project)
        self._active_projects[project_id] = project
        
        return project
    
    def _sanitize_folder_name(self, name: str) -> str:
        """Converte nome para formato seguro de pasta."""
        import re
        # Remove caracteres especiais, mantém apenas letras, números, underscore
        safe = re.sub(r'[^\w\s-]', '', name.lower())
        safe = re.sub(r'[-\s]+', '_', safe)
        return safe[:50]  # Limita tamanho
    
    def _create_folder_structure(self, project_path: Path, project_type: ProjectType):
        """Cria a estrutura de pastas baseada no tipo de projeto."""
        
        # Estrutura base comum a todos
        base_folders = [
            "docs",
            "docs/especificacoes",
            ".agency",
        ]
        
        # Estruturas específicas por tipo
        type_folders = {
            ProjectType.WEB_APP: [
                "src/frontend",
                "src/backend",
                "src/shared",
                "tests/unit",
                "tests/integration",
                "infra/docker",
            ],
            ProjectType.API_ONLY: [
                "src/api",
                "src/models",
                "src/services",
                "src/utils",
                "tests/unit",
                "tests/integration",
                "infra/docker",
            ],
            ProjectType.DATA_PIPELINE: [
                "src/pipelines",
                "src/transformations",
                "src/loaders",
                "src/extractors",
                "src/quality",
                "tests",
                "dags",
                "infra/docker",
                "infra/terraform",
            ],
            ProjectType.ML_PROJECT: [
                "src/data",
                "src/features",
                "src/models",
                "src/training",
                "src/serving",
                "notebooks",
                "tests",
                "mlflow",
                "infra/docker",
            ],
            ProjectType.MOBILE_APP: [
                "src/app",
                "src/components",
                "src/screens",
                "src/services",
                "src/navigation",
                "tests",
                "assets",
            ],
            ProjectType.FULLSTACK: [
                "src/frontend/components",
                "src/frontend/pages",
                "src/frontend/styles",
                "src/backend/api",
                "src/backend/models",
                "src/backend/services",
                "src/database/migrations",
                "src/database/seeds",
                "tests/frontend",
                "tests/backend",
                "tests/e2e",
                "infra/docker",
                "infra/kubernetes",
            ],
            ProjectType.MICROSERVICES: [
                "services",
                "shared/libs",
                "shared/proto",
                "gateway",
                "infra/docker",
                "infra/kubernetes",
                "infra/terraform",
            ],
        }
        
        all_folders = base_folders + type_folders.get(project_type, [])
        
        for folder in all_folders:
            (project_path / folder).mkdir(parents=True, exist_ok=True)
    
    def _create_base_files(
        self,
        project_id: str,
        project_name: str,
        client_request: str,
        project_type: ProjectType
    ) -> List[GeneratedFile]:
        """Cria os arquivos base do projeto."""
        
        timestamp = datetime.now().isoformat()
        files = []
        
        # README.md
        readme_content = f"""# {project_name}

> Projeto gerado automaticamente pela Autonomous Data Agency

## 📋 Descrição

{client_request}

## 🏗️ Tipo de Projeto

**{project_type.value}**

## 📁 Estrutura

```
{project_id}/
├── docs/           # Documentação do projeto
├── src/            # Código fonte
├── tests/          # Testes automatizados
├── infra/          # Infraestrutura (Docker, Terraform, etc.)
└── .agency/        # Metadados da agência
```

## 🚀 Como Executar

Instruções de execução serão geradas após a fase de desenvolvimento.

## 📅 Criado em

{timestamp}

---
*Gerado por Autonomous Data Agency v6.0*
"""
        files.append(GeneratedFile(
            path="README.md",
            content=readme_content,
            generated_by="project_generator",
            timestamp=timestamp,
            description="README principal do projeto"
        ))
        
        # .gitignore
        gitignore_content = """# Dependencies
node_modules/
venv/
.venv/
__pycache__/
*.pyc

# Environment
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp

# Build
dist/
build/
*.egg-info/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Project specific
.agency/execution_log.json
"""
        files.append(GeneratedFile(
            path=".gitignore",
            content=gitignore_content,
            generated_by="project_generator",
            timestamp=timestamp,
            description="Configuração do Git ignore"
        ))
        
        # docs/requisitos.md (placeholder para PO)
        requisitos_content = f"""# Requisitos do Projeto

## Solicitação Original do Cliente

{client_request}

## Requisitos Funcionais

*A ser preenchido pelo time de Product Owner*

## Requisitos Não-Funcionais

*A ser preenchido pelo time de Product Owner*

## User Stories

*A ser preenchido pelo time de Product Owner*

---
*Documento gerado automaticamente - aguardando análise do PO*
"""
        files.append(GeneratedFile(
            path="docs/requisitos.md",
            content=requisitos_content,
            generated_by="project_generator",
            timestamp=timestamp,
            description="Documento de requisitos (template)"
        ))
        
        # docs/plano_projeto.md (placeholder para PM)
        plano_content = """# Plano de Projeto

## Cronograma

*A ser preenchido pelo time de Project Manager*

## Marcos (Milestones)

*A ser preenchido pelo time de Project Manager*

## Riscos Identificados

*A ser preenchido pelo time de Project Manager*

## Recursos Necessários

*A ser preenchido pelo time de Project Manager*

---
*Documento gerado automaticamente - aguardando análise do PM*
"""
        files.append(GeneratedFile(
            path="docs/plano_projeto.md",
            content=plano_content,
            generated_by="project_generator",
            timestamp=timestamp,
            description="Plano de projeto (template)"
        ))
        
        # docs/arquitetura.md (placeholder para Arquiteto)
        arquitetura_content = """# Arquitetura do Sistema

## Visão Geral

*A ser preenchido pelo time de Architecture*

## Diagrama de Arquitetura

```
[A ser gerado]
```

## Tecnologias Escolhidas

*A ser preenchido pelo time de Architecture*

## Decisões Arquiteturais (ADRs)

*A ser preenchido pelo time de Architecture*

---
*Documento gerado automaticamente - aguardando análise do Arquiteto*
"""
        files.append(GeneratedFile(
            path="docs/arquitetura.md",
            content=arquitetura_content,
            generated_by="project_generator",
            timestamp=timestamp,
            description="Documento de arquitetura (template)"
        ))
        
        return files
    
    def add_file(
        self,
        project_id: str,
        file_path: str,
        content: str,
        generated_by: str,
        description: str = ""
    ) -> GeneratedFile:
        """
        Adiciona um novo arquivo ao projeto.
        
        Args:
            project_id: ID do projeto
            file_path: Caminho relativo do arquivo
            content: Conteúdo do arquivo
            generated_by: Time/agente que gerou
            description: Descrição do arquivo
            
        Returns:
            O arquivo gerado
        """
        project = self._get_project(project_id)
        if not project:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        timestamp = datetime.now().isoformat()
        full_path = Path(project.root_path) / file_path
        
        # Cria diretórios se necessário
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escreve o arquivo
        full_path.write_text(content, encoding='utf-8')
        
        # Registra o arquivo
        generated_file = GeneratedFile(
            path=file_path,
            content=content,
            generated_by=generated_by,
            timestamp=timestamp,
            description=description
        )
        
        project.files.append(generated_file)
        
        if generated_by not in project.teams_involved:
            project.teams_involved.append(generated_by)
        
        self._save_project_state(project)
        
        return generated_file
    
    def update_document(
        self,
        project_id: str,
        doc_type: str,  # "requisitos", "plano_projeto", "arquitetura"
        content: str,
        generated_by: str
    ):
        """
        Atualiza um documento do projeto com o conteúdo gerado por um time.
        
        Args:
            project_id: ID do projeto
            doc_type: Tipo do documento
            content: Novo conteúdo
            generated_by: Time que gerou o conteúdo
        """
        doc_paths = {
            "requisitos": "docs/requisitos.md",
            "plano_projeto": "docs/plano_projeto.md",
            "arquitetura": "docs/arquitetura.md",
        }
        
        if doc_type not in doc_paths:
            raise ValueError(f"Tipo de documento inválido: {doc_type}")
        
        self.add_file(
            project_id=project_id,
            file_path=doc_paths[doc_type],
            content=content,
            generated_by=generated_by,
            description=f"Documento de {doc_type} atualizado"
        )
    
    def _get_project(self, project_id: str) -> Optional[ProjectStructure]:
        """Obtém um projeto pelo ID."""
        if project_id in self._active_projects:
            return self._active_projects[project_id]
        
        # Tenta carregar do disco
        return self._load_project_state(project_id)
    
    def _save_project_state(self, project: ProjectStructure):
        """Salva o estado do projeto em disco."""
        state_path = Path(project.root_path) / ".agency" / "project_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Converte para dict serializável
        state_dict = {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "project_type": project.project_type.value,
            "client_request": project.client_request,
            "root_path": project.root_path,
            "files": [asdict(f) for f in project.files],
            "teams_involved": project.teams_involved,
            "created_at": project.created_at,
            "status": project.status,
        }
        
        state_path.write_text(json.dumps(state_dict, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _load_project_state(self, project_id: str) -> Optional[ProjectStructure]:
        """Carrega o estado de um projeto do disco."""
        # Procura a pasta do projeto
        for folder in self.base_path.iterdir():
            if folder.is_dir() and folder.name.startswith(project_id):
                state_path = folder / ".agency" / "project_state.json"
                if state_path.exists():
                    state_dict = json.loads(state_path.read_text(encoding='utf-8'))
                    
                    project = ProjectStructure(
                        project_id=state_dict["project_id"],
                        project_name=state_dict["project_name"],
                        project_type=ProjectType(state_dict["project_type"]),
                        client_request=state_dict["client_request"],
                        root_path=state_dict["root_path"],
                        files=[GeneratedFile(**f) for f in state_dict["files"]],
                        teams_involved=state_dict["teams_involved"],
                        created_at=state_dict["created_at"],
                        status=state_dict["status"]
                    )
                    
                    self._active_projects[project_id] = project
                    return project
        
        return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Lista todos os projetos existentes."""
        projects = []
        
        for folder in self.base_path.iterdir():
            if folder.is_dir():
                state_path = folder / ".agency" / "project_state.json"
                if state_path.exists():
                    state_dict = json.loads(state_path.read_text(encoding='utf-8'))
                    projects.append({
                        "project_id": state_dict["project_id"],
                        "project_name": state_dict["project_name"],
                        "project_type": state_dict["project_type"],
                        "status": state_dict["status"],
                        "created_at": state_dict["created_at"],
                        "path": str(folder),
                    })
        
        return projects
    
    def package_for_delivery(self, project_id: str, output_format: str = "zip") -> str:
        """
        Empacota o projeto para entrega ao cliente.
        
        Args:
            project_id: ID do projeto
            output_format: Formato de saída ("zip", "tar.gz")
            
        Returns:
            Caminho do arquivo gerado
        """
        project = self._get_project(project_id)
        if not project:
            raise ValueError(f"Projeto {project_id} não encontrado")
        
        # Atualiza status
        project.status = "delivered"
        self._save_project_state(project)
        
        # Cria o pacote
        output_name = f"{project.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if output_format == "zip":
            output_path = self.base_path / f"{output_name}.zip"
            shutil.make_archive(
                str(self.base_path / output_name),
                'zip',
                project.root_path
            )
        elif output_format == "tar.gz":
            output_path = self.base_path / f"{output_name}.tar.gz"
            shutil.make_archive(
                str(self.base_path / output_name),
                'gztar',
                project.root_path
            )
        else:
            raise ValueError(f"Formato não suportado: {output_format}")
        
        return str(output_path)


# Singleton instance
_generator_instance: Optional[ProjectGenerator] = None


def get_project_generator(base_path: Optional[str] = None) -> ProjectGenerator:
    """Factory function para obter o gerador de projetos (Singleton)."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = ProjectGenerator(base_path)
    return _generator_instance


if __name__ == "__main__":
    # Teste do gerador
    generator = get_project_generator()
    
    project = generator.create_project(
        project_id="proj_test_001",
        project_name="Sistema de Vendas",
        project_type=ProjectType.FULLSTACK,
        client_request="Preciso de um sistema de vendas com dashboard"
    )
    
    print(f"Projeto criado em: {project.root_path}")
    print(f"Arquivos: {len(project.files)}")
    
    # Lista projetos
    print("\nProjetos existentes:")
    for p in generator.list_projects():
        print(f"  - {p['project_name']} ({p['status']})")
