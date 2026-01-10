"""
Example: Using the autonomous data agency with an LLM.

This example demonstrates how to use the agency with an actual LLM
for intelligent task delegation and execution.

Note: This requires setting up API keys in a .env file or environment variables.
"""

import asyncio
import os

from langchain_openai import ChatOpenAI

from autonomous_data_agency import Agency, MasterAgent, TeamAgent
from autonomous_data_agency.agents.base_agent import AgentCapability
from autonomous_data_agency.utils.config import ConfigManager
from autonomous_data_agency.utils.logger import get_logger


async def main():
    """Run an example with LLM integration."""
    
    # Initialize logger
    logger = get_logger(level="INFO")
    
    print("=" * 60)
    print("Autonomous Data Agency - LLM Example")
    print("=" * 60)
    print()

    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Check if API key is available
    if not config.llm_config.api_key:
        print("Warning: No API key found in environment.")
        print("Please set OPENAI_API_KEY in your .env file or environment.")
        print("Continuing with mock LLM for demonstration...")
        llm = None
    else:
        # Initialize LLM
        llm = ChatOpenAI(
            model=config.llm_config.model,
            temperature=config.llm_config.temperature,
            api_key=config.llm_config.api_key,
        )
        logger.info("LLM initialized successfully")

    # Create specialized team agents with LLM
    research_team = TeamAgent(
        name="Research",
        role="Research Specialist",
        description="Conducts research and gathers information",
        llm=llm,
        capabilities=[
            AgentCapability(
                name="literature_review",
                description="Review academic and industry literature",
            ),
            AgentCapability(
                name="data_gathering",
                description="Gather relevant data from various sources",
            ),
        ],
        system_prompt="""You are a research specialist in the autonomous data agency.
Your role is to conduct thorough research, gather information, and provide 
evidence-based insights. Focus on accuracy, relevance, and citing sources.""",
    )

    analysis_team = TeamAgent(
        name="Analysis",
        role="Data Analyst",
        description="Analyzes data and generates insights",
        llm=llm,
        capabilities=[
            AgentCapability(
                name="quantitative_analysis",
                description="Perform quantitative data analysis",
            ),
            AgentCapability(
                name="insight_generation",
                description="Generate actionable insights from data",
            ),
        ],
        system_prompt="""You are a data analyst in the autonomous data agency.
Your role is to analyze data, identify patterns, and generate actionable insights.
Be analytical, objective, and provide clear recommendations.""",
    )

    reporting_team = TeamAgent(
        name="Reporting",
        role="Report Writer",
        description="Creates comprehensive reports and documentation",
        llm=llm,
        capabilities=[
            AgentCapability(
                name="report_creation",
                description="Create structured reports",
            ),
            AgentCapability(
                name="executive_summary",
                description="Write executive summaries",
            ),
        ],
        system_prompt="""You are a report writer in the autonomous data agency.
Your role is to synthesize information and create clear, comprehensive reports.
Write professionally, structure information logically, and make it accessible.""",
    )

    # Create master agent with LLM
    master = MasterAgent(
        name="ChiefCoordinator",
        role="Master Orchestrator",
        description="Intelligently delegates tasks to specialized teams",
        llm=llm,
    )

    # Create the agency
    agency = Agency(
        master_agent=master,
        team_agents=[research_team, analysis_team, reporting_team],
        max_iterations=5,
    )

    logger.info("Agency initialized with specialized teams")
    print("Agency teams:")
    for team in agency.get_team_info():
        print(f"  - {team['name']}: {team['description']}")
    print()

    # Execute a complex task
    task = """
    Analyze the trends in AI agent frameworks over the past year.
    Gather information about LangChain, LangGraph, and AutoGen.
    Provide insights on adoption patterns and create a summary report.
    """
    
    print(f"Executing task: {task.strip()}")
    print()
    
    logger.log_task_event("main_task", "started", task.strip())
    
    result = await agency.execute(
        task=task,
        context={
            "timeframe": "past 12 months",
            "focus_areas": ["adoption", "features", "community"],
        },
    )

    logger.log_task_event("main_task", "completed")
    
    print("\n" + "=" * 60)
    print("Task Execution Summary")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Teams involved: {', '.join(result['agents_involved'])}")
    
    if result.get('errors'):
        print(f"\nErrors encountered: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")
    
    if result['result']:
        print("\n" + "-" * 60)
        print("Detailed Results")
        print("-" * 60)
        
        if 'results' in result['result']:
            for team_result in result['result']['results']:
                print(f"\n{team_result['team']} Team ({team_result['role']}):")
                print("-" * 40)
                if 'result' in team_result:
                    print(team_result['result'])
                if 'error' in team_result:
                    print(f"Error: {team_result['error']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
