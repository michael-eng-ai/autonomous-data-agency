"""
Test Configuration for Autonomous Data Agency

Este arquivo configura os fixtures necessários para testes.
O llm_config.py detecta automaticamente PYTEST_CURRENT_TEST e usa mocks.
"""
import pytest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_mock_llm():
    """Create a mock LLM that behaves like ChatOpenAI/ChatGoogleGenerativeAI."""
    mock = MagicMock()
    mock.invoke.return_value.content = "Mocked LLM Response"
    mock.model = "mock-model"
    return mock


@pytest.fixture
def mock_llm():
    """Mock for LLM responses."""
    return create_mock_llm()


@pytest.fixture
def orchestrator():
    """
    Create orchestrator for testing.
    O llm_config.py detecta PYTEST_CURRENT_TEST e usa mocks automaticamente
    quando não há chaves de API configuradas.
    """
    # Reset singleton para forçar nova instância
    import core.agency_orchestrator as orch_module
    orch_module._orchestrator_instance = None
    
    from core.agency_orchestrator import AgencyOrchestrator
    orchestrator = AgencyOrchestrator()
    orchestrator.global_master_agent = create_mock_llm()
    return orchestrator
