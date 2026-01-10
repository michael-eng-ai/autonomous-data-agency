# Autonomous Data Agency Framework v6.0

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Um framework avançado para criar agências autônomas de dados usando múltiplos times de agentes de IA com LLMs diversos, **governança e LGPD integrados**, sistema de conhecimento em 3 camadas, validação anti-alucinação robusta, **data quality**, **observabilidade e FinOps**, **data catalog**, **lineage tracking** e **business glossary**.

## 🌟 Novidades da v6.0

- **QuarantineManager**: Gestão de dados inválidos com isolamento e reprocessamento
- **ProcessControl**: Rastreabilidade completa de execuções com checkpoints
- **GovernancePolicies**: Políticas de governança versionáveis em YAML
- **DataCatalog**: Catálogo de dados com integração OpenMetadata
- **LineageTracker**: Rastreamento de linhagem de dados com análise de impacto
- **BusinessGlossary**: Glossário de negócio padronizado com termos e relacionamentos

## 📁 Arquitetura Completa

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AUTONOMOUS DATA AGENCY                             │
│                              Framework v6.0                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│  GOVERNANÇA   │          │ OBSERVABILITY │          │   WORKFLOW    │
│  & LGPD 🛡️   │          │  & FINOPS 📊  │          │  INTEGRADO    │
└───────────────┘          └───────────────┘          └───────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ DATA CATALOG  │          │   LINEAGE     │          │   BUSINESS    │
│     📚        │          │   TRACKER 🔗  │          │   GLOSSARY 📖 │
└───────────────┘          └───────────────┘          └───────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│  QUARANTINE   │          │   PROCESS     │          │  GOVERNANCE   │
│  MANAGER 🔒   │          │   CONTROL ⚙️  │          │  POLICIES 📋  │
└───────────────┘          └───────────────┘          └───────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
             ┌───────────┐    ┌───────────┐    ┌───────────┐
             │    PO     │    │    PM     │    │   ARCH    │
             │   Team    │───▶│   Team    │───▶│   Team    │
             └───────────┘    └───────────┘    └───────────┘
                                                     │
                    ┌────────────────┬───────────────┼───────────────┐
                    │                │               │               │
                    ▼                ▼               ▼               ▼
             ┌───────────┐    ┌───────────┐   ┌───────────┐   ┌───────────┐
             │ Data Eng  │    │  DevOps   │   │Data Science│   │    QA     │
             │   Team    │    │   Team    │   │   Team    │   │   Team    │
             └───────────┘    └───────────┘   └───────────┘   └───────────┘
```

## 🔒 QuarantineManager (NEW v6.0)

Sistema de gestão de dados inválidos inspirado no projeto ABInBev:

### Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Isolamento** | Separa registros problemáticos sem bloquear o pipeline |
| **Classificação** | Categoriza erros (validação, schema, duplicata, etc.) |
| **Reprocessamento** | Permite reprocessar registros após correção |
| **Alertas** | Notifica sobre novos tipos de erros |
| **Estatísticas** | Dashboard de quarentena por período |

### Uso

```python
from core import get_quarantine_manager, QuarantineReason

quarantine = get_quarantine_manager(project_id="meu_projeto")

# Envia registro para quarentena
quarantine.quarantine_record(
    record_id="rec_001",
    source_table="bronze_vendas",
    target_table="silver_vendas",
    record_data={"id": 1, "valor": -100, "data": "2024-01-01"},
    reason=QuarantineReason.VALIDATION_FAILED,
    error_details="Valor não pode ser negativo",
    pipeline_name="vendas_pipeline",
    step_name="validacao_valores"
)

# Obtém estatísticas
stats = quarantine.get_stats()
print(f"Total em quarentena: {stats.total_quarantined}")
print(f"Pendentes: {stats.pending}")
print(f"Reprocessados: {stats.reprocessed}")

# Lista registros por razão
records = quarantine.get_records_by_reason(QuarantineReason.VALIDATION_FAILED)

# Marca para reprocessamento
quarantine.mark_for_reprocessing("rec_001", notes="Valor corrigido")

