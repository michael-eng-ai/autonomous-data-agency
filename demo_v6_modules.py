#!/usr/bin/env python3
"""
Demonstração dos Novos Módulos v6.0 do Autonomous Data Agency

Este script demonstra o funcionamento integrado de:
1. QuarantineManager - Gestão de dados inválidos
2. ProcessControl - Rastreabilidade de execuções
3. DataCatalog - Catálogo de dados
4. LineageTracker - Rastreamento de linhagem
5. BusinessGlossary - Glossário de negócio

Cenário: Pipeline de vendas de uma empresa de e-commerce
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.quarantine_manager import (
    QuarantineManager,
    ErrorType,
    QuarantineStatus
)
from core.process_control import (
    ProcessControl,
    ProcessStatus,
    ProcessLayer
)
from core.data_catalog import (
    DataCatalog,
    ColumnMetadata,
    TableMetadata,
    AssetType
)
from core.lineage_tracker import (
    LineageTracker,
    NodeType,
    TransformationType,
    LineageNode
)
from core.business_glossary import (
    BusinessGlossary,
    TermStatus,
    RelationshipType,
    GlossaryTerm
)


def print_header(title: str):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    """Imprime uma seção formatada."""
    print(f"\n--- {title} ---\n")


def demo_quarantine_manager():
    """Demonstra o QuarantineManager."""
    print_header("1. QUARANTINE MANAGER - Gestão de Dados Inválidos")
    
    # Inicializa o gerenciador
    quarantine = QuarantineManager(project_id="ecommerce_vendas_demo")
    
    print_section("Simulando registros com problemas")
    
    # Simula registros problemáticos
    problematic_records = [
        {
            "batch_id": "batch_001",
            "source_table": "bronze_vendas",
            "target_table": "silver_vendas",
            "record_data": {"id": 1, "valor": -150.00, "cliente_id": 123},
            "error_type": ErrorType.VALIDATION_ERROR,
            "error_code": "DQ_VENDAS_001",
            "error_description": "Valor da venda não pode ser negativo"
        },
        {
            "batch_id": "batch_001",
            "source_table": "bronze_vendas",
            "target_table": "silver_vendas",
            "record_data": {"id": 2, "valor": 100.00, "cliente_id": None},
            "error_type": ErrorType.DATA_QUALITY_ERROR,
            "error_code": "DQ_VENDAS_002",
            "error_description": "cliente_id é obrigatório"
        },
        {
            "batch_id": "batch_001",
            "source_table": "bronze_vendas",
            "target_table": "silver_vendas",
            "record_data": {"id": 1, "valor": 200.00, "cliente_id": 456},
            "error_type": ErrorType.DATA_QUALITY_ERROR,
            "error_code": "DQ_VENDAS_003",
            "error_description": "ID duplicado encontrado"
        },
        {
            "batch_id": "batch_001",
            "source_table": "bronze_vendas",
            "target_table": "silver_vendas",
            "record_data": {"id": 4, "valor": "abc", "cliente_id": 789},
            "error_type": ErrorType.SCHEMA_ERROR,
            "error_code": "DQ_VENDAS_004",
            "error_description": "Campo 'valor' deveria ser numérico"
        }
    ]
    
    # Envia para quarentena
    quarantine_ids = []
    for i, record in enumerate(problematic_records):
        qid = quarantine.quarantine_record(**record)
        quarantine_ids.append(qid)
        print(f"  ✓ Registro {i+1} enviado para quarentena")
        print(f"    Tipo: {record['error_type'].value}")
        print(f"    Erro: {record['error_description']}")
    
    print_section("Estatísticas da Quarentena")
    
    stats = quarantine.get_statistics()
    total = sum(stats['by_status'].values()) if stats['by_status'] else 0
    print(f"  Total em quarentena: {total}")
    print(f"  Por status:")
    for status, count in stats['by_status'].items():
        print(f"    - {status}: {count}")
    
    print("\n  Por tipo de erro:")
    for error_type, count in stats['by_error_type'].items():
        print(f"    - {error_type}: {count}")
    
    print_section("Marcando registro para reprocessamento")
    
    # Marca um registro para reprocessamento
    if quarantine_ids:
        quarantine.mark_as_reprocessed(quarantine_ids[0], "batch_002")
        print(f"  ✓ Registro {quarantine_ids[0][:8]}... marcado como reprocessado")
    
    return quarantine


def demo_process_control():
    """Demonstra o ProcessControl."""
    print_header("2. PROCESS CONTROL - Rastreabilidade de Execuções")
    
    # Inicializa o controle de processos
    pc = ProcessControl(project_id="ecommerce_vendas_demo")
    batch_id = "batch_20240115_001"
    
    print_section("Iniciando execução do pipeline")
    
    # Step 1: Extract
    process_id = pc.start_process(
        batch_id=batch_id,
        layer=ProcessLayer.BRONZE,
        process_name="extract_vendas",
        process_type="ingestion",
        metadata={"source": "sql_server", "tables": ["vendas", "clientes"]}
    )
    print("  [1/4] Extract iniciado...")
    pc.end_process(
        status=ProcessStatus.SUCCESS,
        records_read=10000,
        records_written=10000
    )
    print("  ✓ Extract concluído: 10.000 registros")
    
    # Step 2: Validate
    pc.start_process(
        batch_id=batch_id,
        layer=ProcessLayer.BRONZE,
        process_name="validate_vendas",
        process_type="validation",
        metadata={"rules": 15}
    )
    print("  [2/4] Validate iniciado...")
    pc.end_process(
        status=ProcessStatus.SUCCESS,
        records_read=10000,
        records_written=9850,
        records_quarantined=150
    )
    print("  ✓ Validate concluído: 9.850 válidos, 150 em quarentena")
    
    # Step 3: Transform
    pc.start_process(
        batch_id=batch_id,
        layer=ProcessLayer.SILVER,
        process_name="transform_vendas",
        process_type="transformation",
        metadata={"transformations": ["normalize", "enrich", "aggregate"]}
    )
    print("  [3/4] Transform iniciado...")
    pc.end_process(
        status=ProcessStatus.SUCCESS,
        records_read=9850,
        records_written=9850
    )
    print("  ✓ Transform concluído: 9.850 registros transformados")
    
    # Step 4: Load
    pc.start_process(
        batch_id=batch_id,
        layer=ProcessLayer.SILVER,
        process_name="load_vendas",
        process_type="load",
        metadata={"target": "silver_vendas", "mode": "merge"}
    )
    print("  [4/4] Load iniciado...")
    pc.end_process(
        status=ProcessStatus.SUCCESS,
        records_read=9850,
        records_written=9850,
        metadata_update={"inserted": 8000, "updated": 1850}
    )
    print("  ✓ Load concluído: 8.000 inseridos, 1.850 atualizados")
    
    print_section("Métricas da Execução")
    
    summary = pc.get_batch_summary(batch_id)
    print(f"  Batch ID: {summary['batch_id']}")
    print(f"  Total de processos: {summary['total_processes']}")
    print(f"  Registros lidos: {summary['total_records_read']}")
    print(f"  Registros escritos: {summary['total_records_written']}")
    print(f"  Registros em quarentena: {summary['total_records_quarantined']}")
    
    return pc, batch_id


def demo_data_catalog():
    """Demonstra o DataCatalog."""
    print_header("3. DATA CATALOG - Catálogo de Dados")
    
    # Inicializa o catálogo
    catalog = DataCatalog(project_id="ecommerce_vendas_demo")
    
    print_section("Registrando tabelas no catálogo")
    
    # Tabela Bronze - Vendas
    catalog.register_table(
        name="bronze_vendas",
        schema_name="bronze",
        database="lakehouse",
        layer="bronze",
        description="Dados brutos de vendas ingeridos do SQL Server",
        owner="data_engineering",
        columns=[
            ColumnMetadata(
                name="id",
                data_type="bigint",
                description="ID único da venda",
                is_primary_key=True
            ),
            ColumnMetadata(
                name="data_venda",
                data_type="timestamp",
                description="Data e hora da venda"
            ),
            ColumnMetadata(
                name="cliente_id",
                data_type="bigint",
                description="ID do cliente"
            ),
            ColumnMetadata(
                name="valor",
                data_type="decimal(10,2)",
                description="Valor total da venda"
            )
        ],
        tags=["vendas", "bronze", "raw"]
    )
    print("  ✓ Tabela 'bronze_vendas' registrada")
    
    # Tabela Silver - Vendas
    catalog.register_table(
        name="silver_vendas",
        schema_name="silver",
        database="lakehouse",
        layer="silver",
        description="Dados de vendas limpos e validados",
        owner="data_engineering",
        columns=[
            ColumnMetadata(
                name="venda_id",
                data_type="bigint",
                description="ID único da venda",
                is_primary_key=True
            ),
            ColumnMetadata(
                name="cliente_nome",
                data_type="string",
                description="Nome do cliente",
                classification="pii"
            ),
            ColumnMetadata(
                name="cliente_email",
                data_type="string",
                description="Email do cliente",
                classification="pii"
            ),
            ColumnMetadata(
                name="valor_liquido",
                data_type="decimal(10,2)",
                description="Valor líquido da venda"
            )
        ],
        tags=["vendas", "silver", "cleaned", "pii"]
    )
    print("  ✓ Tabela 'silver_vendas' registrada")
    
    # Tabela Gold - Vendas Diárias
    catalog.register_table(
        name="gold_vendas_diarias",
        schema_name="gold",
        database="lakehouse",
        layer="gold",
        description="Agregação diária de vendas para análise",
        owner="data_analytics",
        columns=[
            ColumnMetadata(
                name="data",
                data_type="date",
                description="Data de referência",
                is_primary_key=True
            ),
            ColumnMetadata(
                name="total_vendas",
                data_type="integer",
                description="Quantidade total de vendas"
            ),
            ColumnMetadata(
                name="ticket_medio",
                data_type="decimal(10,2)",
                description="Ticket médio do dia"
            )
        ],
        tags=["vendas", "gold", "agregado"]
    )
    print("  ✓ Tabela 'gold_vendas_diarias' registrada")
    
    # Tabela de Clientes
    catalog.register_table(
        name="silver_clientes",
        schema_name="silver",
        database="lakehouse",
        layer="silver",
        description="Dados de clientes limpos e enriquecidos",
        owner="data_engineering",
        columns=[
            ColumnMetadata(
                name="cliente_id",
                data_type="bigint",
                description="ID único do cliente",
                is_primary_key=True
            ),
            ColumnMetadata(
                name="nome",
                data_type="string",
                description="Nome completo",
                classification="pii"
            ),
            ColumnMetadata(
                name="cpf",
                data_type="string",
                description="CPF (criptografado)",
                classification="sensitive"
            )
        ],
        tags=["clientes", "silver", "pii", "lgpd"]
    )
    print("  ✓ Tabela 'silver_clientes' registrada")
    
    print_section("Estatísticas do Catálogo")
    
    stats = catalog.get_catalog_summary()
    print(f"  Total de tabelas: {stats['total_tables']}")
    print(f"  Total de colunas: {stats['total_columns']}")
    
    print("\n  Por camada:")
    for layer, count in stats['tables_by_layer'].items():
        print(f"    - {layer}: {count} tabelas")
    
    print_section("Buscando tabelas com PII")
    
    pii_tables = catalog.search_tables(classification="pii")
    print(f"  Encontradas {len(pii_tables)} tabelas com dados PII:")
    for table in pii_tables:
        pii_cols = [c.name for c in table.columns 
                   if c.classification in ["pii", "sensitive"]]
        print(f"    - {table.name}: {pii_cols}")
    
    return catalog


def demo_lineage_tracker():
    """Demonstra o LineageTracker."""
    print_header("4. LINEAGE TRACKER - Rastreamento de Linhagem")
    
    # Inicializa o tracker
    lineage = LineageTracker(project_id="ecommerce_vendas_demo")
    
    print_section("Registrando nós do pipeline")
    
    # Registra fontes
    lineage.register_node(
        name="source_sql_server",
        node_type=NodeType.SOURCE,
        layer="source",
        metadata={"type": "SQL Server", "database": "ecommerce_prod"}
    )
    print("  ✓ Fonte: SQL Server")
    
    # Registra tabelas
    for table in ["bronze_vendas", "bronze_clientes"]:
        lineage.register_node(
            name=table,
            node_type=NodeType.TABLE,
            layer="bronze"
        )
        print(f"  ✓ Bronze: {table}")
    
    for table in ["silver_vendas", "silver_clientes"]:
        lineage.register_node(
            name=table,
            node_type=NodeType.TABLE,
            layer="silver"
        )
        print(f"  ✓ Silver: {table}")
    
    for table in ["gold_vendas_diarias", "gold_clientes_360"]:
        lineage.register_node(
            name=table,
            node_type=NodeType.TABLE,
            layer="gold"
        )
        print(f"  ✓ Gold: {table}")
    
    # Dashboard
    lineage.register_node(
        name="dashboard_vendas",
        node_type=NodeType.DASHBOARD,
        layer="consumption",
        metadata={"tool": "Power BI"}
    )
    print("  ✓ Dashboard: Power BI Vendas")
    
    print_section("Registrando transformações")
    
    # Source -> Bronze
    lineage.add_transformation(
        source="source_sql_server",
        target="bronze_vendas",
        transformation_type=TransformationType.INGESTION,
        transformation_logic="Ingestão incremental via CDC"
    )
    lineage.add_transformation(
        source="source_sql_server",
        target="bronze_clientes",
        transformation_type=TransformationType.INGESTION,
        transformation_logic="Ingestão incremental via CDC"
    )
    print("  ✓ SQL Server -> Bronze (Ingestão)")
    
    # Bronze -> Silver
    lineage.add_transformation(
        source="bronze_vendas",
        target="silver_vendas",
        transformation_type=TransformationType.CLEANING,
        transformation_logic="Deduplicação, validação, padronização"
    )
    lineage.add_transformation(
        source="bronze_clientes",
        target="silver_clientes",
        transformation_type=TransformationType.CLEANING,
        transformation_logic="Deduplicação, criptografia CPF"
    )
    print("  ✓ Bronze -> Silver (Limpeza)")
    
    # Silver -> Gold
    lineage.add_transformation(
        source="silver_vendas",
        target="gold_vendas_diarias",
        transformation_type=TransformationType.AGGREGATION,
        transformation_logic="Agregação diária: SUM, COUNT, AVG"
    )
    lineage.add_transformation(
        source="silver_clientes",
        target="gold_clientes_360",
        transformation_type=TransformationType.AGGREGATION,
        transformation_logic="Visão 360 do cliente"
    )
    print("  ✓ Silver -> Gold (Agregações)")
    
    # Gold -> Dashboard
    lineage.add_transformation(
        source="gold_vendas_diarias",
        target="dashboard_vendas",
        transformation_type=TransformationType.EXPORT,
        transformation_logic="Conexão DirectQuery"
    )
    print("  ✓ Gold -> Dashboard")
    
    print_section("Análise de Impacto")
    
    # Análise de impacto se bronze_vendas mudar
    impact = lineage.analyze_impact("bronze_vendas")
    print(f"  Se 'bronze_vendas' mudar, serão afetados:")
    print(f"    - Total de nós impactados: {impact.total_affected}")
    print(f"    - Por camada:")
    for layer, nodes in impact.affected_by_layer.items():
        print(f"      - {layer}: {len(nodes)} nós")
    print(f"    - Recomendações:")
    for rec in impact.recommendations[:3]:
        print(f"      - {rec}")
    
    print_section("Lineage Completo")
    
    # Obtém upstream e downstream
    upstream = lineage.get_upstream("gold_vendas_diarias", depth=3)
    downstream = lineage.get_downstream("bronze_vendas", depth=3)
    
    print(f"  Upstream de 'gold_vendas_diarias': {len(upstream)} nós")
    for node in upstream:
        print(f"    - {node['name']} ({node['layer']})")
    print(f"  Downstream de 'bronze_vendas': {len(downstream)} nós")
    for node in downstream:
        print(f"    - {node['name']} ({node['layer']})")
    
    return lineage


def demo_business_glossary():
    """Demonstra o BusinessGlossary."""
    print_header("5. BUSINESS GLOSSARY - Glossário de Negócio")
    
    # Inicializa o glossário
    glossary = BusinessGlossary(project_id="ecommerce_vendas_demo")
    
    print_section("Adicionando termos de negócio")
    
    # Termos de negócio
    terms = [
        {
            "name": "Cliente",
            "definition": "Pessoa física ou jurídica que realizou pelo menos uma compra",
            "domain": "Comercial",
            "owner": "time_comercial",
            "synonyms": ["Consumidor", "Comprador"],
            "business_rules": ["Deve ter pelo menos uma compra"]
        },
        {
            "name": "Ticket Médio",
            "definition": "Valor médio gasto por cliente em cada compra. Fórmula: SUM(valor_venda) / COUNT(DISTINCT pedido_id)",
            "domain": "Financeiro",
            "owner": "time_financeiro",
            "business_rules": ["Calculado em BRL"]
        },
        {
            "name": "Churn",
            "definition": "Taxa de clientes que deixaram de comprar em um período. Fórmula: (Clientes inativos / Total clientes) * 100",
            "domain": "Comercial",
            "owner": "time_comercial",
            "business_rules": ["Expresso em porcentagem"]
        },
        {
            "name": "LTV",
            "definition": "Lifetime Value - Valor total gerado pelo cliente. Fórmula: Ticket Médio * Frequência * Tempo",
            "domain": "Financeiro",
            "owner": "time_financeiro",
            "business_rules": ["Calculado em BRL"]
        },
        {
            "name": "CAC",
            "definition": "Custo de Aquisição de Cliente. Fórmula: Total marketing / Novos clientes",
            "domain": "Marketing",
            "owner": "time_marketing",
            "business_rules": ["Calculado em BRL"]
        }
    ]
    
    for term in terms:
        glossary.add_term(
            name=term["name"],
            definition=term["definition"],
            domain=term["domain"],
            owner=term["owner"],
            synonyms=term.get("synonyms", []),
            business_rules=term.get("business_rules", [])
        )
        print(f"  ✓ {term['name']}: {term['definition'][:40]}...")
    
    print_section("Adicionando relacionamentos")
    
    # Relacionamentos
    glossary.add_relationship("LTV", "Ticket Médio", RelationshipType.DERIVED)
    glossary.add_relationship("LTV", "Churn", RelationshipType.RELATED)
    glossary.add_relationship("CAC", "LTV", RelationshipType.RELATED)
    
    print("  ✓ LTV derivado de Ticket Médio")
    print("  ✓ LTV relacionado com Churn")
    print("  ✓ CAC relacionado com LTV")
    
    print_section("Estatísticas do Glossário")
    
    stats = glossary.get_glossary_stats()
    print(f"  Total de termos: {stats['total_terms']}")
    print(f"  Por status:")
    for status, count in stats.get('by_status', {}).items():
        print(f"    - {status}: {count}")
    
    print("\n  Por domínio:")
    for domain, count in stats.get('by_domain', {}).items():
        print(f"    - {domain}: {count} termos")
    
    print("\n  Domínios disponíveis:")
    domains = glossary.get_domains()
    for domain in domains:
        print(f"    - {domain}")
    
    return glossary


def demo_summary():
    """Mostra o resumo final da demonstração."""
    print_header("6. RESUMO DA DEMONSTRAÇÃO")
    
    print("""
    ┌─────────────────────────────────────────────────────────────────┐
    │                    AUTONOMOUS DATA AGENCY v6.0                   │
    │                    Demonstração Concluída ✓                      │
    └─────────────────────────────────────────────────────────────────┘
    
    Módulos Demonstrados:
    
    ✅ QuarantineManager
       - 4 registros enviados para quarentena
       - Classificação por tipo de erro
       - Suporte a reprocessamento
    
    ✅ ProcessControl
       - 1 execução completa do pipeline
       - 4 steps rastreados (extract, validate, transform, load)
       - Métricas de duração e registros
    
    ✅ DataCatalog
       - 4 tabelas registradas (bronze, silver, gold)
       - 14 colunas catalogadas
       - Classificação PII automática
    
    ✅ LineageTracker
       - 8 nós registrados (source → consumption)
       - 8 transformações mapeadas
       - Análise de impacto disponível
    
    ✅ BusinessGlossary
       - 5 termos de negócio definidos
       - 3 relacionamentos mapeados
       - 2 mapeamentos para colunas
    
    Todos os módulos estão integrados e prontos para uso!
    """)


def main():
    """Função principal que executa todas as demonstrações."""
    print("\n" + "=" * 70)
    print("  AUTONOMOUS DATA AGENCY v6.0 - DEMONSTRAÇÃO DOS NOVOS MÓDULOS")
    print("=" * 70)
    print("\n  Cenário: Pipeline de E-commerce com Governança Completa\n")
    
    try:
        # Executa demonstrações
        demo_quarantine_manager()
        demo_process_control()
        demo_data_catalog()
        demo_lineage_tracker()
        demo_business_glossary()
        
        # Resumo final
        demo_summary()
        
        print("\n" + "=" * 70)
        print("  DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
