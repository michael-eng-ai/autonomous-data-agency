#!/usr/bin/env python3
"""
Script de Teste do Sistema de Conhecimento

Este script demonstra as 3 camadas do sistema de conhecimento:
1. Knowledge Base (YAML) - Best practices estáticas
2. RAG Engine (ChromaDB) - Busca semântica
3. Project Memory (SQLite) - Memória persistente

Execute com: python test_knowledge_system.py
"""

import os
import sys

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime


def print_header(title: str) -> None:
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str) -> None:
    """Imprime uma seção formatada."""
    print(f"\n--- {title} ---\n")


def test_knowledge_base():
    """Testa a Camada 1: Knowledge Base (YAML)."""
    print_header("CAMADA 1: KNOWLEDGE BASE (YAML)")
    
    # Import direto do módulo de conhecimento
    from core.knowledge.knowledge_base import get_knowledge_base
    
    kb = get_knowledge_base()
    
    # Lista domínios disponíveis
    print_section("Domínios Disponíveis")
    domains = kb.list_domains()
    for domain in domains:
        print(f"  ✓ {domain}")
    
    # Carrega best practices de Data Engineering
    print_section("Best Practices de Data Engineering")
    de_practices = kb.get_best_practices("data_engineering")
    
    if de_practices:
        # Mostra princípios
        if "principles" in de_practices:
            print("Princípios:")
            for i, principle in enumerate(de_practices["principles"][:3], 1):
                print(f"  {i}. {principle.get('name', 'N/A')}")
                if "guidelines" in principle:
                    for g in principle["guidelines"][:2]:
                        print(f"     - {g}")
        
        # Mostra anti-patterns
        if "anti_patterns" in de_practices:
            print("\nAnti-Patterns:")
            for ap in de_practices["anti_patterns"][:3]:
                print(f"  ⚠ {ap.get('name', 'N/A')}: {ap.get('description', 'N/A')[:60]}...")
    
    # Testa formatação para prompt
    print_section("Contexto Formatado para Prompt")
    context = kb.format_for_prompt("data_engineering", sections=["principles", "anti_patterns"])
    print(context[:500] + "..." if len(context) > 500 else context)
    
    return True


def test_rag_engine():
    """Testa a Camada 2: RAG Engine (ChromaDB)."""
    print_header("CAMADA 2: RAG ENGINE (ChromaDB)")
    
    from core.knowledge.rag_engine import get_rag_engine, Document
    from core.knowledge.knowledge_base import get_knowledge_base
    
    rag = get_rag_engine()
    
    # Verifica disponibilidade
    print_section("Status do RAG Engine")
    print(f"  ✓ RAG Engine disponível: {rag.is_available()}")
    
    if rag.is_available():
        # Indexa a Knowledge Base
        print_section("Indexando Knowledge Base no RAG")
        kb = get_knowledge_base()
        indexed = rag.index_knowledge_base(kb)
        print(f"  ✓ Documentos indexados: {indexed}")
        
        # Adiciona documentos de exemplo
        print_section("Adicionando Documentos de Exemplo")
        docs = [
            Document(
                id="doc_airflow_001",
                content="Apache Airflow é uma plataforma de orquestração de workflows. "
                        "Permite criar, agendar e monitorar pipelines de dados programaticamente. "
                        "Use DAGs (Directed Acyclic Graphs) para definir dependências entre tarefas.",
                metadata={"domain": "data_engineering", "topic": "orchestration", "source": "docs"}
            ),
            Document(
                id="doc_dbt_001",
                content="dbt (data build tool) é uma ferramenta de transformação de dados. "
                        "Permite escrever transformações em SQL e gerenciar dependências. "
                        "Ideal para a camada de transformação em arquiteturas ELT.",
                metadata={"domain": "data_engineering", "topic": "transformation", "source": "docs"}
            ),
            Document(
                id="doc_mlflow_001",
                content="MLflow é uma plataforma open-source para gerenciar o ciclo de vida de ML. "
                        "Inclui tracking de experimentos, empacotamento de modelos e deployment. "
                        "Integra-se com frameworks populares como TensorFlow, PyTorch e scikit-learn.",
                metadata={"domain": "data_science", "topic": "mlops", "source": "docs"}
            ),
        ]
        
        for doc in docs:
            rag.add_document(doc)
            print(f"  ✓ Adicionado: {doc.id}")
        
        # Testa busca semântica
        print_section("Teste de Busca Semântica")
        queries = [
            "como orquestrar pipelines de dados",
            "ferramentas para transformação de dados",
            "gerenciamento de modelos de machine learning"
        ]
        
        for query in queries:
            print(f"\nQuery: \"{query}\"")
            results = rag.search(query, n_results=2)
            for r in results:
                print(f"  → Score: {r.relevance_score:.2%} | {r.content[:60]}...")
    else:
        print("  ⚠ ChromaDB não disponível. Pulando testes de RAG.")
    
    return True


