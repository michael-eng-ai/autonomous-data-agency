"""
Example: Basic usage of the autonomous data agency.

This example demonstrates how to create a simple agency with specialized teams
and execute tasks without requiring an LLM (for testing purposes).
"""

import asyncio

from autonomous_data_agency import Agency, MasterAgent, TeamAgent
from autonomous_data_agency.agents.base_agent import AgentCapability


async def main():
    """Run a basic example of the autonomous data agency."""
    
    print("=" * 60)
    print("Autonomous Data Agency - Basic Example")
    print("=" * 60)
    print()

    # Create specialized team agents
    data_analysis_team = TeamAgent(
        name="DataAnalysis",
        role="Data Analyst",
        description="Specializes in analyzing data and generating insights",
        capabilities=[
            AgentCapability(
                name="statistical_analysis",
                description="Perform statistical analysis on datasets",
                parameters={"data": "array", "method": "string"},
            ),
            AgentCapability(
                name="data_visualization",
                description="Create visualizations from data",
                parameters={"data": "array", "chart_type": "string"},
            ),
        ],
    )

    data_engineering_team = TeamAgent(
        name="DataEngineering",
        role="Data Engineer",
        description="Specializes in data processing and ETL operations",
        capabilities=[
            AgentCapability(
                name="data_transformation",
                description="Transform and clean data",
                parameters={"data": "array", "transformations": "list"},
            ),
            AgentCapability(
                name="pipeline_creation",
                description="Create data processing pipelines",
                parameters={"source": "string", "destination": "string"},
            ),
        ],
    )

    ml_team = TeamAgent(
        name="MachineLearning",
        role="ML Engineer",
        description="Specializes in machine learning model development",
        capabilities=[
            AgentCapability(
                name="model_training",
                description="Train machine learning models",
                parameters={"data": "array", "model_type": "string"},
            ),
            AgentCapability(
                name="model_evaluation",
                description="Evaluate model performance",
                parameters={"model": "object", "test_data": "array"},
            ),
        ],
    )

    # Create master agent
    master = MasterAgent(
        name="MasterCoordinator",
        role="Chief Orchestrator",
        description="Coordinates all specialized teams and delegates tasks",
    )

    # Create the agency
    agency = Agency(
        master_agent=master,
        team_agents=[data_analysis_team, data_engineering_team, ml_team],
        max_iterations=5,
    )

    print("Agency created with the following teams:")
    for team in agency.get_team_info():
        print(f"  - {team['name']} ({team['role']}): {team['description']}")
        print(f"    Capabilities: {len(team['capabilities'])}")
    print()

    # Execute a task
    task = "Analyze the customer purchase dataset and build a prediction model"
    print(f"Executing task: '{task}'")
    print()

    result = await agency.execute(
        task=task,
        context={
            "dataset": "customer_purchases.csv",
            "target": "purchase_amount",
        },
    )

    print("Task execution completed!")
    print()
    print("Result:")
    print(f"  Status: {result['status']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Agents involved: {', '.join(result['agents_involved'])}")
    print()
    
    if result['result']:
        print("Detailed results:")
        if 'results' in result['result']:
            for team_result in result['result']['results']:
                print(f"\n  Team: {team_result['team']} ({team_result['role']})")
                if 'result' in team_result:
                    print(f"    Result: {team_result['result']}")
                if 'error' in team_result:
                    print(f"    Error: {team_result['error']}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
