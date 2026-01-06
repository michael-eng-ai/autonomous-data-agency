# Autonomous Data Agency Framework

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Um framework avançado para criar agências autônomas de dados usando múltiplos times de agentes de IA com LLMs diversos, sistema de conhecimento em 3 camadas, validação anti-alucinação robusta e comunicação entre times.

## 🌟 Novidades da v3.0

- **9 Times Especializados**: PO, PM, Data Engineering, Data Science, Analytics, DevOps, QA, Security, Architecture
- **Sistema Anti-Alucinação Robusto**: Validação multi-camada com detecção de fabricações
- **Comunicação Entre Times**: Message Bus, colaborações, handoffs e escalações
- **Fábrica de Times**: Criação simplificada de times pré-configurados

## 📁 Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENCY ORCHESTRATOR                          │
│                  (Coordenador Global)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  TEAM: PO     │     │ TEAM: DATA    │     │ TEAM: DEVOPS  │
│               │     │ ENGINEERING   │     │               │
│ ┌───────────┐ │     │ ┌───────────┐ │     │ ┌───────────┐ │
│ │  MASTER   │ │     │ │  MASTER   │ │     │ │  MASTER   │ │
│ │ (gpt-4.1) │ │     │ │ (gpt-4.1) │ │     │ │ (gpt-4.1) │ │
│ └───────────┘ │     │ └───────────┘ │     │ └───────────┘ │
│       │       │     │       │       │     │       │       │
│   ┌───┴───┐   │     │   ┌───┴───┐   │     │   ┌───┴───┐   │
│   ▼       ▼   │     │   ▼       ▼   │     │   ▼       ▼   │
│ ┌───┐   ┌───┐ │     │ ┌───┐   ┌───┐ │     │ ┌───┐   ┌───┐ │
│ │Op1│   │Op2│ │     │ │Op1│   │Op2│ │     │ │Op1│   │Op2│ │
│ │4.1│   │gem│ │     │ │nan│   │gem│ │     │ │nan│   │gem│ │
│ └───┘   └───┘ │     │ └───┘   └───┘ │     │ └───┘   └───┘ │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────────────┐
                    │ COMMUNICATION   │
                    │     HUB         │
                    └─────────────────┘
```

## 🧠 Sistema de Conhecimento (3 Camadas)

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE MANAGER                             │
└─────────────────────────────────────────────────────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  KNOWLEDGE BASE │ │   RAG ENGINE    │ │ PROJECT MEMORY  │
│     (YAML)      │ │   (ChromaDB)    │ │    (SQLite)     │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • Best practices│ │ • Docs técnicos │ │ • Decisões      │
│ • Templates     │ │ • Papers        │ │ • Preferências  │
│ • Anti-patterns │ │ • Casos de uso  │ │ • Histórico     │
│ • Checklists    │ │ • Stack Overflow│ │ • Contexto      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🛡️ Sistema Anti-Alucinação

O framework inclui um detector de alucinações robusto que:

- **Verifica contra Knowledge Base**: Valida afirmações contra best practices
- **Detecta fabricações**: Identifica informações inventadas
- **Analisa consistência**: Compara respostas de múltiplos agentes
- **Valida termos técnicos**: Verifica se tecnologias mencionadas existem
- **Detecta excesso de confiança**: Identifica afirmações absolutas sem fundamentação

```python
from core import get_hallucination_detector

detector = get_hallucination_detector()
result = detector.validate_response(
    response="Recomendo usar Apache Airflow...",
    domain="data_engineering"
)
print(f"Válido: {result.is_valid}, Score: {result.overall_score}")
```

## 📡 Sistema de Comunicação Entre Times

```python
from core import get_communication_hub, MessagePriority

hub = get_communication_hub()

# Registra times
hub.register_team("data_engineering")
hub.register_team("devops")

# Solicita ajuda
collab_id = hub.request_help(
    from_team="data_engineering",
    topic="Infraestrutura Kafka",
    description="Precisamos configurar Kafka em produção",
    required_expertise=["kafka", "kubernetes"],
    priority=MessagePriority.HIGH
)

# Handoff de tarefa
hub.handoff_task(
    from_team="data_engineering",
    to_team="data_science",
    task_description="Pipeline pronto. Criar modelos de ML.",
    deliverables=["Modelo de previsão", "API de inferência"],
    context={"data_format": "parquet"}
)

# Escalação de decisão
hub.escalate_decision(
    from_team="data_engineering",
    decision_topic="Escolha de Data Warehouse",
    options=[
        {"name": "Snowflake", "pros": ["Escalável"], "cons": ["Custo"]},
        {"name": "BigQuery", "pros": ["Integração GCP"], "cons": ["Vendor lock-in"]}
    ],
    context="Precisamos de um DW para 10TB de dados"
)
```

## 🏭 Fábrica de Times

```python
from core import get_teams_factory, TeamType

