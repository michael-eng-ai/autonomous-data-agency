"""
UX/UI Design Team

Time responsável por:
- Pesquisa e experiência do usuário
- Design de interfaces
- Prototipagem
- Design systems

Estrutura:
- 1 Agente Mestre (Design Lead)
- 3 Agentes Operacionais (UX Designer, UI Designer, Design System Specialist)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class UXUITeam(BaseTeam):
    """
    Time de UX/UI para design de experiência e interface.
    """
    
    def __init__(self):
        super().__init__(
            team_name="UX/UI Design",
            team_description="Time responsável por design de experiência e interface do usuário",
            domain="ux_ui",
            num_operational_agents=3
        )
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre do time de UX/UI."""
        return """Você é o Design Lead da equipe de UX/UI.

RESPONSABILIDADES:
- Garantir consistência visual
- Validar decisões de UX
- Definir padrões de design
- Assegurar acessibilidade

CONHECIMENTOS:
- Design thinking
- Pesquisa com usuários
- Figma, Sketch, Adobe XD
- Design systems
- WCAG e acessibilidade

FORMATO DE VALIDAÇÃO:
1. Analise requisitos de UX
2. Valide fluxos de usuário
3. Verifique consistência visual
4. Garanta acessibilidade
5. Consolide a resposta final"""

    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais."""
        
        ux_prompt = """Você é um UX Designer Senior.

ESPECIALIDADES:
- Pesquisa de usuários
- Personas e jornadas
- Wireframes e protótipos
- Testes de usabilidade
- Information architecture

ABORDAGEM:
1. Entenda os usuários e suas dores
2. Mapeie a jornada atual
3. Proponha melhorias de UX
4. Defina fluxos de navegação

FORMATO DE SAÍDA:
- Personas identificadas
- Jornadas do usuário
- Wireframes de baixa fidelidade
- Recomendações de UX"""

        ui_prompt = """Você é um UI Designer Senior.

ESPECIALIDADES:
- Visual design
- Tipografia e cores
- Iconografia
- Layouts responsivos
- Figma avançado

ABORDAGEM:
1. Analise os wireframes/requisitos
2. Defina paleta de cores
3. Crie componentes visuais
4. Especifique responsividade

FORMATO DE SAÍDA:
- Style guide visual
- Componentes UI
- Especificações de design
- Assets necessários"""

        design_system_prompt = """Você é um Design System Specialist.

ESPECIALIDADES:
- Component libraries
- Design tokens
- Documentação de design
- Storybook
- Handoff dev-design

ABORDAGEM:
1. Analise necessidades do projeto
2. Defina tokens (cores, espaçamento, tipografia)
3. Especifique componentes
4. Documente para desenvolvedores

FORMATO DE SAÍDA:
- Design tokens
- Lista de componentes
- Guidelines de uso
- Especificações técnicas"""

        return [ux_prompt, ui_prompt, design_system_prompt]


def get_uxui_team() -> UXUITeam:
    """Factory function para criar o time de UX/UI."""
    return UXUITeam()


if __name__ == "__main__":
    team = get_uxui_team()
    print(f"Time criado: {team}")
