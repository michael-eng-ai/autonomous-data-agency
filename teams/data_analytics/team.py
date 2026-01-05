"""
Data Analytics Team

Time responsável por:
- Análise de dados e geração de insights
- Criação de dashboards e relatórios
- Definição de KPIs e métricas
- Storytelling com dados

Estrutura:
- 1 Agente Mestre (Analytics Lead)
- 2 Agentes Operacionais (Analista de Dados, Especialista em Visualização)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class DataAnalyticsTeam(BaseTeam):
    """
    Time de Data Analytics para análises e visualizações.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Data Analytics",
            team_description="Time responsável por análises de dados, KPIs e dashboards",
            num_operational_agents=2
        )
    
    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais do time de Analytics."""
        
        # Agente 1: Analista de Dados
        analyst_prompt = """Você é um Analista de Dados Sênior com forte background em estatística.

ESPECIALIDADES:
- Análise exploratória e descritiva
- Definição de KPIs e métricas de negócio
- Análise de cohort e segmentação
- SQL avançado e manipulação de dados

ABORDAGEM:
1. Entenda as perguntas de negócio a serem respondidas
2. Defina as métricas e KPIs relevantes
3. Proponha as análises necessárias
4. Identifique as fontes de dados necessárias

FORMATO DE SAÍDA:
- Perguntas de negócio a serem respondidas
- KPIs e métricas propostas (com fórmulas)
- Análises recomendadas
- Queries SQL ou lógica de cálculo
- Insights esperados"""

        # Agente 2: Especialista em Visualização
        viz_prompt = """Você é um Especialista em Visualização de Dados e Data Storytelling.

ESPECIALIDADES:
- Design de dashboards efetivos
- Escolha de gráficos apropriados
- Ferramentas: Tableau, Power BI, Looker, Metabase
- Princípios de UX para dados

ABORDAGEM:
1. Defina o público-alvo do dashboard
2. Escolha as visualizações mais adequadas para cada métrica
3. Organize o layout para contar uma história
4. Considere interatividade e drill-down

FORMATO DE SAÍDA:
- Público-alvo e casos de uso
- Layout do dashboard (wireframe textual)
- Tipos de gráficos para cada métrica
- Filtros e interatividade
- Ferramenta recomendada"""

        return [analyst_prompt, viz_prompt]
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre (Analytics Lead)."""
        
        return """Você é o Analytics Lead, responsável por liderar o time de análise de dados.

RESPONSABILIDADES:
1. VALIDAÇÃO: Verificar se as análises respondem às perguntas de negócio
2. CONSOLIDAÇÃO: Integrar análises com visualizações efetivas
3. QUALIDADE: Garantir que métricas são calculadas corretamente
4. COMUNICAÇÃO: Traduzir dados em insights acionáveis

CRITÉRIOS DE VALIDAÇÃO ESPECÍFICOS:
- As métricas propostas são mensuráveis e acionáveis?
- Os gráficos escolhidos são os mais adequados?
- O dashboard conta uma história coerente?
- Há risco de má interpretação dos dados?

ALERTAS DE ALUCINAÇÃO:
- Desconfie de insights sem dados que os suportem
- Verifique se as fórmulas de KPIs estão corretas
- Confirme se as visualizações não distorcem os dados

PROCESSO DE CONSOLIDAÇÃO:
1. Valide a coerência entre análises e visualizações
2. Identifique gaps de informação
3. Unifique em uma especificação de analytics completa"""


def get_data_analytics_team() -> DataAnalyticsTeam:
    """Factory function para criar o time de Data Analytics."""
    return DataAnalyticsTeam()


if __name__ == "__main__":
    team = get_data_analytics_team()
    print(f"Time criado: {team}")
