"""
Project Memory Module

Este módulo implementa a Camada 3 do sistema de conhecimento:
- Memória de longo prazo para projetos
- Armazena decisões, preferências e histórico
- Garante consistência ao longo do projeto

A Project Memory permite que os agentes "lembrem" de
decisões anteriores e mantenham contexto entre sessões.
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class MemoryType(Enum):
    """Tipos de memória armazenada."""
    DECISION = "decision"           # Decisões tomadas
    PREFERENCE = "preference"       # Preferências do cliente
    CONTEXT = "context"             # Contexto do projeto
    INTERACTION = "interaction"     # Histórico de interações
    ARTIFACT = "artifact"           # Artefatos gerados
    FEEDBACK = "feedback"           # Feedback recebido


@dataclass
class MemoryEntry:
    """Representa uma entrada na memória."""
    id: Optional[int]
    project_id: str
    memory_type: str
    key: str
    value: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return asdict(self)


@dataclass
class ProjectContext:
    """Contexto consolidado de um projeto."""
    project_id: str
    project_name: str
    client_name: Optional[str]
    decisions: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    key_artifacts: List[str]
    interaction_summary: str
    last_updated: str


class ProjectMemory:
    """
    Gerenciador de memória de projetos (Camada 3).
    
    Usa SQLite para persistência local, permitindo que
    os agentes mantenham contexto entre sessões.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa a Project Memory.
        
        Args:
            db_path: Caminho para o banco de dados SQLite.
                    Se não fornecido, usa o caminho padrão.
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_dir = project_root / "data" / "memory"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "project_memory.db")
        
        self.db_path = db_path
        self._init_database()
        print(f"[ProjectMemory] Inicializado: {self.db_path}")
    
    def _init_database(self) -> None:
        """Inicializa o schema do banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela principal de memória
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(project_id, memory_type, key)
                )
            """)
            
            # Tabela de projetos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    client_name TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Índices para busca rápida
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_project 
                ON memory(project_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_type 
                ON memory(memory_type)
            """)
            
            conn.commit()
    
    def _now(self) -> str:
        """Retorna timestamp atual em ISO format."""
        return datetime.now().isoformat()
    
    # ==================== Operações de Projeto ====================
    
    def create_project(
        self,
        project_id: str,
        name: str,
        client_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Cria um novo projeto na memória.
        
        Args:
            project_id: ID único do projeto
            name: Nome do projeto
            client_name: Nome do cliente (opcional)
            description: Descrição do projeto (opcional)
        
        Returns:
            True se criado com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = self._now()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO projects 
                    (id, name, client_name, description, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'active', ?, ?)
                """, (project_id, name, client_name, description, now, now))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"[ProjectMemory] Erro ao criar projeto: {e}")
            return False
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um projeto."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM projects WHERE id = ?",
                    (project_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "client_name": row[2],
                        "description": row[3],
                        "status": row[4],
                        "created_at": row[5],
                        "updated_at": row[6]
                    }
                return None
                
        except Exception as e:
            print(f"[ProjectMemory] Erro ao obter projeto: {e}")
            return None
    
    # ==================== Operações de Memória ====================
    
    def store(
        self,
        project_id: str,
        memory_type: MemoryType,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Armazena uma entrada na memória.
        
        Args:
            project_id: ID do projeto
            memory_type: Tipo de memória
            key: Chave identificadora
            value: Valor a armazenar (será serializado para JSON)
            metadata: Metadados adicionais
        
        Returns:
            True se armazenado com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = self._now()
                
                # Serializa valor e metadata
                value_str = json.dumps(value) if not isinstance(value, str) else value
                meta_str = json.dumps(metadata or {})
                
                cursor.execute("""
                    INSERT OR REPLACE INTO memory 
                    (project_id, memory_type, key, value, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    memory_type.value,
                    key,
                    value_str,
                    meta_str,
                    now,
                    now
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"[ProjectMemory] Erro ao armazenar: {e}")
            return False
    
    def retrieve(
        self,
        project_id: str,
        memory_type: Optional[MemoryType] = None,
        key: Optional[str] = None
    ) -> List[MemoryEntry]:
        """
        Recupera entradas da memória.
        
        Args:
            project_id: ID do projeto
            memory_type: Filtrar por tipo (opcional)
            key: Filtrar por chave específica (opcional)
        
        Returns:
            Lista de MemoryEntry
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM memory WHERE project_id = ?"
                params = [project_id]
                
                if memory_type:
                    query += " AND memory_type = ?"
                    params.append(memory_type.value)
                
                if key:
                    query += " AND key = ?"
                    params.append(key)
                
                query += " ORDER BY updated_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                entries = []
                for row in rows:
                    entries.append(MemoryEntry(
                        id=row[0],
                        project_id=row[1],
                        memory_type=row[2],
                        key=row[3],
                        value=row[4],
                        metadata=json.loads(row[5]),
                        created_at=row[6],
                        updated_at=row[7]
                    ))
                
                return entries
                
        except Exception as e:
            print(f"[ProjectMemory] Erro ao recuperar: {e}")
            return []
    
    def get_value(
        self,
        project_id: str,
        memory_type: MemoryType,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Obtém um valor específico da memória.
        
        Args:
            project_id: ID do projeto
            memory_type: Tipo de memória
            key: Chave
            default: Valor padrão se não encontrado
        
        Returns:
            Valor armazenado ou default
        """
        entries = self.retrieve(project_id, memory_type, key)
        if entries:
            try:
                return json.loads(entries[0].value)
            except json.JSONDecodeError:
                return entries[0].value
        return default
    
    # ==================== Métodos de Conveniência ====================
    
    def store_decision(
        self,
        project_id: str,
        decision_key: str,
        decision: str,
        rationale: str,
        alternatives: Optional[List[str]] = None
    ) -> bool:
        """
        Armazena uma decisão tomada no projeto.
        
        Args:
            project_id: ID do projeto
            decision_key: Identificador da decisão
            decision: A decisão tomada
            rationale: Justificativa
            alternatives: Alternativas consideradas
        """
        return self.store(
            project_id=project_id,
            memory_type=MemoryType.DECISION,
            key=decision_key,
            value={
                "decision": decision,
                "rationale": rationale,
                "alternatives": alternatives or []
            },
            metadata={"timestamp": self._now()}
        )
    
    def store_preference(
        self,
        project_id: str,
        preference_key: str,
        preference_value: Any
    ) -> bool:
        """Armazena uma preferência do cliente."""
        return self.store(
            project_id=project_id,
            memory_type=MemoryType.PREFERENCE,
            key=preference_key,
            value=preference_value
        )
    
    def store_interaction(
        self,
        project_id: str,
        interaction_type: str,
        content: str,
        participants: Optional[List[str]] = None
    ) -> bool:
        """Armazena uma interação no histórico."""
        interaction_id = f"{interaction_type}_{self._now()}"
        return self.store(
            project_id=project_id,
            memory_type=MemoryType.INTERACTION,
            key=interaction_id,
            value=content,
            metadata={
                "type": interaction_type,
                "participants": participants or []
            }
        )
    
    def get_all_decisions(self, project_id: str) -> List[Dict[str, Any]]:
        """Obtém todas as decisões de um projeto."""
        entries = self.retrieve(project_id, MemoryType.DECISION)
        decisions = []
        for entry in entries:
            try:
                value = json.loads(entry.value)
                value['key'] = entry.key
                value['timestamp'] = entry.metadata.get('timestamp', entry.created_at)
                decisions.append(value)
            except json.JSONDecodeError:
                pass
        return decisions
    
    def get_all_preferences(self, project_id: str) -> Dict[str, Any]:
        """Obtém todas as preferências de um projeto."""
        entries = self.retrieve(project_id, MemoryType.PREFERENCE)
        preferences = {}
        for entry in entries:
            try:
                preferences[entry.key] = json.loads(entry.value)
            except json.JSONDecodeError:
                preferences[entry.key] = entry.value
        return preferences
    
    # ==================== Contexto Consolidado ====================
    
    def get_project_context(self, project_id: str) -> Optional[ProjectContext]:
        """
        Obtém o contexto consolidado de um projeto.
        
        Útil para fornecer contexto completo aos agentes.
        
        Args:
            project_id: ID do projeto
        
        Returns:
            ProjectContext com todas as informações relevantes
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        decisions = self.get_all_decisions(project_id)
        preferences = self.get_all_preferences(project_id)
        
        # Obtém artefatos
        artifact_entries = self.retrieve(project_id, MemoryType.ARTIFACT)
        artifacts = [e.key for e in artifact_entries]
        
        # Obtém resumo de interações
        interaction_entries = self.retrieve(project_id, MemoryType.INTERACTION)
        interaction_summary = f"{len(interaction_entries)} interações registradas"
        
        return ProjectContext(
            project_id=project_id,
            project_name=project['name'],
            client_name=project.get('client_name'),
            decisions=decisions,
            preferences=preferences,
            key_artifacts=artifacts,
            interaction_summary=interaction_summary,
            last_updated=project['updated_at']
        )
    
    def format_context_for_prompt(self, project_id: str) -> str:
        """
        Formata o contexto do projeto para inclusão em prompts.
        
        Args:
            project_id: ID do projeto
        
        Returns:
            String formatada para inclusão em prompts
        """
        context = self.get_project_context(project_id)
        if not context:
            return ""
        
        output_parts = [
            f"# Contexto do Projeto: {context.project_name}\n",
            f"**ID:** {context.project_id}",
        ]
        
        if context.client_name:
            output_parts.append(f"**Cliente:** {context.client_name}")
        
        # Decisões
        if context.decisions:
            output_parts.append("\n## Decisões Tomadas\n")
            for d in context.decisions[:10]:  # Limita a 10 decisões mais recentes
                output_parts.append(f"- **{d.get('key', 'N/A')}:** {d.get('decision', 'N/A')}")
                output_parts.append(f"  - Justificativa: {d.get('rationale', 'N/A')}")
        
        # Preferências
        if context.preferences:
            output_parts.append("\n## Preferências do Cliente\n")
            for key, value in list(context.preferences.items())[:10]:
                output_parts.append(f"- **{key}:** {value}")
        
        # Artefatos
        if context.key_artifacts:
            output_parts.append("\n## Artefatos Gerados\n")
            for artifact in context.key_artifacts[:10]:
                output_parts.append(f"- {artifact}")
        
        output_parts.append(f"\n*Última atualização: {context.last_updated}*")
        
        return "\n".join(output_parts)
    
    # ==================== Utilitários ====================
    
    def delete_project_memory(self, project_id: str) -> bool:
        """Deleta toda a memória de um projeto."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memory WHERE project_id = ?", (project_id,))
                cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[ProjectMemory] Erro ao deletar projeto: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM projects")
                project_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM memory")
                memory_count = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT memory_type, COUNT(*) 
                    FROM memory 
                    GROUP BY memory_type
                """)
                type_counts = dict(cursor.fetchall())
                
                return {
                    "db_path": self.db_path,
                    "project_count": project_count,
                    "memory_entry_count": memory_count,
                    "entries_by_type": type_counts
                }
                
        except Exception as e:
            return {"error": str(e)}


# Singleton para acesso global
_project_memory_instance: Optional[ProjectMemory] = None


def get_project_memory() -> ProjectMemory:
    """
    Retorna a instância singleton da Project Memory.
    
    Returns:
        Instância da ProjectMemory
    """
    global _project_memory_instance
    if _project_memory_instance is None:
        _project_memory_instance = ProjectMemory()
    return _project_memory_instance


if __name__ == "__main__":
    # Teste da Project Memory
    memory = get_project_memory()
    
    print("\n=== Teste da Project Memory ===")
    
    # Cria um projeto de teste
    test_project_id = "test_project_001"
    memory.create_project(
        project_id=test_project_id,
        name="Projeto de Teste",
        client_name="Cliente Teste",
        description="Um projeto para testar a memória"
    )
    
    # Armazena algumas decisões
    memory.store_decision(
        project_id=test_project_id,
        decision_key="database_choice",
        decision="PostgreSQL",
        rationale="Melhor suporte a JSON e extensibilidade",
        alternatives=["MySQL", "MongoDB"]
    )
    
    memory.store_decision(
        project_id=test_project_id,
        decision_key="cloud_provider",
        decision="AWS",
        rationale="Cliente já tem conta e expertise",
        alternatives=["GCP", "Azure"]
    )
    
    # Armazena preferências
    memory.store_preference(test_project_id, "communication_channel", "Slack")
    memory.store_preference(test_project_id, "meeting_frequency", "weekly")
    
    # Obtém contexto
    print("\n=== Contexto do Projeto ===")
    context_str = memory.format_context_for_prompt(test_project_id)
    print(context_str)
    
    # Estatísticas
    print("\n=== Estatísticas ===")
    stats = memory.get_statistics()
    print(f"Projetos: {stats.get('project_count', 0)}")
    print(f"Entradas de memória: {stats.get('memory_entry_count', 0)}")
    print(f"Por tipo: {stats.get('entries_by_type', {})}")
