"""
Team Communication Module

Este módulo implementa o sistema de comunicação e colaboração
entre times de agentes da Autonomous Data Agency.

Funcionalidades:
1. Message Bus para comunicação assíncrona
2. Solicitação de ajuda entre times
3. Compartilhamento de contexto
4. Escalação de decisões
5. Histórico de comunicações
"""

import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from queue import Queue, PriorityQueue
import threading
from collections import defaultdict


class MessageType(Enum):
    """Tipos de mensagens entre times."""
    REQUEST = "request"           # Solicitação de ajuda
    RESPONSE = "response"         # Resposta a uma solicitação
    NOTIFICATION = "notification" # Notificação informativa
    ESCALATION = "escalation"     # Escalação de decisão
    HANDOFF = "handoff"           # Transferência de tarefa
    FEEDBACK = "feedback"         # Feedback sobre trabalho
    QUESTION = "question"         # Pergunta para outro time
    APPROVAL = "approval"         # Solicitação de aprovação
    CONTEXT_SHARE = "context"     # Compartilhamento de contexto


class MessagePriority(Enum):
    """Prioridade das mensagens."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


class MessageStatus(Enum):
    """Status de uma mensagem."""
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TeamMessage:
    """Representa uma mensagem entre times."""
    id: str
    message_type: MessageType
    priority: MessagePriority
    from_team: str
    to_team: str
    subject: str
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    requires_response: bool = False
    parent_message_id: Optional[str] = None  # Para threads
    status: MessageStatus = MessageStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    delivered_at: Optional[str] = None
    completed_at: Optional[str] = None
    response: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            **asdict(self),
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "status": self.status.value
        }
    
    def __lt__(self, other):
        """Comparação para PriorityQueue."""
        return self.priority.value < other.priority.value


@dataclass
class CollaborationRequest:
    """Solicitação de colaboração entre times."""
    id: str
    requesting_team: str
    target_teams: List[str]
    topic: str
    description: str
    required_expertise: List[str]
    deadline: Optional[str] = None
    responses: Dict[str, str] = field(default_factory=dict)
    status: str = "open"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TeamContext:
    """Contexto compartilhado de um time."""
    team_name: str
    current_task: Optional[str] = None
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    status: str = "idle"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class MessageBus:
    """
    Message Bus para comunicação entre times.
    
    Implementa um sistema de pub/sub com filas prioritárias.
    """
    
    def __init__(self):
        """Inicializa o message bus."""
        self._queues: Dict[str, PriorityQueue] = defaultdict(PriorityQueue)
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._message_history: List[TeamMessage] = []
        self._lock = threading.Lock()
        self._message_counter = 0
    
    def _generate_id(self) -> str:
        """Gera um ID único para mensagem."""
        self._message_counter += 1
        return f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._message_counter:04d}"
    
    def send_message(self, message: TeamMessage) -> str:
        """
        Envia uma mensagem para um time.
        
        Args:
            message: Mensagem a enviar
        
        Returns:
            ID da mensagem
        """
        with self._lock:
            if not message.id:
                message.id = self._generate_id()
            
            # Adiciona à fila do time destinatário
            self._queues[message.to_team].put(message)
            
            # Registra no histórico
            self._message_history.append(message)
            
            # Notifica subscribers
            for callback in self._subscribers.get(message.to_team, []):
                try:
                    callback(message)
                except Exception as e:
                    print(f"[MessageBus] Erro ao notificar subscriber: {e}")
            
            message.status = MessageStatus.DELIVERED
            message.delivered_at = datetime.now().isoformat()
            
            return message.id
    
    def receive_messages(self, team_name: str, max_messages: int = 10) -> List[TeamMessage]:
        """
        Recebe mensagens pendentes para um time.
        
        Args:
            team_name: Nome do time
            max_messages: Máximo de mensagens a retornar
        
        Returns:
            Lista de mensagens
        """
        messages = []
        queue = self._queues[team_name]
        
        while not queue.empty() and len(messages) < max_messages:
            try:
                message = queue.get_nowait()
                message.status = MessageStatus.READ
                messages.append(message)
            except:
                break
        
        return messages
    
    def subscribe(self, team_name: str, callback: Callable[[TeamMessage], None]) -> None:
        """
        Inscreve um callback para receber mensagens de um time.
        
        Args:
            team_name: Nome do time
            callback: Função a chamar quando mensagem chegar
        """
        self._subscribers[team_name].append(callback)
    
    def get_message_history(
        self,
        team_name: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[TeamMessage]:
        """
        Obtém histórico de mensagens.
        
        Args:
            team_name: Filtrar por time (from ou to)
            message_type: Filtrar por tipo
            limit: Máximo de mensagens
        
        Returns:
            Lista de mensagens
        """
        messages = self._message_history
        
        if team_name:
            messages = [m for m in messages if m.from_team == team_name or m.to_team == team_name]
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        return messages[-limit:]
    
    def get_pending_count(self, team_name: str) -> int:
        """Retorna quantidade de mensagens pendentes para um time."""
        return self._queues[team_name].qsize()


class TeamCommunicationHub:
    """
    Hub central de comunicação entre times.
    
    Gerencia:
    - Roteamento de mensagens
    - Colaborações entre times
    - Compartilhamento de contexto
    - Escalações
    """
    
    def __init__(self):
        """Inicializa o hub de comunicação."""
        self.message_bus = MessageBus()
        self._team_contexts: Dict[str, TeamContext] = {}
        self._collaborations: Dict[str, CollaborationRequest] = {}
        self._escalation_handlers: Dict[str, Callable] = {}
        self._collab_counter = 0
        
        # Mapeamento de tópicos para times
        self._topic_routing: Dict[str, List[str]] = {
            "infraestrutura": ["devops", "architecture"],
            "dados": ["data_engineering", "data_analytics"],
            "qualidade": ["qa", "data_engineering"],
            "segurança": ["security", "devops"],
            "ml": ["data_science", "data_engineering"],
            "requisitos": ["product_owner", "project_manager"],
            "arquitetura": ["architecture", "data_engineering", "devops"],
            "deploy": ["devops", "qa"],
            "performance": ["qa", "devops", "data_engineering"],
        }
    
    def _generate_collab_id(self) -> str:
        """Gera ID para colaboração."""
        self._collab_counter += 1
        return f"collab_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._collab_counter:04d}"
    
    def register_team(self, team_name: str) -> None:
        """Registra um time no hub."""
        if team_name not in self._team_contexts:
            self._team_contexts[team_name] = TeamContext(team_name=team_name)
    
    def update_team_context(
        self,
        team_name: str,
        current_task: Optional[str] = None,
        decisions: Optional[List[Dict]] = None,
        blockers: Optional[List[str]] = None,
        artifacts: Optional[List[str]] = None,
        status: Optional[str] = None
    ) -> None:
        """Atualiza o contexto de um time."""
        if team_name not in self._team_contexts:
            self.register_team(team_name)
        
        ctx = self._team_contexts[team_name]
        
        if current_task is not None:
            ctx.current_task = current_task
        if decisions is not None:
            ctx.decisions_made.extend(decisions)
        if blockers is not None:
            ctx.blockers = blockers
        if artifacts is not None:
            ctx.artifacts.extend(artifacts)
        if status is not None:
            ctx.status = status
        
        ctx.last_updated = datetime.now().isoformat()
    
    def get_team_context(self, team_name: str) -> Optional[TeamContext]:
        """Obtém o contexto de um time."""
        return self._team_contexts.get(team_name)
    
    def request_help(
        self,
        from_team: str,
        topic: str,
        description: str,
        required_expertise: List[str],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """
        Solicita ajuda de outros times.
        
        Args:
            from_team: Time solicitante
            topic: Tópico da ajuda
            description: Descrição detalhada
            required_expertise: Expertise necessária
            priority: Prioridade da solicitação
        
        Returns:
            ID da colaboração
        """
        # Encontra times relevantes
        target_teams = self._find_teams_for_topic(topic, required_expertise)
        
        if not target_teams:
            # Se não encontrar times específicos, envia para arquitetura
            target_teams = ["architecture"]
        
        # Cria colaboração
        collab_id = self._generate_collab_id()
        collaboration = CollaborationRequest(
            id=collab_id,
            requesting_team=from_team,
            target_teams=target_teams,
            topic=topic,
            description=description,
            required_expertise=required_expertise
        )
        self._collaborations[collab_id] = collaboration
        
        # Envia mensagens para times relevantes
        for team in target_teams:
            message = TeamMessage(
                id="",
                message_type=MessageType.REQUEST,
                priority=priority,
                from_team=from_team,
                to_team=team,
                subject=f"Solicitação de ajuda: {topic}",
                content=description,
                context={
                    "collaboration_id": collab_id,
                    "required_expertise": required_expertise
                },
                requires_response=True
            )
            self.message_bus.send_message(message)
        
        return collab_id
    
    def respond_to_collaboration(
        self,
        collaboration_id: str,
        team_name: str,
        response: str
    ) -> bool:
        """
        Responde a uma solicitação de colaboração.
        
        Args:
            collaboration_id: ID da colaboração
            team_name: Time respondendo
            response: Resposta
        
        Returns:
            True se sucesso
        """
        if collaboration_id not in self._collaborations:
            return False
        
        collab = self._collaborations[collaboration_id]
        collab.responses[team_name] = response
        
        # Envia resposta ao time solicitante
        message = TeamMessage(
            id="",
            message_type=MessageType.RESPONSE,
            priority=MessagePriority.NORMAL,
            from_team=team_name,
            to_team=collab.requesting_team,
            subject=f"Resposta: {collab.topic}",
            content=response,
            context={"collaboration_id": collaboration_id}
        )
        self.message_bus.send_message(message)
        
        # Verifica se todos responderam
        if set(collab.responses.keys()) >= set(collab.target_teams):
            collab.status = "completed"
        
        return True
    
    def escalate_decision(
        self,
        from_team: str,
        decision_topic: str,
        options: List[Dict[str, Any]],
        context: str,
        to_team: str = "architecture"
    ) -> str:
        """
        Escala uma decisão para outro time.
        
        Args:
            from_team: Time escalando
            decision_topic: Tópico da decisão
            options: Opções disponíveis
            context: Contexto da decisão
            to_team: Time para escalar (default: architecture)
        
        Returns:
            ID da mensagem
        """
        message = TeamMessage(
            id="",
            message_type=MessageType.ESCALATION,
            priority=MessagePriority.HIGH,
            from_team=from_team,
            to_team=to_team,
            subject=f"Escalação: {decision_topic}",
            content=context,
            context={
                "decision_topic": decision_topic,
                "options": options
            },
            requires_response=True
        )
        
        return self.message_bus.send_message(message)
    
    def handoff_task(
        self,
        from_team: str,
        to_team: str,
        task_description: str,
        deliverables: List[str],
        context: Dict[str, Any]
    ) -> str:
        """
        Transfere uma tarefa para outro time.
        
        Args:
            from_team: Time transferindo
            to_team: Time recebendo
            task_description: Descrição da tarefa
            deliverables: Entregáveis esperados
            context: Contexto relevante
        
        Returns:
            ID da mensagem
        """
        # Obtém contexto do time de origem
        from_context = self.get_team_context(from_team)
        
        message = TeamMessage(
            id="",
            message_type=MessageType.HANDOFF,
            priority=MessagePriority.HIGH,
            from_team=from_team,
            to_team=to_team,
            subject=f"Handoff de tarefa: {task_description[:50]}...",
            content=task_description,
            context={
                "deliverables": deliverables,
                "previous_decisions": from_context.decisions_made if from_context else [],
                "artifacts": from_context.artifacts if from_context else [],
                **context
            },
            requires_response=True
        )
        
        return self.message_bus.send_message(message)
    
    def share_context(
        self,
        from_team: str,
        to_teams: List[str],
        context_type: str,
        content: Dict[str, Any]
    ) -> List[str]:
        """
        Compartilha contexto com outros times.
        
        Args:
            from_team: Time compartilhando
            to_teams: Times destinatários
            context_type: Tipo de contexto
            content: Conteúdo do contexto
        
        Returns:
            Lista de IDs das mensagens
        """
        message_ids = []
        
        for team in to_teams:
            message = TeamMessage(
                id="",
                message_type=MessageType.CONTEXT_SHARE,
                priority=MessagePriority.LOW,
                from_team=from_team,
                to_team=team,
                subject=f"Contexto compartilhado: {context_type}",
                content=json.dumps(content, indent=2),
                context={"context_type": context_type}
            )
            msg_id = self.message_bus.send_message(message)
            message_ids.append(msg_id)
        
        return message_ids
    
    def ask_question(
        self,
        from_team: str,
        to_team: str,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Faz uma pergunta para outro time.
        
        Args:
            from_team: Time perguntando
            to_team: Time respondendo
            question: Pergunta
            context: Contexto adicional
        
        Returns:
            ID da mensagem
        """
        message = TeamMessage(
            id="",
            message_type=MessageType.QUESTION,
            priority=MessagePriority.NORMAL,
            from_team=from_team,
            to_team=to_team,
            subject=f"Pergunta: {question[:50]}...",
            content=question,
            context=context or {},
            requires_response=True
        )
        
        return self.message_bus.send_message(message)
    
    def request_approval(
        self,
        from_team: str,
        to_team: str,
        item_to_approve: str,
        details: Dict[str, Any]
    ) -> str:
        """
        Solicita aprovação de outro time.
        
        Args:
            from_team: Time solicitando
            to_team: Time aprovador
            item_to_approve: Item para aprovar
            details: Detalhes do item
        
        Returns:
            ID da mensagem
        """
        message = TeamMessage(
            id="",
            message_type=MessageType.APPROVAL,
            priority=MessagePriority.HIGH,
            from_team=from_team,
            to_team=to_team,
            subject=f"Aprovação necessária: {item_to_approve}",
            content=json.dumps(details, indent=2),
            context={"item": item_to_approve},
            requires_response=True
        )
        
        return self.message_bus.send_message(message)
    
    def _find_teams_for_topic(
        self,
        topic: str,
        expertise: List[str]
    ) -> List[str]:
        """Encontra times relevantes para um tópico."""
        teams = set()
        topic_lower = topic.lower()
        
        # Busca por roteamento de tópicos
        for key, team_list in self._topic_routing.items():
            if key in topic_lower:
                teams.update(team_list)
        
        # Busca por expertise
        for exp in expertise:
            exp_lower = exp.lower()
            for key, team_list in self._topic_routing.items():
                if exp_lower in key or key in exp_lower:
                    teams.update(team_list)
        
        return list(teams)
    
    def get_collaboration_status(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status de uma colaboração."""
        if collaboration_id not in self._collaborations:
            return None
        
        collab = self._collaborations[collaboration_id]
        return {
            "id": collab.id,
            "topic": collab.topic,
            "requesting_team": collab.requesting_team,
            "target_teams": collab.target_teams,
            "responses_received": list(collab.responses.keys()),
            "status": collab.status,
            "created_at": collab.created_at
        }
    
    def get_all_team_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Obtém status de todos os times."""
        return {
            name: {
                "current_task": ctx.current_task,
                "status": ctx.status,
                "blockers_count": len(ctx.blockers),
                "decisions_count": len(ctx.decisions_made),
                "pending_messages": self.message_bus.get_pending_count(name),
                "last_updated": ctx.last_updated
            }
            for name, ctx in self._team_contexts.items()
        }
    
    def generate_communication_report(self) -> str:
        """Gera relatório de comunicações."""
        lines = [
            "=" * 60,
            "  RELATÓRIO DE COMUNICAÇÃO ENTRE TIMES",
            "=" * 60,
            "",
        ]
        
        # Status dos times
        lines.append("STATUS DOS TIMES:")
        lines.append("-" * 40)
        for name, status in self.get_all_team_statuses().items():
            lines.append(f"  {name}:")
            lines.append(f"    Status: {status['status']}")
            lines.append(f"    Tarefa atual: {status['current_task'] or 'Nenhuma'}")
            lines.append(f"    Mensagens pendentes: {status['pending_messages']}")
            lines.append("")
        
        # Colaborações ativas
        active_collabs = [c for c in self._collaborations.values() if c.status != "completed"]
        if active_collabs:
            lines.append("COLABORAÇÕES ATIVAS:")
            lines.append("-" * 40)
            for collab in active_collabs:
                lines.append(f"  {collab.id}: {collab.topic}")
                lines.append(f"    De: {collab.requesting_team}")
                lines.append(f"    Para: {', '.join(collab.target_teams)}")
                lines.append(f"    Respostas: {len(collab.responses)}/{len(collab.target_teams)}")
                lines.append("")
        
        # Estatísticas de mensagens
        history = self.message_bus.get_message_history(limit=1000)
        if history:
            lines.append("ESTATÍSTICAS DE MENSAGENS:")
            lines.append("-" * 40)
            
            by_type = defaultdict(int)
            for msg in history:
                by_type[msg.message_type.value] += 1
            
            for msg_type, count in sorted(by_type.items()):
                lines.append(f"  {msg_type}: {count}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# Singleton do hub
_hub_instance: Optional[TeamCommunicationHub] = None


def get_communication_hub() -> TeamCommunicationHub:
    """Obtém a instância singleton do hub de comunicação."""
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = TeamCommunicationHub()
    return _hub_instance


# ============================================================================
# TESTE DO MÓDULO
# ============================================================================

if __name__ == "__main__":
    hub = get_communication_hub()
    
    # Registra times
    teams = ["data_engineering", "devops", "qa", "data_science", "architecture"]
    for team in teams:
        hub.register_team(team)
    
    # Simula comunicação
    print("Simulando comunicação entre times...\n")
    
    # Data Engineering solicita ajuda
    collab_id = hub.request_help(
        from_team="data_engineering",
        topic="Infraestrutura para pipeline de streaming",
        description="Precisamos de ajuda para configurar Kafka em produção",
        required_expertise=["kafka", "kubernetes", "streaming"]
    )
    print(f"Colaboração criada: {collab_id}")
    
    # DevOps responde
    hub.respond_to_collaboration(
        collaboration_id=collab_id,
        team_name="devops",
        response="Podemos configurar um cluster Kafka no Kubernetes usando Strimzi operator"
    )
    print("DevOps respondeu à colaboração")
    
    # Data Engineering faz pergunta para QA
    msg_id = hub.ask_question(
        from_team="data_engineering",
        to_team="qa",
        question="Quais testes devemos implementar para validar a qualidade dos dados no pipeline?",
        context={"pipeline_type": "streaming", "data_volume": "high"}
    )
    print(f"Pergunta enviada: {msg_id}")
    
    # Handoff de tarefa
    hub.handoff_task(
        from_team="data_engineering",
        to_team="data_science",
        task_description="Pipeline de dados pronto. Agora é necessário criar os modelos de ML",
        deliverables=["Modelo de previsão de vendas", "API de inferência"],
        context={"data_format": "parquet", "features_ready": True}
    )
    print("Handoff realizado para Data Science")
    
    # Gera relatório
    print("\n" + hub.generate_communication_report())
