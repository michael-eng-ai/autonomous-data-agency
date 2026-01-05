"""
Autonomous Data Agency - Ponto de Entrada Principal

Este arquivo serve como o ponto de entrada para interagir com a agência de agentes.
Ele inicializa o time do Product Owner e simula uma interação com o cliente.
"""

import os
import uuid
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (ex: OPENAI_API_KEY)
load_dotenv()

# Importa o grafo do time de Product Owner
from teams.product_owner.team import get_po_team_graph


def run_agency():
    """
    Ponto de entrada principal para interagir com a agência.
    
    Este método:
    1. Inicializa o time do Product Owner
    2. Recebe a solicitação inicial do cliente
    3. Executa o grafo de agentes
    4. Apresenta as perguntas de esclarecimento
    """
    print("=" * 60)
    print("Bem-vindo à Agência de Dados Autônoma!")
    print("=" * 60)
    print()

    # Inicializa o grafo do time do Product Owner
    po_team_graph = get_po_team_graph()

    # Solicita a primeira interação com o cliente
    print("Por favor, descreva seu projeto ou necessidade:")
    print("(Exemplo: 'Quero um sistema de análise de clientes para minha loja')")
    print()
    initial_request = input("> ")

    # Define o estado inicial para a execução do grafo
    # Usamos um ID de thread para manter o estado da conversa
    thread_id = str(uuid.uuid4())
    initial_state = {
        "messages": [("user", initial_request)],
        "team_members": ["Analista de Requisitos", "Escritor de Escopo"],
        "next": "Analista de Requisitos"
    }

    print()
    print("-" * 60)
    print("PO Mestre: 'Recebi sua solicitação. Vou pedir ao meu")
    print("Analista de Requisitos para detalhar isso.'")
    print("-" * 60)
    print()

    # Executa o grafo do time de PO
    # O grafo irá parar quando precisar de uma resposta do usuário (interrupção)
    config = {"recursion_limit": 100, "configurable": {"thread_id": thread_id}}
    
    for step in po_team_graph.stream(initial_state, config):
        # Processa cada passo do grafo
        if "__end__" not in step:
            # Aqui podemos adicionar lógica para processar cada nó
            pass
    
    print()
    print("=" * 60)
    print("O sistema aguarda suas respostas para continuar o processo.")
    print("=" * 60)


if __name__ == "__main__":
    run_agency()
