# Autonomous Data Agency Framework

Um framework Python para criar e orquestrar times de agentes de IA autônomos para projetos de dados. Cada time é composto por múltiplos agentes usando diferentes LLMs para garantir diversidade de pensamento e validação contra alucinações.

## Novidades da v2.0

- **Sistema de Conhecimento em 3 Camadas**: Knowledge Base (YAML), RAG Engine (ChromaDB), Project Memory (SQLite)
- **Fundamentação de Respostas**: Agentes agora têm acesso a best practices, checklists e anti-patterns
- **Memória Persistente**: Decisões e preferências são armazenadas por projeto
- **Busca Semântica**: RAG para conhecimento dinâmico e contextual

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

## Sistema de Conhecimento (3 Camadas)

O framework inclui um sistema de conhecimento híbrido que fundamenta as respostas dos agentes:

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE MANAGER                             │
│              (Gerenciador Unificado de Conhecimento)             │
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

### Camada 1: Knowledge Base (YAML)
- **Propósito**: Best practices, checklists, anti-patterns
- **Características**: Rápido, determinístico, versionável no Git
- **Localização**: `knowledge/*/best_practices.yaml`

### Camada 2: RAG Engine (ChromaDB)
- **Propósito**: Conhecimento dinâmico e busca semântica
- **Características**: Flexível, extensível, contextual
- **Tecnologia**: ChromaDB para armazenamento vetorial

### Camada 3: Project Memory (SQLite)
- **Propósito**: Memória de longo prazo por projeto
- **Características**: Decisões, preferências, histórico
- **Persistência**: Banco SQLite local

## Princípios de Design

1. **Diversidade de LLMs**: Cada agente operacional usa um modelo diferente (GPT-4.1-mini, GPT-4.1-nano, Gemini-2.5-flash) para evitar vieses e aumentar a qualidade das soluções.

2. **Validação Hierárquica**: Agentes Mestres validam e consolidam as respostas dos operacionais, detectando alucinações e inconsistências.

3. **Fundamentação em Conhecimento**: Respostas são validadas contra best practices e anti-patterns da Knowledge Base.

4. **Prevenção de Alucinações**: Sistema de múltiplas camadas de validação para garantir que as respostas são factualmente corretas.

5. **Modularidade**: Cada time é independente e pode ser usado isoladamente ou em conjunto.

## Times Disponíveis

| Time | Domínio | Agentes Operacionais |
|------|---------|---------------------|
| **Product Owner** | `product_owner` | Analista de Requisitos, Escritor de Escopo |
| **Project Manager** | `project_manager` | Planejador de Projeto, Gestor de Riscos |
| **Data Engineering** | `data_engineering` | Arquiteto de Dados, Dev de Pipeline |
| **Data Science** | `data_science` | Cientista de Dados, Engenheiro de ML |
| **Data Analytics** | `data_analytics` | Analista de Dados, Especialista em Viz |
| **DevOps** | `devops` | Eng. de Infraestrutura, Especialista CI/CD |
| **QA** | `qa` | Eng. de Testes, Especialista em Data Quality |

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
from core import get_agency_orchestrator, get_knowledge_manager

# Inicializa o orquestrador
orchestrator = get_agency_orchestrator()

# Opcional: Indexa conhecimento no RAG
km = get_knowledge_manager()
if km.rag_engine.is_available():
    km.rag_engine.index_knowledge_base(km.knowledge_base)

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

### Usando o Sistema de Conhecimento

```python
from core.knowledge import (
    get_knowledge_base,
    get_rag_engine,
    get_project_memory,
    MemoryType
)

# Knowledge Base (YAML)
kb = get_knowledge_base()
de_practices = kb.get_best_practices("data_engineering")
checklists = kb.get_checklists("qa")

# RAG Engine (ChromaDB)
rag = get_rag_engine()
if rag.is_available():
    results = rag.search("como orquestrar pipelines de dados", n_results=3)
    for r in results:
        print(f"Score: {r.relevance_score:.2%} - {r.content[:100]}...")

# Project Memory (SQLite)
memory = get_project_memory()
memory.create_project("proj_001", "Meu Projeto", "Cliente XYZ")
memory.store_decision(
    project_id="proj_001",
    decision_key="database_choice",
    decision="PostgreSQL",
    rationale="Melhor suporte a JSON e extensibilidade",
    alternatives=["MySQL", "MongoDB"]
)

# Recupera contexto do projeto
context = memory.format_context_for_prompt("proj_001")
print(context)
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
│   ├── agency_orchestrator.py  # Orquestrador principal
│   └── knowledge/         # Sistema de conhecimento
│       ├── __init__.py
│       ├── knowledge_base.py   # Camada 1: YAML
│       ├── rag_engine.py       # Camada 2: ChromaDB
│       └── project_memory.py   # Camada 3: SQLite
│
├── knowledge/             # Arquivos de conhecimento (YAML)
│   ├── product_owner/
│   │   └── best_practices.yaml
│   ├── data_engineering/
│   │   └── best_practices.yaml
│   ├── data_science/
│   │   └── best_practices.yaml
│   ├── devops/
│   │   └── best_practices.yaml
│   ├── qa/
│   │   └── best_practices.yaml
│   └── shared/
│       └── general_standards.yaml
│
├── teams/                 # Times de agentes
│   ├── __init__.py
│   ├── product_owner/
│   ├── project_manager/
│   ├── data_engineering/
│   ├── data_science/
│   ├── data_analytics/
│   ├── devops/
│   └── qa/
│
└── data/                  # Dados persistentes (gerado automaticamente)
    ├── vectordb/          # ChromaDB
    └── memory/            # SQLite
```

## Fluxo de Trabalho

1. **Recebimento da Solicitação**: O cliente faz uma solicitação de projeto.

2. **Carregamento de Conhecimento**: O sistema carrega best practices, histórico do projeto e conhecimento relevante.

3. **Análise de Requisitos**: O time de PO analisa a solicitação com múltiplos agentes, cada um oferecendo uma perspectiva diferente, fundamentada no conhecimento base.

4. **Validação do Mestre**: O Agente Mestre do time consolida as respostas, detecta alucinações e valida contra anti-patterns.

5. **Armazenamento de Decisões**: Decisões importantes são armazenadas na Project Memory.

6. **Delegação**: O orquestrador delega tarefas para outros times conforme necessário.

7. **Validação Global**: O Agente Mestre Global revisa todas as saídas, garantindo consistência e qualidade.

8. **Entrega**: O resultado final é entregue ao cliente.

## Criando um Novo Time

```python
from core.base_team import BaseTeam
from typing import List

class MeuNovoTime(BaseTeam):
    def __init__(self):
        super().__init__(
            team_name="Meu Novo Time",
            team_description="Descrição do time",
            domain="meu_dominio",  # Deve corresponder a uma pasta em knowledge/
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

## Adicionando Conhecimento

### Criar arquivo YAML para um novo domínio:

```yaml
# knowledge/meu_dominio/best_practices.yaml
metadata:
  version: "1.0.0"
  last_updated: "2026-01-05"
  domain: "meu_dominio"
  type: "best_practices"

principles:
  - name: "Princípio 1"
    description: "Descrição do princípio"
    guidelines:
      - "Diretriz 1"
      - "Diretriz 2"

checklists:
  review_checklist:
    - "Item 1"
    - "Item 2"

anti_patterns:
  - name: "Anti-pattern 1"
    description: "O que evitar"
    solution: "Como resolver"
```

## Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## Licença

MIT License

## Autor

Desenvolvido por [Michael](https://github.com/michael-eng-ai)
