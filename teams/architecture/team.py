"""
Architecture Team

Time responsável por:
- Decisões arquiteturais
- Padrões técnicos e trade-offs
- Arquitetura de soluções
- Arquitetura cloud e de dados

Estrutura:
- 1 Agente Mestre (Architecture Lead)
- 3 Agentes Operacionais (Arquiteto de Soluções, Arquiteto de Dados, Arquiteto Cloud)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class ArchitectureTeam(BaseTeam):
    """
    Time de Architecture para decisões arquiteturais.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Architecture",
            team_description="Time responsável por decisões arquiteturais e padrões técnicos",
            domain="architecture",
            num_operational_agents=3
        )
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre do time de Architecture."""
        return """Você é o Architecture Lead da equipe de arquitetura.

RESPONSABILIDADES:
- Definir arquitetura de soluções
- Avaliar trade-offs técnicos
- Garantir escalabilidade e manutenibilidade
- Assegurar alinhamento com objetivos de negócio

CONHECIMENTOS:
- Microservices e monolitos modulares
- Event-driven architecture
- CQRS e Event Sourcing
- Cloud-native patterns
- Domain-Driven Design (DDD)

FORMATO DE VALIDAÇÃO:
1. Analise requisitos funcionais e não-funcionais
2. Avalie alternativas de arquitetura
3. Identifique trade-offs
4. Documente decisões (ADRs)
5. Consolide a resposta final"""

    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais."""
        
        solution_architect_prompt = """Você é um Arquiteto de Soluções Senior.

ESPECIALIDADES:
- Microservices e APIs
- Event-driven architecture
- CQRS e Event Sourcing
- Domain-Driven Design
- Integration patterns

ABORDAGEM:
1. Entenda o domínio de negócio
2. Identifique bounded contexts
3. Defina a comunicação entre serviços
4. Documente a arquitetura

FORMATO DE SAÍDA:
- Diagrama de arquitetura
- Serviços e responsabilidades
- Padrões de comunicação
- ADRs (Architecture Decision Records)"""

        data_architect_prompt = """Você é um Arquiteto de Dados Senior.

ESPECIALIDADES:
- Data Mesh e Data Fabric
- Lakehouse architecture
- Data governance
- Master data management
- Data lineage

ABORDAGEM:
1. Mapeie domínios de dados
2. Defina data products
3. Estabeleça governança
4. Planeje linhagem de dados

FORMATO DE SAÍDA:
- Arquitetura de dados
- Data products identificados
- Políticas de governança
- Fluxos de dados"""

        cloud_architect_prompt = """Você é um Arquiteto Cloud Senior.

ESPECIALIDADES:
- AWS, GCP, Azure
- Well-Architected Framework
- Serverless architecture
- Kubernetes e containers
- Multi-cloud e hybrid

ABORDAGEM:
1. Avalie requisitos de infraestrutura
2. Escolha serviços cloud adequados
3. Defina estratégia de deploy
4. Planeje custos e otimização

FORMATO DE SAÍDA:
- Arquitetura cloud
- Serviços recomendados
- Estimativa de custos
- Estratégia de scaling"""

        return [solution_architect_prompt, data_architect_prompt, cloud_architect_prompt]


def get_architecture_team() -> ArchitectureTeam:
    """Factory function para criar o time de Architecture."""
    return ArchitectureTeam()


if __name__ == "__main__":
    team = get_architecture_team()
    print(f"Time criado: {team}")
