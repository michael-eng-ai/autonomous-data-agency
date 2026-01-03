"""Team agent for executing specialized tasks."""

from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from autonomous_data_agency.agents.base_agent import AgentCapability, BaseAgent


class TeamAgent(BaseAgent):
    """
    Team agent that specializes in specific types of tasks.
    
    Team agents are expert workers that:
    - Focus on their area of specialization
    - Execute tasks delegated by the master agent
    - Report results back to the master
    - Can have custom tools and capabilities
    """

    def __init__(
        self,
        name: str,
        role: str,
        description: str,
        llm: Optional[Any] = None,
        capabilities: Optional[List[AgentCapability]] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize a team agent.
        
        Args:
            name: Unique name for the team
            role: Specialization or role of the team
            description: Description of what the team does
            llm: Language model for the team
            capabilities: List of capabilities the team has
            system_prompt: Custom system prompt for the team's behavior
        """
        super().__init__(name, role, description, llm, capabilities)
        self.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        """Generate a default system prompt based on the team's metadata."""
        return f"""You are a specialized AI agent on the {self.metadata.name} team.

Role: {self.metadata.role}
Description: {self.metadata.description}

Your capabilities:
{self._format_capabilities()}

You should focus on tasks related to your specialization and provide expert-level responses.
Be concise, accurate, and actionable in your responses."""

    def _format_capabilities(self) -> str:
        """Format capabilities for display in the system prompt."""
        if not self.metadata.capabilities:
            return "- General task execution"
        
        return "\n".join([
            f"- {cap.name}: {cap.description}"
            for cap in self.metadata.capabilities
        ])

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a task using the team's specialization.
        
        Args:
            task: Description of the task to perform
            context: Optional context information
            
        Returns:
            Dictionary containing the task result
        """
        self.add_message(HumanMessage(content=task))

        if not self.llm:
            # Without LLM, return a simple acknowledgment
            return {
                "status": "success",
                "team": self.metadata.name,
                "role": self.metadata.role,
                "task": task,
                "result": f"Task received and acknowledged by {self.metadata.name} team",
                "note": "No LLM configured - this is a mock response",
            }

        # Create a prompt with the system message and task
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Task: {task}\n\nContext: {context or {}}"),
        ]

        try:
            # Use the LLM to process the task
            # Note: This is a simplified version. In production, you might use LLMChain
            # or more sophisticated LangChain constructs
            response = await self.llm.agenerate([messages])
            result_text = response.generations[0][0].text

            return {
                "status": "success",
                "team": self.metadata.name,
                "role": self.metadata.role,
                "task": task,
                "result": result_text,
            }
        except Exception as e:
            return {
                "status": "error",
                "team": self.metadata.name,
                "role": self.metadata.role,
                "task": task,
                "error": str(e),
            }

    def add_capability(self, capability: AgentCapability) -> None:
        """
        Add a new capability to the team.
        
        Args:
            capability: The capability to add
        """
        if capability not in self.metadata.capabilities:
            self.metadata.capabilities.append(capability)

    def remove_capability(self, capability_name: str) -> bool:
        """
        Remove a capability from the team.
        
        Args:
            capability_name: Name of the capability to remove
            
        Returns:
            True if capability was removed, False if not found
        """
        for i, cap in enumerate(self.metadata.capabilities):
            if cap.name == capability_name:
                self.metadata.capabilities.pop(i)
                return True
        return False
