# Autonomous Data Agency Framework v4.0

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Um framework avançado para criar agências autônomas de dados usando múltiplos times de agentes de IA com LLMs diversos, sistema de conhecimento em 3 camadas, validação anti-alucinação robusta, comunicação entre times e workflow completo de validação.

## 🌟 Novidades da v4.0

- **Time de Arquitetura Expandido**: Agentes especializados em Cloud, Custos, Segurança e Migração
- **PM como Orquestrador Central**: Gerencia cronograma, dependências e paralelização
- **Workflow de Validação QA + PO**: Cada entrega passa por validação técnica e de negócio
- **Knowledge Base de Arquitetura**: Padrões, comparativos de cloud, estimativas de custo
- **Sistema de Dependências**: Tarefas executam na ordem correta, com paralelização quando possível

## 📁 Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AGENCY ORCHESTRATOR                              │
│                    (Coordenador Global da Agência)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│  PO TEAM      │           │  PM TEAM      │           │ ARCHITECTURE  │
│  (Requisitos) │           │ (Cronograma)  │           │  (Decisões)   │
└───────────────┘           └───────────────┘           └───────────────┘
        │                           │                           │
        │                           ▼                           │
        │                   ┌───────────────┐                   │
        │                   │ Task Schedule │                   │
        │                   │ Dependencies  │                   │
        │                   └───────────────┘                   │
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
        ┌─────────────┬─────────────┼─────────────┬─────────────┐
        │             │             │             │             │
        ▼             ▼             ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Data Eng    │ │ DevOps      │ │ Data Science│ │ Analytics   │ │ Security    │
│ Team        │ │ Team        │ │ Team        │ │ Team        │ │ Team        │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
        │             │             │             │             │
        └─────────────┴─────────────┼─────────────┴─────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │   QA TEAM     │
                            │  (Validação   │
                            │   Técnica)    │
                            └───────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │   PO TEAM     │
                            │  (Validação   │
                            │   Negócio)    │
                            └───────────────┘
```

## 🔄 Fluxo de Trabalho

O framework implementa um fluxo de trabalho profissional:

```
Cliente → PO (requisitos) → PM (cronograma) → ARQUITETURA (decisões)
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              Data Eng         DevOps         Data Science
                    ↓               ↓               ↓
                    └───────────────┼───────────────┘
                                    ↓
                              QA (testes)
                                    ↓
                         PO (validação final)
```

**Princípios:**
1. **Arquitetura sempre primeiro** - Decisões de custo, escalabilidade e portabilidade
2. **Paralelização** - Tarefas independentes executam em paralelo
3. **Validação dupla** - QA (técnico) + PO (negócio) para cada entrega
4. **Comunicação estruturada** - Times se comunicam via message bus

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

## 📊 PM como Orquestrador

O Project Manager gerencia todo o ciclo de vida do projeto:

```python
from core import get_pm_orchestrator

pm = get_pm_orchestrator()

# Cria projeto
project = pm.create_project(
    project_id="meu_projeto",
    project_name="Sistema de Análise",
    description="Bot de análise de clientes",
    client_requirements="Requisitos..."
)

# Gera cronograma com dependências
plan = pm.analyze_requirements_and_create_schedule(
    project_id="meu_projeto",
    requirements={
        "has_ml": True,
        "has_analytics": True,
        "data_volume": "medium",
        "team_size": 3
    }
)

# Visualiza ordem de execução
for level in plan["execution_levels"]:
    print(f"Nível {level['level']}:")
    for task in level["tasks"]:
        print(f"  [{task['assigned_team']}] {task['name']}")
```

## ✅ Workflow de Validação (QA + PO)

Cada entrega passa por validação dupla:

```python
from core import get_validation_workflow

workflow = get_validation_workflow()

result = workflow.submit_for_validation(
    task_id="task_001",
    task_name="Pipeline de Dados",
    task_type="data_pipeline",
    assigned_team="data_engineering",
    deliverables=["Pipeline ETL", "Testes", "Docs"],
    original_requirements=["Ingerir dados", "Transformar"],
    test_results={
        "all_tests_passed": True,
        "data_quality_score": 0.95,
        "documentation_complete": True
    }
)

if result["can_proceed"]:
    print("✅ Aprovado por QA e PO!")
else:
    print(f"❌ Rejeitado: {result['feedback']}")
