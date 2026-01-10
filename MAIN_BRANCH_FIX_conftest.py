"""
INSTRUÇÕES: Este arquivo contém a correção para tests/conftest.py na branch MAIN
Para aplicar:
1. Faça checkout da branch main
2. Copie este conteúdo para tests/conftest.py
3. Commit e push
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CORREÇÃO: Configurar fake API key antes de qualquer import que precise dela
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-fake-key-for-testing-only"

@pytest.fixture
def mock_llm():
    """Mock for LLM responses."""
    mock = MagicMock()
    mock.invoke.return_value.content = "Mocked LLM Response"
    return mock

@pytest.fixture
def orchestrator(mock_llm):
    from core.agency_orchestrator import AgencyOrchestrator
    
    # CORREÇÃO: Usar patch.object para mockar get_llm de forma mais robusta
    with patch('core.agency_orchestrator.get_llm', return_value=mock_llm):
        with patch('teams.product_owner.team.get_llm', return_value=mock_llm):
            with patch('teams.architecture.team.get_llm', return_value=mock_llm):
                with patch('teams.data_engineering.team.get_llm', return_value=mock_llm):
                    orchestrator = AgencyOrchestrator()
                    orchestrator.global_master_agent = mock_llm
                    return orchestrator
