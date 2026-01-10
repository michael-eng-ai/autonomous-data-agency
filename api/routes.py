from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import traceback

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
