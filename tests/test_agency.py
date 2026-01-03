"""Tests for agency orchestration."""

import pytest

from autonomous_data_agency.core.agency import Agency
from autonomous_data_agency.agents.master_agent import MasterAgent
from autonomous_data_agency.agents.team_agent import TeamAgent


@pytest.mark.asyncio
async def test_agency_initialization():
    """Test agency initialization."""
    master = MasterAgent()
    teams = [
        TeamAgent(name="Team1", role="Role1", description="Desc1"),
    ]
    
    agency = Agency(master_agent=master, team_agents=teams)
    
    assert agency.master_agent == master
    assert len(agency.team_agents) == 1


@pytest.mark.asyncio
async def test_agency_default_initialization():
    """Test agency with default parameters."""
    agency = Agency()
    
    assert agency.master_agent is not None
    assert isinstance(agency.master_agent, MasterAgent)
    assert len(agency.team_agents) == 0


@pytest.mark.asyncio
async def test_agency_add_team():
    """Test adding teams to agency."""
    agency = Agency()
    
    team1 = TeamAgent(name="Team1", role="Role1", description="Desc1")
    team2 = TeamAgent(name="Team2", role="Role2", description="Desc2")
    
    agency.add_team(team1)
    assert len(agency.team_agents) == 1
    
    agency.add_team(team2)
    assert len(agency.team_agents) == 2
    
    # Adding same team again shouldn't duplicate
    agency.add_team(team1)
    assert len(agency.team_agents) == 2


@pytest.mark.asyncio
async def test_agency_get_team_info():
    """Test getting team information."""
    team1 = TeamAgent(name="Team1", role="Analyst", description="Data analysis")
    team2 = TeamAgent(name="Team2", role="Engineer", description="Data engineering")
    
    agency = Agency(team_agents=[team1, team2])
    
    teams_info = agency.get_team_info()
    
    assert len(teams_info) == 2
    assert teams_info[0]["name"] == "Team1"
    assert teams_info[1]["name"] == "Team2"


@pytest.mark.asyncio
async def test_agency_execute():
    """Test executing a task."""
    team = TeamAgent(name="TestTeam", role="Tester", description="Test team")
    agency = Agency(team_agents=[team])
    
    result = await agency.execute("Test task")
    
    assert "status" in result
    assert "result" in result
    assert result["status"] in ["success", "error"]


@pytest.mark.asyncio
async def test_agency_execute_with_context():
    """Test executing a task with context."""
    team = TeamAgent(name="TestTeam", role="Tester", description="Test team")
    agency = Agency(team_agents=[team])
    
    context = {"dataset": "test.csv", "priority": "high"}
    result = await agency.execute("Test task", context=context)
    
    assert "status" in result


@pytest.mark.asyncio
async def test_agency_max_iterations():
    """Test agency with max iterations limit."""
    agency = Agency(max_iterations=3)
    team = TeamAgent(name="TestTeam", role="Tester", description="Test team")
    agency.add_team(team)
    
    result = await agency.execute("Test task")
    
    assert result["iterations"] <= 3


@pytest.mark.asyncio
async def test_agency_workflow_graph():
    """Test getting workflow graph."""
    agency = Agency()
    
    graph = agency.get_workflow_graph()
    
    assert graph is not None


@pytest.mark.asyncio
async def test_agency_multiple_teams_execution():
    """Test execution with multiple teams."""
    team1 = TeamAgent(name="Team1", role="Analyst", description="Analyzes data")
    team2 = TeamAgent(name="Team2", role="Engineer", description="Processes data")
    team3 = TeamAgent(name="Team3", role="Reporter", description="Creates reports")
    
    agency = Agency(team_agents=[team1, team2, team3])
    
    result = await agency.execute("Analyze, process, and report on data")
    
    assert result["status"] in ["success", "error"]
    if result["status"] == "success":
        assert "agents_involved" in result
