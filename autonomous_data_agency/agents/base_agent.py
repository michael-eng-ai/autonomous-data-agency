"""Base agent class for all agents in the autonomous data agency."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class AgentCapability(BaseModel):
    """Represents a capability that an agent possesses."""

    name: str = Field(description="Name of the capability")
    description: str = Field(description="Description of what the capability does")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters accepted by this capability"
    )


class AgentMetadata(BaseModel):
    """Metadata about an agent."""

    name: str = Field(description="Unique name of the agent")
    role: str = Field(description="Role or specialization of the agent")
    description: str = Field(description="Description of the agent's purpose")
    capabilities: List[AgentCapability] = Field(
        default_factory=list, description="List of agent capabilities"
    )


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the autonomous data agency.
    
    This class provides the foundation for creating specialized agents
    that can work independently or as part of a hierarchical team.
    """

    def __init__(
        self,
        name: str,
        role: str,
        description: str,
        llm: Optional[Any] = None,
        capabilities: Optional[List[AgentCapability]] = None,
    ):
        """
        Initialize a base agent.
        
        Args:
            name: Unique name for the agent
            role: Role or specialization of the agent
            description: Description of the agent's purpose
            llm: Language model to use for the agent
            capabilities: List of capabilities the agent possesses
        """
        self.metadata = AgentMetadata(
            name=name,
            role=role,
            description=description,
            capabilities=capabilities or [],
        )
        self.llm = llm
        self.message_history: List[BaseMessage] = []

    @abstractmethod
    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a task assigned to the agent.
        
        Args:
            task: Description of the task to perform
            context: Optional context information for the task
            
        Returns:
            Dictionary containing the result of processing the task
        """
        pass

    def get_capabilities(self) -> List[AgentCapability]:
        """Return the list of capabilities this agent possesses."""
        return self.metadata.capabilities

    def get_metadata(self) -> AgentMetadata:
        """Return metadata about this agent."""
        return self.metadata

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the agent's history."""
        self.message_history.append(message)

    def get_message_history(self) -> List[BaseMessage]:
        """Return the agent's message history."""
        return self.message_history

    def clear_history(self) -> None:
        """Clear the agent's message history."""
        self.message_history = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.metadata.name}', role='{self.metadata.role}')"
