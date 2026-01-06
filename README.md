# Autonomous Data Agency Framework v5.0

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Um framework avançado para criar agências autônomas de dados usando múltiplos times de agentes de IA com LLMs diversos, **governança e LGPD integrados**, sistema de conhecimento em 3 camadas, validação anti-alucinação robusta, **data quality**, **observabilidade e FinOps**.

## 🌟 Novidades da v5.0

- **Time de Governança e LGPD**: Classificação de dados, base legal, consentimento, auditoria
- **Data Quality**: 6 dimensões de qualidade, validação automática, relatórios
- **Observabilidade e FinOps**: Logging estruturado, métricas, alertas, estimativa de custos
- **Workflow Integrado**: Governança em cada etapa, validação contínua
- **Knowledge Base Expandida**: Governança e Observabilidade

## 📁 Arquitetura Completa

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AUTONOMOUS DATA AGENCY                             │
│                              Framework v5.0                                  │
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
                    │                │               │               │
                    └────────────────┴───────────────┴───────────────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ DATA QUALITY  │
                                    │   Validator   │
                                    └───────────────┘
```

## 🛡️ Governança e LGPD

O framework agora inclui um **Time de Governança** completo para garantir conformidade:

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

### Uso

```python
from core.governance_team import get_governance_team

governance = get_governance_team()

# Classifica dados automaticamente
classification = governance.classify_data({
    "nome": "string",
    "cpf": "string",
    "historico_saude": "string"
})
# Resultado: {"nome": "PII", "cpf": "PII", "historico_saude": "SENSITIVE"}

# Verifica base legal
legal_check = governance.check_legal_basis(
    data_types=["PII", "SENSITIVE"],
    declared_basis="consent",
    has_consent_mechanism=True
)

# Gera checklist LGPD
checklist = governance.generate_lgpd_checklist(project_type="customer_analytics")

# Revisão completa de arquitetura
review = governance.review_architecture({
    "database": "PostgreSQL",
    "encryption": True,
    "access_control": True
})
```

### Knowledge Base de Governança

```yaml
# knowledge/governance/best_practices.yaml
lgpd:
  principles:
    - Finalidade
    - Adequação
    - Necessidade
    - Livre acesso
    - Qualidade dos dados
    - Transparência
    - Segurança
    - Prevenção
    - Não discriminação
    - Responsabilização

  legal_bases:
    - Consentimento
    - Obrigação legal
    - Execução de políticas públicas
    - Estudos por órgão de pesquisa
    - Execução de contrato
    - Exercício regular de direitos
    - Proteção da vida
    - Tutela da saúde
    - Legítimo interesse
    - Proteção do crédito

  data_subject_rights:
    - Confirmação de tratamento
    - Acesso aos dados
    - Correção
    - Anonimização/bloqueio/eliminação
    - Portabilidade
    - Eliminação com consentimento
    - Informação sobre compartilhamento
    - Revogação do consentimento
```

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

### Uso

```python
from core.data_quality import get_data_quality_validator

validator = get_data_quality_validator()

# Define schema
schema = {
    "email": {"type": "string", "nullable": False},
    "idade": {"type": "integer", "nullable": True},
    "cpf": {"type": "string", "nullable": False}
}

# Adiciona regras padrão baseadas no schema
validator.add_standard_rules("clientes", schema)

# Adiciona regra customizada
validator.add_rule(
    dataset="clientes",
    rule_name="idade_valida",
    dimension="accuracy",
    check_function=lambda row: 0 <= row.get("idade", 0) <= 150,
    severity="error"
)

# Valida dados
data = [
    {"email": "joao@email.com", "idade": 30, "cpf": "123.456.789-00"},
    {"email": "invalid-email", "idade": 200, "cpf": ""},
]

report = validator.validate("clientes", data)

print(f"Score: {report.overall_score:.2%}")
print(f"Passou: {report.passed}")
print(f"Violações: {len(report.violations)}")
for v in report.violations:
    print(f"  - {v['rule']}: {v['message']}")
