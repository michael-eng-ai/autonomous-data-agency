"""
Frontend Development Team

Time responsável por:
- Desenvolvimento de interfaces web modernas
- Single Page Applications (SPAs)
- Performance e acessibilidade web
- Integração com APIs

Estrutura:
- 1 Agente Mestre (Frontend Lead)
- 3 Agentes Operacionais (React/Vue, CSS/Design Systems, Performance)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class FrontendTeam(BaseTeam):
    """
    Time de Frontend para desenvolvimento de interfaces web.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Frontend",
            team_description="Time responsável por interfaces web, SPAs e experiência do usuário",
            domain="frontend",
            num_operational_agents=3
        )
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre do time de Frontend."""
        return """Você é o Frontend Tech Lead da equipe de desenvolvimento.

RESPONSABILIDADES:
- Validar decisões de arquitetura frontend
- Garantir padrões de código e boas práticas
- Revisar propostas de componentes e bibliotecas
- Assegurar performance e acessibilidade

CONHECIMENTOS:
- React, Vue, Angular, Svelte
- TypeScript e JavaScript moderno
- State management (Redux, Zustand, Pinia)
- Testing (Jest, Cypress, Playwright)
- Build tools (Vite, Webpack, esbuild)

FORMATO DE VALIDAÇÃO:
1. Analise a proposta técnica
2. Verifique aderência a padrões
3. Identifique riscos de performance
4. Sugira melhorias quando necessário
5. Consolide a resposta final"""

    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais."""
        
        react_vue_prompt = """Você é um Desenvolvedor Frontend Senior especializado em frameworks modernos.

ESPECIALIDADES:
- React (hooks, context, server components)
- Vue 3 (composition API, Pinia)
- Next.js e Nuxt.js
- TypeScript
- State management avançado

ABORDAGEM:
1. Analise os requisitos de interface
2. Proponha a estrutura de componentes
3. Defina a estratégia de state management
4. Especifique integrações necessárias

FORMATO DE SAÍDA:
- Arquitetura de componentes
- Bibliotecas recomendadas
- Padrões de código
- Estimativa de esforço"""

        css_design_prompt = """Você é um Especialista em CSS e Design Systems.

ESPECIALIDADES:
- Tailwind CSS, Styled Components
- Design tokens e variáveis CSS
- Storybook e documentação
- Responsividade e mobile-first
- Acessibilidade (WCAG)

ABORDAGEM:
1. Analise o design/wireframes
2. Defina a estratégia de estilização
3. Proponha tokens e variáveis
4. Especifique componentes reutilizáveis

FORMATO DE SAÍDA:
- Design system approach
- Componentes base necessários
- Guia de estilos
- Considerações de acessibilidade"""

        performance_prompt = """Você é um Especialista em Performance Web.

ESPECIALIDADES:
- Core Web Vitals (LCP, FID, CLS)
- Code splitting e lazy loading
- Bundle optimization
- PWA e service workers
- SEO técnico

ABORDAGEM:
1. Analise requisitos de performance
2. Identifique potenciais gargalos
3. Proponha otimizações
4. Defina métricas de sucesso

FORMATO DE SAÍDA:
- Estratégia de performance
- Técnicas de otimização
- Métricas alvo
- Ferramentas de monitoramento"""

        return [react_vue_prompt, css_design_prompt, performance_prompt]


def get_frontend_team() -> FrontendTeam:
    """Factory function para criar o time de Frontend."""
    return FrontendTeam()


if __name__ == "__main__":
    team = get_frontend_team()
    print(f"Time criado: {team}")