# Reprocessa registros pendentes
reprocessed = quarantine.reprocess_pending(
    callback=lambda record: process_record(record)
)
```

## ⚙️ ProcessControl (NEW v6.0)

Rastreabilidade completa de execuções:

### Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Execuções** | Registro de início, fim e status de cada execução |
| **Steps** | Checkpoints dentro de cada execução |
| **Métricas** | Duração, registros processados, erros |
| **Histórico** | Auditoria completa de todas as execuções |
| **Retry** | Suporte a reexecução de steps falhos |

### Uso

```python
from core import get_process_control, ExecutionStatus

pc = get_process_control(project_id="meu_projeto")

# Inicia execução
execution_id = pc.start_execution(
    pipeline_name="vendas_pipeline",
    triggered_by="scheduler",
    parameters={"date": "2024-01-01"}
)

# Registra steps
pc.start_step(execution_id, "extract", {"source": "sql_server"})
pc.complete_step(execution_id, "extract", records_processed=10000)

pc.start_step(execution_id, "transform", {"rules": 15})
pc.complete_step(execution_id, "transform", records_processed=9500)

pc.start_step(execution_id, "load", {"target": "silver"})
pc.complete_step(execution_id, "load", records_processed=9500)

# Finaliza execução
pc.complete_execution(execution_id)

# Obtém métricas
metrics = pc.get_execution_metrics(execution_id)
print(f"Duração total: {metrics.total_duration_seconds}s")
print(f"Registros processados: {metrics.total_records_processed}")

# Histórico de execuções
history = pc.get_execution_history(
    pipeline_name="vendas_pipeline",
    limit=10
)
```

## 📋 GovernancePolicies (NEW v6.0)

Políticas de governança versionáveis em YAML:

### Estrutura do YAML

```yaml
# config/governance_policies.yaml
version: "1.0"
last_updated: "2024-01-01"

data_classification:
  levels:
    - name: public
      description: Dados públicos
      encryption_required: false
      access_logging: false
    - name: internal
      description: Dados internos
      encryption_required: false
      access_logging: true
    - name: confidential
      description: Dados confidenciais
      encryption_required: true
      access_logging: true
    - name: restricted
      description: Dados restritos (PII)
      encryption_required: true
      access_logging: true
      requires_approval: true

access_policies:
  bronze:
    read: [data_engineer, data_scientist]
    write: [data_engineer]
    delete: []
  silver:
    read: [data_engineer, data_scientist, analyst]
    write: [data_engineer]
    delete: []
  gold:
    read: [analyst, business_user, data_scientist]
    write: [data_engineer]
    delete: []

retention_policies:
  bronze:
    retention_days: 90
    archive_after_days: 30
  silver:
    retention_days: 365
    archive_after_days: 180
  gold:
    retention_days: 730
    archive_after_days: 365

lgpd:
  enabled: true
  dpo_email: "dpo@empresa.com"
  consent_required_for:
    - marketing
    - profiling
    - third_party_sharing
  retention_limits:
    pii: 365
    sensitive: 180
    financial: 1825
```

### Uso

```python
from core import get_governance_policies

policies = get_governance_policies("config/governance_policies.yaml")

# Verifica acesso
can_access = policies.check_access(
    user_role="analyst",
    layer="gold",
    operation="read"
)

# Obtém política de retenção
retention = policies.get_retention_policy("silver")
print(f"Retenção: {retention.retention_days} dias")

# Verifica classificação
classification = policies.get_classification_requirements("restricted")
print(f"Criptografia: {classification.encryption_required}")

# Valida compliance LGPD
lgpd_check = policies.validate_lgpd_compliance(
    data_types=["pii"],
    has_consent=True,
    retention_days=300
)
```

## 📚 DataCatalog (NEW v6.0)

Catálogo de dados com suporte a OpenMetadata:

### Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Registro** | Cadastro de tabelas, colunas e metadados |
| **Classificação** | Classificação automática de PII |
| **Busca** | Busca por nome, descrição, tags |
| **Lineage** | Integração com LineageTracker |
| **OpenMetadata** | Sincronização com OpenMetadata |

### Uso

```python
from core import get_data_catalog, ColumnMetadata

