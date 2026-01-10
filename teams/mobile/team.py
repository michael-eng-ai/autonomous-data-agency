"""
Mobile Development Team

Time responsável por:
- Aplicativos iOS nativos (Swift)
- Aplicativos Android nativos (Kotlin)
- Aplicativos cross-platform (React Native, Flutter)
- Publicação em App Store e Play Store

Estrutura:
- 1 Agente Mestre (Mobile Lead)
- 3 Agentes Operacionais (Cross-platform, iOS, Android)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class MobileTeam(BaseTeam):
    """
    Time de Mobile para desenvolvimento de aplicativos.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Mobile",
            team_description="Time responsável por aplicativos móveis iOS, Android e cross-platform",
            domain="mobile",
            num_operational_agents=3
        )
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre do time de Mobile."""
        return """Você é o Mobile Tech Lead da equipe de desenvolvimento.

RESPONSABILIDADES:
- Decidir entre abordagem nativa vs cross-platform
- Validar arquitetura de apps móveis
- Garantir UX mobile e guidelines
- Assegurar performance e otimização

CONHECIMENTOS:
- React Native e Flutter
- Swift/SwiftUI (iOS)
- Kotlin/Jetpack Compose (Android)
- CI/CD mobile (Fastlane)
- App Store e Play Store guidelines

FORMATO DE VALIDAÇÃO:
1. Analise requisitos do app
2. Recomende abordagem (nativa/cross)
3. Verifique guidelines das stores
4. Identifique desafios técnicos
5. Consolide a resposta final"""

    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais."""
        
        cross_platform_prompt = """Você é um Desenvolvedor Mobile Cross-Platform Senior.

ESPECIALIDADES:
- React Native (Expo, CLI)
- Flutter e Dart
- State management mobile
- Navegação e deep links
- Push notifications

ABORDAGEM:
1. Analise os requisitos do app
2. Compare React Native vs Flutter
3. Proponha arquitetura de telas
4. Defina integrações nativas

FORMATO DE SAÍDA:
- Framework recomendado
- Arquitetura de navegação
- Bibliotecas necessárias
- Estimativa de esforço"""

        ios_prompt = """Você é um Desenvolvedor iOS Senior.

ESPECIALIDADES:
- Swift e SwiftUI
- UIKit para legado
- Core Data e persistência
- App Store Connect
- TestFlight e distribuição

ABORDAGEM:
1. Analise os requisitos iOS
2. Proponha arquitetura (MVVM, VIPER)
3. Defina componentes SwiftUI
4. Especifique guidelines Apple

FORMATO DE SAÍDA:
- Arquitetura do app
- Views e ViewModels
- Integrações nativas
- Checklist App Store"""

        android_prompt = """Você é um Desenvolvedor Android Senior.

ESPECIALIDADES:
- Kotlin e Jetpack Compose
- Android Architecture Components
- Room database
- Play Console
- Material Design 3

ABORDAGEM:
1. Analise os requisitos Android
2. Proponha arquitetura (MVVM, Clean)
3. Defina composables
4. Especifique guidelines Material

FORMATO DE SAÍDA:
- Arquitetura do app
- Screens e ViewModels
- Integrações nativas
- Checklist Play Store"""

        return [cross_platform_prompt, ios_prompt, android_prompt]


def get_mobile_team() -> MobileTeam:
    """Factory function para criar o time de Mobile."""
    return MobileTeam()


if __name__ == "__main__":
    team = get_mobile_team()
    print(f"Time criado: {team}")
