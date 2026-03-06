"""
Conversation Manager

Gerencia a conversa inicial com o cliente antes de iniciar o projeto.
O Product Owner conversa para entender os requisitos antes de iniciar
o desenvolvimento.

Inclui persistência de histórico para permitir voltar a conversas anteriores.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import os
import sqlite3
from pathlib import Path

from config.llm_config import get_llm
from core.quota_tracker import get_quota_tracker


class ConversationPhase(Enum):
    """Fases da conversa com o cliente."""
    GREETING = "greeting"           # Saudação inicial
    DISCOVERY = "discovery"         # Descoberta do projeto
    CLARIFICATION = "clarification" # Esclarecimento de dúvidas
    CONFIRMATION = "confirmation"   # Confirmação antes de iniciar
    READY = "ready"                 # Pronto para iniciar desenvolvimento
    IN_DEVELOPMENT = "in_development"  # Projeto em desenvolvimento


@dataclass
class ConversationMessage:
    """Uma mensagem na conversa."""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConversationState:
    """Estado da conversa com o cliente."""
    session_id: str
    project_id: Optional[str] = None  # Vincula conversa ao projeto
    project_name: Optional[str] = None
    phase: ConversationPhase = ConversationPhase.GREETING
    messages: List[ConversationMessage] = field(default_factory=list)
    extracted_info: Dict[str, Any] = field(default_factory=dict)
    questions_asked: int = 0
    ready_to_start: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_message(self, role: str, content: str):
        self.messages.append(ConversationMessage(role=role, content=content))
        self.updated_at = datetime.now().isoformat()

    def get_conversation_history(self) -> str:
        """Retorna o histórico formatado para o LLM."""
        history = []
        for msg in self.messages:
            prefix = "Cliente" if msg.role == "user" else "PO"
            history.append(f"{prefix}: {msg.content}")
        return "\n".join(history)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "phase": self.phase.value,
            "messages": [m.to_dict() for m in self.messages],
            "extracted_info": self.extracted_info,
            "questions_asked": self.questions_asked,
            "ready_to_start": self.ready_to_start,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationState':
        messages = [ConversationMessage(**m) for m in data.get("messages", [])]
        return cls(
            session_id=data["session_id"],
            project_id=data.get("project_id"),
            project_name=data.get("project_name"),
            phase=ConversationPhase(data.get("phase", "greeting")),
            messages=messages,
            extracted_info=data.get("extracted_info", {}),
            questions_asked=data.get("questions_asked", 0),
            ready_to_start=data.get("ready_to_start", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )


class ConversationStorage:
    """Persistência de conversas em SQLite."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "conversations.db"
            )
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Inicializa o banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    project_name TEXT,
                    phase TEXT,
                    data TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_project_id ON conversations(project_id)
            """)
            conn.commit()

    def save(self, conversation: ConversationState):
        """Salva uma conversa."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversations
                (session_id, project_id, project_name, phase, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation.session_id,
                conversation.project_id,
                conversation.project_name,
                conversation.phase.value,
                json.dumps(conversation.to_dict(), ensure_ascii=False),
                conversation.created_at,
                conversation.updated_at
            ))
            conn.commit()

    def load(self, session_id: str) -> Optional[ConversationState]:
        """Carrega uma conversa pelo session_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM conversations WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                return ConversationState.from_dict(json.loads(row[0]))
        return None

    def load_by_project(self, project_id: str) -> Optional[ConversationState]:
        """Carrega a conversa de um projeto."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM conversations WHERE project_id = ? ORDER BY updated_at DESC LIMIT 1",
                (project_id,)
            )
            row = cursor.fetchone()
            if row:
                return ConversationState.from_dict(json.loads(row[0]))
        return None

    def list_all(self, limit: int = 50) -> List[dict]:
        """Lista todas as conversas (resumo)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT session_id, project_id, project_name, phase, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [
                {
                    "session_id": r[0],
                    "project_id": r[1],
                    "project_name": r[2] or "Conversa sem nome",
                    "phase": r[3],
                    "created_at": r[4],
                    "updated_at": r[5]
                }
                for r in rows
            ]

    def delete(self, session_id: str):
        """Deleta uma conversa."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()