catalog = get_data_catalog(project_id="meu_projeto")

# Registra tabela
catalog.register_table(
    name="silver_clientes",
    schema_name="silver",
    database="lakehouse",
    layer="silver",
    columns=[
        ColumnMetadata(
            name="id",
            data_type="bigint",
            is_primary_key=True,
            description="ID único do cliente"
        ),
        ColumnMetadata(
            name="nome",
            data_type="string",
            classification="pii",
            description="Nome completo"
        ),
        ColumnMetadata(
            name="email",
            data_type="string",
            classification="pii",
            description="Email de contato"
        ),
        ColumnMetadata(
            name="cpf",
            data_type="string",
            classification="pii",
            is_encrypted=True,
            description="CPF (criptografado)"
        )
    ],
    description="Tabela de clientes limpa e validada",
    owner="data_engineering",
    tags=["cliente", "pii", "silver"]
)

# Busca tabelas
results = catalog.search_tables(
    query="cliente",
    layer="silver",
    has_pii=True
)

# Obtém metadados
table = catalog.get_table("silver_clientes")
print(f"Colunas PII: {table.pii_columns}")

# Exporta para OpenMetadata
catalog.sync_to_openmetadata(
    server_url="http://openmetadata:8585",
    api_key="..."
)
```

## 🔗 LineageTracker (NEW v6.0)

Rastreamento de linhagem de dados:

### Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Grafo** | Grafo de dependências entre tabelas |
| **Transformações** | Registro de transformações aplicadas |
| **Impacto** | Análise de impacto de mudanças |
| **Visualização** | Exportação para Mermaid/GraphViz |
| **Column Lineage** | Lineage em nível de coluna |

### Uso

```python
from core import get_lineage_tracker, TransformationType, NodeType

tracker = get_lineage_tracker(project_id="meu_projeto")

# Registra nós
tracker.register_node(
    node_id="landing_vendas",
    node_type=NodeType.FILE,
    layer="landing",
    metadata={"format": "csv", "source": "sftp"}
)

tracker.register_node(
    node_id="bronze_vendas",
    node_type=NodeType.TABLE,
    layer="bronze",
    metadata={"database": "lakehouse"}
)

tracker.register_node(
    node_id="silver_vendas",
    node_type=NodeType.TABLE,
    layer="silver"
)

tracker.register_node(
    node_id="gold_vendas_diarias",
    node_type=NodeType.TABLE,
    layer="gold"
)

# Registra transformações
tracker.add_transformation(
    source="landing_vendas",
    target="bronze_vendas",
    transformation_type=TransformationType.INGESTION,
    transformation_logic="Leitura de CSV e gravação em Delta"
)

tracker.add_transformation(
    source="bronze_vendas",
    target="silver_vendas",
    transformation_type=TransformationType.CLEANING,
    transformation_logic="Remove duplicatas, valida campos, padroniza formatos"
)

tracker.add_transformation(
    source="silver_vendas",
    target="gold_vendas_diarias",
    transformation_type=TransformationType.AGGREGATION,
    transformation_logic="Agregação por dia com métricas de vendas"
)

# Análise de impacto
impact = tracker.analyze_impact("bronze_vendas")
print(f"Nós afetados: {impact.affected_nodes}")
print(f"Nível de risco: {impact.risk_level}")
print(f"Recomendações: {impact.recommendations}")

# Obtém ancestrais e descendentes
ancestors = tracker.get_ancestors("gold_vendas_diarias")
descendants = tracker.get_descendants("bronze_vendas")

# Exporta para Mermaid
mermaid = tracker.export_to_mermaid()
print(mermaid)
# graph TD
#   landing_vendas --> bronze_vendas
#   bronze_vendas --> silver_vendas
#   silver_vendas --> gold_vendas_diarias
```

## 📖 BusinessGlossary (NEW v6.0)

Glossário de negócio padronizado:

### Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Termos** | Cadastro de termos de negócio |
| **Sinônimos** | Mapeamento de sinônimos |
| **Relacionamentos** | Hierarquia e relacionamentos |
| **Mapeamento** | Ligação com colunas do catálogo |
| **Importação** | Import/export YAML |

### Uso

```python
from core import get_business_glossary, TermStatus

