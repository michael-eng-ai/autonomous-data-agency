"""
Data Catalog Module

Módulo para gerenciamento de catálogo de dados.
Suporta integração com OpenMetadata e catálogo local.

Inspirado no projeto ABInBev Case, adaptado para o framework de agentes.
"""

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

__all__ = [
    "DataCatalog",
    "TableMetadata",
    "ColumnMetadata",
    "DataAsset",
    "AssetType",
    "get_data_catalog",
]


class AssetType(Enum):
    """Tipos de ativos de dados."""
    TABLE = "table"
    VIEW = "view"
    PIPELINE = "pipeline"
    DASHBOARD = "dashboard"
    MODEL = "model"
    REPORT = "report"
    DATASET = "dataset"
    FILE = "file"


@dataclass
class ColumnMetadata:
    """Metadados de uma coluna."""
    name: str
    data_type: str
    description: str = ""
    is_nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    classification: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    sample_values: List[Any] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TableMetadata:
    """Metadados de uma tabela."""
    table_id: str
    name: str
    schema_name: str
    database: str
    layer: str
    description: str = ""
    owner: str = ""
    columns: List[ColumnMetadata] = field(default_factory=list)
    row_count: int = 0
    size_bytes: int = 0
    classification: str = "internal"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_profiled_at: Optional[datetime] = None
    upstream_tables: List[str] = field(default_factory=list)
    downstream_tables: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataAsset:
    """Representa um ativo de dados genérico."""
    asset_id: str
    name: str
    asset_type: AssetType
    description: str = ""
    owner: str = ""
    layer: str = ""
    classification: str = "internal"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class DataCatalog:
    """
    Catálogo de dados com suporte a OpenMetadata.
    
    Funcionalidades:
    - Registro de tabelas e colunas
    - Classificação automática de dados
    - Lineage tracking
    - Busca e descoberta de dados
    - Integração com OpenMetadata (opcional)
    
    Uso:
        catalog = DataCatalog(project_id="proj_001")
        
        # Registrar tabela
        catalog.register_table(
            name="silver_clientes",
            schema_name="silver",
            database="lakehouse",
            layer="silver",
            columns=[
                ColumnMetadata(name="id", data_type="bigint", is_primary_key=True),
                ColumnMetadata(name="nome", data_type="string", classification="pii"),
                ColumnMetadata(name="email", data_type="string", classification="pii")
            ]
        )
        
        # Buscar tabelas
        tables = catalog.search_tables(query="cliente")
        
        # Obter lineage
        lineage = catalog.get_lineage("silver_clientes")
    """
    
    def __init__(
        self,
        project_id: str,
        db_path: Optional[str] = None,
        openmetadata_url: Optional[str] = None,
        openmetadata_token: Optional[str] = None
    ):
        """
        Inicializa o catálogo de dados.
        
        Args:
            project_id: ID do projeto
            db_path: Caminho para o banco SQLite local
            openmetadata_url: URL do servidor OpenMetadata (opcional)
            openmetadata_token: Token de autenticação (opcional)
        """
        self.project_id = project_id
        self.db_path = db_path or os.path.expanduser(
            f"~/.autonomous-agency/data_catalog_{project_id}.db"
        )
        
        # OpenMetadata config
        self.openmetadata_url = openmetadata_url or os.getenv("OPENMETADATA_URL")
        self.openmetadata_token = openmetadata_token or os.getenv("OPENMETADATA_TOKEN")
        self.use_openmetadata = bool(self.openmetadata_url and self.openmetadata_token)
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Inicializa o banco local
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite local."""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela de assets
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_assets (
                    asset_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    description TEXT,
                    owner TEXT,
                    layer TEXT,
                    classification TEXT,
                    tags TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Tabela de tabelas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tables (
                    table_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    schema_name TEXT,
                    database TEXT,
                    layer TEXT,
                    description TEXT,
                    owner TEXT,
                    row_count INTEGER DEFAULT 0,
                    size_bytes INTEGER DEFAULT 0,
                    classification TEXT,
                    tags TEXT,
                    custom_properties TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_profiled_at TEXT
                )
            """)
            
            # Tabela de colunas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS columns (
                    column_id TEXT PRIMARY KEY,
                    table_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data_type TEXT,
                    description TEXT,
                    is_nullable INTEGER DEFAULT 1,
                    is_primary_key INTEGER DEFAULT 0,
                    is_foreign_key INTEGER DEFAULT 0,
                    foreign_key_table TEXT,
                    foreign_key_column TEXT,
                    classification TEXT,
                    tags TEXT,
                    sample_values TEXT,
                    statistics TEXT,
                    FOREIGN KEY (table_id) REFERENCES tables(table_id)
                )
            """)
            
            # Tabela de lineage
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lineage (
                    lineage_id TEXT PRIMARY KEY,
                    source_table TEXT NOT NULL,
                    target_table TEXT NOT NULL,
                    transformation_type TEXT,
                    transformation_logic TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Índices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tables_name ON tables(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tables_layer ON tables(layer)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_columns_table ON columns(table_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lineage_source ON lineage(source_table)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lineage_target ON lineage(target_table)")
            
            conn.commit()
    
    def register_table(
        self,
        name: str,
        schema_name: str,
        database: str,
        layer: str,
        columns: List[ColumnMetadata],
        description: str = "",
        owner: str = "",
        classification: str = "internal",
        tags: Optional[List[str]] = None,
        custom_properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registra uma tabela no catálogo.
        
        Args:
            name: Nome da tabela
            schema_name: Nome do schema
            database: Nome do banco de dados
            layer: Camada (bronze, silver, gold)
            columns: Lista de metadados de colunas
            description: Descrição da tabela
            owner: Proprietário
            classification: Classificação de dados
            tags: Tags para busca
            custom_properties: Propriedades customizadas
            
        Returns:
            table_id: ID único da tabela
        """
        table_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Insere tabela
            conn.execute("""
                INSERT INTO tables (
                    table_id, name, schema_name, database, layer,
                    description, owner, classification, tags,
                    custom_properties, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                table_id, name, schema_name, database, layer,
                description, owner, classification,
                json.dumps(tags or []),
                json.dumps(custom_properties or {}),
                now, now
            ))
            
            # Insere colunas
            for col in columns:
                column_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO columns (
                        column_id, table_id, name, data_type, description,
                        is_nullable, is_primary_key, is_foreign_key,
                        foreign_key_table, foreign_key_column, classification,
                        tags, sample_values, statistics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    column_id, table_id, col.name, col.data_type,
                    col.description, 1 if col.is_nullable else 0,
                    1 if col.is_primary_key else 0,
                    1 if col.is_foreign_key else 0,
                    col.foreign_key_table, col.foreign_key_column,
                    col.classification, json.dumps(col.tags),
                    json.dumps(col.sample_values), json.dumps(col.statistics)
                ))
            
            conn.commit()
        
        # Sincroniza com OpenMetadata se configurado
        if self.use_openmetadata:
            self._sync_to_openmetadata(table_id)
        
        print(f"[CATALOG] Tabela registrada: {schema_name}.{name}")
        
        return table_id
    
    def update_table_stats(
        self,
        table_name: str,
        row_count: int,
        size_bytes: int = 0
    ) -> bool:
        """
        Atualiza estatísticas de uma tabela.
        
        Args:
            table_name: Nome da tabela
            row_count: Contagem de linhas
            size_bytes: Tamanho em bytes
            
        Returns:
            True se atualizado com sucesso
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE tables 
                SET row_count = ?, size_bytes = ?, 
                    last_profiled_at = ?, updated_at = ?
                WHERE name = ?
            """, (row_count, size_bytes, now, now, table_name))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def get_table(self, table_name: str) -> Optional[TableMetadata]:
        """
        Retorna metadados de uma tabela.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            TableMetadata ou None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Busca tabela
            cursor = conn.execute(
                "SELECT * FROM tables WHERE name = ?",
                (table_name,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Busca colunas
            cursor = conn.execute(
                "SELECT * FROM columns WHERE table_id = ?",
                (row["table_id"],)
            )
            columns = [self._row_to_column(c) for c in cursor.fetchall()]
            
            # Busca lineage
            cursor = conn.execute(
                "SELECT source_table FROM lineage WHERE target_table = ?",
                (table_name,)
            )
            upstream = [r[0] for r in cursor.fetchall()]
            
            cursor = conn.execute(
                "SELECT target_table FROM lineage WHERE source_table = ?",
                (table_name,)
            )
            downstream = [r[0] for r in cursor.fetchall()]
        
        return TableMetadata(
            table_id=row["table_id"],
            name=row["name"],
            schema_name=row["schema_name"],
            database=row["database"],
            layer=row["layer"],
            description=row["description"] or "",
            owner=row["owner"] or "",
            columns=columns,
            row_count=row["row_count"] or 0,
            size_bytes=row["size_bytes"] or 0,
            classification=row["classification"] or "internal",
            tags=json.loads(row["tags"]) if row["tags"] else [],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_profiled_at=datetime.fromisoformat(row["last_profiled_at"]) if row["last_profiled_at"] else None,
            upstream_tables=upstream,
            downstream_tables=downstream,
            custom_properties=json.loads(row["custom_properties"]) if row["custom_properties"] else {}
        )
    
    def search_tables(
        self,
        query: Optional[str] = None,
        layer: Optional[str] = None,
        classification: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[TableMetadata]:
        """
        Busca tabelas no catálogo.
        
        Args:
            query: Termo de busca (nome ou descrição)
            layer: Filtrar por camada
            classification: Filtrar por classificação
            tags: Filtrar por tags
            limit: Limite de resultados
            
        Returns:
            Lista de TableMetadata
        """
        sql = "SELECT name FROM tables WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if layer:
            sql += " AND layer = ?"
            params.append(layer)
        
        if classification:
            sql += " AND classification = ?"
            params.append(classification)
        
        sql += f" ORDER BY updated_at DESC LIMIT {limit}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql, params)
            table_names = [row[0] for row in cursor.fetchall()]
        
        # Filtra por tags se necessário
        results = []
        for name in table_names:
            table = self.get_table(name)
            if table:
                if tags:
                    if any(t in table.tags for t in tags):
                        results.append(table)
                else:
                    results.append(table)
        
        return results
    
    def add_lineage(
        self,
        source_table: str,
        target_table: str,
        transformation_type: str = "transformation",
        transformation_logic: str = ""
    ) -> str:
        """
        Adiciona relação de lineage entre tabelas.
        
        Args:
            source_table: Tabela de origem
            target_table: Tabela de destino
            transformation_type: Tipo de transformação
            transformation_logic: Lógica da transformação
            
        Returns:
            lineage_id
        """
        lineage_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO lineage (
                    lineage_id, source_table, target_table,
                    transformation_type, transformation_logic, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                lineage_id, source_table, target_table,
                transformation_type, transformation_logic, now
            ))
            conn.commit()
        
        print(f"[CATALOG] Lineage adicionado: {source_table} -> {target_table}")
        
        return lineage_id
    
    def get_lineage(
        self,
        table_name: str,
        direction: str = "both",
        depth: int = 3
    ) -> Dict[str, Any]:
        """
        Retorna lineage de uma tabela.
        
        Args:
            table_name: Nome da tabela
            direction: Direção (upstream, downstream, both)
            depth: Profundidade máxima
            
        Returns:
            Dicionário com lineage
        """
        upstream = []
        downstream = []
        
        if direction in ["upstream", "both"]:
            upstream = self._get_upstream(table_name, depth)
        
        if direction in ["downstream", "both"]:
            downstream = self._get_downstream(table_name, depth)
        
        return {
            "table": table_name,
            "upstream": upstream,
            "downstream": downstream
        }
    
    def _get_upstream(self, table_name: str, depth: int, visited: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """Busca tabelas upstream recursivamente."""
        if depth <= 0:
            return []
        
        if visited is None:
            visited = set()
        
        if table_name in visited:
            return []
        
        visited.add(table_name)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT source_table, transformation_type, transformation_logic
                FROM lineage WHERE target_table = ?
            """, (table_name,))
            
            results = []
            for row in cursor.fetchall():
                source = row[0]
                results.append({
                    "table": source,
                    "transformation_type": row[1],
                    "transformation_logic": row[2],
                    "upstream": self._get_upstream(source, depth - 1, visited)
                })
        
        return results
    
    def _get_downstream(self, table_name: str, depth: int, visited: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """Busca tabelas downstream recursivamente."""
        if depth <= 0:
            return []
        
        if visited is None:
            visited = set()
        
        if table_name in visited:
            return []
        
        visited.add(table_name)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT target_table, transformation_type, transformation_logic
                FROM lineage WHERE source_table = ?
            """, (table_name,))
            
            results = []
            for row in cursor.fetchall():
                target = row[0]
                results.append({
                    "table": target,
                    "transformation_type": row[1],
                    "transformation_logic": row[2],
                    "downstream": self._get_downstream(target, depth - 1, visited)
                })
        
        return results
    
    def register_asset(
        self,
        name: str,
        asset_type: AssetType,
        description: str = "",
        owner: str = "",
        layer: str = "",
        classification: str = "internal",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registra um ativo de dados genérico.
        
        Args:
            name: Nome do ativo
            asset_type: Tipo do ativo
            description: Descrição
            owner: Proprietário
            layer: Camada
            classification: Classificação
            tags: Tags
            metadata: Metadados adicionais
            
        Returns:
            asset_id
        """
        asset_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO data_assets (
                    asset_id, name, asset_type, description, owner,
                    layer, classification, tags, metadata,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset_id, name, asset_type.value, description, owner,
                layer, classification, json.dumps(tags or []),
                json.dumps(metadata or {}), now, now
            ))
            conn.commit()
        
        print(f"[CATALOG] Asset registrado: {asset_type.value}/{name}")
        
        return asset_id
    
    def get_catalog_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo do catálogo.
        
        Returns:
            Dicionário com estatísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            # Total de tabelas
            cursor = conn.execute("SELECT COUNT(*) FROM tables")
            total_tables = cursor.fetchone()[0]
            
            # Por camada
            cursor = conn.execute("""
                SELECT layer, COUNT(*) FROM tables GROUP BY layer
            """)
            by_layer = dict(cursor.fetchall())
            
            # Por classificação
            cursor = conn.execute("""
                SELECT classification, COUNT(*) FROM tables GROUP BY classification
            """)
            by_classification = dict(cursor.fetchall())
            
            # Total de colunas
            cursor = conn.execute("SELECT COUNT(*) FROM columns")
            total_columns = cursor.fetchone()[0]
            
            # Colunas PII
            cursor = conn.execute("""
                SELECT COUNT(*) FROM columns WHERE classification = 'pii'
            """)
            pii_columns = cursor.fetchone()[0]
            
            # Total de relações de lineage
            cursor = conn.execute("SELECT COUNT(*) FROM lineage")
            total_lineage = cursor.fetchone()[0]
            
            # Total de assets
            cursor = conn.execute("SELECT COUNT(*) FROM data_assets")
            total_assets = cursor.fetchone()[0]
        
        return {
            "total_tables": total_tables,
            "total_columns": total_columns,
            "pii_columns": pii_columns,
            "total_lineage_relations": total_lineage,
            "total_assets": total_assets,
            "tables_by_layer": by_layer,
            "tables_by_classification": by_classification
        }
    
    def _row_to_column(self, row: sqlite3.Row) -> ColumnMetadata:
        """Converte uma linha do banco para ColumnMetadata."""
        return ColumnMetadata(
            name=row["name"],
            data_type=row["data_type"],
            description=row["description"] or "",
            is_nullable=bool(row["is_nullable"]),
            is_primary_key=bool(row["is_primary_key"]),
            is_foreign_key=bool(row["is_foreign_key"]),
            foreign_key_table=row["foreign_key_table"],
            foreign_key_column=row["foreign_key_column"],
            classification=row["classification"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            sample_values=json.loads(row["sample_values"]) if row["sample_values"] else [],
            statistics=json.loads(row["statistics"]) if row["statistics"] else {}
        )
    
    def _sync_to_openmetadata(self, table_id: str):
        """Sincroniza tabela com OpenMetadata."""
        # Implementação futura - requer requests
        pass


# Singleton para acesso global
_data_catalog: Optional[DataCatalog] = None


def get_data_catalog(project_id: str = "default") -> DataCatalog:
    """
    Retorna instância singleton do DataCatalog.
    
    Args:
        project_id: ID do projeto
        
    Returns:
        DataCatalog instance
    """
    global _data_catalog
    
    if _data_catalog is None or _data_catalog.project_id != project_id:
        _data_catalog = DataCatalog(project_id)
    
    return _data_catalog
