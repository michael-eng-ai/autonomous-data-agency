"""
Knowledge Base Module

Este módulo implementa a Camada 1 do sistema de conhecimento:
- Carrega e gerencia arquivos YAML de conhecimento
- Fornece acesso rápido e determinístico a best practices
- Suporta busca por domínio e tipo de conhecimento

A Knowledge Base é a fonte primária de conhecimento estruturado
para os agentes, garantindo consistência e velocidade.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class KnowledgeItem:
    """Representa um item de conhecimento carregado."""
    domain: str
    type: str
    content: Dict[str, Any]
    file_path: str
    version: str = "1.0.0"


@dataclass
class KnowledgeQuery:
    """Query para buscar conhecimento."""
    domain: Optional[str] = None
    type: Optional[str] = None
    keywords: List[str] = field(default_factory=list)


class KnowledgeBase:
    """
    Gerenciador da Knowledge Base (Camada 1).
    
    Carrega arquivos YAML de conhecimento e fornece
    acesso estruturado para os agentes.
    """
    
    def __init__(self, knowledge_dir: Optional[str] = None):
        """
        Inicializa a Knowledge Base.
        
        Args:
            knowledge_dir: Diretório raiz dos arquivos de conhecimento.
                          Se não fornecido, usa o diretório padrão.
        """
        if knowledge_dir is None:
            # Caminho padrão: projeto/knowledge/
            project_root = Path(__file__).parent.parent.parent
            knowledge_dir = project_root / "knowledge"
        
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self._load_all_knowledge()
    
    def _load_all_knowledge(self) -> None:
        """Carrega todos os arquivos YAML do diretório de conhecimento."""
        if not self.knowledge_dir.exists():
            print(f"[KnowledgeBase] Diretório não encontrado: {self.knowledge_dir}")
            return
        
        for yaml_file in self.knowledge_dir.rglob("*.yaml"):
            self._load_yaml_file(yaml_file)
        
        print(f"[KnowledgeBase] Carregados {len(self.knowledge_items)} arquivos de conhecimento")
    
    def _load_yaml_file(self, file_path: Path) -> None:
        """Carrega um arquivo YAML individual."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if content is None:
                return
            
            # Extrai metadados
            metadata = content.get('metadata', {})
            domain = metadata.get('domain', file_path.parent.name)
            kb_type = metadata.get('type', file_path.stem)
            version = metadata.get('version', '1.0.0')
            
            # Cria o item de conhecimento
            key = f"{domain}/{kb_type}"
            self.knowledge_items[key] = KnowledgeItem(
                domain=domain,
                type=kb_type,
                content=content,
                file_path=str(file_path),
                version=version
            )
            
        except Exception as e:
            print(f"[KnowledgeBase] Erro ao carregar {file_path}: {e}")
    
    def get_knowledge(
        self,
        domain: str,
        knowledge_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém conhecimento por domínio e tipo.
        
        Args:
            domain: Domínio do conhecimento (ex: "data_engineering")
            knowledge_type: Tipo específico (ex: "best_practices")
        
        Returns:
            Conteúdo do conhecimento ou None se não encontrado
        """
        if knowledge_type:
            key = f"{domain}/{knowledge_type}"
            item = self.knowledge_items.get(key)
            return item.content if item else None
        
        # Retorna todos os conhecimentos do domínio
        domain_knowledge = {}
        for key, item in self.knowledge_items.items():
            if item.domain == domain:
                domain_knowledge[item.type] = item.content
        
        return domain_knowledge if domain_knowledge else None
    
    def get_best_practices(self, domain: str) -> Optional[Dict[str, Any]]:
        """Atalho para obter best practices de um domínio."""
        return self.get_knowledge(domain, "best_practices")
    
    def get_checklists(self, domain: str) -> Optional[Dict[str, List[str]]]:
        """Obtém checklists de um domínio."""
        knowledge = self.get_knowledge(domain, "best_practices")
        if knowledge:
            return knowledge.get('checklists', {})
        return None
    
    def get_anti_patterns(self, domain: str) -> Optional[List[Dict[str, str]]]:
        """Obtém anti-patterns de um domínio."""
        knowledge = self.get_knowledge(domain, "best_practices")
        if knowledge:
            return knowledge.get('anti_patterns', [])
        return None
    
    def search(self, query: KnowledgeQuery) -> List[KnowledgeItem]:
        """
        Busca conhecimento baseado em uma query.
        
        Args:
            query: Objeto KnowledgeQuery com critérios de busca
        
        Returns:
            Lista de KnowledgeItems que correspondem à query
        """
        results = []
        
        for item in self.knowledge_items.values():
            # Filtra por domínio
            if query.domain and item.domain != query.domain:
                continue
            
            # Filtra por tipo
            if query.type and item.type != query.type:
                continue
            
            # Filtra por keywords (busca no conteúdo serializado)
            if query.keywords:
                content_str = str(item.content).lower()
                if not all(kw.lower() in content_str for kw in query.keywords):
                    continue
            
            results.append(item)
        
        return results
    
    def format_for_prompt(
        self,
        domain: str,
        sections: Optional[List[str]] = None
    ) -> str:
        """
        Formata o conhecimento de um domínio para inclusão em prompts.
        
        Args:
            domain: Domínio do conhecimento
            sections: Seções específicas para incluir (opcional)
        
        Returns:
            String formatada para inclusão em prompts de LLM
        """
        knowledge = self.get_best_practices(domain)
        if not knowledge:
            return ""
        
        output_parts = [f"# Knowledge Base: {domain.replace('_', ' ').title()}\n"]
        
        # Se seções específicas foram solicitadas
        if sections:
            for section in sections:
                if section in knowledge:
                    output_parts.append(f"\n## {section.replace('_', ' ').title()}\n")
                    output_parts.append(yaml.dump(knowledge[section], default_flow_style=False, allow_unicode=True))
        else:
            # Inclui seções principais
            priority_sections = ['principles', 'checklists', 'anti_patterns']
            for section in priority_sections:
                if section in knowledge:
                    output_parts.append(f"\n## {section.replace('_', ' ').title()}\n")
                    output_parts.append(yaml.dump(knowledge[section], default_flow_style=False, allow_unicode=True))
        
        return "\n".join(output_parts)
    
    def list_domains(self) -> List[str]:
        """Lista todos os domínios disponíveis."""
        return list(set(item.domain for item in self.knowledge_items.values()))
    
    def list_types(self, domain: Optional[str] = None) -> List[str]:
        """Lista todos os tipos de conhecimento, opcionalmente filtrado por domínio."""
        if domain:
            return [item.type for item in self.knowledge_items.values() if item.domain == domain]
        return list(set(item.type for item in self.knowledge_items.values()))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre a Knowledge Base."""
        domains = self.list_domains()
        return {
            "total_items": len(self.knowledge_items),
            "domains": domains,
            "items_per_domain": {
                domain: len([i for i in self.knowledge_items.values() if i.domain == domain])
                for domain in domains
            }
        }


# Singleton para acesso global
_knowledge_base_instance: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    """
    Retorna a instância singleton da Knowledge Base.
    
    Returns:
        Instância da KnowledgeBase
    """
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        _knowledge_base_instance = KnowledgeBase()
    return _knowledge_base_instance


if __name__ == "__main__":
    # Teste da Knowledge Base
    kb = get_knowledge_base()
    
    print("\n=== Estatísticas da Knowledge Base ===")
    stats = kb.get_statistics()
    print(f"Total de itens: {stats['total_items']}")
    print(f"Domínios: {stats['domains']}")
    print(f"Itens por domínio: {stats['items_per_domain']}")
    
    print("\n=== Exemplo: Best Practices de Data Engineering ===")
    de_knowledge = kb.get_best_practices("data_engineering")
    if de_knowledge:
        print(f"Seções disponíveis: {list(de_knowledge.keys())}")
    
    print("\n=== Exemplo: Checklists de QA ===")
    qa_checklists = kb.get_checklists("qa")
    if qa_checklists:
        print(f"Checklists disponíveis: {list(qa_checklists.keys())}")
