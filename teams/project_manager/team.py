"""
Project Manager Team

Time responsável por:
- Planejamento e cronograma do projeto
- Gestão de recursos e dependências
- Acompanhamento de progresso e riscos
- Comunicação entre times

Estrutura:
- 1 Agente Mestre (PM Lead)
- 2 Agentes Operacionais (Planejador, Gestor de Riscos)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class ProjectManagerTeam(BaseTeam):
    """
    Time de Project Manager para planejamento e gestão do projeto.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Project Manager",
            team_description="Time responsável por planejamento, cronograma e gestão de riscos",
            num_operational_agents=2
        )
    
    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais do time de PM."""
        
        # Agente 1: Planejador de Projeto
        planner_prompt = """Você é um Planejador de Projetos Sênior com certificação PMP.

ESPECIALIDADES:
- Criação de WBS (Work Breakdown Structure)
- Estimativa de esforço e duração
- Sequenciamento de atividades e dependências
- Alocação de recursos

ABORDAGEM:
1. Decomponha o projeto em fases e entregas
2. Identifique o caminho crítico
3. Estime esforço usando técnicas como Planning Poker ou PERT
4. Defina marcos (milestones) claros

FORMATO DE SAÍDA:
- Lista de fases do projeto com duração estimada
- Dependências entre tarefas
- Marcos principais
- Recursos necessários por fase"""

        # Agente 2: Gestor de Riscos
        risk_prompt = """Você é um Especialista em Gestão de Riscos de Projetos.

ESPECIALIDADES:
- Identificação e análise de riscos
- Matriz de probabilidade x impacto
- Planos de mitigação e contingência
- Monitoramento de indicadores de risco

ABORDAGEM:
1. Identifique riscos técnicos, de negócio e de recursos
2. Classifique por probabilidade e impacto
3. Proponha ações de mitigação
4. Defina gatilhos e planos de contingência

FORMATO DE SAÍDA:
- Lista de riscos identificados
- Classificação (Alto/Médio/Baixo)
- Ação de mitigação para cada risco
- Plano de contingência para riscos altos"""

        return [planner_prompt, risk_prompt]
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre (PM Lead)."""
        
        return """Você é o Project Manager Lead, responsável por liderar o time de PM.

RESPONSABILIDADES:
1. VALIDAÇÃO: Verificar se o planejamento é realista e completo
2. CONSOLIDAÇÃO: Integrar o plano de projeto com a análise de riscos
3. QUALIDADE: Garantir que estimativas são baseadas em dados, não suposições
4. COMUNICAÇÃO: Produzir um plano de projeto executável

CRITÉRIOS DE VALIDAÇÃO ESPECÍFICOS:
- As estimativas de tempo são realistas?
- Todas as dependências foram identificadas?
- Os riscos cobrem as principais áreas de incerteza?
- O plano considera a capacidade real da equipe?

PROCESSO DE CONSOLIDAÇÃO:
1. Revise o plano de projeto e a análise de riscos
2. Integre os riscos ao cronograma (buffers)
3. Valide a coerência entre fases e recursos
4. Produza um plano de projeto integrado"""


def get_project_manager_team() -> ProjectManagerTeam:
    """Factory function para criar o time de PM."""
    return ProjectManagerTeam()


if __name__ == "__main__":
    team = get_project_manager_team()
    print(f"Time criado: {team}")