```

## 📈 Observabilidade e FinOps

Sistema completo de monitoramento e gestão de custos:

### Componentes

| Componente | Funcionalidade |
|------------|----------------|
| **Logger** | Logging estruturado com níveis e contexto |
| **Metrics** | Métricas (4 Golden Signals) |
| **Alerts** | Alertas configuráveis com thresholds |
| **Costs** | Estimativa e tracking de custos |

### Uso

```python
from core.observability_team import get_observability_team

obs = get_observability_team()

# Registra ação de agente
obs.record_agent_action(
    agent_name="data_engineer",
    action="create_pipeline",
    duration_ms=1500,
    success=True,
    tokens_used=2000,
    model="gpt-4.1-mini"
)

# Estima custos do projeto
estimate = obs.costs.estimate_project_cost({
    "duration_days": 30,
    "llm_calls_per_day": 100,
    "avg_tokens_per_call": 2000,
    "storage_gb": 50,
    "compute_hours_per_day": 8
})

print(f"Custo estimado: ${estimate['total_estimated']:.2f}")
print(f"  - LLM: ${estimate['breakdown']['llm_costs']:.2f}")
print(f"  - Storage: ${estimate['breakdown']['storage_costs']:.2f}")
print(f"  - Compute: ${estimate['breakdown']['compute_costs']:.2f}")

# Configura alerta
obs.alerts.add_alert(
    name="high_error_rate",
    metric="error_rate",
    threshold=0.1,
    operator="greater_than",
    severity="critical"
)

# Dashboard de observabilidade
dashboard = obs.get_dashboard_data()
```

### Knowledge Base de Observabilidade

```yaml
# knowledge/observability/best_practices.yaml
golden_signals:
  - Latency (tempo de resposta)
  - Traffic (volume de requisições)
  - Errors (taxa de erros)
  - Saturation (utilização de recursos)

cost_optimization:
  strategies:
    - Usar modelos menores para tarefas simples
    - Cache de respostas frequentes
    - Batch processing quando possível
    - Auto-scaling baseado em demanda
```

## 🔄 Workflow Integrado

O novo workflow integra governança em cada etapa:

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Cliente │────▶│   PO    │────▶│   PM    │────▶│  ARCH   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                     │                               │
                     ▼                               ▼
              ┌─────────────┐                 ┌─────────────┐
              │ GOVERNANÇA  │                 │ GOVERNANÇA  │
              │ (Requisitos)│                 │(Arquitetura)│
              └─────────────┘                 └─────────────┘
                                                     │
                    ┌────────────────────────────────┼────────────────────────────────┐
                    │                                │                                │
                    ▼                                ▼                                ▼
             ┌───────────┐                    ┌───────────┐                    ┌───────────┐
             │ Data Eng  │                    │  DevOps   │                    │Data Science│
             └───────────┘                    └───────────┘                    └───────────┘
                    │                                │                                │
                    ▼                                ▼                                ▼
             ┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
             │DATA QUALITY │                 │DATA QUALITY │                 │DATA QUALITY │
             └─────────────┘                 └─────────────┘                 └─────────────┘
                    │                                │                                │
                    └────────────────────────────────┼────────────────────────────────┘
                                                     │
                                                     ▼
                                              ┌─────────────┐
                                              │     QA      │
                                              │ + Governança│
                                              └─────────────┘
                                                     │
                                                     ▼
                                              ┌─────────────┐
                                              │     PO      │
                                              │ (Validação) │
                                              └─────────────┘
```

### Uso do Workflow Integrado

