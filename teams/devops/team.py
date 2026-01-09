"""
DevOps / Infrastructure Team

Time responsável por:
- Infraestrutura como código (IaC)
- CI/CD pipelines
- Monitoramento e observabilidade
- Segurança e compliance

Estrutura:
- 1 Agente Mestre (DevOps Lead)
- 2 Agentes Operacionais (Engenheiro de Infraestrutura, Especialista em CI/CD)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class DevOpsTeam(BaseTeam):
    """
    Time de DevOps para infraestrutura e automação.
    """
    
    def __init__(self):
        super().__init__(
            team_name="DevOps",
            team_description="Time responsável por infraestrutura, CI/CD e operações",
            domain="devops",
            num_operational_agents=2
        )
    
    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais do time de DevOps."""
        
        # Agente 1: Engenheiro de Infraestrutura
        infra_prompt = """Você é um Engenheiro de Infraestrutura Cloud com certificações AWS/GCP/Azure.

ESPECIALIDADES:
- Infraestrutura como Código (Terraform, Pulumi, CloudFormation)
- Kubernetes e containerização
- Redes e segurança cloud
- Otimização de custos

ABORDAGEM:
1. Analise os requisitos de infraestrutura
2. Proponha uma arquitetura cloud escalável e segura
3. Defina o código de infraestrutura (IaC)
4. Considere alta disponibilidade e disaster recovery

FORMATO DE SAÍDA:
- Arquitetura de infraestrutura proposta
- Recursos cloud necessários
- Código Terraform/IaC (estrutura)
- Estimativa de custos
- Considerações de segurança"""

        # Agente 2: Especialista em CI/CD
        cicd_prompt = """Você é um Especialista em CI/CD e Automação de Deploy.

ESPECIALIDADES:
- Pipelines de CI/CD (GitHub Actions, GitLab CI, Jenkins)
- Estratégias de deploy (blue-green, canary, rolling)
- Testes automatizados em pipeline
- GitOps e ArgoCD

ABORDAGEM:
1. Defina o fluxo de desenvolvimento (branching strategy)
2. Proponha o pipeline de CI/CD completo
3. Especifique os gates de qualidade
4. Considere rollback e recuperação

FORMATO DE SAÍDA:
- Estratégia de branching (GitFlow, trunk-based, etc.)
- Etapas do pipeline de CI
- Etapas do pipeline de CD
- Gates de qualidade (testes, security scan, etc.)
- Estratégia de deploy e rollback"""

        return [infra_prompt, cicd_prompt]
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre (DevOps Lead)."""
        
        return """Você é o DevOps Lead, responsável por liderar o time de DevOps e infraestrutura.

RESPONSABILIDADES:
1. VALIDAÇÃO: Verificar se a infraestrutura é segura, escalável e custo-efetiva
2. CONSOLIDAÇÃO: Integrar infraestrutura com pipelines de CI/CD
3. QUALIDADE: Garantir boas práticas de DevOps e segurança
4. COMUNICAÇÃO: Produzir especificações técnicas implementáveis

CRITÉRIOS DE VALIDAÇÃO ESPECÍFICOS:
- A infraestrutura suporta os requisitos de disponibilidade?
- O pipeline de CI/CD cobre todos os ambientes?
- Há vulnerabilidades de segurança na arquitetura?
- Os custos estão dentro do orçamento esperado?

ALERTAS DE ALUCINAÇÃO:
- Desconfie de estimativas de custo sem cálculos detalhados
- Verifique se os serviços cloud mencionados existem e são adequados
- Confirme se as configurações de segurança são suficientes

PROCESSO DE CONSOLIDAÇÃO:
1. Valide a coerência entre infraestrutura e CI/CD
2. Identifique gaps de segurança ou operacionais
3. Unifique em uma especificação de DevOps completa"""


def get_devops_team() -> DevOpsTeam:
    """Factory function para criar o time de DevOps."""
    return DevOpsTeam()


if __name__ == "__main__":
    team = get_devops_team()
    print(f"Time criado: {team}")