glossary = get_business_glossary(project_id="meu_projeto")

# Adiciona termos
glossary.add_term(
    name="Cliente",
    definition="Pessoa física ou jurídica que adquire produtos ou serviços",
    domain="Comercial",
    owner="time_comercial",
    synonyms=["Consumidor", "Comprador"],
    related_terms=["Prospect", "Lead"],
    examples=["Cliente PF", "Cliente PJ"],
    status=TermStatus.APPROVED
)

glossary.add_term(
    name="Ticket Médio",
    definition="Valor médio das compras por cliente em um período",
    domain="Financeiro",
    formula="SUM(valor_venda) / COUNT(DISTINCT cliente_id)",
    unit="BRL",
    owner="time_financeiro"
)

glossary.add_term(
    name="Churn",
    definition="Taxa de cancelamento ou abandono de clientes",
    domain="Comercial",
    formula="Clientes perdidos / Total de clientes * 100",
    unit="%"
)

# Mapeia para colunas
glossary.map_to_column(
    term_name="Cliente",
    table_name="silver_clientes",
    column_name="id"
)

# Busca termos
results = glossary.search_terms("cliente")

# Obtém termo
term = glossary.get_term("Ticket Médio")
print(f"Definição: {term.definition}")
print(f"Fórmula: {term.formula}")

# Exporta para YAML
glossary.export_to_yaml("glossary.yaml")

# Importa de YAML
glossary.import_from_yaml("glossary.yaml")
```

## 🛡️ Governança e LGPD

O framework inclui um **Time de Governança** completo:

### Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Classificação de Dados** | Identifica automaticamente PII, dados sensíveis e públicos |
| **Base Legal** | Valida se há base legal adequada (consentimento, contrato, etc.) |
| **Consentimento** | Verifica mecanismos de consentimento para dados sensíveis |
| **Direitos do Titular** | Garante canais para acesso, correção, exclusão, portabilidade |
| **Retenção** | Valida políticas de retenção e exclusão |
| **Auditoria** | Registra todas as operações para compliance |
| **DPIA** | Suporte a Data Protection Impact Assessment |

## 📊 Data Quality

Sistema completo de validação de qualidade de dados:

### 6 Dimensões de Qualidade

| Dimensão | Descrição | Exemplo |
|----------|-----------|---------|
| **Completude** | Campos não nulos | Email obrigatório |
| **Consistência** | Formato correto | Email válido |
| **Precisão** | Valores corretos | Idade entre 0-150 |
| **Unicidade** | Sem duplicatas | CPF único |
| **Atualidade** | Dados recentes | Última atualização < 30 dias |
| **Validade** | Valores permitidos | Status in ['ativo', 'inativo'] |

## 📈 Observabilidade e FinOps

Sistema completo de monitoramento e gestão de custos:

### Componentes

| Componente | Funcionalidade |
|------------|----------------|
| **Logger** | Logging estruturado com níveis e contexto |
| **Metrics** | Métricas (4 Golden Signals) |
| **Alerts** | Alertas configuráveis com thresholds |
| **Costs** | Estimativa e tracking de custos |

## 📊 Times Disponíveis

| Time | Agentes | Especialização |
|------|---------|----------------|
| **Product Owner** | 4 | Requisitos, user stories, priorização |
| **Project Manager** | 4 | Planejamento, cronograma, riscos |
| **Architecture** | 5 | Decisões técnicas, custos, escalabilidade |
| **Data Engineering** | 4 | Pipelines, ETL, qualidade de dados |
| **Data Science** | 4 | ML, modelos preditivos, MLOps |
| **Data Analytics** | 4 | Dashboards, métricas, insights |
| **DevOps** | 4 | Infraestrutura, CI/CD, monitoramento |
| **QA** | 4 | Testes, validação, qualidade |
| **Security** | 4 | Segurança, LGPD, compliance |
| **Governance** | 4 | LGPD, auditoria, conformidade |

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/michael-eng-ai/autonomous-data-agency.git
cd autonomous-data-agency

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com sua OPENAI_API_KEY
```