```

## 🏗️ Time de Arquitetura Expandido

O time de Arquitetura agora inclui especialistas em:

| Agente | Foco | Responsabilidades |
|--------|------|-------------------|
| **Arquiteto Mestre** | Consolidação | Trade-offs, decisões finais |
| **Arquiteto de Soluções** | Integrações | Padrões, APIs, microservices |
| **Arquiteto de Dados** | Data Architecture | Data mesh, lakehouse, governança |
| **Arquiteto Cloud** | Infraestrutura | Custos, escalabilidade, migração |
| **Arquiteto de Segurança** | Compliance | LGPD, criptografia, IAM |

### Knowledge Base de Arquitetura

```yaml
# knowledge/architecture/best_practices.yaml
patterns:
  - Data Lakehouse
  - Data Mesh
  - Lambda Architecture
  - Kappa Architecture
  - Event-Driven Architecture

cloud_comparison:
  aws: {strengths, weaknesses, services}
  gcp: {strengths, weaknesses, services}
  azure: {strengths, weaknesses, services}
  open_source: {strengths, weaknesses, services}

cost_estimation:
  small_project: "$100-500/mês"
  medium_project: "$500-2000/mês"
  large_project: "$2000-10000+/mês"
```

## 🛡️ Sistema Anti-Alucinação

```python
from core import get_hallucination_detector

detector = get_hallucination_detector()
result = detector.validate_response(
    response="Recomendo usar Apache Airflow...",
    domain="data_engineering"
)

print(f"Válido: {result.is_valid}")
print(f"Score: {result.overall_score}")
print(f"Issues: {result.issues}")
```

## 📡 Comunicação Entre Times

```python
from core import get_communication_hub

hub = get_communication_hub()

# Handoff de tarefa
hub.send_message(
    from_team="architecture",
    to_team="data_engineering",
    message_type="task_handoff",
    content={"task": "Implementar pipeline", "priority": "high"}
)

# Solicita ajuda
hub.request_help(
    from_team="data_science",
    topic="Feature Engineering",
    description="Preciso de features agregadas",
    required_expertise=["sql", "spark"]
)
```

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

## 📖 Uso

### Demo do Workflow Completo (Recomendado)
```bash
python demo_complete_workflow.py
```

### Demo Multi-Time
```bash
python demo_multi_team.py
```

### Demo de Um Time
```bash
python demo_full_system.py
```

### Teste do Sistema de Conhecimento
```bash
python test_knowledge_system.py
```

## 📁 Estrutura do Projeto

```
autonomous-data-agency/
├── config/
│   └── llm_config.py           # Configuração de LLMs
├── core/
│   ├── base_team.py            # Classe base para times
│   ├── agency_orchestrator.py  # Orquestrador principal
│   ├── teams_factory.py        # Fábrica de times
│   ├── task_orchestrator.py    # Orquestrador de tarefas
│   ├── pm_orchestrator.py      # PM como coordenador
│   ├── validation_workflow.py  # Fluxo QA + PO
│   ├── hallucination_detector.py
│   ├── team_communication.py
│   └── knowledge/
│       ├── knowledge_base.py   # Camada 1: YAML
│       ├── rag_engine.py       # Camada 2: ChromaDB
│       └── project_memory.py   # Camada 3: SQLite
├── knowledge/
│   ├── architecture/           # NEW: KB de Arquitetura
│   ├── data_engineering/
│   ├── data_science/
│   ├── devops/
│   ├── product_owner/
│   ├── qa/
│   └── shared/
├── teams/
│   └── [times especializados]
├── demo_complete_workflow.py   # NEW: Demo completa
├── demo_multi_team.py
├── demo_full_system.py
├── test_knowledge_system.py
├── main.py
├── requirements.txt
└── README.md
```

## 🧪 Testes

```bash
# Testa o sistema de conhecimento
python test_knowledge_system.py

# Testa módulos individuais
python -m core.pm_orchestrator
python -m core.validation_workflow
python -m core.hallucination_detector
```

## 📈 Roadmap

- [x] Time de Arquitetura expandido
- [x] PM como orquestrador central
- [x] Workflow de validação QA + PO
- [x] Sistema de dependências e paralelização
- [ ] Interface web para visualização
- [ ] API REST para integração externa
- [ ] Execução real de código pelos agentes
- [ ] Métricas e dashboards de performance

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📄 Licença

MIT License

## 👨‍💻 Autor

Desenvolvido por [Michael](https://github.com/michael-eng-ai)
