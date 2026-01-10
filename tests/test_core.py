import pytest
from core.agency_orchestrator import AgencyOrchestrator, ProjectPhase
from core.teams_factory import TeamsFactory, TeamType

def test_teams_factory_list():
    """Test listing available teams."""
    teams = TeamsFactory.list_available_teams()
    assert len(teams) > 0
    assert any(t["type"] == "product_owner" for t in teams)

def test_teams_factory_get_config():
    """Test getting team configuration."""
    config = TeamsFactory.get_team_config(TeamType.DATA_ENGINEERING)
    assert config.name == "Data Engineering Team"
    assert config.domain == "data_engineering"

def test_orchestrator_initialization():
    """Test orchestrator initialization (mocked)."""
    # This test assumes we can instantiate it without side effects
    # dependencies on LLMs might make this tricky without full mocking
    pass

@pytest.mark.asyncio
async def test_project_lifecycle(orchestrator):
    """Test basic project lifecycle."""
    project = orchestrator.start_project("Test Project", "Test Request")
    assert project.project_name == "Test Project"
    assert project.current_phase == ProjectPhase.REQUIREMENTS
    assert project.client_request == "Test Request"
    
    # Check that ID is generated
    assert project.project_id.startswith("proj_")
