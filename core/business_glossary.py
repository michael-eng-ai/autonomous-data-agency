"""
Business Glossary Module

Módulo para gerenciamento de glossário de negócio.
Padroniza termos, definições e relacionamentos entre conceitos.

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
import yaml

__all__ = [
    "BusinessGlossary",
    "GlossaryTerm",
    "TermRelationship",
    "TermStatus",
    "get_business_glossary",
]


class TermStatus(Enum):
    """Status de um termo no glossário."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class RelationshipType(Enum):
    """Tipos de relacionamento entre termos."""
    SYNONYM = "synonym"
    ANTONYM = "antonym"
    PARENT = "parent"
    CHILD = "child"
    RELATED = "related"
    DERIVED = "derived"
    COMPOSED_OF = "composed_of"


@dataclass
class TermRelationship:
    """Relacionamento entre termos."""
    related_term: str
    relationship_type: RelationshipType
    description: str = ""


@dataclass
class GlossaryTerm:
    """Representa um termo do glossário de negócio."""
    term_id: str
    name: str
    definition: str
    domain: str = ""
    synonyms: List[str] = field(default_factory=list)
    related_columns: List[str] = field(default_factory=list)
    related_tables: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    owner: str = ""
    steward: str = ""
    status: TermStatus = TermStatus.DRAFT
    tags: List[str] = field(default_factory=list)
    relationships: List[TermRelationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    approved_by: str = ""


class BusinessGlossary:
    """
    Glossário de negócio para padronização de termos.
    
    Funcionalidades:
    - Registro de termos e definições
    - Sinônimos e relacionamentos
    - Mapeamento para colunas/tabelas
    - Busca e descoberta
    - Importação/exportação YAML
    - Validação de consistência
    
    Uso:
        glossary = BusinessGlossary(project_id="proj_001")
        
        # Adicionar termo
        glossary.add_term(
            name="Cliente",
            definition="Pessoa física ou jurídica que realiza compras",
            domain="Vendas",
            synonyms=["Consumidor", "Comprador"],
            related_columns=["cliente_id", "customer_id"]
        )
        
        # Buscar termo
        term = glossary.get_term("Cliente")
        
        # Buscar por coluna
        terms = glossary.find_terms_for_column("cliente_id")
    """
    
    def __init__(
        self,
        project_id: str,
        db_path: Optional[str] = None
    ):
        """
        Inicializa o glossário de negócio.
        
        Args:
            project_id: ID do projeto
            db_path: Caminho para o banco SQLite
        """
        self.project_id = project_id
        self.db_path = db_path or os.path.expanduser(
            f"~/.autonomous-agency/glossary_{project_id}.db"
        )
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Inicializa o banco
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela de termos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS glossary_terms (
                    term_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    definition TEXT NOT NULL,
                    domain TEXT,
                    synonyms TEXT,
                    related_columns TEXT,
                    related_tables TEXT,
                    examples TEXT,
                    business_rules TEXT,
                    owner TEXT,
                    steward TEXT,
                    status TEXT DEFAULT 'draft',
                    tags TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    approved_at TEXT,
                    approved_by TEXT
                )
            """)
            
            # Tabela de relacionamentos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS term_relationships (
                    relationship_id TEXT PRIMARY KEY,
                    term_id TEXT NOT NULL,
                    related_term_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (term_id) REFERENCES glossary_terms(term_id),
                    FOREIGN KEY (related_term_id) REFERENCES glossary_terms(term_id)
                )
            """)
            
            # Tabela de histórico de alterações
            conn.execute("""
                CREATE TABLE IF NOT EXISTS term_history (
                    history_id TEXT PRIMARY KEY,
                    term_id TEXT NOT NULL,
                    field_changed TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by TEXT,
                    changed_at TEXT NOT NULL,
                    FOREIGN KEY (term_id) REFERENCES glossary_terms(term_id)
                )
            """)
            
            # Índices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_terms_name ON glossary_terms(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_terms_domain ON glossary_terms(domain)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_terms_status ON glossary_terms(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_term ON term_relationships(term_id)")
            
            conn.commit()
    
    def add_term(
        self,
        name: str,
        definition: str,
        domain: str = "",
        synonyms: Optional[List[str]] = None,
        related_columns: Optional[List[str]] = None,
        related_tables: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        business_rules: Optional[List[str]] = None,
        owner: str = "",
        steward: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Adiciona um termo ao glossário.
        
        Args:
            name: Nome do termo
            definition: Definição clara e concisa
            domain: Domínio de negócio
            synonyms: Lista de sinônimos
            related_columns: Colunas relacionadas no banco
            related_tables: Tabelas relacionadas
            examples: Exemplos de uso
            business_rules: Regras de negócio associadas
            owner: Proprietário do termo
            steward: Data steward responsável
            tags: Tags para busca
            metadata: Metadados adicionais
            
        Returns:
            term_id
        """
        term_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT INTO glossary_terms (
                        term_id, name, definition, domain, synonyms,
                        related_columns, related_tables, examples,
                        business_rules, owner, steward, status, tags,
                        metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    term_id, name, definition, domain,
                    json.dumps(synonyms or []),
                    json.dumps(related_columns or []),
                    json.dumps(related_tables or []),
                    json.dumps(examples or []),
                    json.dumps(business_rules or []),
                    owner, steward, TermStatus.DRAFT.value,
                    json.dumps(tags or []),
                    json.dumps(metadata or {}),
                    now, now
                ))
                conn.commit()
                print(f"[GLOSSARY] Termo adicionado: {name}")
            except sqlite3.IntegrityError:
                # Termo já existe
                cursor = conn.execute(
                    "SELECT term_id FROM glossary_terms WHERE name = ?",
                    (name,)
                )
                row = cursor.fetchone()
                if row:
                    return row[0]
        
        return term_id
    
    def get_term(self, name: str) -> Optional[GlossaryTerm]:
        """
        Retorna um termo pelo nome.
        
        Args:
            name: Nome do termo
            
        Returns:
            GlossaryTerm ou None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM glossary_terms WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_term(row)
    
    def search_terms(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        status: Optional[TermStatus] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[GlossaryTerm]:
        """
        Busca termos no glossário.
        
        Args:
            query: Termo de busca (nome, definição, sinônimos)
            domain: Filtrar por domínio
            status: Filtrar por status
            tags: Filtrar por tags
            limit: Limite de resultados
            
        Returns:
            Lista de GlossaryTerm
        """
        sql = "SELECT * FROM glossary_terms WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (name LIKE ? OR definition LIKE ? OR synonyms LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        
        if status:
            sql += " AND status = ?"
            params.append(status.value)
        
        sql += f" ORDER BY name LIMIT {limit}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            terms = [self._row_to_term(row) for row in cursor.fetchall()]
        
        # Filtra por tags se necessário
        if tags:
            terms = [t for t in terms if any(tag in t.tags for tag in tags)]
        
        return terms
    
    def find_terms_for_column(self, column_name: str) -> List[GlossaryTerm]:
        """
        Encontra termos relacionados a uma coluna.
        
        Args:
            column_name: Nome da coluna
            
        Returns:
            Lista de termos relacionados
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM glossary_terms WHERE related_columns LIKE ?",
                (f"%{column_name}%",)
            )
            return [self._row_to_term(row) for row in cursor.fetchall()]
    
    def find_terms_for_table(self, table_name: str) -> List[GlossaryTerm]:
        """
        Encontra termos relacionados a uma tabela.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Lista de termos relacionados
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM glossary_terms WHERE related_tables LIKE ?",
                (f"%{table_name}%",)
            )
            return [self._row_to_term(row) for row in cursor.fetchall()]
    
    def add_relationship(
        self,
        term_name: str,
        related_term_name: str,
        relationship_type: RelationshipType,
        description: str = ""
    ) -> str:
        """
        Adiciona relacionamento entre termos.
        
        Args:
            term_name: Nome do termo principal
            related_term_name: Nome do termo relacionado
            relationship_type: Tipo de relacionamento
            description: Descrição do relacionamento
            
        Returns:
            relationship_id
        """
        term_id = self._get_term_id(term_name)
        related_term_id = self._get_term_id(related_term_name)
        
        if not term_id or not related_term_id:
            raise ValueError(f"Termo não encontrado: {term_name} ou {related_term_name}")
        
        relationship_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO term_relationships (
                    relationship_id, term_id, related_term_id,
                    relationship_type, description, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                relationship_id, term_id, related_term_id,
                relationship_type.value, description, now
            ))
            conn.commit()
        
        print(f"[GLOSSARY] Relacionamento adicionado: {term_name} --{relationship_type.value}--> {related_term_name}")
        
        return relationship_id
    
    def approve_term(self, name: str, approved_by: str) -> bool:
        """
        Aprova um termo no glossário.
        
        Args:
            name: Nome do termo
            approved_by: Quem aprovou
            
        Returns:
            True se aprovado com sucesso
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE glossary_terms 
                SET status = ?, approved_at = ?, approved_by = ?, updated_at = ?
                WHERE name = ?
            """, (TermStatus.APPROVED.value, now, approved_by, now, name))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"[GLOSSARY] Termo aprovado: {name} por {approved_by}")
                return True
        
        return False
    
    def deprecate_term(self, name: str, reason: str = "") -> bool:
        """
        Deprecia um termo no glossário.
        
        Args:
            name: Nome do termo
            reason: Motivo da depreciação
            
        Returns:
            True se depreciado com sucesso
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Registra no histórico
            term_id = self._get_term_id(name)
            if term_id:
                history_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO term_history (
                        history_id, term_id, field_changed,
                        old_value, new_value, changed_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (history_id, term_id, "status", "approved", "deprecated", now))
            
            cursor = conn.execute("""
                UPDATE glossary_terms 
                SET status = ?, updated_at = ?
                WHERE name = ?
            """, (TermStatus.DEPRECATED.value, now, name))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"[GLOSSARY] Termo depreciado: {name}")
                return True
        
        return False
    
    def import_from_yaml(self, yaml_path: str) -> int:
        """
        Importa termos de um arquivo YAML.
        
        Args:
            yaml_path: Caminho para o arquivo YAML
            
        Returns:
            Número de termos importados
        """
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        count = 0
        terms = data.get('business_glossary', {}).get('terms', [])
        
        for term_data in terms:
            self.add_term(
                name=term_data.get('term', ''),
                definition=term_data.get('definition', ''),
                domain=term_data.get('domain', ''),
                synonyms=term_data.get('synonyms', []),
                related_columns=term_data.get('related_columns', []),
                examples=term_data.get('examples', []),
                business_rules=term_data.get('business_rules', [])
            )
            count += 1
        
        print(f"[GLOSSARY] {count} termos importados de {yaml_path}")
        return count
    
    def export_to_yaml(self, yaml_path: str) -> int:
        """
        Exporta termos para um arquivo YAML.
        
        Args:
            yaml_path: Caminho para o arquivo YAML
            
        Returns:
            Número de termos exportados
        """
        terms = self.search_terms(limit=10000)
        
        data = {
            'business_glossary': {
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'terms': []
            }
        }
        
        for term in terms:
            data['business_glossary']['terms'].append({
                'term': term.name,
                'definition': term.definition,
                'domain': term.domain,
                'synonyms': term.synonyms,
                'related_columns': term.related_columns,
                'related_tables': term.related_tables,
                'examples': term.examples,
                'business_rules': term.business_rules,
                'owner': term.owner,
                'steward': term.steward,
                'status': term.status.value,
                'tags': term.tags
            })
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        print(f"[GLOSSARY] {len(terms)} termos exportados para {yaml_path}")
        return len(terms)
    
    def get_domains(self) -> List[str]:
        """
        Retorna lista de domínios no glossário.
        
        Returns:
            Lista de domínios únicos
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT domain FROM glossary_terms WHERE domain != ''"
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_glossary_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do glossário.
        
        Returns:
            Dicionário com estatísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            # Total de termos
            cursor = conn.execute("SELECT COUNT(*) FROM glossary_terms")
            total_terms = cursor.fetchone()[0]
            
            # Por status
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM glossary_terms GROUP BY status
            """)
            by_status = dict(cursor.fetchall())
            
            # Por domínio
            cursor = conn.execute("""
                SELECT domain, COUNT(*) FROM glossary_terms 
                WHERE domain != '' GROUP BY domain
            """)
            by_domain = dict(cursor.fetchall())
            
            # Total de relacionamentos
            cursor = conn.execute("SELECT COUNT(*) FROM term_relationships")
            total_relationships = cursor.fetchone()[0]
            
            # Termos sem definição completa
            cursor = conn.execute("""
                SELECT COUNT(*) FROM glossary_terms 
                WHERE definition = '' OR definition IS NULL
            """)
            incomplete = cursor.fetchone()[0]
        
        return {
            "total_terms": total_terms,
            "by_status": by_status,
            "by_domain": by_domain,
            "total_relationships": total_relationships,
            "incomplete_terms": incomplete,
            "completion_rate": round((total_terms - incomplete) / max(total_terms, 1) * 100, 2)
        }
    
    def validate_consistency(self) -> List[Dict[str, Any]]:
        """
        Valida consistência do glossário.
        
        Returns:
            Lista de problemas encontrados
        """
        issues = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Termos sem definição
            cursor = conn.execute("""
                SELECT name FROM glossary_terms 
                WHERE definition = '' OR definition IS NULL
            """)
            for row in cursor.fetchall():
                issues.append({
                    "type": "missing_definition",
                    "term": row["name"],
                    "severity": "high",
                    "message": f"Termo '{row['name']}' não possui definição"
                })
            
            # Termos sem domínio
            cursor = conn.execute("""
                SELECT name FROM glossary_terms 
                WHERE domain = '' OR domain IS NULL
            """)
            for row in cursor.fetchall():
                issues.append({
                    "type": "missing_domain",
                    "term": row["name"],
                    "severity": "medium",
                    "message": f"Termo '{row['name']}' não possui domínio definido"
                })
            
            # Sinônimos que não existem como termos
            cursor = conn.execute("SELECT name, synonyms FROM glossary_terms")
            all_terms = set()
            for row in cursor.fetchall():
                all_terms.add(row["name"].lower())
            
            cursor = conn.execute("SELECT name, synonyms FROM glossary_terms")
            for row in cursor.fetchall():
                synonyms = json.loads(row["synonyms"]) if row["synonyms"] else []
                for syn in synonyms:
                    if syn.lower() in all_terms and syn.lower() != row["name"].lower():
                        issues.append({
                            "type": "synonym_is_term",
                            "term": row["name"],
                            "severity": "low",
                            "message": f"Sinônimo '{syn}' do termo '{row['name']}' também existe como termo separado"
                        })
        
        return issues
    
    def _row_to_term(self, row: sqlite3.Row) -> GlossaryTerm:
        """Converte uma linha do banco para GlossaryTerm."""
        return GlossaryTerm(
            term_id=row["term_id"],
            name=row["name"],
            definition=row["definition"],
            domain=row["domain"] or "",
            synonyms=json.loads(row["synonyms"]) if row["synonyms"] else [],
            related_columns=json.loads(row["related_columns"]) if row["related_columns"] else [],
            related_tables=json.loads(row["related_tables"]) if row["related_tables"] else [],
            examples=json.loads(row["examples"]) if row["examples"] else [],
            business_rules=json.loads(row["business_rules"]) if row["business_rules"] else [],
            owner=row["owner"] or "",
            steward=row["steward"] or "",
            status=TermStatus(row["status"]) if row["status"] else TermStatus.DRAFT,
            tags=json.loads(row["tags"]) if row["tags"] else [],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            approved_at=datetime.fromisoformat(row["approved_at"]) if row["approved_at"] else None,
            approved_by=row["approved_by"] or ""
        )
    
    def _get_term_id(self, name: str) -> Optional[str]:
        """Obtém ID de um termo pelo nome."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT term_id FROM glossary_terms WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            return row[0] if row else None


# Singleton para acesso global
_business_glossary: Optional[BusinessGlossary] = None


def get_business_glossary(project_id: str = "default") -> BusinessGlossary:
    """
    Retorna instância singleton do BusinessGlossary.
    
    Args:
        project_id: ID do projeto
        
    Returns:
        BusinessGlossary instance
    """
    global _business_glossary
    
    if _business_glossary is None or _business_glossary.project_id != project_id:
        _business_glossary = BusinessGlossary(project_id)
    
    return _business_glossary
