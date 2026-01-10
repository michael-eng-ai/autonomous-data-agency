from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import traceback
import os

from core.agency_orchestrator import get_agency_orchestrator
from core.project_manager import get_project_manager, ProjectStatus

router = APIRouter()
orchestrator = get_agency_orchestrator()
project_manager = get_project_manager()

class ProjectRequest(BaseModel):
    name: str
    description: str
    project_type: Optional[str] = "fullstack"

class ChatMessage(BaseModel):
    message: str
    project_id: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str
    details: Optional[str] = ""

class GitHubLink(BaseModel):
    github_url: str


def run_project_workflow(project_name: str, description: str):
    """Executa o workflow completo do projeto em background."""
    try:
        # 1. Inicia o projeto
        orchestrator.start_project(project_name, description)
        
        # 2. Executa o Product Owner para análise de requisitos
        orchestrator.emit_event_threadsafe("team_dialog", {
            "team": "product_owner",
            "message": f"Analisando solicitação: {description[:100]}...",
            "type": "thinking"
        })
        
        po_output = orchestrator.execute_team("product_owner", description)
        
        orchestrator.emit_event_threadsafe("team_dialog", {
            "team": "product_owner",
            "message": po_output.final_output[:500],
            "type": "response"
        })
        
        # 3. Project Manager cria o plano
        orchestrator.emit_event_threadsafe("team_dialog", {
            "team": "project_manager", 
            "message": "Criando plano de projeto baseado nos requisitos...",
            "type": "thinking"
        })
        
        pm_context = f"""
Solicitação original: {description}

Análise do Product Owner:
{po_output.final_output}
"""
        pm_output = orchestrator.execute_team("project_manager", pm_context)
        
        orchestrator.emit_event_threadsafe("team_dialog", {
            "team": "project_manager",
            "message": pm_output.final_output[:500],
            "type": "response"
        })
        
        # 4. Emite conclusão
        orchestrator.emit_event_threadsafe("project_phase_changed", {
            "phase": "planning_complete",
            "summary": "Requisitos analisados e plano criado. Aguardando aprovação para prosseguir."
        })
        
    except Exception as e:
        print(f"Erro no workflow: {e}")
        traceback.print_exc()
        orchestrator.emit_event_threadsafe("project_error", {
            "error": str(e),
            "phase": "workflow_execution"
        })

@router.post("/start-project")
async def start_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """Inicia um novo projeto em background."""
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    
    # Executa em background para não bloquear a API
    background_tasks.add_task(
        orchestrator.start_project, 
        request.name, 
        request.description
    )
    
    return {"project_id": project_id, "status": "started", "message": "Project execution started in background"}

@router.post("/chat")
async def chat(message: ChatMessage, background_tasks: BackgroundTasks):
    """Envia uma mensagem para o chat do cliente."""
    
    # Se não há projeto ativo, a primeira mensagem inicia o projeto
    if not orchestrator.current_project:
        # Define um nome genérico ou extrai da mensagem (simplificado)
        project_name = f"Project from Chat {uuid.uuid4().hex[:4]}"
        
        print(f"Starting project from chat: {message.message[:50]}...")
        
        # Executa o workflow completo em background
        background_tasks.add_task(
            run_project_workflow, 
            project_name, 
            message.message
        )
        return {
            "response": "🚀 Projeto iniciado! Estou analisando sua solicitação. Acompanhe o progresso no painel central e à direita.", 
            "status": "started"
        }
    
    # Se já existe projeto, trata como resposta a uma pergunta
    orchestrator.emit_event_threadsafe("client_message", {
        "message": message.message
    })
    
    return {"response": "✅ Recebido. O sistema está processando sua mensagem.", "status": "ok"}

@router.get("/projects")
async def list_projects():
    """Lista projetos ativos (mock)."""
    if orchestrator.current_project:
        return [orchestrator.current_project]
    return []