## 📖 Demos

```bash
# Demo do workflow completo com governança
python demo_complete_workflow.py

# Demo multi-time com comunicação
python demo_multi_team.py

# Demo de um time
python demo_full_system.py

# Teste do sistema de conhecimento
python test_knowledge_system.py
```

## 📁 Estrutura do Projeto

```
autonomous-data-agency/
├── config/
│   ├── llm_config.py              # Configuração de LLMs
│   └── governance_policies.yaml   # Políticas de governança
├── core/
│   ├── base_team.py               # Classe base para times
│   ├── agency_orchestrator.py     # Orquestrador principal
│   ├── teams_factory.py           # Fábrica de times
│   ├── task_orchestrator.py       # Orquestrador de tarefas
│   ├── pm_orchestrator.py         # PM como coordenador
│   ├── validation_workflow.py     # Fluxo QA + PO
│   ├── hallucination_detector.py  # Detecção de alucinações
│   ├── team_communication.py      # Comunicação entre times
│   ├── governance_team.py         # Time de Governança/LGPD
│   ├── data_quality.py            # Validação de qualidade
│   ├── observability_team.py      # Observabilidade/FinOps
│   ├── integrated_workflow.py     # Workflow integrado
│   ├── quarantine_manager.py      # 🆕 Gestão de quarentena
│   ├── process_control.py         # 🆕 Controle de processos
│   ├── governance_policies.py     # 🆕 Políticas YAML
│   ├── data_catalog.py            # 🆕 Catálogo de dados
│   ├── lineage_tracker.py         # 🆕 Rastreamento de linhagem
│   ├── business_glossary.py       # 🆕 Glossário de negócio
│   └── knowledge/
│       ├── knowledge_base.py      # Camada 1: YAML
│       ├── rag_engine.py          # Camada 2: ChromaDB
│       └── project_memory.py      # Camada 3: SQLite
├── knowledge/
│   ├── architecture/
│   ├── data_engineering/
│   ├── data_science/
│   ├── devops/
│   ├── governance/
│   ├── observability/
│   ├── product_owner/
│   ├── qa/
│   └── shared/
├── teams/
│   ├── product_owner/
│   ├── project_manager/
│   ├── data_engineering/
│   ├── data_science/
│   ├── data_analytics/
│   ├── devops/
│   └── qa/
├── demo_complete_workflow.py
├── demo_full_system.py
├── demo_integrated_v5.py
├── demo_multi_team.py
├── test_knowledge_system.py
├── main.py
├── requirements.txt
└── README.md
```

## 🔄 Changelog

### v6.0.0 (2024-01)
- ✨ QuarantineManager para gestão de dados inválidos
- ✨ ProcessControl para rastreabilidade de execuções
- ✨ GovernancePolicies com suporte a YAML
- ✨ DataCatalog com integração OpenMetadata
- ✨ LineageTracker para rastreamento de linhagem
- ✨ BusinessGlossary para termos padronizados

### v5.0.0 (2024-01)
- ✨ Time de Governança e LGPD
- ✨ Data Quality com 6 dimensões
- ✨ Observabilidade e FinOps
- ✨ Workflow Integrado

### v4.0.0 (2024-01)
- ✨ Time de Arquitetura expandido
- ✨ PM como orquestrador central
- ✨ Sistema de dependências e paralelização
- ✨ Validação QA + PO

### v3.0.0 (2024-01)
- ✨ Sistema de conhecimento em 3 camadas
- ✨ RAG com ChromaDB
- ✨ Project Memory com SQLite

### v2.0.0 (2024-01)
- ✨ Multi-agent com diversidade de LLMs
- ✨ Validação anti-alucinação
- ✨ Comunicação entre times

### v1.0.0 (2024-01)
- 🎉 Versão inicial

## 📄 Licença

MIT License

## 👨‍💻 Autor

Desenvolvido com ❤️ para automação de projetos de dados.
