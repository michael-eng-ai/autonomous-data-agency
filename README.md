# Autonomous Data Agency Framework

Este repositório contém um framework para construir uma "Agência Autônoma" de agentes de IA usando LangGraph. A arquitetura é hierárquica e recursiva, permitindo que "times" de agentes (que são grafos LangGraph) chamem outros times para delegar tarefas.

## Arquitetura

O framework implementa uma estrutura organizacional de agentes de IA:

- **PO Mestre (Product Owner):** O ponto de entrada principal. Ele recebe os requisitos do cliente e os traduz em tarefas para os times especialistas.
- **Times de Especialistas:** Cada time é um sub-grafo LangGraph com um "Líder" (supervisor) e "Trabalhadores" (agentes que executam tarefas).
  - `product_owner`: Time responsável por interagir com o cliente e definir o escopo.
  - `data_engineering`: Time para tarefas de pipeline de dados.
  - `ml_ops`: Time para tarefas de Machine Learning.
  - `qa`: Time para testes e qualidade.

## Estrutura do Projeto

```
autonomous-data-agency/
├── .gitignore
├── .env.example
├── README.md
├── requirements.txt
├── main.py
└── teams/
    ├── __init__.py
    └── product_owner/
        ├── __init__.py
        ├── agents.py
        └── team.py
```

## Como Usar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Configure suas chaves de API

Copie o arquivo de exemplo e adicione sua chave da OpenAI:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```
OPENAI_API_KEY="sua_chave_aqui"
```

### 3. Execute o Ponto de Entrada

O arquivo `main.py` simula uma interação com a agência:

```bash
python main.py
```

## Conceitos Principais

### Agentes
Cada agente é uma combinação de um prompt de sistema (que define sua "persona") e um modelo de linguagem (LLM). Os agentes são definidos no arquivo `agents.py` de cada time.

### Times
Um time é um grafo LangGraph que orquestra múltiplos agentes. O grafo define o fluxo de trabalho: quem fala primeiro, quem fala depois, e quando parar para pedir input do usuário.

### Interrupções
O framework suporta "interrupções" - pontos no fluxo onde o sistema para e aguarda input do usuário antes de continuar.

## Extensibilidade

Para adicionar um novo time de especialistas:

1. Crie um novo diretório em `teams/` (ex: `teams/data_engineering/`)
2. Defina os agentes em `agents.py`
3. Construa o grafo do time em `team.py`
4. Importe e conecte o novo time no `main.py`

## Licença

MIT License
