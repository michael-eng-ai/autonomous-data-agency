"""Master agent for delegating tasks to specialized teams."""

from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from autonomous_data_agency.agents.base_agent import AgentCapability, BaseAgent


class MasterAgent(BaseAgent):
    """
    Master agent that orchestrates and delegates tasks to specialized team agents.
    
    The master agent is responsible for:
    - Understanding incoming requests
    - Breaking down complex tasks
    - Delegating subtasks to appropriate team agents
    - Coordinating responses from multiple teams
    - Synthesizing final results
    """

    def __init__(
        self,
        name: str = "Master",
        role: str = "Orchestrator",
        description: str = "Orchestrates and delegates tasks to specialized teams",
        llm: Optional[Any] = None,
        team_agents: Optional[List[BaseAgent]] = None,
    ):
        """
        Initialize the master agent.
        
        Args:
            name: Name of the master agent
            role: Role of the master agent
            description: Description of the master agent's purpose
            llm: Language model for the master agent
            team_agents: List of team agents available for delegation
        """
        capabilities = [
            AgentCapability(
                name="task_delegation",
                description="Delegate tasks to specialized team agents",
                parameters={"team_agents": "list"},
            ),
            AgentCapability(
                name="task_decomposition",
                description="Break down complex tasks into subtasks",
                parameters={"task": "string"},
            ),
            AgentCapability(
                name="result_synthesis",
                description="Combine results from multiple teams",
                parameters={"results": "list"},
            ),
        ]
        super().__init__(name, role, description, llm, capabilities)
        self.team_agents = team_agents or []

    def register_team(self, team_agent: BaseAgent) -> None:
        """
        Register a new team agent for delegation.
        
        Args:
            team_agent: The team agent to register
        """
        if team_agent not in self.team_agents:
            self.team_agents.append(team_agent)

    def get_available_teams(self) -> List[Dict[str, Any]]:
        """
        Get information about available team agents.
        
        Returns:
            List of dictionaries containing team metadata
        """
        return [
            {
                "name": agent.metadata.name,
                "role": agent.metadata.role,
                "description": agent.metadata.description,
                "capabilities": [cap.dict() for cap in agent.get_capabilities()],
            }
            for agent in self.team_agents
        ]

    async def _select_teams(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[BaseAgent]:
        """
        Select appropriate team agents for a given task.
        
        Args:
            task: The task to be performed
            context: Optional context information
            
        Returns:
            List of selected team agents
        """
        if not self.llm:
            # Without LLM, return all teams
            return self.team_agents

        teams_info = self.get_available_teams()
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a master agent responsible for selecting the right teams for a task.
Given a task and available teams, identify which teams should work on the task.
Respond with a JSON list of team names."""),
            HumanMessage(content=f"""Task: {task}

Available teams:
{teams_info}

Select the appropriate teams (respond with JSON array of team names):"""),
        ])

        # For now, return all teams if we have an LLM
        # In a full implementation, this would use the LLM to intelligently select
        return self.team_agents

    async def _decompose_task(self, task: str, selected_teams: List[BaseAgent]) -> List[Dict[str, Any]]:
        """
        Decompose a task into subtasks for each team.
        
        Args:
            task: The main task
            selected_teams: Teams that will work on the task
            
        Returns:
            List of subtasks with assigned teams
        """
        subtasks = []
        for team in selected_teams:
            subtasks.append({
                "team": team,
                "task": f"[{team.metadata.role}] {task}",
                "original_task": task,
            })
        return subtasks

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a task by delegating to appropriate team agents.
        
        Args:
            task: Description of the task to perform
            context: Optional context information
            
        Returns:
            Dictionary containing the aggregated results from all teams
        """
        self.add_message(HumanMessage(content=task))

        # Select appropriate teams
        selected_teams = await self._select_teams(task, context)

        if not selected_teams:
            return {
                "status": "error",
                "message": "No teams available to handle the task",
                "task": task,
            }

        # Decompose task into subtasks
        subtasks = await self._decompose_task(task, selected_teams)

        # Delegate to teams and collect results
        team_results = []
        for subtask in subtasks:
            team = subtask["team"]
            team_task = subtask["task"]
            
            try:
                result = await team.process(team_task, context)
                team_results.append({
                    "team": team.metadata.name,
                    "role": team.metadata.role,
                    "result": result,
                })
            except Exception as e:
                team_results.append({
                    "team": team.metadata.name,
                    "role": team.metadata.role,
                    "error": str(e),
                })

        # Synthesize results
        response = {
            "status": "success",
            "task": task,
            "teams_involved": [team.metadata.name for team in selected_teams],
            "results": team_results,
            "summary": f"Task delegated to {len(selected_teams)} team(s) and completed",
        }

        return response