class ConversationManager:
    """
    Gerencia a conversa inicial com o cliente.

    O PO (Product Owner) conversa de forma rápida e amigável para
    entender o que o cliente precisa antes de iniciar o projeto.
    """

    def __init__(self):
        self.conversations: Dict[str, ConversationState] = {}
        self.storage = ConversationStorage()
        self.llm = get_llm("master", temperature_override=0.7)

        # Prompt do PO conversacional
        self.system_prompt = """Você é o Product Owner da Autonomous Data Agency, uma agência de desenvolvimento de software com IA.

PERSONALIDADE:
- Amigável e profissional
- Objetivo e direto ao ponto
- Entusiasta e positivo
- Fala em português brasileiro

SEU OBJETIVO:
Entender rapidamente o que o cliente precisa construir para que a equipe possa começar o desenvolvimento.

INFORMAÇÕES QUE VOCÊ PRECISA COLETAR:
1. **Tipo de Projeto**: O que exatamente o cliente quer construir? (app, site, sistema, API, dashboard, etc.)
2. **Objetivo Principal**: Qual problema o projeto vai resolver? Quem vai usar?
3. **Funcionalidades Essenciais**: Quais são as 3-5 funcionalidades mais importantes?
4. **Integrações**: Precisa se conectar com outros sistemas? (pagamentos, redes sociais, APIs externas)
5. **Design/Referências**: Tem alguma referência visual ou projeto similar?
6. **Prazo/Urgência**: Há algum prazo específico?

REGRAS DE CONVERSA:
1. Faça UMA ou DUAS perguntas por vez (máximo)
2. Seja breve nas respostas (2-3 frases no máximo)
3. Não repita perguntas já respondidas
4. Quando tiver informações suficientes (pelo menos tipo, objetivo e funcionalidades), pergunte se pode iniciar
5. Use emojis com moderação para ser amigável
6. Confirme o entendimento antes de iniciar

FORMATO DE RESPOSTA:
Responda APENAS com sua mensagem para o cliente. Não inclua explicações ou metadados.

QUANDO INICIAR O PROJETO:
Quando você tiver coletado informações suficientes, termine sua mensagem com:
[READY_TO_START]

Isso indica que podemos iniciar o desenvolvimento. Só use isso quando tiver:
- Tipo de projeto claro
- Objetivo principal definido
- Pelo menos 2-3 funcionalidades principais
- Confirmação do cliente que pode começar"""

    def get_or_create_conversation(self, session_id: str) -> ConversationState:
        """Obtém ou cria uma conversa para a sessão."""
        # Primeiro tenta do cache em memória
        if session_id in self.conversations:
            return self.conversations[session_id]

        # Tenta carregar do banco
        conversation = self.storage.load(session_id)
        if conversation:
            self.conversations[session_id] = conversation
            return conversation

        # Cria nova conversa
        conversation = ConversationState(session_id=session_id)
        self.conversations[session_id] = conversation
        return conversation

    def get_greeting(self) -> str:
        """Retorna a saudação inicial do PO."""
        return """👋 Olá! Sou o Product Owner da Autonomous Data Agency.

Estou aqui para entender o que você precisa construir. Me conta: **o que você gostaria de criar hoje?**

Pode ser um site, aplicativo, dashboard, sistema, API... qualquer coisa! 🚀"""

    async def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário e retorna a resposta do PO.

        Returns:
            Dict com:
            - response: str - Resposta do PO
            - ready_to_start: bool - Se está pronto para iniciar desenvolvimento
            - extracted_info: dict - Informações extraídas da conversa
        """
        conversation = self.get_or_create_conversation(session_id)

        # Adiciona mensagem do usuário
        conversation.add_message("user", user_message)

        # Monta o contexto para o LLM
        context = f"""HISTÓRICO DA CONVERSA:
{conversation.get_conversation_history()}

INFORMAÇÕES JÁ COLETADAS:
{json.dumps(conversation.extracted_info, indent=2, ensure_ascii=False) if conversation.extracted_info else "Nenhuma ainda"}

NÚMERO DE PERGUNTAS JÁ FEITAS: {conversation.questions_asked}

