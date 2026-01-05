"""
Knowledge Package

Este pacote implementa o sistema de conhecimento em 3 camadas:

1. Knowledge Base (YAML): Conhecimento estruturado e determinístico
2. RAG Engine (ChromaDB): Busca semântica para conhecimento dinâmico
3. Project Memory (SQLite): Memória de longo prazo para projetos

Cada camada complementa as outras:
- Knowledge Base: Rápido, determinístico, versionável
- RAG Engine: Flexível, semântico, extensível
- Project Memory: Contextual, persistente, específico por projeto
"""

from .knowledge_base import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeQuery,
    get_knowledge_base
)

from .rag_engine import (
    RAGEngine,
    Document,
    SearchResult,
    get_rag_engine
)

from .project_memory import (
    ProjectMemory,
    MemoryType,
    MemoryEntry,
    ProjectContext,
    get_project_memory
)

__all__ = [
    # Knowledge Base
    "KnowledgeBase",
    "KnowledgeItem",
    "KnowledgeQuery",
    "get_knowledge_base",
    # RAG Engine
    "RAGEngine",
    "Document",
    "SearchResult",
    "get_rag_engine",
    # Project Memory
    "ProjectMemory",
    "MemoryType",
    "MemoryEntry",
    "ProjectContext",
    "get_project_memory",
]


class KnowledgeManager:
    """
    Gerenciador unificado das 3 camadas de conhecimento.
    
    Fornece uma interface única para acessar conhecimento
    de todas as fontes de forma coordenada.
    """
    
    def __init__(self):
        """Inicializa o gerenciador com todas as camadas."""
        self.knowledge_base = get_knowledge_base()
        self.rag_engine = get_rag_engine()
        self.project_memory = get_project_memory()
    
    def get_knowledge_for_agent(
        self,
        domain: str,
        task: str,
        project_id: str = None
    ) -> str:
        """
        Obtém conhecimento consolidado para um agente.
        
        Combina conhecimento das 3 camadas em um único contexto.
        
        Args:
            domain: Domínio do agente (ex: "data_engineering")
            task: Descrição da tarefa atual
            project_id: ID do projeto (opcional)
        
        Returns:
            String formatada com conhecimento relevante
        """
        parts = []
        
        # Camada 1: Knowledge Base (sempre disponível)
        kb_knowledge = self.knowledge_base.format_for_prompt(
            domain,
            sections=['principles', 'checklists', 'anti_patterns']
        )
        if kb_knowledge:
            parts.append("# CONHECIMENTO BASE (Best Practices)\n")
            parts.append(kb_knowledge)
        
        # Camada 2: RAG (se disponível e relevante)
        if self.rag_engine.is_available():
            rag_knowledge = self.rag_engine.search_for_prompt(
                query=task,
                n_results=3,
                domain_filter=domain
            )
            if rag_knowledge:
                parts.append("\n# CONHECIMENTO DINÂMICO (RAG)\n")
                parts.append(rag_knowledge)
        
        # Camada 3: Project Memory (se projeto especificado)
        if project_id:
            project_context = self.project_memory.format_context_for_prompt(project_id)
            if project_context:
                parts.append("\n# CONTEXTO DO PROJETO\n")
                parts.append(project_context)
        
        return "\n".join(parts)
    
    def store_project_decision(
        self,
        project_id: str,
        decision_key: str,
        decision: str,
        rationale: str,
        alternatives: list = None
    ) -> bool:
        """Armazena uma decisão do projeto."""
        return self.project_memory.store_decision(
            project_id=project_id,
            decision_key=decision_key,
            decision=decision,
            rationale=rationale,
            alternatives=alternatives
        )
    
    def get_statistics(self) -> dict:
        """Retorna estatísticas de todas as camadas."""
        return {
            "knowledge_base": self.knowledge_base.get_statistics(),
            "rag_engine": self.rag_engine.get_statistics(),
            "project_memory": self.project_memory.get_statistics()
        }


# Singleton do gerenciador
_knowledge_manager_instance = None


def get_knowledge_manager() -> KnowledgeManager:
    """Retorna a instância singleton do KnowledgeManager."""
    global _knowledge_manager_instance
    if _knowledge_manager_instance is None:
        _knowledge_manager_instance = KnowledgeManager()
    return _knowledge_manager_instance