@router.get("/project/status")
async def get_project_status():
    """Retorna o status atual do projeto."""
    if not orchestrator.current_project:
        return {"status": "no_project", "message": "Nenhum projeto ativo"}
    
    p = orchestrator.current_project
    project_path = orchestrator.get_project_path()
    
    return {
        "status": "active",
        "project_id": p.project_id,
        "name": p.project_name,
        "phase": p.current_phase.value,
        "project_path": project_path,
        "teams_executed": list(p.team_outputs.keys()),
        "created_at": p.created_at,
        "updated_at": p.updated_at
    }

@router.get("/project/summary")
async def get_project_summary():
    """Retorna um resumo completo do projeto."""
    return {"summary": orchestrator.get_project_summary()}

@router.post("/project/finalize")
async def finalize_project(output_format: str = "zip"):
    """
    Finaliza o projeto e gera o pacote para download.
    
    Args:
        output_format: "zip" ou "tar.gz"
    """
    if not orchestrator.current_project:
        raise HTTPException(status_code=404, detail="Nenhum projeto ativo")
    
    if output_format not in ["zip", "tar.gz"]:
        raise HTTPException(status_code=400, detail="Formato deve ser 'zip' ou 'tar.gz'")
    
    try:
        package_path = orchestrator.finalize_project(output_format)
        return {
            "status": "success",
            "package_path": package_path,
            "download_url": f"/api/project/download?path={package_path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/project/download")
async def download_project(path: str):
    """
    Faz o download do pacote do projeto.
    
    Args:
        path: Caminho do arquivo gerado por /project/finalize
    """
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    filename = os.path.basename(path)
    media_type = "application/zip" if path.endswith(".zip") else "application/gzip"
    
    return FileResponse(
        path=path,
        filename=filename,
        media_type=media_type
    )

@router.get("/project/files")
async def list_project_files():
    """Lista todos os arquivos gerados no projeto."""
    project_path = orchestrator.get_project_path()
    
    if not project_path or not os.path.exists(project_path):
        return {"files": [], "message": "Nenhum projeto ativo ou diretório não existe"}
    
    files = []
    for root, dirs, filenames in os.walk(project_path):
        # Ignorar pastas ocultas e __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for filename in filenames:
            if not filename.startswith('.'):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, project_path)
                files.append({
                    "path": rel_path,
                    "size": os.path.getsize(full_path),
                    "modified": os.path.getmtime(full_path)
                })
    
    return {
        "project_path": project_path,
        "files": sorted(files, key=lambda x: x["path"])
    }

@router.get("/project/file/{file_path:path}")
async def get_project_file(file_path: str):
    """
    Retorna o conteúdo de um arquivo específico do projeto.
    
    Args:
        file_path: Caminho relativo do arquivo dentro do projeto
    """
    project_path = orchestrator.get_project_path()
    
    if not project_path:
        raise HTTPException(status_code=404, detail="Nenhum projeto ativo")
    
    full_path = os.path.join(project_path, file_path)
    
    # Segurança: garantir que o path está dentro do projeto
    if not os.path.realpath(full_path).startswith(os.path.realpath(project_path)):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"path": file_path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler arquivo: {str(e)}") from e

@router.get("/teams")
async def list_teams():
    """Lista todos os times disponíveis."""
    return {
        "teams": list(orchestrator.teams.keys()),
        "total": len(orchestrator.teams)
    }


# ============================================================
# ENDPOINTS DE GERENCIAMENTO DE PROJETOS
# ============================================================

@router.post("/projects/create")
async def create_new_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """
    Cria um novo projeto e inicia o workflow de análise.
    
    Args:
        request: Nome, descrição e tipo do projeto
    """
    # Cria o projeto no gerenciador
    project_info = project_manager.create_project(
        name=request.name,
        description=request.description,
        project_type=request.project_type or "fullstack"
    )
    
    # Inicia o workflow em background
    background_tasks.add_task(
        run_project_workflow,
        project_info.name,
        project_info.description
    )
    
    return {
        "status": "created",
        "project_id": project_info.project_id,
        "name": project_info.name,
        "project_type": project_info.project_type,
        "path": project_info.path,
        "message": f"Projeto '{project_info.name}' criado com sucesso! Análise iniciada."
    }


