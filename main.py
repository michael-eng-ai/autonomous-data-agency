"""
Autonomous Data Agency - Main Entry Point

Este é o ponto de entrada principal do framework.
Demonstra como usar a agência de agentes para executar um projeto completo.

Arquitetura:
- Cada time tem 1 Agente Mestre + 2 Agentes Operacionais
- Cada agente operacional usa um LLM diferente (diversidade)
- O Agente Mestre valida, consolida e previne alucinações
- O Orquestrador coordena todos os times

Times Disponíveis:
- Product Owner: Requisitos e escopo
- Project Manager: Planejamento e gestão
- Data Engineering: Arquitetura e pipelines
- Data Science: ML e MLOps
- Data Analytics: Análises e dashboards
- DevOps: Infraestrutura e CI/CD
- QA: Testes e qualidade
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Verifica se a API key está configurada
if not os.getenv("OPENAI_API_KEY"):
    print("ERRO: OPENAI_API_KEY não configurada.")
    print("Por favor, crie um arquivo .env com sua chave de API.")
    sys.exit(1)

from core import (
    AgencyOrchestrator,
    get_agency_orchestrator,
    ProjectPhase
)
from config import describe_llm_diversity


def run_demo():
    """Executa uma demonstração do framework."""
    
    print("\n" + "="*70)
    print(" AUTONOMOUS DATA AGENCY - DEMONSTRAÇÃO ")
    print("="*70 + "\n")
    
    # Mostra a configuração de LLMs
    describe_llm_diversity()
    
    # Inicializa o orquestrador
    print("\n[1] Inicializando o Orquestrador da Agência...")
    orchestrator = get_agency_orchestrator()
    
    print(f"\n[2] Times disponíveis: {list(orchestrator.teams.keys())}")
    
    # Inicia um projeto de exemplo
    print("\n[3] Iniciando projeto de exemplo...")
    project = orchestrator.start_project(
        project_name="Bot de Análise de Clientes",
        client_request="""
        Eu quero ter um bot de análise de clientes para ter o perfil dele,
        saber o que ele comprou, o que ele pode comprar mais, quando ele compra,
        qual será a próxima compra dele em estimativa, que produtos ele compra
        e quais ele poderia comprar, lembretes de aniversário e datas especiais
        para chamar o cliente e ter mais proximidade dele, e com tudo isso
        aumentar minhas vendas e criar ou melhorar fidelidade do cliente.
        """
    )
    
    # Executa o time de Product Owner
    print("\n[4] Executando Time de Product Owner...")
    po_output = orchestrator.execute_team(
        "product_owner",
        project.client_request
    )
    
    print("\n" + "-"*50)
    print("SAÍDA DO TIME DE PRODUCT OWNER:")
    print("-"*50)
    print(po_output.final_output[:1000] + "..." if len(po_output.final_output) > 1000 else po_output.final_output)
    
    # Mostra o resumo do projeto
    print(orchestrator.get_project_summary())
    
    return orchestrator, project


def run_full_workflow():
    """Executa um workflow completo com múltiplos times."""
    
    print("\n" + "="*70)
    print(" WORKFLOW COMPLETO - MÚLTIPLOS TIMES ")
    print("="*70 + "\n")
    
    orchestrator = get_agency_orchestrator()
    
    # Inicia o projeto
    project = orchestrator.start_project(
        project_name="Sistema de Recomendação de Produtos",
        client_request="Preciso de um sistema de recomendação de produtos para minha loja online."
    )
    
    # Executa workflow com múltiplos times
    outputs = orchestrator.execute_workflow(
        teams_sequence=["product_owner", "project_manager", "data_engineering"],
        initial_task=project.client_request
    )
    
    # Validação global
    print("\n[5] Executando Validação Global...")
    validation = orchestrator.global_validation(outputs)
    
    print("\n" + "="*50)
    print("RESULTADO DA VALIDAÇÃO GLOBAL")
    print("="*50)
    print(f"Válido: {validation.is_valid}")
    print(f"Score de Qualidade: {validation.overall_quality_score * 100:.0f}%")
    print("\nEntrega Consolidada:")
    print("-"*50)
    print(validation.consolidated_output[:2000] + "..." if len(validation.consolidated_output) > 2000 else validation.consolidated_output)
    
    return orchestrator, validation


def interactive_mode():
    """Modo interativo para conversar com a agência."""
    
    print("\n" + "="*70)
    print(" MODO INTERATIVO ")
    print("="*70)
    print("\nBem-vindo à Agência Autônoma de Dados!")
    print("Digite sua solicitação de projeto ou 'sair' para encerrar.\n")
    
    orchestrator = get_agency_orchestrator()
    
    while True:
        user_input = input("\nVocê: ").strip()
        
        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("\nObrigado por usar a Agência Autônoma de Dados!")
            break
        
        if not user_input:
            continue
        
        # Inicia um projeto com a solicitação do usuário
        project = orchestrator.start_project(
            project_name="Projeto do Usuário",
            client_request=user_input
        )
        
        # Executa o time de PO para análise inicial
        print("\n[Analisando sua solicitação com o Time de Product Owner...]")
        po_output = orchestrator.execute_team("product_owner", user_input)
        
        print("\n" + "-"*50)
        print("ANÁLISE DO TIME DE PRODUCT OWNER:")
        print("-"*50)
        print(po_output.final_output)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Data Agency")
    parser.add_argument(
        "--mode",
        choices=["demo", "workflow", "interactive"],
        default="demo",
        help="Modo de execução: demo, workflow, ou interactive"
    )
    
    args = parser.parse_args()
    
    if args.mode == "demo":
        run_demo()
    elif args.mode == "workflow":
        run_full_workflow()
    elif args.mode == "interactive":
        interactive_mode()
