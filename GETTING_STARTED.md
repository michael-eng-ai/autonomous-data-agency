# Getting Started with Autonomous Data Agency

This guide will help you get started with the Autonomous Data Agency framework.

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/michael-eng-ai/autonomous-data-agency.git
cd autonomous-data-agency
```

2. **Install the package:**
```bash
pip install -e .
```

Or install dependencies separately:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Usage (No LLM Required)

The simplest way to get started is without an LLM. This is perfect for testing and understanding the framework:

```python
import asyncio
from autonomous_data_agency import Agency, MasterAgent, TeamAgent
from autonomous_data_agency.agents.base_agent import AgentCapability

async def main():
    # Create a specialized team
    analyst_team = TeamAgent(
        name="DataAnalyst",
        role="Data Analyst",
        description="Analyzes data and provides insights",
        capabilities=[
            AgentCapability(
                name="data_analysis",
                description="Analyze datasets",
            )
        ]
    )
    
    # Create the agency
    agency = Agency(team_agents=[analyst_team])
    
    # Execute a task
    result = await agency.execute("Analyze sales data for Q4")
    print(result)

asyncio.run(main())
```

### 2. Using with an LLM

To use the framework with actual AI capabilities:

1. **Set up your API key:**
Create a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4
```

2. **Use the LLM in your agents:**
```python
import asyncio
from langchain_openai import ChatOpenAI
from autonomous_data_agency import Agency, MasterAgent, TeamAgent

async def main():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # Create team with LLM
    analyst_team = TeamAgent(
        name="DataAnalyst",
        role="Data Analyst",
        description="Analyzes data",
        llm=llm,
        system_prompt="You are an expert data analyst..."
    )
    
    # Create master with LLM
    master = MasterAgent(llm=llm)
    
    # Create agency
    agency = Agency(master_agent=master, team_agents=[analyst_team])
    
    # Execute task
    result = await agency.execute("Analyze customer churn patterns")
    print(result)

asyncio.run(main())
```

### 3. Run the Examples

Try the included examples:

```bash
# Basic example (no API key needed)
python examples/basic_example.py

# LLM example (requires OpenAI API key)
python examples/llm_example.py
```

## Key Concepts

### Agents

- **BaseAgent**: Base class for all agents
- **MasterAgent**: Coordinates and delegates tasks to teams
- **TeamAgent**: Specialized agents that execute tasks

### Agency

The Agency class orchestrates the entire workflow using LangGraph:

```python
agency = Agency(
    master_agent=master,
    team_agents=[team1, team2, team3],
    max_iterations=10
)
```

### Capabilities

Define what each team can do:

```python
capability = AgentCapability(
    name="data_visualization",
    description="Create charts and graphs",
    parameters={"chart_type": "string", "data": "array"}
)
```

### State Management

The framework automatically manages state throughout task execution:
- Task tracking
- Agent outputs
- Message history
- Error handling

## Creating Custom Teams

```python
custom_team = TeamAgent(
    name="CustomTeam",
    role="Specialist",
    description="Does specialized work",
    llm=llm,  # Optional
    capabilities=[...],  # Optional
    system_prompt="Custom instructions..."  # Optional
)

agency.add_team(custom_team)
```

## Configuration

Use environment variables or configuration files:

```python
from autonomous_data_agency.utils.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config()

# Update configuration
config_manager.update_config(
    max_iterations=20,
    log_level="DEBUG"
)
```

## Testing

Run the test suite:

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_agency.py

# With verbose output
pytest tests/ -v
```

## Common Use Cases

### Data Science Workflow

```python
teams = [
    TeamAgent(name="DataCollection", role="Data Engineer", ...),
    TeamAgent(name="DataAnalysis", role="Data Scientist", ...),
    TeamAgent(name="Modeling", role="ML Engineer", ...),
    TeamAgent(name="Reporting", role="Report Writer", ...)
]
```

### Research & Analysis

```python
teams = [
    TeamAgent(name="Research", role="Researcher", ...),
    TeamAgent(name="Analysis", role="Analyst", ...),
    TeamAgent(name="Writing", role="Writer", ...)
]
```

### Customer Service

```python
teams = [
    TeamAgent(name="Routing", role="Classifier", ...),
    TeamAgent(name="Technical", role="Tech Support", ...),
    TeamAgent(name="Billing", role="Billing Support", ...),
    TeamAgent(name="Escalation", role="Senior Support", ...)
]
```

## Next Steps

1. **Read the full documentation**: Check out the README.md for detailed information
2. **Explore examples**: Look at the examples/ directory for more use cases
3. **Customize**: Create your own specialized teams and workflows
4. **Integrate**: Connect with your data sources, tools, and systems
5. **Deploy**: Use in production for real-world tasks

## Troubleshooting

### Import Errors

Make sure all dependencies are installed:
```bash
pip install langchain langchain-core langchain-openai langgraph pydantic python-dotenv
```

### API Key Issues

Ensure your `.env` file is in the project root and contains:
```bash
OPENAI_API_KEY=your_actual_key_here
```

### LangChain Version Issues

This framework is tested with LangChain 0.1.0+. If you have issues:
```bash
pip install --upgrade langchain langchain-core langchain-openai langgraph
```

## Support

- **Issues**: Open an issue on GitHub
- **Documentation**: See README.md for comprehensive documentation
- **Examples**: Check the examples/ directory

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

---

Happy building with Autonomous Data Agency! 🤖