Responda à última mensagem do cliente de forma natural e objetiva."""

        # Chama o LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context}
        ]

        try:
            response = await self._call_llm(messages)

            # Verifica se está pronto para iniciar
            ready_to_start = "[READY_TO_START]" in response

            # Remove o marcador da resposta
            clean_response = response.replace("[READY_TO_START]", "").strip()

            # Adiciona resposta ao histórico
            conversation.add_message("assistant", clean_response)
            conversation.questions_asked += 1

            if ready_to_start:
                conversation.phase = ConversationPhase.READY
                conversation.ready_to_start = True
                # Extrai informações da conversa
                await self._extract_project_info(conversation)

            # Salva no banco
            self.storage.save(conversation)

            return {
                "response": clean_response,
                "ready_to_start": ready_to_start,
                "extracted_info": conversation.extracted_info,
                "phase": conversation.phase.value,
                "session_id": session_id
            }

        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
            return {
                "response": "Desculpe, tive um problema técnico. Pode repetir o que você disse?",
                "ready_to_start": False,
                "extracted_info": {},
                "phase": conversation.phase.value,
                "session_id": session_id
            }

    async def _call_llm(self, messages: List[Dict]) -> str:
        """Chama o LLM de forma assíncrona."""
        from langchain_core.messages import SystemMessage, HumanMessage
        import asyncio
        import re

        lc_messages = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            else:
                lc_messages.append(HumanMessage(content=msg["content"]))

        # Registra a requisição no quota tracker
        quota_tracker = get_quota_tracker()
        quota_tracker.record_request()

        try:
            # Usa invoke síncrono em um thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: self.llm.invoke(lc_messages)
            )
            return result.content
        except Exception as e:
            error_str = str(e)
            # Detecta rate limit (429)
            if "429" in error_str or "rate" in error_str.lower():
                # Tenta extrair retry_after do erro
                retry_match = re.search(r'retry in (\d+)', error_str.lower())
                retry_after = int(retry_match.group(1)) if retry_match else 60
                quota_tracker.record_rate_limit(error_str, retry_after)
            raise

    async def _extract_project_info(self, conversation: ConversationState):
        """Extrai informações estruturadas da conversa."""

        extraction_prompt = f"""Analise a conversa abaixo e extraia as informações do projeto em formato JSON.

CONVERSA:
{conversation.get_conversation_history()}

Extraia e retorne APENAS um JSON válido com a estrutura:
{{
    "project_type": "tipo do projeto (site, app, sistema, etc.)",
    "project_name": "nome sugerido para o projeto",
    "objective": "objetivo principal do projeto",
    "target_users": "quem vai usar o sistema",
    "main_features": ["lista", "de", "funcionalidades", "principais"],
    "integrations": ["integrações", "necessárias"],
    "references": "referências visuais ou projetos similares mencionados",
    "urgency": "urgência ou prazo mencionado",
    "additional_notes": "outras informações relevantes"
}}

Retorne APENAS o JSON, sem explicações."""

        try:
            messages = [{"role": "user", "content": extraction_prompt}]
            result = await self._call_llm(messages)

            # Tenta parsear o JSON
            # Remove possíveis marcadores de código
            json_str = result.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
            json_str = json_str.strip()

            conversation.extracted_info = json.loads(json_str)

            # Atualiza o nome do projeto
            if conversation.extracted_info.get("project_name"):
                conversation.project_name = conversation.extracted_info["project_name"]

        except Exception as e:
            print(f"Erro ao extrair informações: {e}")
            # Fallback básico
            conversation.extracted_info = {
                "project_type": "software",
                "objective": "A ser definido",
                "main_features": [],
                "raw_conversation": conversation.get_conversation_history()
            }

    def link_to_project(self, session_id: str, project_id: str, project_name: str = None):
        """Vincula uma conversa a um projeto."""
        conversation = self.get_or_create_conversation(session_id)
        conversation.project_id = project_id
        if project_name:
            conversation.project_name = project_name
        conversation.phase = ConversationPhase.IN_DEVELOPMENT
        self.storage.save(conversation)

    def get_project_summary(self, session_id: str) -> str:
        """Retorna um resumo do projeto baseado na conversa."""
        conversation = self.conversations.get(session_id)
        if not conversation:
            conversation = self.storage.load(session_id)

        if not conversation:
            return ""

        info = conversation.extracted_info
        summary_parts = []

        if info.get("project_type"):
            summary_parts.append(f"Tipo: {info['project_type']}")
        if info.get("objective"):
            summary_parts.append(f"Objetivo: {info['objective']}")
        if info.get("main_features"):
            features = ", ".join(info["main_features"][:5])
            summary_parts.append(f"Funcionalidades: {features}")
        if info.get("target_users"):
            summary_parts.append(f"Usuários: {info['target_users']}")

        return "\n".join(summary_parts)

    def list_conversations(self, limit: int = 50) -> List[dict]:
        """Lista todas as conversas."""
        return self.storage.list_all(limit)

    def load_conversation(self, session_id: str) -> Optional[ConversationState]:
        """Carrega uma conversa específica."""
        return self.get_or_create_conversation(session_id)

    def get_conversation_messages(self, session_id: str) -> List[dict]:
        """Retorna as mensagens de uma conversa para exibição no frontend."""
        conversation = self.get_or_create_conversation(session_id)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in conversation.messages
        ]

    def clear_conversation(self, session_id: str):
        """Limpa a conversa de uma sessão (remove do cache, mantém no banco)."""
        if session_id in self.conversations:
            del self.conversations[session_id]


# Singleton
_conversation_manager: Optional[ConversationManager] = None

def get_conversation_manager() -> ConversationManager:
    """Retorna a instância singleton do ConversationManager."""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
