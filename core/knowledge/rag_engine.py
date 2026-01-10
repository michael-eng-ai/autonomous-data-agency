"""
RAG Engine Module

Este módulo implementa a Camada 2 do sistema de conhecimento:
- Retrieval-Augmented Generation usando ChromaDB
- Indexação de documentos técnicos
- Busca semântica para conhecimento dinâmico

O RAG Engine complementa a Knowledge Base (YAML) com
conhecimento mais detalhado e contextual.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib


@dataclass
class Document:
    """Representa um documento para indexação."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """Resultado de uma busca no RAG."""
    document_id: str
    content: str
    metadata: Dict[str, Any]
    relevance_score: float


class RAGEngine:
    """
    Motor de RAG usando ChromaDB para busca semântica.
    
    Fornece conhecimento dinâmico complementar à Knowledge Base estática.
    """
    
    def __init__(
        self,
        collection_name: str = "agency_knowledge",
        persist_directory: Optional[str] = None
    ):
        """
        Inicializa o RAG Engine.
        
        Args:
            collection_name: Nome da coleção no ChromaDB
            persist_directory: Diretório para persistir o banco vetorial
        """
        self.collection_name = collection_name
        
        if persist_directory is None:
            project_root = Path(__file__).parent.parent.parent
            persist_directory = str(project_root / "data" / "vectordb")
        
        self.persist_directory = persist_directory
        self._initialized = False
        self._collection = None
        self._client = None
        
        # Tenta inicializar (pode falhar se ChromaDB não estiver instalado)
        self._try_initialize()
    
    def _try_initialize(self) -> bool:
        """Tenta inicializar o ChromaDB."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Cria o diretório se não existir
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Inicializa o cliente com persistência
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Obtém ou cria a coleção
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Knowledge base for autonomous data agency"}
            )
            
            self._initialized = True
            print(f"[RAGEngine] Inicializado com sucesso. Coleção: {self.collection_name}")
            return True
            
        except ImportError:
            print("[RAGEngine] ChromaDB não instalado. RAG desabilitado.")
            print("[RAGEngine] Instale com: pip install chromadb")
            return False
        except Exception as e:
            print(f"[RAGEngine] Erro na inicialização: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica se o RAG Engine está disponível."""
        return self._initialized
    
    def _generate_id(self, content: str) -> str:
        """Gera um ID único baseado no conteúdo."""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Adiciona um documento ao índice.
        
        Args:
            content: Conteúdo do documento
            metadata: Metadados associados (domain, type, source, etc.)
            document_id: ID opcional (gerado automaticamente se não fornecido)
        
        Returns:
            ID do documento adicionado ou None se falhar
        """
        if not self._initialized:
            print("[RAGEngine] Engine não inicializado")
            return None
        
        try:
            doc_id = document_id or self._generate_id(content)
            meta = metadata or {}
            
            self._collection.add(
                documents=[content],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            return doc_id
            
        except Exception as e:
            print(f"[RAGEngine] Erro ao adicionar documento: {e}")
            return None
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> int:
        """
        Adiciona múltiplos documentos ao índice.
        
        Args:
            documents: Lista de dicts com 'content', 'metadata' (opcional), 'id' (opcional)
        
        Returns:
            Número de documentos adicionados com sucesso
        """
        if not self._initialized:
            return 0
        
        try:
            contents = []
            metadatas = []
            ids = []
            
            for doc in documents:
                content = doc.get('content', '')
                if not content:
                    continue
                
                contents.append(content)
                metadatas.append(doc.get('metadata', {}))
                ids.append(doc.get('id') or self._generate_id(content))
            
            if contents:
                self._collection.add(
                    documents=contents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            return len(contents)
            
        except Exception as e:
            print(f"[RAGEngine] Erro ao adicionar documentos: {e}")
            return 0
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        domain_filter: Optional[str] = None,
        min_relevance: float = 0.0
    ) -> List[SearchResult]:
        """
        Busca documentos relevantes para a query.
        
        Args:
            query: Texto da busca
            n_results: Número máximo de resultados
            domain_filter: Filtrar por domínio específico
            min_relevance: Score mínimo de relevância (0-1)
        
        Returns:
            Lista de SearchResults ordenados por relevância
        """
        if not self._initialized:
            return []
        
        try:
            # Prepara filtro
            where_filter = None
            if domain_filter:
                where_filter = {"domain": domain_filter}
            
            # Executa a busca
            results = self._collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            # Converte para SearchResults
            search_results = []
            
            if results and results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
                ids = results['ids'][0] if results['ids'] else [''] * len(documents)
                distances = results['distances'][0] if results.get('distances') else [0] * len(documents)
                
                for i, doc in enumerate(documents):
                    # Converte distância para score de relevância (0-1)
                    # ChromaDB usa distância L2, menor = mais similar
                    relevance = 1.0 / (1.0 + distances[i]) if distances[i] else 1.0
                    
                    if relevance >= min_relevance:
                        search_results.append(SearchResult(
                            document_id=ids[i],
                            content=doc,
                            metadata=metadatas[i],
                            relevance_score=relevance
                        ))
            
            return search_results
            
        except Exception as e:
            print(f"[RAGEngine] Erro na busca: {e}")
            return []
    
    def search_for_prompt(
        self,
        query: str,
        n_results: int = 3,
        domain_filter: Optional[str] = None
    ) -> str:
        """
        Busca e formata resultados para inclusão em prompts.
        
        Args:
            query: Texto da busca
            n_results: Número de resultados
            domain_filter: Filtrar por domínio
        
        Returns:
            String formatada para inclusão em prompts
        """
        results = self.search(query, n_results, domain_filter)
        
        if not results:
            return ""
        
        output_parts = ["# Conhecimento Relevante (RAG)\n"]
        
        for i, result in enumerate(results, 1):
            source = result.metadata.get('source', 'Unknown')
            domain = result.metadata.get('domain', 'General')
            
            output_parts.append(f"\n## Fonte {i}: {source} ({domain})")
            output_parts.append(f"Relevância: {result.relevance_score:.2%}\n")
            output_parts.append(result.content[:1000])  # Limita tamanho
            if len(result.content) > 1000:
                output_parts.append("...[truncado]")
            output_parts.append("\n")
        
        return "\n".join(output_parts)
    
    def delete_document(self, document_id: str) -> bool:
        """Remove um documento do índice."""
        if not self._initialized:
            return False
        
        try:
            self._collection.delete(ids=[document_id])
            return True
        except Exception as e:
            print(f"[RAGEngine] Erro ao deletar documento: {e}")
            return False
    
    def clear_collection(self) -> bool:
        """Limpa toda a coleção."""
        if not self._initialized:
            return False
        
        try:
            # Deleta e recria a coleção
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.create_collection(
                name=self.collection_name,
                metadata={"description": "Knowledge base for autonomous data agency"}
            )
            return True
        except Exception as e:
            print(f"[RAGEngine] Erro ao limpar coleção: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do índice."""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        try:
            count = self._collection.count()
            return {
                "status": "initialized",
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def index_knowledge_base(self, knowledge_base) -> int:
        """
        Indexa o conteúdo da Knowledge Base no RAG.
        
        Isso permite busca semântica sobre o conhecimento estruturado.
        
        Args:
            knowledge_base: Instância de KnowledgeBase
        
        Returns:
            Número de documentos indexados
        """
        if not self._initialized:
            return 0
        
        documents = []
        
        for key, item in knowledge_base.knowledge_items.items():
            # Serializa o conteúdo para texto
            import yaml
            content_text = yaml.dump(item.content, default_flow_style=False, allow_unicode=True)
            
            # Divide em chunks menores se necessário
            chunks = self._chunk_text(content_text, max_chars=2000)
            
            for i, chunk in enumerate(chunks):
                documents.append({
                    'content': chunk,
                    'metadata': {
                        'domain': item.domain,
                        'type': item.type,
                        'source': f"knowledge_base:{key}",
                        'chunk': i
                    },
                    'id': f"{key}_{i}"
                })
        
        return self.add_documents(documents)
    
    def _chunk_text(self, text: str, max_chars: int = 2000) -> List[str]:
        """Divide texto em chunks menores."""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Divide por linhas para manter contexto
        lines = text.split('\n')
        
        for line in lines:
            if len(current_chunk) + len(line) + 1 <= max_chars:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


# Singleton para acesso global
_rag_engine_instance: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """
    Retorna a instância singleton do RAG Engine.
    
    Returns:
        Instância do RAGEngine
    """
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance


if __name__ == "__main__":
    # Teste do RAG Engine
    rag = get_rag_engine()
    
    print("\n=== Estatísticas do RAG Engine ===")
    stats = rag.get_statistics()
    print(f"Status: {stats}")
    
    if rag.is_available():
        # Adiciona alguns documentos de teste
        print("\n=== Adicionando documentos de teste ===")
        
        test_docs = [
            {
                "content": "Apache Airflow é uma plataforma para criar, agendar e monitorar workflows programaticamente.",
                "metadata": {"domain": "data_engineering", "source": "test"}
            },
            {
                "content": "dbt (data build tool) permite transformar dados em seu warehouse usando SQL.",
                "metadata": {"domain": "data_engineering", "source": "test"}
            },
            {
                "content": "XGBoost é um algoritmo de gradient boosting otimizado para performance e velocidade.",
                "metadata": {"domain": "data_science", "source": "test"}
            }
        ]
        
        added = rag.add_documents(test_docs)
        print(f"Documentos adicionados: {added}")
        
        # Testa busca
        print("\n=== Teste de Busca ===")
        results = rag.search("como orquestrar pipelines de dados", n_results=2)
        for r in results:
            print(f"- {r.content[:100]}... (score: {r.relevance_score:.2%})")
