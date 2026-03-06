from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import traceback
import os

from core.agency_orchestrator import get_agency_orchestrator
from core.project_manager import get_project_manager, ProjectStatus
from core.conversation_manager import get_conversation_manager
from core.quota_tracker import get_quota_tracker

router = APIRouter()
orchestrator = get_agency_orchestrator()
project_manager = get_project_manager()
conversation_manager = get_conversation_manager()

class ProjectRequest(BaseModel):
    name: str
    description: str
    project_type: Optional[str] = "fullstack"

class ChatMessage(BaseModel):
    message: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None  # Para rastrear a conversa

class StatusUpdate(BaseModel):
    status: str
    details: Optional[str] = ""

class GitHubLink(BaseModel):
    github_url: str


def run_project_workflow(project_name: str, description: str):
    """Executa o workflow completo do projeto em background."""
    # IMPORTANT: Get fresh singleton reference to ensure we have the configured instance
    orch = get_agency_orchestrator()

    try:
        # 1. Inicia o projeto
        orch.start_project(project_name, description)

        # 2. Executa o Product Owner para análise de requisitos
        orch.emit_event_threadsafe("team_dialog", {
            "team": "product_owner",
            "message": f"Analisando solicitação: {description[:100]}...",
            "type": "thinking"
        })

        po_output = orch.execute_team("product_owner", description)

        orch.emit_event_threadsafe("team_dialog", {
            "team": "product_owner",
            "message": po_output.final_output[:500],
            "type": "response"
        })

        # 3. Project Manager cria o plano
        orch.emit_event_threadsafe("team_dialog", {
            "team": "project_manager",
            "message": "Criando plano de projeto baseado nos requisitos...",
            "type": "thinking"
        })

        pm_context = f"""
Solicitação original: {description}

Análise do Product Owner:
{po_output.final_output}
"""
        pm_output = orch.execute_team("project_manager", pm_context)

        orch.emit_event_threadsafe("team_dialog", {
            "team": "project_manager",
            "message": pm_output.final_output[:500],
            "type": "response"
        })

        # 4. Emite conclusão
        orch.emit_event_threadsafe("project_phase_changed", {
            "phase": "planning_complete",
            "summary": "Requisitos analisados e plano criado. Aguardando aprovação para prosseguir."
        })

    except Exception as e:
        print(f"Erro no workflow: {e}")
        traceback.print_exc()
        orch.emit_event_threadsafe("project_error", {
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
    """
    Endpoint de chat conversacional.

    FLUXO:
    1. Se não há projeto ativo, entra em modo de conversa com o PO
    2. O PO faz perguntas para entender o projeto
    3. Quando tiver informações suficientes, inicia o desenvolvimento
    4. Se já há projeto, a mensagem é processada como feedback
    """
    # Gera ou usa session_id existente
    session_id = message.session_id or str(uuid.uuid4())

    # Se já existe um projeto em desenvolvimento, processa como feedback
    if orchestrator.current_project and orchestrator.current_project.current_phase.value != "requirements":
        orchestrator.emit_event_threadsafe("client_message", {
            "message": message.message
        })
        return {
            "response": "✅ Recebido! Sua mensagem foi registrada.",
            "status": "ok",
            "session_id": session_id
        }

    # Modo conversacional com o PO
    conv_manager = get_conversation_manager()

    # Processa a mensagem com o PO
    result = await conv_manager.process_message(session_id, message.message)

    # Emite evento de conversa para o WebSocket
    orch = get_agency_orchestrator()
    orch.emit_event_threadsafe("po_conversation", {
        "session_id": session_id,
        "user_message": message.message,
        "po_response": result["response"],
        "phase": result["phase"],
        "ready_to_start": result["ready_to_start"]
    })

    # Se está pronto para iniciar o desenvolvimento
    if result["ready_to_start"]:
        # Extrai informações do projeto
        project_info = result["extracted_info"]
        project_name = project_info.get("project_name", f"Project {uuid.uuid4().hex[:4]}")

        # Cria descrição detalhada baseada na conversa
        description = _build_project_description(project_info, conv_manager.get_project_summary(session_id))

        print(f"[Chat] Iniciando desenvolvimento: {project_name}")
        print(f"[Chat] Descrição: {description[:200]}...")

        # Gera project_id para vincular a conversa
        project_id = f"proj_{uuid.uuid4().hex[:8]}"

        # Vincula a conversa ao projeto (mantém no banco)
        conv_manager.link_to_project(session_id, project_id, project_name)

        # Inicia o workflow em background
        background_tasks.add_task(
            run_project_workflow,
            project_name,
            description
        )

        return {
            "response": result["response"] + "\n\n🚀 **Iniciando o desenvolvimento!** Acompanhe o progresso no painel à direita.",
            "status": "started",
            "session_id": session_id,
            "project_id": project_id,
            "project_info": project_info
        }

    # Continua a conversa
    return {
        "response": result["response"],
        "status": "conversation",
        "session_id": session_id,
        "phase": result["phase"]
    }


@router.get("/chat/greeting")
async def get_chat_greeting():
    """Retorna a saudação inicial do PO."""
    conv_manager = get_conversation_manager()
    return {
        "greeting": conv_manager.get_greeting(),
        "session_id": str(uuid.uuid4())
    }


@router.post("/chat/start-development")
async def force_start_development(message: ChatMessage, background_tasks: BackgroundTasks):
    """
    Força o início do desenvolvimento mesmo sem todas as informações.
    Útil quando o usuário quer pular a conversa.
    """
    session_id = message.session_id or str(uuid.uuid4())
    conv_manager = get_conversation_manager()

    # Pega informações que já foram coletadas (se houver)
    conversation = conv_manager.conversations.get(session_id)
    project_info = conversation.extracted_info if conversation else {}

    project_name = project_info.get("project_name", f"Project {uuid.uuid4().hex[:4]}")
    description = message.message or project_info.get("objective", "Projeto iniciado via chat")

    # Inicia o workflow
    background_tasks.add_task(
        run_project_workflow,
        project_name,
        description
    )

    # Limpa a conversa
    conv_manager.clear_conversation(session_id)

    return {
        "response": "🚀 Iniciando desenvolvimento com as informações disponíveis!",
        "status": "started",
        "session_id": session_id
    }


def _build_project_description(project_info: dict, conversation_summary: str) -> str:
    """Constrói uma descrição detalhada do projeto baseada nas informações coletadas."""
    parts = []

    if project_info.get("project_type"):
        parts.append(f"Tipo de Projeto: {project_info['project_type']}")

    if project_info.get("objective"):
        parts.append(f"Objetivo: {project_info['objective']}")

    if project_info.get("target_users"):
        parts.append(f"Usuários Alvo: {project_info['target_users']}")

    if project_info.get("main_features"):
        features = project_info["main_features"]
        if isinstance(features, list):
            features_str = ", ".join(features)
        else:
            features_str = str(features)
        parts.append(f"Funcionalidades Principais: {features_str}")

    if project_info.get("integrations"):
        integrations = project_info["integrations"]
        if isinstance(integrations, list):
            integrations_str = ", ".join(integrations)
        else:
            integrations_str = str(integrations)
        parts.append(f"Integrações: {integrations_str}")

    if project_info.get("references"):
        parts.append(f"Referências: {project_info['references']}")

    if project_info.get("additional_notes"):
        parts.append(f"Observações: {project_info['additional_notes']}")

    if conversation_summary:
        parts.append(f"\nResumo da Conversa:\n{conversation_summary}")

    return "\n".join(parts) if parts else "Projeto iniciado via chat"

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


# ============================================================
# ENDPOINTS DE HISTÓRICO DE CONVERSAS
# ============================================================

@router.get("/conversations")
async def list_conversations(limit: int = 50):
    """
    Lista todas as conversas salvas.

    Args:
        limit: Número máximo de conversas a retornar (padrão: 50)
    """
    conv_manager = get_conversation_manager()
    conversations = conv_manager.list_conversations(limit)
    return {
        "conversations": conversations,
        "total": len(conversations)
    }


@router.get("/conversations/{session_id}")
async def get_conversation(session_id: str):
    """
    Obtém detalhes completos de uma conversa.

    Args:
        session_id: ID da sessão/conversa
    """
    conv_manager = get_conversation_manager()
    conversation = conv_manager.load_conversation(session_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    return {
        "session_id": conversation.session_id,
        "project_id": conversation.project_id,
        "project_name": conversation.project_name,
        "phase": conversation.phase.value,
        "messages": conv_manager.get_conversation_messages(session_id),
        "extracted_info": conversation.extracted_info,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }


@router.delete("/conversations/{session_id}")
async def delete_conversation(session_id: str):
    """
    Deleta uma conversa.

    Args:
        session_id: ID da sessão/conversa
    """
    conv_manager = get_conversation_manager()

    # Verifica se existe
    conversation = conv_manager.storage.load(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    conv_manager.storage.delete(session_id)
    conv_manager.clear_conversation(session_id)

    return {
        "status": "deleted",
        "session_id": session_id
    }


@router.post("/conversations/{session_id}/continue")
async def continue_conversation(session_id: str):
    """
    Continua uma conversa existente.
    Carrega a conversa e prepara para receber novas mensagens.

    Args:
        session_id: ID da sessão/conversa
    """
    conv_manager = get_conversation_manager()
    conversation = conv_manager.load_conversation(session_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    # Se já está em desenvolvimento, retorna info do projeto
    if conversation.phase.value == "in_development" and conversation.project_id:
        return {
            "session_id": session_id,
            "status": "in_development",
            "project_id": conversation.project_id,
            "project_name": conversation.project_name,
            "message": "Este projeto já está em desenvolvimento. Você pode enviar feedback."
        }

    # Retorna a conversa pronta para continuar
    return {
        "session_id": session_id,
        "status": "ready",
        "phase": conversation.phase.value,
        "messages": conv_manager.get_conversation_messages(session_id),
        "extracted_info": conversation.extracted_info,
        "message": "Conversa carregada. Você pode continuar de onde parou."
    }


@router.get("/conversations/project/{project_id}")
async def get_conversation_by_project(project_id: str):
    """
    Obtém a conversa associada a um projeto.

    Args:
        project_id: ID do projeto
    """
    conv_manager = get_conversation_manager()
    conversation = conv_manager.storage.load_by_project(project_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Nenhuma conversa encontrada para este projeto")

    return {
        "session_id": conversation.session_id,
        "project_id": conversation.project_id,
        "project_name": conversation.project_name,
        "phase": conversation.phase.value,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in conversation.messages
        ],
        "extracted_info": conversation.extracted_info,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }


# ============================================================
# ENDPOINTS DE STATUS DA API / QUOTA
# ============================================================

@router.get("/api/quota")
async def get_api_quota():
    """
    Retorna o status atual de uso da API (rate limits).

    Mostra:
    - Requisições por minuto (RPM) usadas/disponíveis
    - Requisições por dia (RPD) usadas/disponíveis
    - Status de rate limit (se houver)
    - Tempo restante para retry (se em rate limit)
    """
    quota_tracker = get_quota_tracker()
    return quota_tracker.get_status_dict()
