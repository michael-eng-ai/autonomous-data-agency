"""
Process Control Module

Módulo para registro e monitoramento de execuções do pipeline.
Registra metadados de cada processamento para observabilidade e rastreabilidade.

Inspirado no projeto ABInBev Case, adaptado para o framework de agentes.
"""

import json
import os
import sqlite3
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

__all__ = [
    "ProcessControl",
    "ProcessRecord",
    "ProcessStatus",
    "ProcessLayer",
    "get_process_control",
]


class ProcessStatus(Enum):
    """Status de um processo."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class ProcessLayer(Enum):
    """Camadas do pipeline de dados."""
    LANDING = "landing"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    CONSUMPTION = "consumption"
    AGGREGATION = "aggregation"
    AGENT = "agent"
    WORKFLOW = "workflow"


@dataclass
class ProcessRecord:
    """Representa um registro de processo."""
    process_id: str
    batch_id: str
    project_id: str
    layer: ProcessLayer
    process_name: str
    process_type: str
    status: ProcessStatus
    start_timestamp: datetime
    end_timestamp: Optional[datetime]
    duration_seconds: Optional[float]
    records_read: int
    records_written: int
    records_quarantined: int
    records_failed: int
    error_message: Optional[str]
    error_stack_trace: Optional[str]
    metadata: Dict[str, Any]
    parent_process_id: Optional[str]
    created_at: datetime


class ProcessControl:
    """
    Gerencia registros de controle de processos.
    
    Cada execução de cada tabela/agente em cada camada é registrada
    para rastreabilidade e observabilidade.
    
    Funcionalidades:
    - Registro de início/fim de processos
    - Rastreamento de métricas (registros lidos, escritos, etc.)
    - Hierarquia de processos (pai/filho)
    - Histórico de execuções
    - Métricas de performance
    
    Uso:
        control = ProcessControl(project_id="proj_001")
        
        # Inicia processo
        process_id = control.start_process(
            batch_id="batch_001",
            layer=ProcessLayer.SILVER,
            process_name="transform_sales",
            process_type="transformation"
        )
        
        # ... executa processamento ...
        
        # Finaliza processo
        control.end_process(
            status=ProcessStatus.SUCCESS,
            records_read=1000,
            records_written=950,
            records_quarantined=50
        )
    """
    
    def __init__(
        self,
        project_id: str,
        db_path: Optional[str] = None
    ):
        """
        Inicializa o controlador de processos.
        
        Args:
            project_id: ID do projeto
            db_path: Caminho para o banco SQLite (opcional)
        """
        self.project_id = project_id
        self.db_path = db_path or os.path.expanduser(
            f"~/.autonomous-agency/process_control_{project_id}.db"
        )
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Inicializa o banco
        self._init_database()
        
        # Processo atual
        self._current_process: Optional[Dict[str, Any]] = None
        
        # Stack de processos (para hierarquia)
        self._process_stack: List[Dict[str, Any]] = []
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS process_control (
                    process_id TEXT PRIMARY KEY,
                    batch_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    layer TEXT NOT NULL,
                    process_name TEXT NOT NULL,
                    process_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_timestamp TEXT NOT NULL,
                    end_timestamp TEXT,
                    duration_seconds REAL,
                    records_read INTEGER DEFAULT 0,
                    records_written INTEGER DEFAULT 0,
                    records_quarantined INTEGER DEFAULT 0,
                    records_failed INTEGER DEFAULT 0,
                    error_message TEXT,
                    error_stack_trace TEXT,
                    metadata TEXT,
                    parent_process_id TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (parent_process_id) REFERENCES process_control(process_id)
                )
            """)
            
            # Índices para consultas frequentes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_process_batch 
                ON process_control(batch_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_process_layer 
                ON process_control(layer)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_process_status 
                ON process_control(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_process_name 
                ON process_control(process_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_process_parent 
                ON process_control(parent_process_id)
            """)
            
            conn.commit()
    
    def start_process(
        self,
        batch_id: str,
        layer: ProcessLayer,
        process_name: str,
        process_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
        parent_process_id: Optional[str] = None
    ) -> str:
        """
        Inicia registro de um processo.
        
        Args:
            batch_id: ID do lote de processamento
            layer: Camada (landing, bronze, silver, gold, etc.)
            process_name: Nome do processo
            process_type: Tipo do processo (transformation, validation, etc.)
            metadata: Metadados adicionais
            parent_process_id: ID do processo pai (para hierarquia)
            
        Returns:
            process_id: ID único do processo
        """
        process_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Se há processo atual, usa como pai
        if parent_process_id is None and self._current_process:
            parent_process_id = self._current_process["process_id"]
        
        process_data = {
            "process_id": process_id,
            "batch_id": batch_id,
            "project_id": self.project_id,
            "layer": layer.value,
            "process_name": process_name,
            "process_type": process_type,
            "status": ProcessStatus.RUNNING.value,
            "start_timestamp": now.isoformat(),
            "end_timestamp": None,
            "duration_seconds": None,
            "records_read": 0,
            "records_written": 0,
            "records_quarantined": 0,
            "records_failed": 0,
            "error_message": None,
            "error_stack_trace": None,
            "metadata": metadata or {},
            "parent_process_id": parent_process_id,
            "created_at": now.isoformat()
        }
        
        # Salva processo atual na stack
        if self._current_process:
            self._process_stack.append(self._current_process)
        
        self._current_process = process_data
        
        # Salva no banco
        self._save_process_record(process_data)
        
        print(f"[PROCESS_CONTROL] Iniciado: {layer.value}/{process_name} (ID: {process_id[:8]}...)")
        
        return process_id
    
    def end_process(
        self,
        status: ProcessStatus = ProcessStatus.SUCCESS,
        records_read: int = 0,
        records_written: int = 0,
        records_quarantined: int = 0,
        records_failed: int = 0,
        error_message: Optional[str] = None,
        error_stack_trace: Optional[str] = None,
        metadata_update: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Finaliza registro de um processo.
        
        Args:
            status: Status final (SUCCESS, FAILED, PARTIAL)
            records_read: Registros lidos
            records_written: Registros escritos
            records_quarantined: Registros em quarentena
            records_failed: Registros com erro
            error_message: Mensagem de erro (se houver)
            error_stack_trace: Stack trace (se houver)
            metadata_update: Metadados adicionais para atualizar
            
        Returns:
            process_id do processo finalizado
        """
        if not self._current_process:
            print("[PROCESS_CONTROL] Aviso: Nenhum processo iniciado.")
            return None
        
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self._current_process["start_timestamp"])
        duration = (end_time - start_time).total_seconds()
        
        # Atualiza processo
        self._current_process.update({
            "status": status.value,
            "end_timestamp": end_time.isoformat(),
            "duration_seconds": round(duration, 2),
            "records_read": records_read,
            "records_written": records_written,
            "records_quarantined": records_quarantined,
            "records_failed": records_failed,
            "error_message": error_message,
            "error_stack_trace": error_stack_trace
        })
        
        if metadata_update:
            self._current_process["metadata"].update(metadata_update)
        
        # Atualiza no banco
        self._update_process_record(self._current_process)
        
        process_id = self._current_process["process_id"]
        layer = self._current_process["layer"]
        process_name = self._current_process["process_name"]
        
        print(f"[PROCESS_CONTROL] Finalizado: {layer}/{process_name}")
        print(f"  Status: {status.value}")
        print(f"  Duração: {duration:.2f}s")
        print(f"  Lidos: {records_read} | Escritos: {records_written}")
        print(f"  Quarentena: {records_quarantined} | Falhas: {records_failed}")
        
        # Restaura processo pai da stack
        if self._process_stack:
            self._current_process = self._process_stack.pop()
        else:
            self._current_process = None
        
        return process_id
    
    def fail_process(
        self,
        error: Exception,
        records_read: int = 0,
        records_written: int = 0
    ) -> Optional[str]:
        """
        Marca processo como falho com exceção.
        
        Args:
            error: Exceção que causou a falha
            records_read: Registros lidos antes da falha
            records_written: Registros escritos antes da falha
            
        Returns:
            process_id do processo falho
        """
        return self.end_process(
            status=ProcessStatus.FAILED,
            records_read=records_read,
            records_written=records_written,
            error_message=str(error),
            error_stack_trace=traceback.format_exc()
        )
    
    def get_last_successful_batch(
        self,
        layer: ProcessLayer,
        process_name: str
    ) -> Optional[str]:
        """
        Retorna o batch_id da última execução bem sucedida.
        
        Args:
            layer: Camada
            process_name: Nome do processo
            
        Returns:
            batch_id ou None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT batch_id FROM process_control
                WHERE layer = ? AND process_name = ? AND status = ? AND project_id = ?
                ORDER BY end_timestamp DESC
                LIMIT 1
            """, (layer.value, process_name, ProcessStatus.SUCCESS.value, self.project_id))
            
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_process_history(
        self,
        layer: Optional[ProcessLayer] = None,
        process_name: Optional[str] = None,
        status: Optional[ProcessStatus] = None,
        batch_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ProcessRecord]:
        """
        Retorna histórico de execuções.
        
        Args:
            layer: Filtrar por camada
            process_name: Filtrar por nome do processo
            status: Filtrar por status
            batch_id: Filtrar por batch
            limit: Limite de registros
            
        Returns:
            Lista de ProcessRecord
        """
        query = "SELECT * FROM process_control WHERE project_id = ?"
        params = [self.project_id]
        
        if layer:
            query += " AND layer = ?"
            params.append(layer.value)
        
        if process_name:
            query += " AND process_name = ?"
            params.append(process_name)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        if batch_id:
            query += " AND batch_id = ?"
            params.append(batch_id)
        
        query += f" ORDER BY start_timestamp DESC LIMIT {limit}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_batch_summary(self, batch_id: str) -> Dict[str, Any]:
        """
        Retorna resumo de um batch.
        
        Args:
            batch_id: ID do batch
            
        Returns:
            Dicionário com resumo
        """
        with sqlite3.connect(self.db_path) as conn:
            # Processos do batch
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_processes,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'partial' THEN 1 ELSE 0 END) as partial,
                    SUM(records_read) as total_read,
                    SUM(records_written) as total_written,
                    SUM(records_quarantined) as total_quarantined,
                    SUM(records_failed) as total_failed,
                    SUM(duration_seconds) as total_duration,
                    MIN(start_timestamp) as batch_start,
                    MAX(end_timestamp) as batch_end
                FROM process_control
                WHERE batch_id = ? AND project_id = ?
            """, (batch_id, self.project_id))
            
            row = cursor.fetchone()
            
            # Por camada
            cursor = conn.execute("""
                SELECT layer, COUNT(*) as count, 
                       SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful
                FROM process_control
                WHERE batch_id = ? AND project_id = ?
                GROUP BY layer
            """, (batch_id, self.project_id))
            
            by_layer = {r[0]: {"count": r[1], "successful": r[2]} for r in cursor.fetchall()}
        
        return {
            "batch_id": batch_id,
            "total_processes": row[0] or 0,
            "successful": row[1] or 0,
            "failed": row[2] or 0,
            "partial": row[3] or 0,
            "total_records_read": row[4] or 0,
            "total_records_written": row[5] or 0,
            "total_records_quarantined": row[6] or 0,
            "total_records_failed": row[7] or 0,
            "total_duration_seconds": row[8] or 0,
            "batch_start": row[9],
            "batch_end": row[10],
            "by_layer": by_layer
        }
    
    def get_performance_metrics(
        self,
        process_name: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Retorna métricas de performance de um processo.
        
        Args:
            process_name: Nome do processo
            days: Número de dias para análise
            
        Returns:
            Métricas de performance
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as executions,
                    AVG(duration_seconds) as avg_duration,
                    MIN(duration_seconds) as min_duration,
                    MAX(duration_seconds) as max_duration,
                    AVG(records_read) as avg_records_read,
                    AVG(records_written) as avg_records_written,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM process_control
                WHERE process_name = ? 
                AND project_id = ?
                AND start_timestamp >= datetime('now', ?)
            """, (process_name, self.project_id, f'-{days} days'))
            
            row = cursor.fetchone()
        
        return {
            "process_name": process_name,
            "period_days": days,
            "total_executions": row[0] or 0,
            "avg_duration_seconds": round(row[1] or 0, 2),
            "min_duration_seconds": round(row[2] or 0, 2),
            "max_duration_seconds": round(row[3] or 0, 2),
            "avg_records_read": round(row[4] or 0, 0),
            "avg_records_written": round(row[5] or 0, 0),
            "success_rate_percent": round(row[6] or 0, 2)
        }
    
    def get_child_processes(self, parent_process_id: str) -> List[ProcessRecord]:
        """
        Retorna processos filhos de um processo pai.
        
        Args:
            parent_process_id: ID do processo pai
            
        Returns:
            Lista de processos filhos
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM process_control
                WHERE parent_process_id = ?
                ORDER BY start_timestamp ASC
            """, (parent_process_id,))
            rows = cursor.fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def _save_process_record(self, process_data: Dict[str, Any]):
        """Salva registro no banco."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO process_control (
                    process_id, batch_id, project_id, layer, process_name,
                    process_type, status, start_timestamp, end_timestamp,
                    duration_seconds, records_read, records_written,
                    records_quarantined, records_failed, error_message,
                    error_stack_trace, metadata, parent_process_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                process_data["process_id"],
                process_data["batch_id"],
                process_data["project_id"],
                process_data["layer"],
                process_data["process_name"],
                process_data["process_type"],
                process_data["status"],
                process_data["start_timestamp"],
                process_data["end_timestamp"],
                process_data["duration_seconds"],
                process_data["records_read"],
                process_data["records_written"],
                process_data["records_quarantined"],
                process_data["records_failed"],
                process_data["error_message"],
                process_data["error_stack_trace"],
                json.dumps(process_data["metadata"]),
                process_data["parent_process_id"],
                process_data["created_at"]
            ))
            conn.commit()
    
    def _update_process_record(self, process_data: Dict[str, Any]):
        """Atualiza registro no banco."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE process_control SET
                    status = ?,
                    end_timestamp = ?,
                    duration_seconds = ?,
                    records_read = ?,
                    records_written = ?,
                    records_quarantined = ?,
                    records_failed = ?,
                    error_message = ?,
                    error_stack_trace = ?,
                    metadata = ?
                WHERE process_id = ?
            """, (
                process_data["status"],
                process_data["end_timestamp"],
                process_data["duration_seconds"],
                process_data["records_read"],
                process_data["records_written"],
                process_data["records_quarantined"],
                process_data["records_failed"],
                process_data["error_message"],
                process_data["error_stack_trace"],
                json.dumps(process_data["metadata"]),
                process_data["process_id"]
            ))
            conn.commit()
    
    def _row_to_record(self, row: sqlite3.Row) -> ProcessRecord:
        """Converte uma linha do banco para ProcessRecord."""
        return ProcessRecord(
            process_id=row["process_id"],
            batch_id=row["batch_id"],
            project_id=row["project_id"],
            layer=ProcessLayer(row["layer"]),
            process_name=row["process_name"],
            process_type=row["process_type"],
            status=ProcessStatus(row["status"]),
            start_timestamp=datetime.fromisoformat(row["start_timestamp"]),
            end_timestamp=datetime.fromisoformat(row["end_timestamp"]) if row["end_timestamp"] else None,
            duration_seconds=row["duration_seconds"],
            records_read=row["records_read"],
            records_written=row["records_written"],
            records_quarantined=row["records_quarantined"],
            records_failed=row["records_failed"],
            error_message=row["error_message"],
            error_stack_trace=row["error_stack_trace"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            parent_process_id=row["parent_process_id"],
            created_at=datetime.fromisoformat(row["created_at"])
        )


# Singleton para acesso global
_process_control: Optional[ProcessControl] = None


def get_process_control(project_id: str = "default") -> ProcessControl:
    """
    Retorna instância singleton do ProcessControl.
    
    Args:
        project_id: ID do projeto
        
    Returns:
        ProcessControl instance
    """
    global _process_control
    
    if _process_control is None or _process_control.project_id != project_id:
        _process_control = ProcessControl(project_id)
    
    return _process_control
