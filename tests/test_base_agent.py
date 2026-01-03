"""Tests for base agent functionality."""

import pytest

from autonomous_data_agency.agents.base_agent import AgentCapability, AgentMetadata, BaseAgent


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    async def process(self, task: str, context=None):
        return {"status": "success", "task": task, "result": "mock result"}


def test_agent_metadata_creation():
    """Test creating agent metadata."""
    metadata = AgentMetadata(
        name="TestAgent",
        role="Tester",
        description="A test agent",
        capabilities=[],
    )
    
    assert metadata.name == "TestAgent"
    assert metadata.role == "Tester"
    assert metadata.description == "A test agent"
    assert len(metadata.capabilities) == 0


def test_agent_capability_creation():
    """Test creating agent capabilities."""
    capability = AgentCapability(
        name="test_capability",
        description="A test capability",
        parameters={"param1": "string"},
    )
    
    assert capability.name == "test_capability"
    assert capability.description == "A test capability"
    assert capability.parameters == {"param1": "string"}


def test_base_agent_initialization():
    """Test base agent initialization."""
    capabilities = [
        AgentCapability(
            name="capability1",
            description="First capability",
        )
    ]
    
    agent = MockAgent(
        name="TestAgent",
        role="Tester",
        description="Test agent description",
        capabilities=capabilities,
    )
    
    assert agent.metadata.name == "TestAgent"
    assert agent.metadata.role == "Tester"
    assert len(agent.metadata.capabilities) == 1


def test_agent_get_capabilities():
    """Test getting agent capabilities."""
    capabilities = [
        AgentCapability(name="cap1", description="Capability 1"),
        AgentCapability(name="cap2", description="Capability 2"),
    ]
    
    agent = MockAgent(
        name="TestAgent",
        role="Tester",
        description="Test",
        capabilities=capabilities,
    )
    
    result = agent.get_capabilities()
    assert len(result) == 2
    assert result[0].name == "cap1"
    assert result[1].name == "cap2"


def test_agent_message_history():
    """Test agent message history management."""
    from langchain.schema import HumanMessage, AIMessage
    
    agent = MockAgent(
        name="TestAgent",
        role="Tester",
        description="Test",
    )
    
    # Initially empty
    assert len(agent.get_message_history()) == 0
    
    # Add messages
    agent.add_message(HumanMessage(content="Hello"))
    agent.add_message(AIMessage(content="Hi there"))
    
    # Check history
    history = agent.get_message_history()
    assert len(history) == 2
    assert history[0].content == "Hello"
    assert history[1].content == "Hi there"
    
    # Clear history
    agent.clear_history()
    assert len(agent.get_message_history()) == 0


@pytest.mark.asyncio
async def test_agent_process():
    """Test agent process method."""
    agent = MockAgent(
        name="TestAgent",
        role="Tester",
        description="Test",
    )
    
    result = await agent.process("test task")
    
    assert result["status"] == "success"
    assert result["task"] == "test task"
    assert "result" in result


def test_agent_repr():
    """Test agent string representation."""
    agent = MockAgent(
        name="TestAgent",
        role="Tester",
        description="Test",
    )
    
    repr_str = repr(agent)
    assert "MockAgent" in repr_str
    assert "TestAgent" in repr_str
    assert "Tester" in repr_str