```python
from core.integrated_workflow import get_integrated_workflow

workflow = get_integrated_workflow()

# Cria projeto
project = workflow.create_project(
    name="Bot de Análise de Clientes",
    description="Sistema de análise e recomendação",
    client="Empresa XYZ",
    initial_requirements={
        "data_fields": ["nome", "email", "cpf", "historico_compras"],
        "legal_basis": "contract",
        "retention_period": "5 years"
    }
)

# Submete requisitos (validação de governança automática)
result = workflow.submit_requirements(
    project_id=project.id,
    requirements={
        "functional": ["Análise de perfil", "Recomendações"],
        "non_functional": ["LGPD compliant", "99.9% uptime"],
        "data_fields": ["nome", "email", "cpf"],
        "legal_basis": "contract"
    }
)

if result["blocked"]:
    print("Bloqueado por governança:")
    for issue in result["governance_issues"]:
        print(f"  - {issue['message']}")

# Submete arquitetura (inclui estimativa de custos)
result = workflow.submit_architecture(
    project_id=project.id,
    architecture={
        "database": "PostgreSQL",
        "orchestration": "Apache Airflow",
        "ml_platform": "MLflow",
        "cloud": "AWS",
        "timeline_days": 30
    }
)

print(f"Custo estimado: ${result['cost_estimate']['total_estimated']:.2f}")

# Completa revisão de governança
result = workflow.complete_governance_review(
    project_id=project.id,
    dpia_required=True,
    dpia_result={"risk_level": "medium", "mitigations": ["Criptografia", "Anonimização"]}
)

# Submete entregas com validação de qualidade
result = workflow.submit_deliverable(
    project_id=project.id,
    deliverable_name="pipeline_ingestao",
    deliverable_type="pipeline",
    data_sample=[{"nome": "João", "email": "joao@email.com", "cpf": "123.456.789-00"}],
    schema={"nome": {"type": "string", "nullable": False}}
)

# Gera relatório final
report = workflow.generate_project_report(project.id)
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
│   └── llm_config.py              # Configuração de LLMs
├── core/
│   ├── base_team.py               # Classe base para times
│   ├── agency_orchestrator.py     # Orquestrador principal
│   ├── teams_factory.py           # Fábrica de times
│   ├── task_orchestrator.py       # Orquestrador de tarefas
│   ├── pm_orchestrator.py         # PM como coordenador
│   ├── validation_workflow.py     # Fluxo QA + PO
│   ├── hallucination_detector.py  # Detecção de alucinações
│   ├── team_communication.py      # Comunicação entre times
│   ├── governance_team.py         # 🆕 Time de Governança/LGPD
│   ├── data_quality.py            # 🆕 Validação de qualidade
│   ├── observability_team.py      # 🆕 Observabilidade/FinOps
│   ├── integrated_workflow.py     # 🆕 Workflow integrado
│   └── knowledge/
│       ├── knowledge_base.py      # Camada 1: YAML
│       ├── rag_engine.py          # Camada 2: ChromaDB
│       └── project_memory.py      # Camada 3: SQLite
├── knowledge/
│   ├── architecture/
│   ├── data_engineering/
│   ├── data_science/
│   ├── devops/
│   ├── governance/                # 🆕 KB de Governança
│   ├── observability/             # 🆕 KB de Observabilidade
│   ├── product_owner/
│   ├── qa/
│   └── shared/
├── teams/
│   └── [times especializados]
├── demo_complete_workflow.py
├── demo_multi_team.py
├── demo_full_system.py
├── test_knowledge_system.py
├── main.py
├── requirements.txt
└── README.md
```

## 📈 Roadmap

- [x] Time de Arquitetura expandido
- [x] PM como orquestrador central
- [x] Workflow de validação QA + PO
- [x] Sistema de dependências e paralelização
- [x] **Time de Governança e LGPD**
- [x] **Data Quality com 6 dimensões**
- [x] **Observabilidade e FinOps**
- [x] **Workflow integrado com governança**
- [ ] Interface web para visualização
- [ ] API REST para integração externa
- [ ] Execução real de código pelos agentes
- [ ] Integração com cloud providers

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📄 Licença

MIT License

## 👨‍💻 Autor

Desenvolvido por [Michael](https://github.com/michael-eng-ai)

---

**Autonomous Data Agency v5.0** - Agora com Governança, LGPD, Data Quality e Observabilidade integrados.
