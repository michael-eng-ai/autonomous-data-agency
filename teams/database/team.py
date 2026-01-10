"""
Database Administration Team

Time responsável por:
- Modelagem de dados
- Administração de bancos SQL e NoSQL
- Otimização de queries
- Backup, recovery e alta disponibilidade

Estrutura:
- 1 Agente Mestre (DBA Lead)
- 3 Agentes Operacionais (DBA SQL, DBA NoSQL, Data Modeling)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class DatabaseTeam(BaseTeam):
    """
    Time de Database para administração e modelagem de dados.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Database",
            team_description="Time responsável por modelagem, otimização e administração de bancos de dados",
            domain="database",
            num_operational_agents=3
        )
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre do time de Database."""
        return """Você é o DBA Lead da equipe de banco de dados.

RESPONSABILIDADES:
- Validar modelagem de dados
- Garantir performance de queries
- Definir estratégias de backup/recovery
- Assegurar segurança de dados

CONHECIMENTOS:
- PostgreSQL, MySQL, SQL Server
- MongoDB, Redis, Elasticsearch
- Modelagem relacional e dimensional
- Índices, particionamento, sharding
- Replicação e alta disponibilidade

FORMATO DE VALIDAÇÃO:
1. Analise requisitos de dados
2. Valide modelo proposto
3. Verifique índices necessários
4. Identifique gargalos potenciais
5. Consolide a resposta final"""

    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais."""
        
        sql_prompt = """Você é um DBA especialista em bancos relacionais.

ESPECIALIDADES:
- PostgreSQL avançado
- MySQL/MariaDB
- SQL Server
- Otimização de queries
- Índices e execution plans

ABORDAGEM:
1. Analise os requisitos de dados
2. Proponha esquema relacional
3. Defina índices estratégicos
4. Otimize queries críticas

FORMATO DE SAÍDA:
- DDL das tabelas
- Índices recomendados
- Queries otimizadas
- Estratégia de manutenção"""

        nosql_prompt = """Você é um DBA especialista em bancos NoSQL.

ESPECIALIDADES:
- MongoDB (documentos)
- Redis (cache, sessões)
- Elasticsearch (busca)
- DynamoDB (serverless)
- Cassandra (wide-column)

ABORDAGEM:
1. Analise padrões de acesso
2. Escolha o banco adequado
3. Defina modelo de dados
4. Configure replicação

FORMATO DE SAÍDA:
- Banco recomendado
- Schema/collections
- Índices e sharding
- Padrões de acesso"""

        modeling_prompt = """Você é um Especialista em Modelagem de Dados.

ESPECIALIDADES:
- Modelagem ER
- Normalização (1NF a 5NF)
- Modelagem dimensional (Star, Snowflake)
- Dicionário de dados
- Data governance

ABORDAGEM:
1. Entenda o domínio de negócio
2. Identifique entidades e relacionamentos
3. Normalize até o nível adequado
4. Documente o modelo

FORMATO DE SAÍDA:
- Diagrama ER
- Descrição de entidades
- Relacionamentos e cardinalidades
- Dicionário de dados"""

        return [sql_prompt, nosql_prompt, modeling_prompt]


def get_database_team() -> DatabaseTeam:
    """Factory function para criar o time de Database."""
    return DatabaseTeam()


if __name__ == "__main__":
    team = get_database_team()
    print(f"Time criado: {team}")