def test_project_memory():
    """Testa a Camada 3: Project Memory (SQLite)."""
    print_header("CAMADA 3: PROJECT MEMORY (SQLite)")
    
    from core.knowledge.project_memory import get_project_memory, MemoryType
    
    memory = get_project_memory()
    
    # Cria um projeto de teste
    print_section("Criando Projeto de Teste")
    project_id = f"test_proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    memory.create_project(
        project_id=project_id,
        name="Sistema de Análise de Clientes",
        client_name="Empresa Demo"
    )
    print(f"  ✓ Projeto criado: {project_id}")
    
    # Armazena decisões
    print_section("Armazenando Decisões")
    decisions = [
        {
            "key": "database_choice",
            "decision": "PostgreSQL",
            "rationale": "Melhor suporte a JSON, extensibilidade e comunidade ativa",
            "alternatives": ["MySQL", "MongoDB", "SQLite"]
        },
        {
            "key": "orchestration_tool",
            "decision": "Apache Airflow",
            "rationale": "Padrão de mercado, boa documentação, integração com cloud",
            "alternatives": ["Prefect", "Dagster", "Luigi"]
        },
        {
            "key": "cloud_provider",
            "decision": "AWS",
            "rationale": "Cliente já possui conta AWS, equipe tem experiência",
            "alternatives": ["GCP", "Azure"]
        }
    ]
    
    for d in decisions:
        memory.store_decision(
            project_id=project_id,
            decision_key=d["key"],
            decision=d["decision"],
            rationale=d["rationale"],
            alternatives=d["alternatives"]
        )
        print(f"  ✓ Decisão armazenada: {d['key']} = {d['decision']}")
    
    # Armazena preferências do cliente
    print_section("Armazenando Preferências do Cliente")
    preferences = {
        "communication_channel": "WhatsApp",
        "report_frequency": "semanal",
        "preferred_language": "Python",
        "budget_constraint": "médio"
    }
    
    for key, value in preferences.items():
        memory.store(
            project_id=project_id,
            memory_type=MemoryType.PREFERENCE,
            key=key,
            value=value
        )
        print(f"  ✓ Preferência armazenada: {key} = {value}")
    
    # Armazena interações
    print_section("Armazenando Interações")
    memory.store_interaction(
        project_id=project_id,
        interaction_type="requirements_gathering",
        content="Cliente solicitou sistema de análise de clientes com recomendações automáticas",
        participants=["PO Team", "Cliente"]
    )
    memory.store_interaction(
        project_id=project_id,
        interaction_type="architecture_review",
        content="Time de Data Engineering propôs arquitetura com Airflow + dbt + PostgreSQL",
        participants=["Data Engineering Team", "DevOps Team"]
    )
    print("  ✓ Interações armazenadas")
    
    # Recupera contexto do projeto
    print_section("Contexto do Projeto (Formatado para Prompt)")
    context = memory.format_context_for_prompt(project_id)
    print(context)
    
    # Verifica se o projeto foi criado corretamente
    print_section("Verificando Projeto Criado")
    project = memory.get_project(project_id)
    if project:
        print(f"  ✓ Projeto encontrado: {project['name']}")
        print(f"    Cliente: {project['client_name']}")
        print(f"    Status: {project['status']}")
    else:
        print("  ✗ Projeto não encontrado")
    
    return True


def test_knowledge_manager():
    """Testa o Knowledge Manager (integração das 3 camadas)."""
    print_header("KNOWLEDGE MANAGER (INTEGRAÇÃO)")
    
    from core.knowledge import get_knowledge_manager
    
    km = get_knowledge_manager()
    
    print_section("Status do Sistema de Conhecimento")
    print(f"  ✓ Knowledge Base: {km.knowledge_base is not None}")
    print(f"  ✓ RAG Engine: {km.rag_engine is not None and km.rag_engine.is_available()}")
    print(f"  ✓ Project Memory: {km.project_memory is not None}")
    
    # Testa obtenção de conhecimento unificado
    print_section("Conhecimento Unificado para Agente")
    context = km.get_knowledge_for_agent(
        domain="data_engineering",
        task="Projetar arquitetura de dados para sistema de recomendação",
        project_id=None  # Sem projeto específico
    )
    
    print("Contexto gerado:")
    print("-" * 50)
    # Mostra apenas os primeiros 800 caracteres
    print(context[:800] + "..." if len(context) > 800 else context)
    
    return True


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("  TESTE DO SISTEMA DE CONHECIMENTO - AUTONOMOUS DATA AGENCY")
    print("=" * 70)
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    tests = [
        ("Knowledge Base (YAML)", test_knowledge_base),
        ("RAG Engine (ChromaDB)", test_rag_engine),
        ("Project Memory (SQLite)", test_project_memory),
        ("Knowledge Manager", test_knowledge_manager),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "✓ PASSOU" if success else "✗ FALHOU"))
        except Exception as e:
            print(f"\n  ✗ ERRO: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, f"✗ ERRO: {str(e)[:50]}"))
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    for name, result in results:
        print(f"  {result} - {name}")
    
    print("\n" + "=" * 70)
    print("  TESTE CONCLUÍDO")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
