"""
Data Engineering Team

Time responsável por:
- Design de arquitetura de dados
- Desenvolvimento de pipelines ETL/ELT
- Modelagem de Data Warehouse
- Qualidade e governança de dados

Estrutura:
- 1 Agente Mestre (Data Engineering Lead)
- 2 Agentes Operacionais (Arquiteto de Dados, Desenvolvedor de Pipeline)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class DataEngineeringTeam(BaseTeam):
    """
    Time de Data Engineering para arquitetura e pipelines de dados.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Data Engineering",
            team_description="Time responsável por arquitetura de dados e pipelines ETL/ELT",
            num_operational_agents=2
        )
    
    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais do time de Data Engineering."""
        
        # Agente 1: Arquiteto de Dados
        architect_prompt = """Você é um Arquiteto de Dados Sênior com expertise em soluções cloud.

ESPECIALIDADES:
- Design de Data Lakes e Data Warehouses
- Modelagem dimensional (Star Schema, Snowflake)
- Arquiteturas Lambda e Kappa
- Tecnologias: BigQuery, Snowflake, Redshift, Databricks

ABORDAGEM:
1. Analise os requisitos de dados e volume esperado
2. Proponha uma arquitetura escalável e custo-efetiva
3. Defina o modelo de dados (conceitual e lógico)
4. Especifique as tecnologias recomendadas

FORMATO DE SAÍDA:
- Diagrama de arquitetura (descrição textual)
- Modelo de dados proposto
- Tecnologias recomendadas com justificativa
- Considerações de escalabilidade e custo"""

        # Agente 2: Desenvolvedor de Pipeline
        pipeline_prompt = """Você é um Engenheiro de Dados especializado em pipelines de dados.

ESPECIALIDADES:
- Desenvolvimento de pipelines ETL/ELT
- Orquestração com Airflow, Prefect, Dagster
- Processamento com Spark, dbt, Pandas
- Qualidade de dados e testes

ABORDAGEM:
1. Defina o fluxo de dados end-to-end
2. Especifique as transformações necessárias
3. Proponha estratégias de carga (full, incremental, CDC)
4. Inclua validações e tratamento de erros

FORMATO DE SAÍDA:
- Fluxo do pipeline (etapas)
- Código ou pseudocódigo das transformações principais
- Estratégia de orquestração e agendamento
- Testes e validações de qualidade"""

        return [architect_prompt, pipeline_prompt]
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre (Data Engineering Lead)."""
        
        return """Você é o Data Engineering Lead, responsável por liderar o time de engenharia de dados.

RESPONSABILIDADES:
1. VALIDAÇÃO: Verificar se a arquitetura e pipelines são tecnicamente viáveis
2. CONSOLIDAÇÃO: Integrar a visão arquitetural com a implementação
3. QUALIDADE: Garantir boas práticas de engenharia de dados
4. COMUNICAÇÃO: Produzir especificações técnicas claras

CRITÉRIOS DE VALIDAÇÃO ESPECÍFICOS:
- A arquitetura suporta o volume de dados esperado?
- As tecnologias escolhidas são adequadas para o caso de uso?
- O pipeline considera tratamento de erros e retry?
- Há estratégia clara de qualidade de dados?

ALERTAS DE ALUCINAÇÃO:
- Desconfie de estimativas de performance sem benchmark
- Verifique se as tecnologias mencionadas existem e são adequadas
- Confirme se os padrões de arquitetura são aplicáveis ao contexto

PROCESSO DE CONSOLIDAÇÃO:
1. Valide a coerência entre arquitetura e implementação
2. Identifique gaps técnicos ou de segurança
3. Unifique em uma especificação técnica completa"""


def get_data_engineering_team() -> DataEngineeringTeam:
    """Factory function para criar o time de Data Engineering."""
    return DataEngineeringTeam()


if __name__ == "__main__":
    team = get_data_engineering_team()
    print(f"Time criado: {team}")
