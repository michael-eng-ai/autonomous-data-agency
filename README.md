# Autonomous Data Agency Framework

Um framework Python para criar e orquestrar times de agentes de IA autônomos para projetos de dados. Cada time é composto por múltiplos agentes usando diferentes LLMs para garantir diversidade de pensamento e validação contra alucinações.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENCY ORCHESTRATOR                          │
│                  (Agente Mestre Global)                         │
│         Valida, consolida e previne alucinações                 │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Product      │    │  Data         │    │  DevOps       │
│  Owner Team   │    │  Engineering  │    │  Team         │
├───────────────┤    ├───────────────┤    ├───────────────┤
│ ┌───────────┐ │    │ ┌───────────┐ │    │ ┌───────────┐ │
│ │  Master   │ │    │ │  Master   │ │    │ │  Master   │ │
│ │  Agent    │ │    │ │  Agent    │ │    │ │  Agent    │ │
│ └───────────┘ │    │ └───────────┘ │    │ └───────────┘ │
│       │       │    │       │       │    │       │       │
│   ┌───┴───┐   │    │   ┌───┴───┐   │    │   ┌───┴───┐   │
│   ▼       ▼   │    │   ▼       ▼   │    │   ▼       ▼   │
│ ┌───┐   ┌───┐ │    │ ┌───┐   ┌───┐ │    │ ┌───┐   ┌───┐ │
│ │Op1│   │Op2│ │    │ │Op1│   │Op2│ │    │ │Op1│   │Op2│ │
│ │GPT│   │Gem│ │    │ │GPT│   │Gem│ │    │ │GPT│   │Gem│ │
│ └───┘   └───┘ │    │ └───┘   └───┘ │    │ └───┘   └───┘ │
└───────────────┘    └───────────────┘    └───────────────┘
```

### Princípios de Design

1. **Diversidade de LLMs**: Cada agente operacional usa um modelo diferente (GPT-4.1-mini, GPT-4.1-nano, Gemini-2.5-flash) para evitar vieses e aumentar a qualidade das soluções.

2. **Validação Hierárquica**: Agentes Mestres validam e consolidam as respostas dos operacionais, detectando alucinações e inconsistências.

3. **Prevenção de Alucinações**: Sistema de múltiplas camadas de validação para garantir que as respostas são factualmente corretas.

4. **Modularidade**: Cada time é independente e pode ser usado isoladamente ou em conjunto.

## Times Disponíveis

| Time | Descrição | Agentes Operacionais |
|------|-----------|---------------------|
| **Product Owner** | Requisitos e escopo | Analista de Requisitos, Escritor de Escopo |
| **Project Manager** | Planejamento e gestão | Planejador de Projeto, Gestor de Riscos |
| **Data Engineering** | Arquitetura e pipelines | Arquiteto de Dados, Dev de Pipeline |
| **Data Science** | ML e MLOps | Cientista de Dados, Engenheiro de ML |
| **Data Analytics** | Análises e dashboards | Analista de Dados, Especialista em Viz |
| **DevOps** | Infraestrutura e CI/CD | Eng. de Infraestrutura, Especialista CI/CD |
| **QA** | Testes e qualidade | Eng. de Testes, Especialista em Data Quality |

## Instalação

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

## Uso Rápido

### Modo Demo
```bash
python main.py --mode demo
```

### Modo Workflow Completo
```bash
python main.py --mode workflow
```

### Modo Interativo
```bash
python main.py --mode interactive
```

### Uso Programático

```python
from core import get_agency_orchestrator

# Inicializa o orquestrador
orchestrator = get_agency_orchestrator()

# Inicia um projeto
project = orchestrator.start_project(
    project_name="Meu Projeto",
    client_request="Preciso de um sistema de análise de vendas"
)

# Executa um time específico
po_output = orchestrator.execute_team("product_owner", project.client_request)

# Ou executa um workflow completo
outputs = orchestrator.execute_workflow(
    teams_sequence=["product_owner", "project_manager", "data_engineering"],
    initial_task=project.client_request
)

# Validação global
validation = orchestrator.global_validation(outputs)
print(f"Qualidade: {validation.overall_quality_score * 100}%")
```

## Estrutura do Projeto

```
autonomous-data-agency/
├── main.py                 # Ponto de entrada principal
├── requirements.txt        # Dependências
├── .env.example           # Exemplo de configuração
├── README.md              # Este arquivo
│
├── config/                # Configurações
│   ├── __init__.py
│   └── llm_config.py      # Configuração de múltiplos LLMs
│
├── core/                  # Núcleo do framework
│   ├── __init__.py
│   ├── base_team.py       # Classe base para times
│   └── agency_orchestrator.py  # Orquestrador principal
│
└── teams/                 # Times de agentes
    ├── __init__.py
    ├── product_owner/
    │   ├── __init__.py
    │   └── team.py
    ├── project_manager/
    │   ├── __init__.py
    │   └── team.py
    ├── data_engineering/
    │   ├── __init__.py
    │   └── team.py
    ├── data_science/
    │   ├── __init__.py
    │   └── team.py
    ├── data_analytics/
    │   ├── __init__.py
    │   └── team.py
    ├── devops/
    │   ├── __init__.py
    │   └── team.py
    └── qa/
        ├── __init__.py
        └── team.py
```

## Fluxo de Trabalho

1. **Recebimento da Solicitação**: O cliente faz uma solicitação de projeto.

2. **Análise de Requisitos**: O time de PO analisa a solicitação com múltiplos agentes, cada um oferecendo uma perspectiva diferente.

3. **Validação do Mestre**: O Agente Mestre do time consolida as respostas, detecta alucinações e produz uma saída validada.

4. **Delegação**: O orquestrador delega tarefas para outros times conforme necessário.

5. **Validação Global**: O Agente Mestre Global revisa todas as saídas, garantindo consistência e qualidade.

6. **Entrega**: O resultado final é entregue ao cliente.

## Configuração de LLMs

O framework usa múltiplos LLMs para garantir diversidade:

```python
# config/llm_config.py
LLM_CONFIGS = {
    "master": LLMConfig(
        model_name="gpt-4.1-mini",
        temperature=0.3,  # Mais determinístico
    ),
    "operational_1": LLMConfig(
        model_name="gpt-4.1-mini",
        temperature=0.7,
    ),
    "operational_2": LLMConfig(
        model_name="gpt-4.1-nano",
        temperature=0.8,
    ),
    "operational_3": LLMConfig(
        model_name="gemini-2.5-flash",
        temperature=0.7,
    ),
}
```

## Criando um Novo Time

```python
from core.base_team import BaseTeam
from typing import List

class MeuNovoTime(BaseTeam):
    def __init__(self):
        super().__init__(
            team_name="Meu Novo Time",
            team_description="Descrição do time",
            num_operational_agents=2
        )
    
    def _get_operational_prompts(self) -> List[str]:
        return [
            "Prompt do primeiro agente operacional...",
            "Prompt do segundo agente operacional..."
        ]
    
    def _get_master_prompt(self) -> str:
        return "Prompt do agente mestre..."
```

## Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## Licença

MIT License

## Autor

Desenvolvido como parte de um projeto de demonstração de arquitetura multi-agente.
