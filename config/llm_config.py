"""
LLM Configuration Module

Este módulo gerencia a configuração de múltiplos modelos de LLM para garantir
diversidade de pensamento entre os agentes. Cada agente operacional usa um
modelo diferente para evitar vieses e aumentar a qualidade das soluções.

Modelos Suportados:
- GPT-4o-mini (OpenAI)
- GPT-3.5-turbo (OpenAI)
- Gemini-2.5-flash (Google) - DEFAULT
"""

import os
import sys
from typing import Dict, Optional, Literal, Union, Any
from dataclasses import dataclass
from enum import Enum
from unittest.mock import MagicMock

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


# Detecta modo de teste (CI/CD sem chaves reais)
def _is_testing_mode() -> bool:
    """Verifica se está em modo de teste."""
    return os.getenv("TESTING", "").lower() == "true" or os.getenv("PYTEST_CURRENT_TEST") is not None


class LLMProvider(Enum):
    """Provedores de LLM disponíveis."""
    OPENAI_MINI = "gpt-4o-mini"
    OPENAI = "gpt-3.5-turbo"
    GEMINI_FLASH = "gemini-2.5-flash"


@dataclass
class LLMConfig:
    """Configuração de um modelo de LLM."""
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 4096
    description: str = ""


# Configurações padrão para cada tipo de agente
LLM_CONFIGS: Dict[str, LLMConfig] = {
    # Agentes Mestres - usam modelo mais capaz para validação
    "master": LLMConfig(
        model_name="gemini-2.5-flash",
        temperature=0.3,
        description="Modelo principal para agentes mestres (validação e consolidação) - Google"
    ),
    
    # Agentes Operacionais - usam modelos diferentes para diversidade
    "operational_1": LLMConfig(
        model_name="gemini-2.5-flash",
        temperature=0.7,
        description="Primeiro modelo operacional (criativo) - Google"
    ),
    "operational_2": LLMConfig(
        model_name="gemini-2.5-flash",
        temperature=0.7,
        description="Segundo modelo operacional (rápido e diverso) - Google"
    ),
    "operational_3": LLMConfig(
        model_name="gpt-3.5-turbo",
        temperature=0.8,
        description="Terceiro modelo operacional (backup)"
    ),
}


class MissingAPIKeyError(Exception):
    """Erro quando a chave de API necessária não está configurada."""
    pass


def check_api_keys() -> Dict[str, bool]:
    """Verifica quais chaves de API estão configuradas."""
    return {
        "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY")),
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
    }


def validate_environment():
    """
    Valida se o ambiente está configurado corretamente.
    Deve ser chamado antes de iniciar o sistema.
    """
    keys = check_api_keys()
    
    if not keys["GOOGLE_API_KEY"] and not keys["OPENAI_API_KEY"]:
        print("\n" + "=" * 70)
        print("❌ ERRO: CHAVE DE API NÃO CONFIGURADA")
        print("=" * 70)
        print("\nPara usar a Autonomous Data Agency, você precisa configurar")
        print("pelo menos uma das seguintes variáveis de ambiente:\n")
        print("  🔹 GOOGLE_API_KEY  - Para usar Gemini (RECOMENDADO)")
        print("  🔹 OPENAI_API_KEY  - Para usar GPT\n")
        print("Como configurar:")
        print("-" * 70)
        print("\n1. Crie um arquivo .env na raiz do projeto:")
        print("   GOOGLE_API_KEY=sua_chave_aqui\n")
        print("2. Ou exporte no terminal:")
        print("   export GOOGLE_API_KEY=sua_chave_aqui\n")
        print("3. Obtenha sua chave em:")
        print("   • Google AI Studio: https://aistudio.google.com/app/apikey")
        print("   • OpenAI: https://platform.openai.com/api-keys")
        print("=" * 70 + "\n")
        raise MissingAPIKeyError(
            "Configure GOOGLE_API_KEY ou OPENAI_API_KEY antes de executar. "
            "Veja as instruções acima."
        )
    
    # Mostra status das chaves
    print("\n✅ Configuração de API Keys:")
    print(f"   • GOOGLE_API_KEY: {'✓ Configurada' if keys['GOOGLE_API_KEY'] else '✗ Não configurada'}")
    print(f"   • OPENAI_API_KEY: {'✓ Configurada' if keys['OPENAI_API_KEY'] else '✗ Não configurada'}")
    print()


