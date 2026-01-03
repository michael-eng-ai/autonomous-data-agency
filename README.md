# Autonomous Data Agency

A Python framework for orchestrating hierarchical teams of AI agents using LangChain and LangGraph.

## Overview

The Autonomous Data Agency is a powerful framework that enables you to create, manage, and orchestrate teams of specialized AI agents. It uses a hierarchical structure where a **Master Agent** coordinates and delegates tasks to specialized **Team Agents**, each with their own expertise and capabilities.

### Key Features

- 🤖 **Hierarchical Agent Architecture**: Master agent delegates to specialized team agents
- 🔄 **LangGraph Integration**: Built-in workflow orchestration using LangGraph state machines
- 🎯 **Specialized Teams**: Create teams with specific roles and capabilities
- 📊 **State Management**: Comprehensive state tracking throughout task execution
- 🔧 **Flexible Configuration**: Easy configuration via environment variables or config files
- 📝 **Logging & Monitoring**: Built-in logging utilities for tracking agent activities
- 🚀 **Async Support**: Fully asynchronous for high-performance execution

## Architecture

```
┌─────────────────────────────────────────┐
│         Master Agent                     │
│  (Orchestrates & Delegates)             │
└────────────┬────────────────────────────┘
             │
             ├─────────────┬──────────────┬──────────────┐
             │             │              │              │
        ┌────▼────┐   ┌───▼────┐   ┌────▼────┐   ┌────▼────┐
        │ Team A  │   │ Team B │   │ Team C  │   │ Team D  │
        │ Agent   │   │ Agent  │   │ Agent   │   │ Agent   │
        └─────────┘   └────────┘   └─────────┘   └─────────┘
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or poetry for package management

### Install from source

```bash
git clone https://github.com/michael-eng-ai/autonomous-data-agency.git
cd autonomous-data-agency
pip install -e .
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Example (No LLM Required)

```python
import asyncio
from autonomous_data_agency import Agency, MasterAgent, TeamAgent
from autonomous_data_agency.agents.base_agent import AgentCapability

async def main():
    # Create specialized team agents
    data_team = TeamAgent(
        name="DataAnalysis",
        role="Data Analyst",
        description="Analyzes data and generates insights",
        capabilities=[
            AgentCapability(
                name="statistical_analysis",
                description="Perform statistical analysis",
            )
        ],
    )
    
    # Create master agent
    master = MasterAgent()
    
    # Create agency
    agency = Agency(
        master_agent=master,
        team_agents=[data_team],
    )
    
    # Execute a task
    result = await agency.execute(
        task="Analyze customer purchase patterns",
        context={"dataset": "purchases.csv"}
    )
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example with LLM Integration

```python
import asyncio
from langchain_openai import ChatOpenAI
from autonomous_data_agency import Agency, MasterAgent, TeamAgent

async def main():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # Create team with LLM
    research_team = TeamAgent(
        name="Research",
        role="Research Specialist",
        description="Conducts research and gathers information",
        llm=llm,
        system_prompt="You are an expert research analyst..."
    )
    
    # Create master with LLM
    master = MasterAgent(llm=llm)
    
    # Create agency
    agency = Agency(
        master_agent=master,
        team_agents=[research_team],
    )
    
    # Execute task
    result = await agency.execute(
        task="Research AI agent frameworks"
    )
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# LLM Configuration
OPENAI_API_KEY=your_api_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Agency Configuration
AGENCY_NAME=My Data Agency
MAX_ITERATIONS=10

# Logging
ENABLE_LOGGING=true
LOG_LEVEL=INFO
```

### Programmatic Configuration

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

## Core Components

### BaseAgent

Abstract base class for all agents. Provides:
- Message history management
- Capability registration
- Metadata management

### MasterAgent

Orchestrates and delegates tasks to team agents:
- Task decomposition
- Team selection
- Result synthesis
- Coordination

### TeamAgent

Specialized agents for specific tasks:
- Domain expertise
- Custom capabilities
- Task execution
- Result reporting

### Agency

Main orchestration class:
- Workflow management using LangGraph
- State management
- Task execution coordination
- Result aggregation

### AgencyState

State management for workflow:
- Task tracking
- Agent status
- Message history
- Results aggregation

## Examples

Run the provided examples:

```bash
# Basic example (no LLM required)
python examples/basic_example.py

# LLM example (requires API key)
python examples/llm_example.py
```

## Advanced Usage

### Custom Team Agents

```python
from autonomous_data_agency.agents.team_agent import TeamAgent
from autonomous_data_agency.agents.base_agent import AgentCapability

custom_team = TeamAgent(
    name="CustomTeam",
    role="Custom Specialist",
    description="Handles custom tasks",
    capabilities=[
        AgentCapability(
            name="custom_capability",
            description="Custom functionality",
            parameters={"param1": "type1"}
        )
    ],
    system_prompt="Custom system prompt for specialized behavior"
)
```

### Adding Teams Dynamically

```python
agency = Agency(master_agent=master)

# Add teams after initialization
agency.add_team(data_team)
agency.add_team(ml_team)
agency.add_team(reporting_team)
```

### State Management

```python
from autonomous_data_agency.core.state import StateManager

state_manager = StateManager()
initial_state = state_manager.create_initial_state(
    input_text="Task description",
    context={"key": "value"},
    max_iterations=15
)
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black autonomous_data_agency/
isort autonomous_data_agency/
```

### Type Checking

```bash
mypy autonomous_data_agency/
```

## Architecture Decisions

### Why LangGraph?

LangGraph provides:
- State management for complex workflows
- Conditional routing between agents
- Built-in support for cycles and loops
- Easy visualization of agent workflows

### Why Hierarchical?

The hierarchical structure:
- Mirrors real organizational structures
- Enables specialization and expertise
- Scales to complex multi-step tasks
- Provides clear responsibility boundaries

## Use Cases

### Data Science Workflows

- Data collection → Analysis → Modeling → Reporting
- Each step handled by a specialized team

### Research & Analysis

- Research team gathers information
- Analysis team processes data
- Writing team creates reports

### Software Development

- Planning team breaks down requirements
- Development teams implement features
- QA team validates implementation

### Customer Service

- Routing team categorizes requests
- Specialized teams handle specific issues
- Escalation team handles complex cases

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Roadmap

- [ ] Enhanced LLM provider support (Anthropic, etc.)
- [ ] Tool integration for team agents
- [ ] Workflow visualization tools
- [ ] Persistent state storage
- [ ] Multi-turn conversations
- [ ] Agent memory and learning
- [ ] Performance monitoring dashboard
- [ ] Integration templates for common use cases

## Support

- Create an issue for bug reports or feature requests
- Discussions for questions and ideas

## Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - Framework for LLM applications
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent workflow orchestration
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation

---

Made with ❤️ for the AI agent community