"""
Quarantine Manager Module

Módulo para gerenciamento de registros em quarentena.
Registros que falham nas validações de qualidade de dados são
armazenados aqui para posterior análise e reprocessamento.

Inspirado no projeto ABInBev Case, adaptado para o framework de agentes.
"""

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

__all__ = [
    "QuarantineManager",
    "QuarantineRecord",
    "QuarantineStatus",
    "ErrorType",
    "get_quarantine_manager",
]


class ErrorType(Enum):
    """Tipos de erro para quarentena."""
    VALIDATION_ERROR = "validation_error"
    SCHEMA_ERROR = "schema_error"
    TRANSFORMATION_ERROR = "transformation_error"
    BUSINESS_RULE_ERROR = "business_rule_error"
    DATA_QUALITY_ERROR = "data_quality_error"
    UNKNOWN_ERROR = "unknown_error"


class QuarantineStatus(Enum):
    """Status de um registro em quarentena."""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    REPROCESSED = "reprocessed"
    DISCARDED = "discarded"
    FIXED = "fixed"


@dataclass
class QuarantineRecord:
    """Representa um registro em quarentena."""
    quarantine_id: str
    batch_id: str
    project_id: str
    source_table: str
    target_table: str
    record_data: Dict[str, Any]
    error_type: ErrorType
    error_code: str
    error_description: str
    dq_rule_name: Optional[str]
    is_known_rule: bool
    status: QuarantineStatus
    reprocess_batch_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None


