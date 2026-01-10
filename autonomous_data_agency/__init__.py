"""
Autonomous Data Agency

A framework for orchestrating hierarchical teams of AI agents using LangChain and LangGraph.
"""

__version__ = "0.1.0"

from autonomous_data_agency.agents.base_agent import BaseAgent
from autonomous_data_agency.agents.master_agent import MasterAgent
from autonomous_data_agency.agents.team_agent import TeamAgent
from autonomous_data_agency.core.agency import Agency
from autonomous_data_agency.core.state import AgencyState

__all__ = [
    "BaseAgent",
    "MasterAgent",
    "TeamAgent",
    "Agency",
    "AgencyState",
]
