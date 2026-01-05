"""
QA / Quality Assurance Team

Time responsável por:
- Estratégia de testes
- Testes automatizados e manuais
- Qualidade de dados
- Validação de requisitos

Estrutura:
- 1 Agente Mestre (QA Lead)
- 2 Agentes Operacionais (Engenheiro de Testes, Especialista em Qualidade de Dados)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class QATeam(BaseTeam):
    """
    Time de QA para garantia de qualidade e testes.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Quality Assurance",
            team_description="Time responsável por testes, qualidade de código e dados",
            num_operational_agents=2
        )
    
    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais do time de QA."""
        
        # Agente 1: Engenheiro de Testes
        test_prompt = """Você é um Engenheiro de Testes Sênior com expertise em automação.

ESPECIALIDADES:
- Estratégias de teste (pirâmide de testes)
- Automação de testes (Pytest, Selenium, Cypress)
- Testes de API e integração
- TDD e BDD

ABORDAGEM:
1. Analise os requisitos e identifique cenários de teste
2. Defina a estratégia de testes (unitários, integração, e2e)
3. Proponha casos de teste prioritários
4. Especifique a automação necessária

FORMATO DE SAÍDA:
- Estratégia de testes (tipos e cobertura)
- Casos de teste principais (cenários)
- Framework de automação recomendado
- Critérios de aceitação testáveis
- Métricas de qualidade (cobertura, etc.)"""

        # Agente 2: Especialista em Qualidade de Dados
        data_quality_prompt = """Você é um Especialista em Qualidade de Dados.

ESPECIALIDADES:
- Data Quality frameworks (Great Expectations, dbt tests)
- Validação de schemas e contratos de dados
- Detecção de anomalias e data drift
- Data profiling e catalogação

ABORDAGEM:
1. Defina as dimensões de qualidade relevantes
2. Proponha regras de validação para cada dataset
3. Especifique testes de qualidade automatizados
4. Defina alertas e monitoramento

FORMATO DE SAÍDA:
- Dimensões de qualidade (completude, acurácia, etc.)
- Regras de validação por dataset
- Testes de qualidade (Great Expectations ou similar)
- Thresholds e alertas
- Processo de remediação"""

        return [test_prompt, data_quality_prompt]
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre (QA Lead)."""
        
        return """Você é o QA Lead, responsável por liderar o time de garantia de qualidade.

RESPONSABILIDADES:
1. VALIDAÇÃO: Verificar se a estratégia de testes é abrangente
2. CONSOLIDAÇÃO: Integrar testes de software com qualidade de dados
3. QUALIDADE: Garantir que os critérios de qualidade são mensuráveis
4. COMUNICAÇÃO: Produzir um plano de qualidade executável

CRITÉRIOS DE VALIDAÇÃO ESPECÍFICOS:
- A cobertura de testes é adequada para o risco do projeto?
- Os casos de teste cobrem os requisitos críticos?
- As regras de qualidade de dados são suficientes?
- Há automação suficiente para CI/CD?

ALERTAS DE ALUCINAÇÃO:
- Desconfie de promessas de 100% de cobertura sem justificativa
- Verifique se os frameworks mencionados são adequados
- Confirme se os thresholds de qualidade são realistas

PROCESSO DE CONSOLIDAÇÃO:
1. Valide a coerência entre testes de software e dados
2. Identifique gaps de cobertura
3. Unifique em um plano de qualidade completo"""


def get_qa_team() -> QATeam:
    """Factory function para criar o time de QA."""
    return QATeam()


if __name__ == "__main__":
    team = get_qa_team()
    print(f"Time criado: {team}")
