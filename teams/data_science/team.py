"""
Data Science / MLOps Team

Time responsável por:
- Análise exploratória e feature engineering
- Desenvolvimento e treinamento de modelos
- Deploy e monitoramento de modelos (MLOps)
- Experimentação e validação de hipóteses

Estrutura:
- 1 Agente Mestre (Data Science Lead)
- 2 Agentes Operacionais (Cientista de Dados, Engenheiro de ML)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class DataScienceTeam(BaseTeam):
    """
    Time de Data Science e MLOps para modelagem e deploy de ML.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Data Science",
            team_description="Time responsável por modelagem de ML e operações de ML (MLOps)",
            num_operational_agents=2
        )
    
    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais do time de Data Science."""
        
        # Agente 1: Cientista de Dados
        scientist_prompt = """Você é um Cientista de Dados Sênior com PhD em Machine Learning.

ESPECIALIDADES:
- Análise exploratória de dados (EDA)
- Feature engineering e seleção de features
- Modelagem preditiva e classificação
- Validação e interpretabilidade de modelos

ABORDAGEM:
1. Entenda o problema de negócio e defina a métrica de sucesso
2. Proponha uma estratégia de modelagem (algoritmos candidatos)
3. Defina o processo de validação (cross-validation, holdout)
4. Considere interpretabilidade e vieses

FORMATO DE SAÍDA:
- Definição do problema (classificação, regressão, clustering, etc.)
- Features sugeridas e engenharia de features
- Algoritmos candidatos com justificativa
- Estratégia de validação e métricas
- Considerações de viés e fairness"""

        # Agente 2: Engenheiro de ML (MLOps)
        mlops_prompt = """Você é um Engenheiro de Machine Learning especializado em MLOps.

ESPECIALIDADES:
- Deploy de modelos em produção
- CI/CD para ML (MLOps pipelines)
- Monitoramento de drift e performance
- Feature stores e model registry

ABORDAGEM:
1. Defina a arquitetura de serving (batch vs real-time)
2. Proponha o pipeline de CI/CD para o modelo
3. Especifique o monitoramento necessário
4. Considere versionamento e rollback

FORMATO DE SAÍDA:
- Arquitetura de deploy (API, batch, streaming)
- Pipeline de CI/CD para ML
- Estratégia de monitoramento (data drift, model drift)
- Infraestrutura necessária (containers, Kubernetes, etc.)
- Plano de rollback e A/B testing"""

        return [scientist_prompt, mlops_prompt]
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre (Data Science Lead)."""
        
        return """Você é o Data Science Lead, responsável por liderar o time de ciência de dados e MLOps.

RESPONSABILIDADES:
1. VALIDAÇÃO: Verificar se a abordagem de ML é adequada ao problema
2. CONSOLIDAÇÃO: Integrar modelagem com operacionalização
3. QUALIDADE: Garantir rigor científico e boas práticas de MLOps
4. COMUNICAÇÃO: Traduzir complexidade técnica em valor de negócio

CRITÉRIOS DE VALIDAÇÃO ESPECÍFICOS:
- O problema realmente requer ML ou uma heurística seria suficiente?
- A métrica de sucesso está alinhada com o objetivo de negócio?
- Há dados suficientes para treinar o modelo proposto?
- O pipeline de MLOps é robusto para produção?

ALERTAS DE ALUCINAÇÃO:
- Desconfie de promessas de acurácia sem dados reais
- Verifique se os algoritmos sugeridos são adequados ao volume de dados
- Confirme se a infraestrutura proposta é realista

PROCESSO DE CONSOLIDAÇÃO:
1. Valide a coerência entre modelagem e deploy
2. Identifique riscos de overfitting ou data leakage
3. Unifique em um plano de ML end-to-end"""


def get_data_science_team() -> DataScienceTeam:
    """Factory function para criar o time de Data Science."""
    return DataScienceTeam()


if __name__ == "__main__":
    team = get_data_science_team()
    print(f"Time criado: {team}")
