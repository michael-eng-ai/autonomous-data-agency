"""State management for the autonomous data agency using LangGraph."""

from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class TaskInfo(BaseModel):
    """Information about a task in the agency."""

    task_id: str = Field(description="Unique identifier for the task")
    description: str = Field(description="Description of the task")
    status: str = Field(default="pending", description="Status of the task (pending, in_progress, completed, failed)")
    assigned_to: Optional[str] = Field(default=None, description="Agent assigned to the task")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Result of the task execution")
    parent_task_id: Optional[str] = Field(default=None, description="Parent task ID if this is a subtask")
    subtasks: List[str] = Field(default_factory=list, description="IDs of subtasks")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")


class AgencyState(TypedDict, total=False):
    """
    State object for the autonomous data agency graph.
    
    This state is passed between nodes in the LangGraph workflow and tracks
    the current state of task execution.
    """

    # Current request/task
    input: str
    context: Dict[str, Any]
    
    # Task tracking
    current_task_id: str
    tasks: Dict[str, TaskInfo]
    
    # Agent states
    active_agents: List[str]
    agent_outputs: Dict[str, Any]
    
    # Workflow control
    next_step: str
    iteration: int
    max_iterations: int
    
    # Results
    final_output: Optional[Dict[str, Any]]
    errors: List[str]
    
    # Message history
    messages: List[Dict[str, Any]]


class StateManager:
    """
    Manages the state of the autonomous data agency.
    
    This class provides utilities for creating, updating, and querying
    the agency state during task execution.
    """

    @staticmethod
    def create_initial_state(
        input_text: str,
        context: Optional[Dict[str, Any]] = None,
        max_iterations: int = 10,
    ) -> AgencyState:
        """
        Create an initial state for a new task.
        
        Args:
            input_text: The input task or request
            context: Optional context information
            max_iterations: Maximum number of iterations allowed
            
        Returns:
            Initial AgencyState
        """
        return AgencyState(
            input=input_text,
            context=context or {},
            current_task_id="task_0",
            tasks={},
            active_agents=[],
            agent_outputs={},
            next_step="process",
            iteration=0,
            max_iterations=max_iterations,
            final_output=None,
            errors=[],
            messages=[],
        )

    @staticmethod
    def add_task(state: AgencyState, task: TaskInfo) -> AgencyState:
        """
        Add a new task to the state.
        
        Args:
            state: Current agency state
            task: Task information to add
            
        Returns:
            Updated state
        """
        state["tasks"][task.task_id] = task
        return state

    @staticmethod
    def update_task_status(
        state: AgencyState,
        task_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> AgencyState:
        """
        Update the status of a task.
        
        Args:
            state: Current agency state
            task_id: ID of the task to update
            status: New status
            result: Optional result data
            
        Returns:
            Updated state
        """
        if task_id in state["tasks"]:
            task = state["tasks"][task_id]
            task.status = status
            if result is not None:
                task.result = result
        return state

    @staticmethod
    def add_agent_output(
        state: AgencyState,
        agent_name: str,
        output: Any,
    ) -> AgencyState:
        """
        Add output from an agent to the state.
        
        Args:
            state: Current agency state
            agent_name: Name of the agent
            output: Output from the agent
            
        Returns:
            Updated state
        """
        state["agent_outputs"][agent_name] = output
        if agent_name not in state["active_agents"]:
            state["active_agents"].append(agent_name)
        return state

    @staticmethod
    def add_message(
        state: AgencyState,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgencyState:
        """
        Add a message to the state history.
        
        Args:
            state: Current agency state
            role: Role of the message sender
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Updated state
        """
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        state["messages"].append(message)
        return state

    @staticmethod
    def increment_iteration(state: AgencyState) -> AgencyState:
        """
        Increment the iteration counter.
        
        Args:
            state: Current agency state
            
        Returns:
            Updated state
        """
        state["iteration"] = state.get("iteration", 0) + 1
        return state

    @staticmethod
    def should_continue(state: AgencyState) -> bool:
        """
        Check if the workflow should continue.
        
        Args:
            state: Current agency state
            
        Returns:
            True if should continue, False otherwise
        """
        if state.get("final_output") is not None:
            return False
        if state.get("iteration", 0) >= state.get("max_iterations", 10):
            return False
        return True

    @staticmethod
    def set_final_output(
        state: AgencyState,
        output: Dict[str, Any],
    ) -> AgencyState:
        """
        Set the final output and mark completion.
        
        Args:
            state: Current agency state
            output: Final output data
            
        Returns:
            Updated state
        """
        state["final_output"] = output
        state["next_step"] = "end"
        return state

    @staticmethod
    def add_error(state: AgencyState, error: str) -> AgencyState:
        """
        Add an error to the state.
        
        Args:
            state: Current agency state
            error: Error message
            
        Returns:
            Updated state
        """
        state["errors"].append(error)
        return state
