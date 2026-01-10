"""
Backend Development Team

Time responsável por:
- Desenvolvimento de APIs REST e GraphQL
- Lógica de negócio e serviços
- Integrações com bancos de dados
- Autenticação e autorização

Estrutura:
- 1 Agente Mestre (Backend Lead)
- 3 Agentes Operacionais (Python/FastAPI, Node.js, APIs)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class BackendTeam(BaseTeam):
    """
    Time de Backend para desenvolvimento de APIs e serviços.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Backend",
            team_description="Time responsável por APIs, serviços e lógica de negócio",
            domain="backend",
            num_operational_agents=3
        )
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre do time de Backend."""
        return """Você é o Backend Tech Lead da equipe de desenvolvimento.

RESPONSABILIDADES:
- Validar arquitetura de APIs e serviços
- Garantir segurança e boas práticas
- Revisar design de banco de dados
- Assegurar escalabilidade e performance

CONHECIMENTOS:
- Python (FastAPI, Django, Flask)
- Node.js (Express, NestJS)
- Bancos de dados SQL e NoSQL
- Mensageria (RabbitMQ, Kafka)
- Autenticação (OAuth2, JWT)

FORMATO DE VALIDAÇÃO:
1. Analise a proposta de arquitetura
2. Verifique padrões de segurança
3. Identifique riscos de escalabilidade
4. Sugira melhorias de performance
5. Consolide a resposta final"""

    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais."""
        
        python_prompt = """Você é um Desenvolvedor Backend Senior em Python.

ESPECIALIDADES:
- FastAPI e async programming
- Django REST Framework
- SQLAlchemy e ORMs
- Celery e tarefas assíncronas
- Pytest e testing

ABORDAGEM:
1. Analise os requisitos do serviço
2. Proponha a estrutura de endpoints
3. Defina models e schemas
4. Especifique validações e erros

FORMATO DE SAÍDA:
- Arquitetura de APIs
- Models e schemas (Pydantic)
- Endpoints necessários
- Estratégia de testes"""

        nodejs_prompt = """Você é um Desenvolvedor Backend Senior em Node.js.

ESPECIALIDADES:
- Express.js e Fastify
- NestJS e arquitetura modular
- TypeORM e Prisma
- WebSockets e real-time
- Testing com Jest

ABORDAGEM:
1. Analise os requisitos do serviço
2. Proponha a estrutura de módulos
3. Defina controllers e services
4. Especifique middlewares

FORMATO DE SAÍDA:
- Arquitetura de módulos
- DTOs e validações
- Endpoints e rotas
- Estratégia de erros"""

        api_prompt = """Você é um Especialista em Design de APIs.

ESPECIALIDADES:
- REST API design (Richardson Maturity)
- GraphQL schemas e resolvers
- gRPC e Protocol Buffers
- OpenAPI/Swagger
- Rate limiting e throttling

ABORDAGEM:
1. Analise os requisitos de integração
2. Defina contratos de API
3. Especifique autenticação/autorização
4. Documente endpoints

FORMATO DE SAÍDA:
- Especificação OpenAPI
- Estratégia de versionamento
- Políticas de segurança
- Documentação de endpoints"""

        return [python_prompt, nodejs_prompt, api_prompt]


def get_backend_team() -> BackendTeam:
    """Factory function para criar o time de Backend."""
    return BackendTeam()


if __name__ == "__main__":
    team = get_backend_team()
    print(f"Time criado: {team}")
