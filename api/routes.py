from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import traceback
import os

from core.agency_orchestrator import get_agency_orchestrator

router = APIRouter()
orchestrator = get_agency_orchestrator()

class ProjectRequest(BaseModel):
    name: str
    description: str

class ChatMessage(BaseModel):
    message: str
    project_id: Optional[str] = None


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
