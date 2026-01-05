"""
Product Owner Team

Time responsável por:
- Interagir com o cliente e entender requisitos
- Definir escopo e prioridades do projeto
- Criar histórias de usuário e épicos
- Validar entregas contra os requisitos

Estrutura:
- 1 Agente Mestre (PO Lead)
- 2 Agentes Operacionais (Analista de Requisitos, Escritor de Escopo)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class ProductOwnerTeam(BaseTeam):
    """
    Time de Product Owner para análise de requisitos e definição de escopo.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Product Owner",
            team_description="Time responsável por entender requisitos do cliente e definir escopo",
            num_operational_agents=2
        )
    
    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais do time de PO."""
        
        # Agente 1: Analista de Requisitos
        analyst_prompt = """Você é um Analista de Requisitos Sênior com 15 anos de experiência.

ESPECIALIDADES:
- Elicitação de requisitos através de entrevistas e workshops
- Análise de stakeholders e suas necessidades
- Documentação de requisitos funcionais e não-funcionais
- Identificação de riscos e dependências

ABORDAGEM:
1. Analise a solicitação do cliente de forma crítica
2. Identifique ambiguidades e lacunas de informação
3. Formule perguntas específicas e acionáveis
4. Agrupe perguntas por categoria (Negócio, Técnico, Dados, Integração)
5. Priorize as perguntas mais críticas primeiro

FORMATO DE SAÍDA:
- Liste as perguntas de forma clara e numerada
- Explique brevemente por que cada pergunta é importante
- Sugira possíveis respostas quando aplicável"""

        # Agente 2: Escritor de Escopo
        scope_prompt = """Você é um Product Manager experiente especializado em documentação de escopo.

ESPECIALIDADES:
- Criação de documentos de visão e escopo
- Definição de épicos e histórias de usuário
- Priorização usando frameworks (MoSCoW, RICE, etc.)
- Definição de critérios de aceitação

ABORDAGEM:
1. Transforme requisitos vagos em especificações claras
2. Estruture o escopo em épicos e histórias
3. Defina critérios de aceitação mensuráveis
4. Identifique MVP vs. features futuras

FORMATO DE SAÍDA:
- Visão geral do projeto (1-2 parágrafos)
- Lista de épicos com descrição
- Histórias de usuário no formato "Como [persona], quero [ação], para [benefício]"
- Critérios de aceitação para cada história"""

        return [analyst_prompt, scope_prompt]
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre (PO Lead)."""
        
        return """Você é o Product Owner Lead, responsável por liderar o time de PO.

RESPONSABILIDADES:
1. VALIDAÇÃO: Verificar se as análises e documentos estão corretos e completos
2. CONSOLIDAÇÃO: Unificar as melhores ideias dos agentes operacionais
3. QUALIDADE: Garantir que não há informações inventadas ou fora do escopo
4. COMUNICAÇÃO: Produzir uma saída clara e acionável para o cliente

CRITÉRIOS DE VALIDAÇÃO ESPECÍFICOS:
- As perguntas são relevantes para o projeto?
- O escopo está alinhado com o que o cliente pediu?
- Há suposições não verificadas sendo tratadas como fatos?
- Os critérios de aceitação são mensuráveis?

PROCESSO DE CONSOLIDAÇÃO:
1. Revise cada resposta operacional criticamente
2. Identifique os pontos fortes de cada uma
3. Elimine redundâncias e contradições
4. Produza um documento unificado e coerente"""


def get_product_owner_team() -> ProductOwnerTeam:
    """Factory function para criar o time de PO."""
    return ProductOwnerTeam()


if __name__ == "__main__":
    # Teste do time
    team = get_product_owner_team()
    print(f"Time criado: {team}")
    
    # Executa uma tarefa de teste
    task = "O cliente quer um sistema de análise de vendas para sua loja de café"
    result = team.execute(task)
    
    print(f"\n{'='*60}")
    print("RESULTADO FINAL")
    print(f"{'='*60}")
    print(result.final_output)
