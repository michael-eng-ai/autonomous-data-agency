from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from core.agency_orchestrator import get_agency_orchestrator

router = APIRouter()
orchestrator = get_agency_orchestrator()

class ProjectRequest(BaseModel):
    name: str
    description: str

class ChatMessage(BaseModel):
    message: str
    project_id: Optional[str] = None

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
        
        background_tasks.add_task(
            orchestrator.start_project, 
            project_name, 
            message.message
        )
        return {"response": "Projeto iniciado com sua solicitação! Acompanhe o feed.", "status": "started"}
    
    # Se já existe projeto, trata como resposta a uma pergunta (se houver)
    # Por enquanto, apenas registramos
    # orchestrator.receive_client_response(...) # Requer lógica mais complexa de estado
    
    return {"response": "Recebido. O sistema está processando.", "status": "ok"}

@router.get("/projects")
async def list_projects():
    """Lista projetos ativos (mock)."""
    if orchestrator.current_project:
        return [orchestrator.current_project]
    return []
