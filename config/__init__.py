"""
Configuration Package

Este pacote contém as configurações globais do framework,
incluindo a configuração de múltiplos LLMs para diversidade.
"""

from .llm_config import (
    get_llm,
    get_diverse_llms,
    LLMConfig,
    LLMProvider,
    LLM_CONFIGS,
    describe_llm_diversity
)

__all__ = [
    "get_llm",
    "get_diverse_llms",
    "LLMConfig",
    "LLMProvider",
    "LLM_CONFIGS",
    "describe_llm_diversity"
]
