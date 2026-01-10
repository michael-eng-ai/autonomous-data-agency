"""Tests for master agent functionality."""

import pytest

from autonomous_data_agency.agents.master_agent import MasterAgent
from autonomous_data_agency.agents.team_agent import TeamAgent


@pytest.mark.asyncio
async def test_master_agent_initialization():
    """Test master agent initialization."""
    master = MasterAgent()
    
    assert master.metadata.name == "Master"
    assert master.metadata.role == "Orchestrator"
    assert len(master.team_agents) == 0
    assert len(master.get_capabilities()) == 3  # Default capabilities


@pytest.mark.asyncio
async def test_master_agent_register_team():
    """Test registering team agents."""
    master = MasterAgent()
    team1 = TeamAgent(name="Team1", role="Role1", description="Desc1")
    team2 = TeamAgent(name="Team2", role="Role2", description="Desc2")
    
    master.register_team(team1)
    assert len(master.team_agents) == 1
    
    master.register_team(team2)
    assert len(master.team_agents) == 2
    
    # Registering same team again shouldn't duplicate
    master.register_team(team1)
    assert len(master.team_agents) == 2


@pytest.mark.asyncio
async def test_master_agent_get_available_teams():
    """Test getting available teams information."""
    master = MasterAgent()
    team1 = TeamAgent(name="Team1", role="Role1", description="Desc1")
    team2 = TeamAgent(name="Team2", role="Role2", description="Desc2")
    
    master.register_team(team1)
    master.register_team(team2)
    
    teams_info = master.get_available_teams()
    
    assert len(teams_info) == 2
    assert teams_info[0]["name"] == "Team1"
    assert teams_info[1]["name"] == "Team2"
    assert "capabilities" in teams_info[0]


@pytest.mark.asyncio
async def test_master_agent_process_no_teams():
    """Test processing when no teams are available."""
    master = MasterAgent()
    
    result = await master.process("test task")
    
    assert result["status"] == "error"
    assert "No teams available" in result["message"]


@pytest.mark.asyncio
async def test_master_agent_process_with_teams():
    """Test processing with registered teams."""
    master = MasterAgent()
    team1 = TeamAgent(name="Team1", role="Analyst", description="Analysis team")
    team2 = TeamAgent(name="Team2", role="Engineer", description="Engineering team")
    
    master.register_team(team1)
    master.register_team(team2)
    
    result = await master.process("Analyze and build a system")
    
    assert result["status"] == "success"
    assert "teams_involved" in result
    assert len(result["results"]) == 2
    assert result["results"][0]["team"] == "Team1"
    assert result["results"][1]["team"] == "Team2"


@pytest.mark.asyncio
async def test_master_agent_process_with_context():
    """Test processing with context."""
    master = MasterAgent()
    team = TeamAgent(name="Team1", role="Analyst", description="Analysis team")
    master.register_team(team)
    
    context = {"dataset": "test.csv", "priority": "high"}
    result = await master.process("Analyze data", context=context)
    
    assert result["status"] == "success"
    assert "results" in result


@pytest.mark.asyncio
async def test_master_agent_custom_initialization():
    """Test master agent with custom parameters."""
    teams = [
        TeamAgent(name="Team1", role="Role1", description="Desc1"),
        TeamAgent(name="Team2", role="Role2", description="Desc2"),
    ]
    
    master = MasterAgent(
        name="CustomMaster",
        role="CustomRole",
        description="Custom description",
        team_agents=teams,
    )
    
    assert master.metadata.name == "CustomMaster"
    assert master.metadata.role == "CustomRole"
    assert len(master.team_agents) == 2
