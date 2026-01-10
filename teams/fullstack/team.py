"""
Fullstack Development Team

Time responsável por:
- Desenvolvimento end-to-end de aplicações
- Integração frontend + backend
- Aplicações web completas
- Sistemas SaaS e produtos digitais

Estrutura:
- 1 Agente Mestre (Fullstack Lead)
- 3 Agentes Operacionais (MERN/PERN, Python Fullstack, Next.js/T3)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class FullstackTeam(BaseTeam):
    """
    Time Fullstack para desenvolvimento end-to-end.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Fullstack",
            team_description="Time responsável por desenvolvimento end-to-end de aplicações web",
            domain="fullstack",
            num_operational_agents=3
        )
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre do time Fullstack."""
        return """Você é o Fullstack Tech Lead da equipe de desenvolvimento.

RESPONSABILIDADES:
- Definir stack tecnológica completa
- Integrar frontend e backend
- Garantir fluxo end-to-end
- Otimizar developer experience

CONHECIMENTOS:
- Stacks JavaScript (MERN, PERN, T3)
- Stacks Python (Django, FastAPI + React)
- ORMs e bancos de dados
- Deploy e infraestrutura básica
- Autenticação e autorização

FORMATO DE VALIDAÇÃO:
1. Analise requisitos completos
2. Defina stack recomendada
3. Verifique integrações
4. Identifique complexidades
5. Consolide a resposta final"""

    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais."""
        
        mern_prompt = """Você é um Desenvolvedor Fullstack MERN/PERN Senior.

ESPECIALIDADES:
- MongoDB/PostgreSQL
- Express.js
- React
- Node.js
- Mongoose/Prisma

ABORDAGEM:
1. Analise os requisitos do sistema
2. Defina estrutura do projeto
3. Proponha models e APIs
4. Integre frontend com backend

FORMATO DE SAÍDA:
- Arquitetura completa
- Estrutura de pastas
- Models e controllers
- Componentes React"""

        python_fullstack_prompt = """Você é um Desenvolvedor Fullstack Python Senior.

ESPECIALIDADES:
- Django + Django REST
- FastAPI + SQLAlchemy
- React/Vue frontend
- PostgreSQL/Redis
- Celery para background jobs

ABORDAGEM:
1. Analise os requisitos do sistema
2. Defina backend Python
3. Integre com frontend JS
4. Configure tarefas assíncronas

FORMATO DE SAÍDA:
- Arquitetura Django/FastAPI
- Apps e models
- APIs e serializers
- Integração frontend"""

        nextjs_prompt = """Você é um Desenvolvedor Fullstack Next.js/T3 Senior.

ESPECIALIDADES:
- Next.js 14+ (App Router)
- tRPC para type-safety
- Prisma ORM
- NextAuth.js
- Vercel deployment

ABORDAGEM:
1. Analise os requisitos
2. Defina estrutura Next.js
3. Configure tRPC/API routes
4. Implemente auth e database

FORMATO DE SAÍDA:
- Estrutura App Router
- Prisma schema
- tRPC routers
- Server components"""

        return [mern_prompt, python_fullstack_prompt, nextjs_prompt]


def get_fullstack_team() -> FullstackTeam:
    """Factory function para criar o time Fullstack."""
    return FullstackTeam()


if __name__ == "__main__":
    team = get_fullstack_team()
    print(f"Time criado: {team}")