@router.get("/projects/list")
async def get_all_projects(status: Optional[str] = None):
    """
    Lista todos os projetos.
    
    Args:
        status: Filtrar por status (initiated, analyzing, planning, in_progress, review, completed, delivered, cancelled)
    """
    status_filter = None
    if status:
        try:
            status_filter = ProjectStatus(status)
        except ValueError:
            valid_statuses = [s.value for s in ProjectStatus]
            raise HTTPException(
                status_code=400, 
                detail=f"Status inválido. Use: {', '.join(valid_statuses)}"
            )
    
    projects = project_manager.list_projects(status_filter)
    summary = project_manager.get_projects_summary()
    
    return {
        "projects": projects,
        "summary": summary
    }


@router.get("/projects/summary")
async def get_projects_overview():
    """Retorna estatísticas gerais dos projetos."""
    return project_manager.get_projects_summary()


@router.get("/projects/{project_id}")
async def get_project_details(project_id: str):
    """
    Obtém detalhes completos de um projeto.
    
    Args:
        project_id: ID do projeto
    """
    try:
        details = project_manager.get_project_details(project_id)
        return details
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/projects/{project_id}/status")
async def update_project_status(project_id: str, update: StatusUpdate):
    """
    Atualiza o status de um projeto.
    
    Args:
        project_id: ID do projeto
        update: Novo status e detalhes
    """
    try:
        new_status = ProjectStatus(update.status)
    except ValueError:
        valid_statuses = [s.value for s in ProjectStatus]
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido. Use: {', '.join(valid_statuses)}"
        )
    
    try:
        project_manager.update_status(project_id, new_status, update.details or "")
        return {
            "status": "updated",
            "project_id": project_id,
            "new_status": new_status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/projects/{project_id}/prepare-github")
async def prepare_project_for_github(project_id: str):
    """
    Prepara um projeto para ser enviado ao GitHub.
    Inicializa git, cria .gitignore e faz commit inicial.
    
    Args:
        project_id: ID do projeto
    """
    try:
        path = project_manager.prepare_for_github(project_id)
        return {
            "status": "prepared",
            "project_id": project_id,
            "path": path,
            "message": "Projeto preparado para GitHub. Use 'git remote add origin <url>' e 'git push -u origin main' para enviar."
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/projects/{project_id}/github-link")
async def link_project_to_github(project_id: str, link: GitHubLink):
    """
    Vincula um projeto a um repositório GitHub.
    
    Args:
        project_id: ID do projeto
        link: URL do repositório GitHub
    """
    try:
        project_manager.set_github_url(project_id, link.github_url)
        return {
            "status": "linked",
            "project_id": project_id,
            "github_url": link.github_url
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/projects/{project_id}/activities")
async def get_project_activities(project_id: str):
    """
    Obtém o histórico de atividades de um projeto.
    
    Args:
        project_id: ID do projeto
    """
    try:
        details = project_manager.get_project_details(project_id)
        return {
            "project_id": project_id,
            "activities": details["activities"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/projects/{project_id}/package")
async def package_project(project_id: str, output_format: str = "zip"):
    """
    Empacota um projeto para download.
    
    Args:
        project_id: ID do projeto
        output_format: Formato do pacote (zip ou tar.gz)
    """
    from core.project_generator import get_project_generator
    
    if output_format not in ["zip", "tar.gz"]:
        raise HTTPException(status_code=400, detail="Formato deve ser 'zip' ou 'tar.gz'")
    
    try:
        generator = get_project_generator()
        package_path = generator.package_for_delivery(project_id, output_format)
        
        # Atualiza status para delivered
        project_manager.update_status(
            project_id, 
            ProjectStatus.DELIVERED, 
            f"Pacote gerado: {os.path.basename(package_path)}"
        )
        
        return {
            "status": "packaged",
            "project_id": project_id,
            "package_path": package_path,
            "download_url": f"/api/project/download?path={package_path}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