class QuarantineManager:
    """
    Gerencia registros em quarentena.
    
    Funcionalidades:
    - Armazena registros que falharam na validação
    - Permite reprocessamento posterior
    - Identifica erros conhecidos vs. desconhecidos
    - Gera alertas para erros novos
    - Rastreia status de cada registro
    
    Uso:
        manager = QuarantineManager(project_id="proj_001")
        
        # Enviar para quarentena
        manager.quarantine_record(
            batch_id="batch_001",
            source_table="bronze_sales",
            target_table="silver_sales",
            record_data={"id": 1, "value": -100},
            error_type=ErrorType.VALIDATION_ERROR,
            error_code="DQ_SALES_001",
            error_description="Valor negativo não permitido"
        )
        
        # Listar pendentes
        pending = manager.get_pending_records()
        
        # Marcar como reprocessado
        manager.mark_as_reprocessed(quarantine_id, "batch_002")
    """
    
    def __init__(
        self,
        project_id: str,
        db_path: Optional[str] = None
    ):
        """
        Inicializa o gerenciador de quarentena.
        
        Args:
            project_id: ID do projeto
            db_path: Caminho para o banco SQLite (opcional)
        """
        self.project_id = project_id
        self.db_path = db_path or os.path.expanduser(
            f"~/.autonomous-agency/quarantine_{project_id}.db"
        )
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Inicializa o banco
        self._init_database()
        
        # Contadores de sessão
        self._session_stats = {
            "quarantined": 0,
            "reprocessed": 0,
            "discarded": 0,
            "alerts_generated": 0
        }
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quarantine (
                    quarantine_id TEXT PRIMARY KEY,
                    batch_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    source_table TEXT NOT NULL,
                    target_table TEXT NOT NULL,
                    record_data TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_code TEXT NOT NULL,
                    error_description TEXT NOT NULL,
                    dq_rule_name TEXT,
                    is_known_rule INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    reprocess_batch_id TEXT,
                    reviewed_by TEXT,
                    review_notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Índices para consultas frequentes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_quarantine_status 
                ON quarantine(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_quarantine_batch 
                ON quarantine(batch_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_quarantine_error_code 
                ON quarantine(error_code)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_quarantine_known_rule 
                ON quarantine(is_known_rule)
            """)
            
            conn.commit()
    
    def quarantine_record(
        self,
        batch_id: str,
        source_table: str,
        target_table: str,
        record_data: Dict[str, Any],
        error_type: ErrorType,
        error_code: str,
        error_description: str,
        dq_rule_name: Optional[str] = None,
        is_known_rule: bool = True
    ) -> str:
        """
        Envia um registro para quarentena.
        
        Args:
            batch_id: ID do lote de processamento
            source_table: Tabela de origem
            target_table: Tabela de destino
            record_data: Dados do registro
            error_type: Tipo de erro
            error_code: Código do erro (ex: DQ_SALES_001)
            error_description: Descrição do erro
            dq_rule_name: Nome da regra de DQ (opcional)
            is_known_rule: True se erro conhecido, False se novo
            
        Returns:
            quarantine_id: ID único do registro em quarentena
        """
        quarantine_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO quarantine (
                    quarantine_id, batch_id, project_id, source_table,
                    target_table, record_data, error_type, error_code,
                    error_description, dq_rule_name, is_known_rule,
                    status, reprocess_batch_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                quarantine_id, batch_id, self.project_id, source_table,
                target_table, json.dumps(record_data), error_type.value,
                error_code, error_description, dq_rule_name,
                1 if is_known_rule else 0, QuarantineStatus.PENDING.value,
                None, now, now
            ))
            conn.commit()
        
        self._session_stats["quarantined"] += 1
        
        # Gera alerta se erro desconhecido
        if not is_known_rule:
            self._generate_alert(error_code, error_description)
        
        return quarantine_id
    
    def quarantine_batch(
        self,
        batch_id: str,
        source_table: str,
        target_table: str,
        records: List[Dict[str, Any]],
        error_type: ErrorType,
        error_code: str,
        error_description: str,
        dq_rule_name: Optional[str] = None,
        is_known_rule: bool = True
    ) -> List[str]:
        """
        Envia múltiplos registros para quarentena.
        
        Args:
            batch_id: ID do lote
            source_table: Tabela de origem
            target_table: Tabela de destino
            records: Lista de registros
            error_type: Tipo de erro
            error_code: Código do erro
            error_description: Descrição do erro
            dq_rule_name: Nome da regra de DQ
            is_known_rule: Se é erro conhecido
            
        Returns:
            Lista de quarantine_ids
        """
        quarantine_ids = []
        
        for record in records:
            qid = self.quarantine_record(
                batch_id=batch_id,
                source_table=source_table,
                target_table=target_table,
                record_data=record,
                error_type=error_type,
                error_code=error_code,
                error_description=error_description,
                dq_rule_name=dq_rule_name,
                is_known_rule=is_known_rule
            )
            quarantine_ids.append(qid)
        
        print(f"[QUARANTINE] {len(records)} registros quarentenados: {error_code}")
        
        return quarantine_ids
    
    def get_pending_records(
        self,
        source_table: Optional[str] = None,
        error_code: Optional[str] = None,
        limit: int = 100
    ) -> List[QuarantineRecord]:
        """
        Retorna registros pendentes de reprocessamento.
        
        Args:
            source_table: Filtrar por tabela de origem
            error_code: Filtrar por código de erro
            limit: Limite de registros
            
        Returns:
            Lista de QuarantineRecord
        """
        query = """
            SELECT * FROM quarantine 
            WHERE status = ? AND project_id = ?
        """
        params = [QuarantineStatus.PENDING.value, self.project_id]
        
        if source_table:
            query += " AND source_table = ?"
            params.append(source_table)
        
        if error_code:
            query += " AND error_code = ?"
            params.append(error_code)
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_unknown_errors(self) -> List[QuarantineRecord]:
        """
        Retorna erros desconhecidos que precisam de novas regras.
        
        Returns:
            Lista de registros com erros desconhecidos
        """
        query = """
            SELECT * FROM quarantine 
            WHERE is_known_rule = 0 
            AND status = ?
            AND project_id = ?
            ORDER BY created_at DESC
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, [
                QuarantineStatus.PENDING.value,
                self.project_id
            ])
            rows = cursor.fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def mark_as_reprocessed(
        self,
        quarantine_id: str,
        reprocess_batch_id: str
    ) -> bool:
        """
        Marca um registro como reprocessado.
        
        Args:
            quarantine_id: ID do registro em quarentena
            reprocess_batch_id: ID do batch de reprocessamento
            
        Returns:
            True se atualizado com sucesso
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE quarantine 
                SET status = ?, reprocess_batch_id = ?, updated_at = ?
                WHERE quarantine_id = ?
            """, (
                QuarantineStatus.REPROCESSED.value,
                reprocess_batch_id,
                now,
                quarantine_id
            ))
            conn.commit()
            
            if cursor.rowcount > 0:
                self._session_stats["reprocessed"] += 1
                return True
        
        return False
    
    def mark_as_discarded(
        self,
        quarantine_id: str,
        reviewed_by: str,
        review_notes: str
    ) -> bool:
        """
        Marca um registro como descartado (não será reprocessado).
        
        Args:
            quarantine_id: ID do registro
            reviewed_by: Quem revisou
            review_notes: Notas da revisão
            
        Returns:
            True se atualizado com sucesso
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE quarantine 
                SET status = ?, reviewed_by = ?, review_notes = ?, updated_at = ?
                WHERE quarantine_id = ?
            """, (
                QuarantineStatus.DISCARDED.value,
                reviewed_by,
                review_notes,
                now,
                quarantine_id
            ))
            conn.commit()
            
            if cursor.rowcount > 0:
                self._session_stats["discarded"] += 1
                return True
        
        return False
    
    def mark_as_fixed(
        self,
        quarantine_id: str,
        reviewed_by: str,
        review_notes: str
    ) -> bool:
        """
        Marca um registro como corrigido manualmente.
        
        Args:
            quarantine_id: ID do registro
            reviewed_by: Quem corrigiu
            review_notes: Descrição da correção
            
        Returns:
            True se atualizado com sucesso
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE quarantine 
                SET status = ?, reviewed_by = ?, review_notes = ?, updated_at = ?
                WHERE quarantine_id = ?
            """, (
                QuarantineStatus.FIXED.value,
                reviewed_by,
                review_notes,
                now,
                quarantine_id
            ))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da quarentena.
        
        Returns:
            Dicionário com estatísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            # Total por status
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM quarantine
                WHERE project_id = ?
                GROUP BY status
            """, [self.project_id])
            status_counts = dict(cursor.fetchall())
            
            # Total por tipo de erro
            cursor = conn.execute("""
                SELECT error_type, COUNT(*) as count
                FROM quarantine
                WHERE project_id = ?
                GROUP BY error_type
            """, [self.project_id])
            error_type_counts = dict(cursor.fetchall())
            
            # Top 10 códigos de erro
            cursor = conn.execute("""
                SELECT error_code, COUNT(*) as count
                FROM quarantine
                WHERE project_id = ?
                GROUP BY error_code
                ORDER BY count DESC
                LIMIT 10
            """, [self.project_id])
            top_errors = dict(cursor.fetchall())
            
            # Erros desconhecidos
            cursor = conn.execute("""
                SELECT COUNT(*) FROM quarantine
                WHERE project_id = ? AND is_known_rule = 0
            """, [self.project_id])
            unknown_errors = cursor.fetchone()[0]
        
        return {
            "project_id": self.project_id,
            "by_status": status_counts,
            "by_error_type": error_type_counts,
            "top_error_codes": top_errors,
            "unknown_errors": unknown_errors,
            "session_stats": self._session_stats
        }
    
    def get_error_summary(self) -> List[Dict[str, Any]]:
        """
        Retorna resumo de erros para análise.
        
        Returns:
            Lista de erros com contagem e exemplos
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT 
                    error_code,
                    error_description,
                    error_type,
                    is_known_rule,
                    COUNT(*) as count,
                    MIN(created_at) as first_occurrence,
                    MAX(created_at) as last_occurrence
                FROM quarantine
                WHERE project_id = ?
                GROUP BY error_code, error_description, error_type, is_known_rule
                ORDER BY count DESC
            """, [self.project_id])
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _generate_alert(self, error_code: str, error_description: str):
        """Gera alerta para erro desconhecido."""
        self._session_stats["alerts_generated"] += 1
        print(f"[ALERT] ERRO DESCONHECIDO: {error_code}")
        print(f"[ALERT] Descrição: {error_description}")
        print(f"[ALERT] Ação necessária: Criar nova regra de DQ")
    
    def _row_to_record(self, row: sqlite3.Row) -> QuarantineRecord:
        """Converte uma linha do banco para QuarantineRecord."""
        return QuarantineRecord(
            quarantine_id=row["quarantine_id"],
            batch_id=row["batch_id"],
            project_id=row["project_id"],
            source_table=row["source_table"],
            target_table=row["target_table"],
            record_data=json.loads(row["record_data"]),
            error_type=ErrorType(row["error_type"]),
            error_code=row["error_code"],
            error_description=row["error_description"],
            dq_rule_name=row["dq_rule_name"],
            is_known_rule=bool(row["is_known_rule"]),
            status=QuarantineStatus(row["status"]),
            reprocess_batch_id=row["reprocess_batch_id"],
            reviewed_by=row["reviewed_by"],
            review_notes=row["review_notes"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )


# Singleton para acesso global
_quarantine_manager: Optional[QuarantineManager] = None


def get_quarantine_manager(project_id: str = "default") -> QuarantineManager:
    """
    Retorna instância singleton do QuarantineManager.
    
    Args:
        project_id: ID do projeto
        
    Returns:
        QuarantineManager instance
    """
    global _quarantine_manager
    
    if _quarantine_manager is None or _quarantine_manager.project_id != project_id:
        _quarantine_manager = QuarantineManager(project_id)
    
    return _quarantine_manager
