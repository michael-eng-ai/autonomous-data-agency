import typer
import sys
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agency_orchestrator import get_agency_orchestrator
from core.teams_factory import get_teams_factory, list_teams
from config import describe_llm_diversity

load_dotenv()

app = typer.Typer(
    name="autonomous-data-agency",
    help="Autonomous Data Agency - AI Agent Framework",
    add_completion=False,
)
console = Console()

@app.command()
def start_project(
    name: str = typer.Option(..., "--name", "-n", help="Name of the project"),
    request: str = typer.Option(..., "--request", "-r", help="Initial client request"),
):
    """Start a new project with a specific request."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error: OPENAI_API_KEY not found in environment.[/bold red]")
        raise typer.Exit(code=1)

    console.print(Panel(f"[bold blue]Starting Project:[/bold blue] {name}"))
    orchestrator = get_agency_orchestrator()
    project = orchestrator.start_project(project_name=name, client_request=request)
    
    console.print("[bold green]Project initialized successfully![/bold green]")
    console.print(orchestrator.get_project_summary())
    
    # Run PO analysis
    console.print("\n[bold yellow]Running Product Owner Analysis...[/bold yellow]")
    output = orchestrator.execute_team("product_owner", request)
    console.print(Panel(output.final_output, title="Product Owner Output"))

@app.command()
def demo(
    type: str = typer.Option("simple", "--type", "-t", help="Type of demo: simple, workflow, multi-team")
):
    """Run demonstration scenarios."""
    import main as legacy_main
    if type == "simple":
        legacy_main.run_demo()
    elif type == "workflow":
        legacy_main.run_full_workflow()
    else:
        console.print(f"[red]Unknown demo type: {type}[/red]")

@app.command()
def interactive():
    """Start interactive mode."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Warning: OPENAI_API_KEY not found. Some features may not work.[/bold red]")
    
    import main as legacy_main
    legacy_main.interactive_mode()

@app.command()
def list():
    """List available teams."""
    list_teams()

@app.command()
def info():
    """Show information about LLM diversity and configuration."""
    describe_llm_diversity()

if __name__ == "__main__":
    app()
