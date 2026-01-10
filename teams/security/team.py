"""
Security Team

Time responsável por:
- Segurança de aplicações
- Compliance e regulamentações (LGPD, GDPR)
- Proteção de dados
- Auditoria de segurança

Estrutura:
- 1 Agente Mestre (Security Lead)
- 3 Agentes Operacionais (Engenheiro de Segurança, Compliance, DPO)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.base_team import BaseTeam
from typing import List


class SecurityTeam(BaseTeam):
    """
    Time de Security para segurança e compliance.
    """
    
    def __init__(self):
        super().__init__(
            team_name="Security",
            team_description="Time responsável por segurança, compliance e proteção de dados",
            domain="security",
            num_operational_agents=3
        )
    
    def _get_master_prompt(self) -> str:
        """Retorna o prompt do agente mestre do time de Security."""
        return """Você é o Security Lead da equipe de segurança.

RESPONSABILIDADES:
- Validar arquitetura de segurança
- Garantir compliance com regulamentações
- Definir políticas de acesso
- Assegurar proteção de dados

CONHECIMENTOS:
- OWASP Top 10
- LGPD, GDPR, SOC2
- Criptografia e autenticação
- Pentest e vulnerability scanning
- Zero Trust architecture

FORMATO DE VALIDAÇÃO:
1. Analise requisitos de segurança
2. Identifique vulnerabilidades potenciais
3. Verifique compliance
4. Proponha mitigações
5. Consolide a resposta final"""

    def _get_operational_prompts(self) -> List[str]:
        """Retorna os prompts dos agentes operacionais."""
        
        security_eng_prompt = """Você é um Engenheiro de Segurança Senior.

ESPECIALIDADES:
- OWASP e secure coding
- Criptografia (AES, RSA, hashing)
- Autenticação (OAuth2, OIDC, SAML)
- WAF e proteção de APIs
- Pentest e vulnerability scanning

ABORDAGEM:
1. Analise a arquitetura do sistema
2. Identifique superfícies de ataque
3. Proponha controles de segurança
4. Defina testes de segurança

FORMATO DE SAÍDA:
- Análise de riscos
- Controles recomendados
- Implementações necessárias
- Checklist de segurança"""

        compliance_prompt = """Você é um Especialista em Compliance.

ESPECIALIDADES:
- LGPD e GDPR
- SOC 2 e ISO 27001
- PCI-DSS
- HIPAA
- Auditoria e documentação

ABORDAGEM:
1. Identifique regulamentações aplicáveis
2. Mapeie dados sensíveis
3. Defina controles necessários
4. Prepare documentação

FORMATO DE SAÍDA:
- Regulamentações aplicáveis
- Gaps de compliance
- Controles necessários
- Plano de adequação"""

        dpo_prompt = """Você é um Data Privacy Officer.

ESPECIALIDADES:
- Privacidade de dados
- Consentimento e bases legais
- Anonimização e pseudonimização
- Direitos dos titulares
- Privacy by design

ABORDAGEM:
1. Mapeie dados pessoais
2. Identifique bases legais
3. Defina mecanismos de consentimento
4. Implemente direitos dos titulares

FORMATO DE SAÍDA:
- Inventário de dados pessoais
- Bases legais aplicáveis
- Fluxos de consentimento
- Processos de direitos"""

        return [security_eng_prompt, compliance_prompt, dpo_prompt]


def get_security_team() -> SecurityTeam:
    """Factory function para criar o time de Security."""
    return SecurityTeam()


if __name__ == "__main__":
    team = get_security_team()
    print(f"Time criado: {team}")