factory = get_teams_factory()

# Lista times disponíveis
teams = factory.list_available_teams()
for team in teams:
    print(f"{team['name']}: {team['description']}")

# Obtém configuração de um time
config = factory.get_team_config(TeamType.DATA_ENGINEERING)
print(f"Time: {config.name}")
print(f"Master: {config.master_config.name}")
print(f"Operacionais: {[a.name for a in config.operational_agents]}")

# Encontra times por tópico
teams = factory.get_teams_for_topic("machine learning")
# Retorna: [TeamType.DATA_SCIENCE, TeamType.DATA_ENGINEERING]
```

## 📊 Times Disponíveis

| Time | Domínio | Agentes | Especialização |
|------|---------|---------|----------------|
| **Product Owner** | `product_owner` | 4 | Requisitos, user stories, priorização |
| **Project Manager** | `project_manager` | 4 | Planejamento, riscos, cronograma |
| **Data Engineering** | `data_engineering` | 4 | Pipelines, ETL, arquitetura de dados |
| **Data Science** | `data_science` | 4 | ML, modelos preditivos, MLOps |
| **Data Analytics** | `data_analytics` | 4 | Dashboards, métricas, insights |
| **DevOps** | `devops` | 4 | Infraestrutura, CI/CD, monitoramento |
| **QA** | `qa` | 4 | Testes, qualidade de dados, validação |
| **Security** | `security` | 4 | Segurança, LGPD, compliance |
| **Architecture** | `architecture` | 4 | Decisões arquiteturais, padrões |

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/michael-eng-ai/autonomous-data-agency.git
cd autonomous-data-agency

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com sua OPENAI_API_KEY
```

## 📖 Uso

### Demo Básica (Um Time)
```bash
python demo_full_system.py
```

### Demo Multi-Time Completa
```bash
python demo_multi_team.py
```

### Modo Interativo
```bash
python main.py --mode interactive
```

### Uso Programático

```python
from core import (
    get_agency_orchestrator,
    get_knowledge_manager,
    get_hallucination_detector,
    get_communication_hub
)

# Inicializa componentes
orchestrator = get_agency_orchestrator()
km = get_knowledge_manager()
detector = get_hallucination_detector()
hub = get_communication_hub()

# Inicia um projeto
project = orchestrator.start_project(
    project_name="Meu Projeto",
    client_request="Preciso de um sistema de análise de vendas"
)

# Executa workflow completo
outputs = orchestrator.execute_workflow(
    teams_sequence=["product_owner", "data_engineering", "devops"],
    initial_task=project.client_request
)

# Validação global
validation = orchestrator.global_validation(outputs)
print(f"Qualidade: {validation.overall_quality_score * 100}%")
```

## 📁 Estrutura do Projeto

```
autonomous-data-agency/
├── config/
│   ├── __init__.py
│   └── llm_config.py           # Configuração de LLMs
├── core/
│   ├── __init__.py
│   ├── base_team.py            # Classe base para times
│   ├── agency_orchestrator.py  # Orquestrador principal
│   ├── teams_factory.py        # Fábrica de times
│   ├── hallucination_detector.py # Detector de alucinações
│   ├── team_communication.py   # Sistema de comunicação
│   └── knowledge/
│       ├── knowledge_base.py   # Camada 1: YAML
│       ├── rag_engine.py       # Camada 2: ChromaDB
│       └── project_memory.py   # Camada 3: SQLite
├── knowledge/
│   ├── data_engineering/
│   ├── data_science/
│   ├── devops/
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
├── data/
│   ├── chroma/                 # Banco vetorial
│   └── memory/                 # Memória de projetos
├── main.py
├── demo_full_system.py
├── demo_multi_team.py
├── test_knowledge_system.py
├── requirements.txt
└── README.md
```

## 🧪 Testes

```bash
# Testa o sistema de conhecimento
python test_knowledge_system.py

# Testa os módulos individuais
python -m core.hallucination_detector
python -m core.team_communication
python -m core.teams_factory
```

## 📈 Roadmap

- [ ] Interface web para visualização
- [ ] Integração com mais provedores de LLM
- [ ] Suporte a execução de código pelos agentes
- [ ] Métricas e dashboards de performance
- [ ] API REST para integração externa
- [ ] Suporte a plugins customizados

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📄 Licença

MIT License

## 👨‍💻 Autor

Desenvolvido por [Michael](https://github.com/michael-eng-ai)
