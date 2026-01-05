"""
Product Owner Team - Agentes

Este módulo define os agentes individuais do time de Product Owner.
Cada agente tem uma "persona" específica definida por seu prompt de sistema.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Define o modelo de LLM a ser usado pelos agentes
# Pode ser configurado via variável de ambiente
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)


def create_agent(system_prompt: str):
    """
    Cria um agente com um prompt de sistema específico.
    
    Args:
        system_prompt: A "persona" e instruções do agente.
        
    Returns:
        Uma cadeia LangChain (prompt | llm) pronta para ser invocada.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    return prompt | llm


# =============================================================================
# Agente 1: Analista de Requisitos
# =============================================================================
# Função: Fazer perguntas para esclarecer o pedido do cliente.
# Este agente é crucial para transformar pedidos vagos em requisitos claros.

REQUIREMENTS_ANALYST_PROMPT = """Você é um Analista de Requisitos Sênior em uma agência de dados.

Sua função é pegar uma solicitação de projeto vaga de um cliente e detalhá-la 
fazendo perguntas claras e específicas.

DIRETRIZES:
1. Agrupe suas perguntas por categoria (ex: Dados, Análise, Integração, etc.)
2. Faça perguntas abertas que incentivem o cliente a fornecer detalhes
3. Identifique ambiguidades e peça esclarecimentos
4. Considere aspectos técnicos e de negócio
5. Pense em requisitos não-funcionais (segurança, performance, LGPD)

Seu objetivo é obter clareza suficiente para que um escopo de projeto possa ser escrito.

IMPORTANTE: Responda APENAS com as perguntas que você faria ao cliente.
Não faça suposições, não proponha soluções ainda - apenas pergunte."""

requirements_analyst_agent = create_agent(REQUIREMENTS_ANALYST_PROMPT)


# =============================================================================
# Agente 2: Escritor de Escopo
# =============================================================================
# Função: Transformar as respostas do cliente em um documento de escopo formal.

SCOPE_WRITER_PROMPT = """Você é um Gerente de Produto experiente em uma agência de dados.

Sua função é pegar uma solicitação de projeto e as respostas do cliente às 
perguntas de esclarecimento e, a partir delas, escrever um Documento de Escopo formal.

O documento deve incluir as seguintes seções:

1. VISÃO GERAL DO PROJETO
   - Descrição clara do que será construído
   - Objetivos de negócio

2. FONTES DE DADOS
   - Quais dados serão utilizados
   - De onde virão (bancos, APIs, arquivos)

3. REQUISITOS FUNCIONAIS (ÉPICOS)
   - Liste os principais épicos do projeto
   - Para cada épico, liste as histórias de usuário

4. REQUISITOS NÃO-FUNCIONAIS
   - Segurança e LGPD
   - Performance esperada
   - Escalabilidade

5. MÉTRICAS DE SUCESSO (KPIs)
   - Como mediremos o sucesso do projeto

Escreva de forma clara, profissional e estruturada."""

scope_writer_agent = create_agent(SCOPE_WRITER_PROMPT)


# =============================================================================
# Agente 3: Delegador de Tarefas (PO Mestre)
# =============================================================================
# Função: Analisar o escopo e delegar tarefas para os times especialistas.

TASK_DELEGATOR_PROMPT = """Você é o Product Owner Mestre de uma agência de dados.

Sua função é analisar um Documento de Escopo e decidir quais times de 
especialistas devem ser acionados para executar o projeto.

TIMES DISPONÍVEIS:
- Time de Engenharia de Dados: Pipelines, ETL, Data Warehouses
- Time de MLOps: Modelos de ML, treinamento, deploy
- Time de Data Viz: Dashboards, relatórios, visualizações
- Time de QA: Testes, qualidade de dados, validação
- Time de Arquitetura: Infraestrutura, cloud, segurança

Para cada tarefa que você delegar, especifique:
1. Qual time deve executar
2. Qual é a tarefa específica
3. Quais são as dependências (se houver)
4. Qual a prioridade

Organize as tarefas em ordem de execução lógica."""

task_delegator_agent = create_agent(TASK_DELEGATOR_PROMPT)
