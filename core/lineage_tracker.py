"""
Lineage Tracker Module

Módulo para rastreamento de linhagem de dados.
Registra transformações, dependências e impacto de mudanças.

Inspirado no projeto ABInBev Case, adaptado para o framework de agentes.
"""

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

__all__ = [
    "LineageTracker",
    "LineageNode",
    "LineageEdge",
    "TransformationType",
    "ImpactAnalysis",
    "get_lineage_tracker",
]


class TransformationType(Enum):
    """Tipos de transformação."""
    INGESTION = "ingestion"
    CLEANING = "cleaning"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    JOIN = "join"
    FILTER = "filter"
    ENRICHMENT = "enrichment"
    DEDUPLICATION = "deduplication"
    VALIDATION = "validation"
    ML_FEATURE = "ml_feature"
    ML_PREDICTION = "ml_prediction"
    EXPORT = "export"


class NodeType(Enum):
    """Tipos de nó no grafo de lineage."""
    SOURCE = "source"
    TABLE = "table"
    VIEW = "view"
    PIPELINE = "pipeline"
    MODEL = "model"
    DASHBOARD = "dashboard"
    REPORT = "report"
    API = "api"
    FILE = "file"


@dataclass
class LineageNode:
    """Representa um nó no grafo de lineage."""
    node_id: str
    name: str
    node_type: NodeType
    layer: str = ""
    description: str = ""
    owner: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LineageEdge:
    """Representa uma aresta (transformação) no grafo de lineage."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    transformation_type: TransformationType
    transformation_logic: str = ""
    columns_mapping: Dict[str, str] = field(default_factory=dict)
    sql_query: str = ""
    pipeline_name: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class ImpactAnalysis:
    """Resultado de análise de impacto."""
    source_node: str
    affected_nodes: List[str]
    affected_by_layer: Dict[str, List[str]]
    total_affected: int
    critical_paths: List[List[str]]
    recommendations: List[str]


class LineageTracker:
    """
    Rastreador de linhagem de dados.
    
    Funcionalidades:
    - Registro de nós (tabelas, views, pipelines, etc.)
    - Registro de transformações entre nós
    - Análise de impacto de mudanças
    - Visualização de lineage
    - Rastreamento de colunas
    
    Uso:
        tracker = LineageTracker(project_id="proj_001")
        
        # Registrar nós
        tracker.register_node("bronze_vendas", NodeType.TABLE, layer="bronze")
        tracker.register_node("silver_vendas", NodeType.TABLE, layer="silver")
        
        # Registrar transformação
        tracker.add_transformation(
            source="bronze_vendas",
            target="silver_vendas",
            transformation_type=TransformationType.CLEANING,
            transformation_logic="Remove duplicatas, valida campos"
        )
        
        # Análise de impacto
        impact = tracker.analyze_impact("bronze_vendas")
    """
    
    def __init__(
        self,
        project_id: str,
        db_path: Optional[str] = None
    ):
        """
        Inicializa o rastreador de lineage.
        
        Args:
            project_id: ID do projeto
            db_path: Caminho para o banco SQLite
        """
        self.project_id = project_id
        self.db_path = db_path or os.path.expanduser(
            f"~/.autonomous-agency/lineage_{project_id}.db"
        )
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Inicializa o banco
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela de nós
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lineage_nodes (
                    node_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    node_type TEXT NOT NULL,
                    layer TEXT,
                    description TEXT,
                    owner TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Tabela de arestas (transformações)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lineage_edges (
                    edge_id TEXT PRIMARY KEY,
                    source_node_id TEXT NOT NULL,
                    target_node_id TEXT NOT NULL,
                    transformation_type TEXT NOT NULL,
                    transformation_logic TEXT,
                    columns_mapping TEXT,
                    sql_query TEXT,
                    pipeline_name TEXT,
                    created_at TEXT NOT NULL,
                    created_by TEXT,
                    FOREIGN KEY (source_node_id) REFERENCES lineage_nodes(node_id),
                    FOREIGN KEY (target_node_id) REFERENCES lineage_nodes(node_id)
                )
            """)
            
            # Tabela de mapeamento de colunas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS column_lineage (
                    mapping_id TEXT PRIMARY KEY,
                    edge_id TEXT NOT NULL,
                    source_column TEXT NOT NULL,
                    target_column TEXT NOT NULL,
                    transformation TEXT,
                    FOREIGN KEY (edge_id) REFERENCES lineage_edges(edge_id)
                )
            """)
            
            # Índices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_name ON lineage_nodes(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON lineage_nodes(node_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON lineage_edges(source_node_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON lineage_edges(target_node_id)")
            
            conn.commit()
    
    def register_node(
        self,
        name: str,
        node_type: NodeType,
        layer: str = "",
        description: str = "",
        owner: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registra um nó no grafo de lineage.
        
        Args:
            name: Nome único do nó
            node_type: Tipo do nó
            layer: Camada (bronze, silver, gold)
            description: Descrição
            owner: Proprietário
            metadata: Metadados adicionais
            
        Returns:
            node_id
        """
        node_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT INTO lineage_nodes (
                        node_id, name, node_type, layer, description,
                        owner, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    node_id, name, node_type.value, layer, description,
                    owner, json.dumps(metadata or {}), now
                ))
                conn.commit()
                print(f"[LINEAGE] Nó registrado: {node_type.value}/{name}")
            except sqlite3.IntegrityError:
                # Nó já existe, retorna o ID existente
                cursor = conn.execute(
                    "SELECT node_id FROM lineage_nodes WHERE name = ?",
                    (name,)
                )
                row = cursor.fetchone()
                if row:
                    return row[0]
        
        return node_id
    
    def add_transformation(
        self,
        source: str,
        target: str,
        transformation_type: TransformationType,
        transformation_logic: str = "",
        columns_mapping: Optional[Dict[str, str]] = None,
        sql_query: str = "",
        pipeline_name: str = "",
        created_by: str = ""
    ) -> str:
        """
        Adiciona uma transformação entre dois nós.
        
        Args:
            source: Nome do nó de origem
            target: Nome do nó de destino
            transformation_type: Tipo de transformação
            transformation_logic: Descrição da lógica
            columns_mapping: Mapeamento de colunas {source_col: target_col}
            sql_query: Query SQL (se aplicável)
            pipeline_name: Nome do pipeline
            created_by: Quem criou
            
        Returns:
            edge_id
        """
        # Obtém IDs dos nós
        source_id = self._get_node_id(source)
        target_id = self._get_node_id(target)
        
        if not source_id or not target_id:
            raise ValueError(f"Nó não encontrado: source={source}, target={target}")
        
        edge_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO lineage_edges (
                    edge_id, source_node_id, target_node_id,
                    transformation_type, transformation_logic,
                    columns_mapping, sql_query, pipeline_name,
                    created_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                edge_id, source_id, target_id,
                transformation_type.value, transformation_logic,
                json.dumps(columns_mapping or {}), sql_query,
                pipeline_name, now, created_by
            ))
            
            # Adiciona mapeamento de colunas
            if columns_mapping:
                for source_col, target_col in columns_mapping.items():
                    mapping_id = str(uuid.uuid4())
                    conn.execute("""
                        INSERT INTO column_lineage (
                            mapping_id, edge_id, source_column,
                            target_column, transformation
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (mapping_id, edge_id, source_col, target_col, ""))
            
            conn.commit()
        
        print(f"[LINEAGE] Transformação adicionada: {source} -> {target} ({transformation_type.value})")
        
        return edge_id
    
    def get_upstream(
        self,
        node_name: str,
        depth: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retorna nós upstream (dependências).
        
        Args:
            node_name: Nome do nó
            depth: Profundidade máxima
            
        Returns:
            Lista de nós upstream com transformações
        """
        return self._traverse(node_name, "upstream", depth)
    
    def get_downstream(
        self,
        node_name: str,
        depth: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retorna nós downstream (dependentes).
        
        Args:
            node_name: Nome do nó
            depth: Profundidade máxima
            
        Returns:
            Lista de nós downstream com transformações
        """
        return self._traverse(node_name, "downstream", depth)
    
    def _traverse(
        self,
        node_name: str,
        direction: str,
        depth: int,
        visited: Optional[Set[str]] = None
    ) -> List[Dict[str, Any]]:
        """Traversa o grafo em uma direção."""
        if depth <= 0:
            return []
        
        if visited is None:
            visited = set()
        
        if node_name in visited:
            return []
        
        visited.add(node_name)
        
        node_id = self._get_node_id(node_name)
        if not node_id:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if direction == "upstream":
                cursor = conn.execute("""
                    SELECT n.name, n.node_type, n.layer, e.transformation_type,
                           e.transformation_logic, e.columns_mapping
                    FROM lineage_edges e
                    JOIN lineage_nodes n ON e.source_node_id = n.node_id
                    WHERE e.target_node_id = ?
                """, (node_id,))
            else:  # downstream
                cursor = conn.execute("""
                    SELECT n.name, n.node_type, n.layer, e.transformation_type,
                           e.transformation_logic, e.columns_mapping
                    FROM lineage_edges e
                    JOIN lineage_nodes n ON e.target_node_id = n.node_id
                    WHERE e.source_node_id = ?
                """, (node_id,))
            
            results = []
            for row in cursor.fetchall():
                related_name = row["name"]
                results.append({
                    "name": related_name,
                    "node_type": row["node_type"],
                    "layer": row["layer"],
                    "transformation_type": row["transformation_type"],
                    "transformation_logic": row["transformation_logic"],
                    "columns_mapping": json.loads(row["columns_mapping"]) if row["columns_mapping"] else {},
                    direction: self._traverse(related_name, direction, depth - 1, visited)
                })
        
        return results
    
    def analyze_impact(self, node_name: str) -> ImpactAnalysis:
        """
        Analisa o impacto de mudanças em um nó.
        
        Args:
            node_name: Nome do nó
            
        Returns:
            ImpactAnalysis com nós afetados
        """
        # Obtém todos os nós downstream
        downstream = self._get_all_downstream(node_name)
        
        # Agrupa por camada
        by_layer: Dict[str, List[str]] = {}
        for node in downstream:
            layer = node.get("layer", "unknown")
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(node["name"])
        
        # Identifica caminhos críticos (até dashboards/reports)
        critical_paths = self._find_critical_paths(node_name)
        
        # Gera recomendações
        recommendations = []
        
        if len(downstream) > 10:
            recommendations.append(
                f"ALTO IMPACTO: {len(downstream)} nós serão afetados. "
                "Considere fazer a mudança em horário de baixo uso."
            )
        
        if "gold" in by_layer or "consumption" in by_layer:
            recommendations.append(
                "ATENÇÃO: Tabelas de consumo serão afetadas. "
                "Notifique os usuários de BI antes da mudança."
            )
        
        if any(n.get("node_type") == "dashboard" for n in downstream):
            recommendations.append(
                "CRÍTICO: Dashboards serão afetados. "
                "Valide com os stakeholders antes de prosseguir."
            )
        
        return ImpactAnalysis(
            source_node=node_name,
            affected_nodes=[n["name"] for n in downstream],
            affected_by_layer=by_layer,
            total_affected=len(downstream),
            critical_paths=critical_paths,
            recommendations=recommendations
        )
    
    def _get_all_downstream(
        self,
        node_name: str,
        visited: Optional[Set[str]] = None
    ) -> List[Dict[str, Any]]:
        """Obtém todos os nós downstream recursivamente."""
        if visited is None:
            visited = set()
        
        if node_name in visited:
            return []
        
        visited.add(node_name)
        
        node_id = self._get_node_id(node_name)
        if not node_id:
            return []
        
        results = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT n.name, n.node_type, n.layer
                FROM lineage_edges e
                JOIN lineage_nodes n ON e.target_node_id = n.node_id
                WHERE e.source_node_id = ?
            """, (node_id,))
            
            for row in cursor.fetchall():
                target_name = row["name"]
                results.append({
                    "name": target_name,
                    "node_type": row["node_type"],
                    "layer": row["layer"]
                })
                results.extend(self._get_all_downstream(target_name, visited))
        
        return results
    
    def _find_critical_paths(
        self,
        node_name: str,
        current_path: Optional[List[str]] = None
    ) -> List[List[str]]:
        """Encontra caminhos até nós críticos (dashboards, reports)."""
        if current_path is None:
            current_path = [node_name]
        
        node_id = self._get_node_id(node_name)
        if not node_id:
            return []
        
        critical_paths = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT n.name, n.node_type
                FROM lineage_edges e
                JOIN lineage_nodes n ON e.target_node_id = n.node_id
                WHERE e.source_node_id = ?
            """, (node_id,))
            
            for row in cursor.fetchall():
                target_name = row["name"]
                target_type = row["node_type"]
                
                new_path = current_path + [target_name]
                
                # Se é um nó crítico, adiciona o caminho
                if target_type in ["dashboard", "report", "api"]:
                    critical_paths.append(new_path)
                else:
                    # Continua buscando
                    critical_paths.extend(
                        self._find_critical_paths(target_name, new_path)
                    )
        
        return critical_paths
    
    def get_column_lineage(
        self,
        table_name: str,
        column_name: str
    ) -> Dict[str, Any]:
        """
        Retorna lineage de uma coluna específica.
        
        Args:
            table_name: Nome da tabela
            column_name: Nome da coluna
            
        Returns:
            Dicionário com lineage da coluna
        """
        node_id = self._get_node_id(table_name)
        if not node_id:
            return {"error": f"Tabela não encontrada: {table_name}"}
        
        upstream_columns = []
        downstream_columns = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Busca colunas upstream
            cursor = conn.execute("""
                SELECT cl.source_column, cl.transformation, n.name as table_name
                FROM column_lineage cl
                JOIN lineage_edges e ON cl.edge_id = e.edge_id
                JOIN lineage_nodes n ON e.source_node_id = n.node_id
                WHERE e.target_node_id = ? AND cl.target_column = ?
            """, (node_id, column_name))
            
            for row in cursor.fetchall():
                upstream_columns.append({
                    "table": row["table_name"],
                    "column": row["source_column"],
                    "transformation": row["transformation"]
                })
            
            # Busca colunas downstream
            cursor = conn.execute("""
                SELECT cl.target_column, cl.transformation, n.name as table_name
                FROM column_lineage cl
                JOIN lineage_edges e ON cl.edge_id = e.edge_id
                JOIN lineage_nodes n ON e.target_node_id = n.node_id
                WHERE e.source_node_id = ? AND cl.source_column = ?
            """, (node_id, column_name))
            
            for row in cursor.fetchall():
                downstream_columns.append({
                    "table": row["table_name"],
                    "column": row["target_column"],
                    "transformation": row["transformation"]
                })
        
        return {
            "table": table_name,
            "column": column_name,
            "upstream": upstream_columns,
            "downstream": downstream_columns
        }
    
    def get_full_lineage_graph(self) -> Dict[str, Any]:
        """
        Retorna o grafo completo de lineage.
        
        Returns:
            Dicionário com nós e arestas
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Busca todos os nós
            cursor = conn.execute("SELECT * FROM lineage_nodes")
            nodes = [dict(row) for row in cursor.fetchall()]
            
            # Busca todas as arestas
            cursor = conn.execute("""
                SELECT e.*, 
                       s.name as source_name, 
                       t.name as target_name
                FROM lineage_edges e
                JOIN lineage_nodes s ON e.source_node_id = s.node_id
                JOIN lineage_nodes t ON e.target_node_id = t.node_id
            """)
            edges = [dict(row) for row in cursor.fetchall()]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }
    
    def export_to_mermaid(self) -> str:
        """
        Exporta o grafo de lineage para formato Mermaid.
        
        Returns:
            String com diagrama Mermaid
        """
        graph = self.get_full_lineage_graph()
        
        lines = ["graph LR"]
        
        # Adiciona nós com estilos por tipo
        node_styles = {
            "source": "[({})]",
            "table": "[{}]",
            "view": "{{{}}}",
            "pipeline": "([{}])",
            "model": ">{}]",
            "dashboard": r"[/{}\\]",
            "report": r"[\\{}/]"
        }
        
        for node in graph["nodes"]:
            name = node["name"].replace("-", "_")
            node_type = node["node_type"]
            style = node_styles.get(node_type, "[{}]")
            lines.append(f"    {name}{style.format(node['name'])}")
        
        # Adiciona arestas
        for edge in graph["edges"]:
            source = edge["source_name"].replace("-", "_")
            target = edge["target_name"].replace("-", "_")
            label = edge["transformation_type"]
            lines.append(f"    {source} -->|{label}| {target}")
        
        return "\n".join(lines)
    
    def _get_node_id(self, name: str) -> Optional[str]:
        """Obtém ID de um nó pelo nome."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT node_id FROM lineage_nodes WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            return row[0] if row else None


# Singleton para acesso global
_lineage_tracker: Optional[LineageTracker] = None


def get_lineage_tracker(project_id: str = "default") -> LineageTracker:
    """
    Retorna instância singleton do LineageTracker.
    
    Args:
        project_id: ID do projeto
        
    Returns:
        LineageTracker instance
    """
    global _lineage_tracker
    
    if _lineage_tracker is None or _lineage_tracker.project_id != project_id:
        _lineage_tracker = LineageTracker(project_id)
    
    return _lineage_tracker
