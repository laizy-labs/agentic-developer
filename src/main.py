import os
import sys
import subprocess
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from src.skills import SkillEngine
from src.jira import JiraClient
from src.git import GitExecutor

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="agentic-dev")
def cli():
    """Agentic Developer: CLI Assistant connecting JIRA (MCP), GitHub/GitLab, and customized skills."""
    pass


@cli.command(name="setup")
def setup_command():
    """Run onboarding setup script to verify dependencies and configure environment."""
    console.print("[bold cyan]Running setup & onboarding verification script...[/bold cyan]\n")
    setup_script = Path.cwd() / "scripts" / "setup.sh"
    
    if not setup_script.exists():
        console.print(f"[red]Error: Setup script not found at {setup_script}[/red]")
        sys.exit(1)

    try:
        subprocess.run(["bash", str(setup_script)], check=True)
    except subprocess.CalledProcessError:
        console.print("\n[red]Setup script execution failed.[/red]")
        sys.exit(1)


@cli.group(name="skills")
def skills_group():
    """Manage and view developer workflow skills."""
    pass


@skills_group.command(name="list")
def list_skills():
    """List all available workflow skills defined in config/skills.yaml."""
    try:
        engine = SkillEngine()
        skills = engine.get_skills()

        table = Table(title="🚀 Defined Developer Skills", show_header=True, header_style="bold magenta")
        table.add_column("Skill Key", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")
        table.add_column("Target Status", style="yellow")

        for key, skill in skills.items():
            table.add_row(
                key,
                skill.get("name", key),
                skill.get("description", ""),
                skill.get("jira_transition", "N/A"),
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error loading skills: {e}[/red]")
        sys.exit(1)


@cli.command(name="run")
@click.argument("skill_key")
@click.argument("jira_key")
@click.option("-d", "--dry-run", is_flag=True, help="Simulate skill steps without executing commands.")
@click.option("-f", "--force", is_flag=True, help="Bypass safety confirmation guardrail prompts for destructive actions.")
def run_skill(skill_key: str, jira_key: str, dry_run: bool, force: bool):
    """Execute a customized developer workflow skill based on JIRA ticket context."""
    try:
        engine = SkillEngine()
        engine.execute_skill(skill_key, jira_key, dry_run=dry_run, force=force)
    except Exception as e:
        console.print(f"\n[bold red]Skill Execution Failed:[/bold red] {e}")
        sys.exit(1)


@cli.group(name="jira")
def jira_group():
    """JIRA context commands via MCP / REST API."""
    pass


@jira_group.command(name="view")
@click.argument("jira_key")
def view_jira(jira_key: str):
    """Fetch and display JIRA issue details."""
    try:
        jira = JiraClient()
        console.print(f"[cyan]Fetching details for JIRA issue {jira_key.upper()}...[/cyan]\n")
        issue = jira.get_issue(jira_key)

        console.print(f"[bold green][{issue.key}] {issue.summary}[/bold green]")
        console.print(f"[dim]URL      :[/dim] {issue.url}")
        console.print(f"[dim]Status   :[/dim] {issue.status}")
        console.print(f"[dim]Type     :[/dim] {issue.issue_type}")
        console.print(f"[dim]Assignee :[/dim] {issue.assignee}")
        console.print("\n[bold]Description:[/bold]")
        console.print(issue.description or "[dim](No description)[/dim]\n")
    except Exception as e:
        console.print(f"[red]Failed to fetch JIRA issue: {e}[/red]")
        sys.exit(1)


@cli.group(name="pr")
def pr_group():
    """Pull Request / Merge Request operations."""
    pass


@pr_group.command(name="create")
@click.argument("jira_key")
@click.option("-d", "--draft", is_flag=True, help="Create Pull Request as draft.")
def create_pr(jira_key: str, draft: bool):
    """Push active branch and create PR/MR linked to JIRA issue context."""
    try:
        jira = JiraClient()
        git = GitExecutor()
        issue = jira.get_issue(jira_key)

        console.print(f"[cyan]Pushing active branch and creating PR for {jira_key}...[/cyan]")
        git.push(set_upstream=True, is_force=False)

        pr_title = f"[{issue.key}] {issue.summary}"
        pr_body = f"Closes [{issue.key}]({issue.url})\n\n### Description\n{issue.description}"

        git.create_pull_request(title=pr_title, body=pr_body, draft=draft)
        console.print(f"[bold green]PR created successfully for JIRA Issue {jira_key}![/bold green]")
    except Exception as e:
        console.print(f"[red]Failed to create PR: {e}[/red]")
        sys.exit(1)


def main():
    cli()


if __name__ == "__main__":
    main()
