import pytest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_llm():
    """Mock for LLM responses."""
    mock = MagicMock()
    mock.invoke.return_value.content = "Mocked LLM Response"
    return mock

@pytest.fixture
def orchestrator(mock_llm):
    from core.agency_orchestrator import AgencyOrchestrator
    
    # Patch get_llm to return mock
    with pytest.MonkeyPatch.context() as m:
        m.setattr("core.agency_orchestrator.get_llm", lambda *args, **kwargs: MagicMock())
        # We also need to mock the internal agents creation
        orchestrator = AgencyOrchestrator()
        orchestrator.global_master_agent = mock_llm
        return orchestrator
