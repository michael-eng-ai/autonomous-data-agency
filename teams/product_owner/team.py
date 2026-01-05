"""
Product Owner Team - Grafo de Orquestração

Este módulo constrói o grafo LangGraph que orquestra os agentes do time
de Product Owner. O grafo define o fluxo de trabalho entre os agentes.
"""

from typing import TypedDict, Annotated, List, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from .agents import (
    requirements_analyst_agent,
    scope_writer_agent,
    task_delegator_agent
)


# =============================================================================
# Definição do Estado do Grafo
# =============================================================================

class AgentState(TypedDict):
    """
    Estado compartilhado entre os nós do grafo.
    
    Attributes:
        messages: Lista de mensagens trocadas (usuário e agentes)
        team_members: Lista de agentes disponíveis no time
        next: Próximo agente a ser executado
        scope_document: Documento de escopo gerado (quando disponível)
    """
    messages: Annotated[List[tuple], lambda x, y: x + y]
    team_members: List[str]
    next: str
    scope_document: str


# =============================================================================
# Nós do Grafo (Funções que os agentes executam)
# =============================================================================

def requirements_analyst_node(state: AgentState) -> dict:
    """
    Nó que invoca o agente Analista de Requisitos.
    
    Este agente analisa a solicitação do cliente e gera perguntas
    de esclarecimento para detalhar os requisitos.
    """
    # Pega a última mensagem do usuário
    user_input = state["messages"][-1][1]
    
    # Invoca o agente
    response = requirements_analyst_agent.invoke({"input": user_input})
    
    # Retorna o estado atualizado
    return {
        "messages": [("Analista de Requisitos", response.content)],
        "next": "ask_user"
    }


def scope_writer_node(state: AgentState) -> dict:
    """
    Nó que invoca o agente Escritor de Escopo.
    
    Este agente pega todas as informações coletadas e gera
    um documento de escopo formal.
    """
    # Compila todas as mensagens em um contexto
    context = "\n".join([f"{role}: {msg}" for role, msg in state["messages"]])
    
    # Invoca o agente
    response = scope_writer_agent.invoke({
        "input": f"Com base nas seguintes informações, crie o documento de escopo:\n\n{context}"
    })
    
    # Retorna o estado com o documento de escopo
    return {
        "messages": [("Escritor de Escopo", response.content)],
        "scope_document": response.content,
        "next": "task_delegator"
    }


def task_delegator_node(state: AgentState) -> dict:
    """
    Nó que invoca o agente Delegador de Tarefas (PO Mestre).
    
    Este agente analisa o escopo e decide quais times devem
    ser acionados para executar o projeto.
    """
    scope = state.get("scope_document", "")
    
    # Invoca o agente
    response = task_delegator_agent.invoke({
        "input": f"Analise o seguinte escopo e delegue as tarefas:\n\n{scope}"
    })
    
    return {
        "messages": [("PO Mestre", response.content)],
        "next": "end"
    }


def ask_user_node(state: AgentState) -> dict:
    """
    Nó de Interrupção: Pausa o grafo para obter feedback do usuário.
    
    Este nó representa um ponto onde o sistema precisa de input
    do usuário antes de continuar. Na prática, isso retornaria
    o controle para a aplicação principal.
    """
    # A última mensagem é do agente (as perguntas)
    agent_message = state["messages"][-1]
    
    print()
    print("=" * 60)
    print(f"{agent_message[0]} pergunta:")
    print("=" * 60)
    print(agent_message[1])
    print()
    
    # Termina o fluxo por enquanto - o usuário precisa responder
    return {"next": "end"}


# =============================================================================
# Função de Roteamento
# =============================================================================

def route_next(state: AgentState) -> Literal["ask_user", "scope_writer", "task_delegator", "end"]:
    """
    Função de roteamento que decide o próximo nó baseado no estado.
    """
    next_node = state.get("next", "end")
    
    if next_node == "ask_user":
        return "ask_user"
    elif next_node == "scope_writer":
        return "scope_writer"
    elif next_node == "task_delegator":
        return "task_delegator"
    else:
        return "end"


# =============================================================================
# Construção do Grafo
# =============================================================================

def get_po_team_graph():
    """
    Constrói e retorna o grafo LangGraph para o Time de Product Owner.
    
    O fluxo básico é:
    1. Analista de Requisitos faz perguntas
    2. Sistema aguarda resposta do usuário
    3. (Após respostas) Escritor de Escopo cria o documento
    4. PO Mestre delega as tarefas
    
    Returns:
        Um grafo LangGraph compilado e pronto para execução.
    """
    # Cria o grafo com o tipo de estado definido
    graph = StateGraph(AgentState)

    # Adiciona os nós ao grafo
    graph.add_node("Analista de Requisitos", requirements_analyst_node)
    graph.add_node("ask_user", ask_user_node)
    graph.add_node("scope_writer", scope_writer_node)
    graph.add_node("task_delegator", task_delegator_node)

    # Define o ponto de entrada
    graph.set_entry_point("Analista de Requisitos")
    
    # Define as arestas (transições entre nós)
    graph.add_edge("Analista de Requisitos", "ask_user")
    graph.add_edge("ask_user", END)
    graph.add_edge("scope_writer", "task_delegator")
    graph.add_edge("task_delegator", END)
    
    # Compila o grafo
    return graph.compile()


# =============================================================================
# Função para continuar o fluxo após input do usuário
# =============================================================================

def continue_with_user_response(graph, state: AgentState, user_response: str) -> AgentState:
    """
    Continua a execução do grafo após o usuário fornecer uma resposta.
    
    Args:
        graph: O grafo compilado
        state: O estado atual do grafo
        user_response: A resposta do usuário às perguntas
        
    Returns:
        O novo estado após processar a resposta
    """
    # Adiciona a resposta do usuário ao estado
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [("user", user_response)]
    new_state["next"] = "scope_writer"
    
    # Continua a execução
    for step in graph.stream(new_state):
        if "__end__" not in step:
            pass
    
    return new_state
