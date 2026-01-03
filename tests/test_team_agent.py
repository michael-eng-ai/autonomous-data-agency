"""Tests for team agent functionality."""

import pytest

from autonomous_data_agency.agents.base_agent import AgentCapability
from autonomous_data_agency.agents.team_agent import TeamAgent


def test_team_agent_initialization():
    """Test team agent initialization."""
    capabilities = [
        AgentCapability(name="cap1", description="Capability 1"),
    ]
    
    team = TeamAgent(
        name="TestTeam",
        role="Tester",
        description="Test team",
        capabilities=capabilities,
    )
    
    assert team.metadata.name == "TestTeam"
    assert team.metadata.role == "Tester"
    assert len(team.metadata.capabilities) == 1


def test_team_agent_default_system_prompt():
    """Test default system prompt generation."""
    team = TeamAgent(
        name="TestTeam",
        role="Analyst",
        description="Analyzes data",
    )
    
    assert "TestTeam" in team.system_prompt
    assert "Analyst" in team.system_prompt


def test_team_agent_custom_system_prompt():
    """Test custom system prompt."""
    custom_prompt = "You are a custom agent with special instructions."
    
    team = TeamAgent(
        name="TestTeam",
        role="Tester",
        description="Test team",
        system_prompt=custom_prompt,
    )
    
    assert team.system_prompt == custom_prompt


@pytest.mark.asyncio
async def test_team_agent_process_without_llm():
    """Test processing without LLM (mock mode)."""
    team = TeamAgent(
        name="TestTeam",
        role="Tester",
        description="Test team",
    )
    
    result = await team.process("test task")
    
    assert result["status"] == "success"
    assert result["team"] == "TestTeam"
    assert result["role"] == "Tester"
    assert result["task"] == "test task"
    assert "note" in result  # Mock response note


@pytest.mark.asyncio
async def test_team_agent_process_with_context():
    """Test processing with context."""
    team = TeamAgent(
        name="TestTeam",
        role="Tester",
        description="Test team",
    )
    
    context = {"key": "value", "priority": "high"}
    result = await team.process("test task", context=context)
    
    assert result["status"] == "success"
    assert result["task"] == "test task"


def test_team_agent_add_capability():
    """Test adding capabilities dynamically."""
    team = TeamAgent(
        name="TestTeam",
        role="Tester",
        description="Test team",
    )
    
    # Initially no custom capabilities
    initial_count = len(team.metadata.capabilities)
    
    # Add capability
    new_cap = AgentCapability(name="new_cap", description="New capability")
    team.add_capability(new_cap)
    
    assert len(team.metadata.capabilities) == initial_count + 1
    assert team.metadata.capabilities[-1].name == "new_cap"
    
    # Adding same capability again
    team.add_capability(new_cap)
    assert len(team.metadata.capabilities) == initial_count + 1  # No duplicate


def test_team_agent_remove_capability():
    """Test removing capabilities."""
    capabilities = [
        AgentCapability(name="cap1", description="Capability 1"),
        AgentCapability(name="cap2", description="Capability 2"),
    ]
    
    team = TeamAgent(
        name="TestTeam",
        role="Tester",
        description="Test team",
        capabilities=capabilities,
    )
    
    # Remove existing capability
    result = team.remove_capability("cap1")
    assert result is True
    assert len(team.metadata.capabilities) == 1
    assert team.metadata.capabilities[0].name == "cap2"
    
    # Try to remove non-existent capability
    result = team.remove_capability("cap_nonexistent")
    assert result is False
    assert len(team.metadata.capabilities) == 1


def test_team_agent_format_capabilities():
    """Test capability formatting."""
    capabilities = [
        AgentCapability(name="cap1", description="First capability"),
        AgentCapability(name="cap2", description="Second capability"),
    ]
    
    team = TeamAgent(
        name="TestTeam",
        role="Tester",
        description="Test team",
        capabilities=capabilities,
    )
    
    formatted = team._format_capabilities()
    assert "cap1" in formatted
    assert "cap2" in formatted
    assert "First capability" in formatted
    assert "Second capability" in formatted


def test_team_agent_with_no_capabilities():
    """Test team agent without capabilities."""
    team = TeamAgent(
        name="TestTeam",
        role="Tester",
        description="Test team",
    )
    
    formatted = team._format_capabilities()
    assert "General task execution" in formatted
