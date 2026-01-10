"""Main agency orchestration class using LangGraph."""

from typing import Any, Dict, List, Optional

from langgraph.graph import END, StateGraph

from autonomous_data_agency.agents.base_agent import BaseAgent
from autonomous_data_agency.agents.master_agent import MasterAgent
from autonomous_data_agency.core.state import AgencyState, StateManager, TaskInfo


class Agency:
    """
    Main orchestration class for the autonomous data agency.
    
    The Agency class coordinates the master agent and team agents,
    manages the workflow using LangGraph, and provides the main
    interface for executing tasks.
    """

    def __init__(
        self,
        master_agent: Optional[MasterAgent] = None,
        team_agents: Optional[List[BaseAgent]] = None,
        max_iterations: int = 10,
    ):
        """
        Initialize the agency.
        
        Args:
            master_agent: The master orchestration agent
            team_agents: List of specialized team agents
            max_iterations: Maximum iterations for task processing
        """
        self.master_agent = master_agent or MasterAgent()
        self.team_agents = team_agents or []
        self.max_iterations = max_iterations
        self.state_manager = StateManager()
        
        # Register team agents with master
        for agent in self.team_agents:
            self.master_agent.register_team(agent)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()

    def add_team(self, team_agent: BaseAgent) -> None:
        """
        Add a team agent to the agency.
        
        Args:
            team_agent: The team agent to add
        """
        if team_agent not in self.team_agents:
            self.team_agents.append(team_agent)
            self.master_agent.register_team(team_agent)

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for the agency.
        
        Returns:
            Compiled StateGraph workflow
        """
        workflow = StateGraph(AgencyState)

        # Define nodes
        workflow.add_node("start", self._start_node)
        workflow.add_node("process", self._process_node)
        workflow.add_node("finalize", self._finalize_node)

        # Define edges
        workflow.set_entry_point("start")
        workflow.add_edge("start", "process")
        workflow.add_conditional_edges(
            "process",
            self._should_continue,
            {
                "continue": "process",
                "finalize": "finalize",
            },
        )
        workflow.add_edge("finalize", END)

        return workflow.compile()

    async def _start_node(self, state: AgencyState) -> AgencyState:
        """
        Initialize the workflow.
        
        Args:
            state: Current agency state
            
        Returns:
            Updated state
        """
        # Create initial task
        task = TaskInfo(
            task_id=state["current_task_id"],
            description=state["input"],
            status="pending",
        )
        state = self.state_manager.add_task(state, task)
        state = self.state_manager.add_message(
            state,
            role="user",
            content=state["input"],
        )
        return state

    async def _process_node(self, state: AgencyState) -> AgencyState:
        """
        Process tasks using the master agent.
        
        Args:
            state: Current agency state
            
        Returns:
            Updated state
        """
        state = self.state_manager.increment_iteration(state)
        
        try:
            # Process with master agent
            result = await self.master_agent.process(
                state["input"],
                state.get("context", {}),
            )
            
            # Update state with result
            state = self.state_manager.add_agent_output(
                state,
                self.master_agent.metadata.name,
                result,
            )
            
            state = self.state_manager.update_task_status(
                state,
                state["current_task_id"],
                "completed",
                result,
            )
            
            # Add message to history
            state = self.state_manager.add_message(
                state,
                role="assistant",
                content=str(result),
                metadata={"agent": self.master_agent.metadata.name},
            )
            
        except Exception as e:
            state = self.state_manager.add_error(state, str(e))
            state = self.state_manager.update_task_status(
                state,
                state["current_task_id"],
                "failed",
            )
        
        return state

    async def _finalize_node(self, state: AgencyState) -> AgencyState:
        """
        Finalize the workflow and prepare output.
        
        Args:
            state: Current agency state
            
        Returns:
            Updated state with final output
        """
        # Gather all results
        task_id = state["current_task_id"]
        task = state["tasks"].get(task_id)
        
        final_output = {
            "status": "success" if task and task.status == "completed" else "error",
            "input": state["input"],
            "result": task.result if task else None,
            "agents_involved": state["active_agents"],
            "iterations": state["iteration"],
            "errors": state.get("errors", []),
        }
        
        state = self.state_manager.set_final_output(state, final_output)
        return state

    def _should_continue(self, state: AgencyState) -> str:
        """
        Determine if the workflow should continue or finalize.
        
        Args:
            state: Current agency state
            
        Returns:
            "continue" or "finalize"
        """
        # Check if max iterations reached
        if state.get("iteration", 0) >= self.max_iterations:
            return "finalize"
        
        # Check if task is completed
        task_id = state["current_task_id"]
        task = state["tasks"].get(task_id)
        if task and task.status in ["completed", "failed"]:
            return "finalize"
        
        # Check if there are errors
        if state.get("errors"):
            return "finalize"
        
        return "continue"

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a task using the agency.
        
        Args:
            task: The task description
            context: Optional context information
            
        Returns:
            Dictionary containing the execution result
        """
        # Create initial state
        initial_state = self.state_manager.create_initial_state(
            task,
            context,
            self.max_iterations,
        )
        
        # Run the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        # Return the final output
        return final_state.get("final_output", {
            "status": "error",
            "message": "No output generated",
        })

    def get_team_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered teams.
        
        Returns:
            List of team information dictionaries
        """
        return self.master_agent.get_available_teams()

    def get_workflow_graph(self) -> Any:
        """
        Get the workflow graph for visualization.
        
        Returns:
            The compiled workflow graph
        """
        return self.workflow
