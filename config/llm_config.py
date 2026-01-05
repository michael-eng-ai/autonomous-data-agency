"""
LLM Configuration Module

Este módulo gerencia a configuração de múltiplos modelos de LLM para garantir
diversidade de pensamento entre os agentes. Cada agente operacional usa um
modelo diferente para evitar vieses e aumentar a qualidade das soluções.

Modelos Suportados:
- GPT-4.1-mini (OpenAI)
- GPT-4.1-nano (OpenAI)
- Gemini-2.5-flash (Google)
"""

import os
from typing import Dict, Optional, Literal
from dataclasses import dataclass
from enum import Enum

from langchain_openai import ChatOpenAI


class LLMProvider(Enum):
    """Provedores de LLM disponíveis."""
    OPENAI_MINI = "gpt-4.1-mini"
    OPENAI_NANO = "gpt-4.1-nano"
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
        model_name="gpt-4.1-mini",
        temperature=0.3,  # Mais determinístico para validação
        description="Modelo principal para agentes mestres (validação e consolidação)"
    ),
    
    # Agentes Operacionais - usam modelos diferentes para diversidade
    "operational_1": LLMConfig(
        model_name="gpt-4.1-mini",
        temperature=0.7,
        description="Primeiro modelo operacional (criativo)"
    ),
    "operational_2": LLMConfig(
        model_name="gpt-4.1-nano",
        temperature=0.8,
        description="Segundo modelo operacional (rápido e diverso)"
    ),
    "operational_3": LLMConfig(
        model_name="gemini-2.5-flash",
        temperature=0.7,
        description="Terceiro modelo operacional (perspectiva Google)"
    ),
}


def get_llm(
    agent_type: Literal["master", "operational_1", "operational_2", "operational_3"],
    temperature_override: Optional[float] = None
) -> ChatOpenAI:
    """
    Retorna uma instância de LLM configurada para o tipo de agente.
    
    Args:
        agent_type: Tipo do agente (master, operational_1, operational_2, operational_3)
        temperature_override: Sobrescreve a temperatura padrão se fornecido
        
    Returns:
        Instância de ChatOpenAI configurada
    """
    config = LLM_CONFIGS.get(agent_type, LLM_CONFIGS["operational_1"])
    
    temperature = temperature_override if temperature_override is not None else config.temperature
    
    return ChatOpenAI(
        model=config.model_name,
        temperature=temperature,
        max_tokens=config.max_tokens
    )


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
MODEL_DESCRIPTIONS = {
    "gpt-4.1-mini": "GPT-4.1 Mini (OpenAI) - Equilibrado e versátil",
    "gpt-4.1-nano": "GPT-4.1 Nano (OpenAI) - Rápido e eficiente",
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