def get_llm(
    agent_type: Literal["master", "operational_1", "operational_2", "operational_3"],
    temperature_override: Optional[float] = None
) -> Union[ChatOpenAI, ChatGoogleGenerativeAI, MagicMock]:
    """
    Retorna uma instância de LLM configurada para o tipo de agente.
    
    Args:
        agent_type: Tipo do agente (master, operational_1, operational_2, operational_3)
        temperature_override: Sobrescreve a temperatura padrão se fornecido
        
    Returns:
        Instância de ChatOpenAI ou ChatGoogleGenerativeAI configurada
        
    Raises:
        MissingAPIKeyError: Se nenhuma chave de API estiver configurada (fora de testes)
    """
    config = LLM_CONFIGS.get(agent_type, LLM_CONFIGS["operational_1"])
    temperature = temperature_override if temperature_override is not None else config.temperature
    
    # Verifica se há chaves de API disponíveis
    google_key = os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Em modo de teste sem chaves, usa mock
    if _is_testing_mode() and not google_key and not openai_key:
        mock = MagicMock()
        mock.invoke.return_value.content = "Mocked LLM Response for testing"
        mock.model = "mock-model"
        return mock
    
    # Se não há nenhuma chave e não está em modo de teste, lança erro
    if not google_key and not openai_key:
        raise MissingAPIKeyError(
            "Nenhuma API key configurada. Configure GOOGLE_API_KEY ou OPENAI_API_KEY. "
            "Execute 'python -c \"from config.llm_config import validate_environment; validate_environment()\"' "
            "para ver instruções detalhadas."
        )
    
    if "gemini" in config.model_name:
        if google_key:
            return ChatGoogleGenerativeAI(
                model=config.model_name,
                temperature=temperature,
                max_output_tokens=config.max_tokens,
                google_api_key=google_key
            )
        elif openai_key:
            # Fallback para OpenAI se chave do Google não existir
            print(f"⚠️  GOOGLE_API_KEY não encontrada. Usando OpenAI como fallback para {agent_type}.")
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=temperature,
                max_tokens=config.max_tokens
            )
    
    # OpenAI model
    if openai_key:
        return ChatOpenAI(
            model=config.model_name,
            temperature=temperature,
            max_tokens=config.max_tokens
        )
    elif google_key:
        # Fallback para Gemini se só tiver chave do Google
        print(f"⚠️  OPENAI_API_KEY não encontrada. Usando Gemini como fallback para {agent_type}.")
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=temperature,
            max_output_tokens=config.max_tokens,
            google_api_key=google_key
        )
    
    # Não deveria chegar aqui, mas por segurança
    raise MissingAPIKeyError("Nenhuma API key válida encontrada.")


def get_diverse_llms(n: int = 2) -> list:
    """
    Retorna uma lista de LLMs diversos para agentes operacionais.
    
    Args:
        n: Número de LLMs a retornar (máximo 3)
        
    Returns:
        Lista de instâncias de ChatOpenAI
    """
    operational_types = ["operational_1", "operational_2", "operational_3"]
    return [get_llm(t) for t in operational_types[:min(n, 3)]]


# Mapeamento de modelos para descrições amigáveis
# Mapeamento de modelos para descrições amigáveis
MODEL_DESCRIPTIONS = {
    "gpt-4o-mini": "GPT-4o Mini (OpenAI) - Equilibrado e versátil",
    "gpt-3.5-turbo": "GPT-3.5 Turbo (OpenAI) - Rápido e eficiente",
    "gemini-2.5-flash": "Gemini 2.5 Flash (Google) - Perspectiva alternativa",
}


def describe_llm_diversity():
    """Imprime informações sobre a diversidade de LLMs configurada."""
    print("=" * 60)
    print("CONFIGURAÇÃO DE DIVERSIDADE DE LLMs")
    print("=" * 60)
    for agent_type, config in LLM_CONFIGS.items():
        print(f"\n[{agent_type.upper()}]")
        print(f"  Modelo: {config.model_name}")
        print(f"  Temperatura: {config.temperature}")
        print(f"  Descrição: {config.description}")
    print("=" * 60)


if __name__ == "__main__":
    describe_llm_diversity()
