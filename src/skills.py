import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console

from src.jira import JiraClient, JiraIssue
from src.git import GitExecutor

console = Console()


class SkillEngine:
    """
    Parser and execution engine for developer workflow patterns defined in config/skills.yaml.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or Path.cwd() / "config" / "skills.yaml")
        self.jira_client = JiraClient()
        self.git_executor = GitExecutor()
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Read and parse YAML skill configuration file.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Skill configuration file not found at: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def get_skills(self) -> Dict[str, Any]:
        """
        Get all defined skills from configuration.
        """
        return self.config.get("skills", {})

    @staticmethod
    def slugify(text: str) -> str:
        """
        Helper: Convert summary to URL/branch-safe slug.
        """
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        return text.strip("-")

    def interpolate(self, template: str, context: Dict[str, str]) -> str:
        """
        Substitute variables in template strings (e.g. {jira_key}, {summary}).
        """
        result = template
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", str(value or ""))
        return result

    def build_context(self, issue_key: str, issue: JiraIssue, skill_type: str = "feature") -> Dict[str, str]:
        """
        Build template substitution context mapping.
        """
        slugified_summary = self.slugify(issue.summary)

        base_context = {
            "jira_key": issue.key,
            "summary": issue.summary,
            "slugified_summary": slugified_summary,
            "jira_description": issue.description,
            "jira_url": issue.url,
            "type": skill_type,
        }

        conventions = self.config.get("conventions", {
            "branch_pattern": "{type}/{jira_key}-{slugified_summary}",
            "commit_pattern": "[{jira_key}] {type}: {summary}",
            "pr_title_pattern": "[{jira_key}] {summary}",
        })

        branch_name = self.interpolate(conventions.get("branch_pattern", ""), base_context)
        pr_title = self.interpolate(conventions.get("pr_title_pattern", ""), base_context)
        commit_msg = self.interpolate(conventions.get("commit_pattern", ""), base_context)

        return {
            **base_context,
            "branch_name": branch_name,
            "pr_title": pr_title,
            "commit_msg": commit_msg,
        }

    def execute_skill(self, skill_key: str, jira_key: str, dry_run: bool = False, force: bool = False) -> None:
        """
        Execute a defined skill workflow by key name.
        """
        skills = self.get_skills()
        if skill_key not in skills:
            raise KeyError(f"Skill '{skill_key}' is not defined in {self.config_path}")

        skill = skills[skill_key]
        console.print(f"\n[bold cyan]⚡ Executing Skill: {skill.get('name', skill_key)} ({skill_key})[/bold cyan]")
        console.print(f"[dim]Description: {skill.get('description', '')}[/dim]")

        if dry_run:
            console.print("[bold yellow]\n[DRY RUN MODE ENABLED] - Commands will be simulated without execution.\n[/bold yellow]")

        if skill.get("safety_confirm_required"):
            confirmed = self.git_executor.confirm_destructive_action(
                f"Execute skill workflow '{skill_key}'", force=force
            )
            if not confirmed:
                console.print("[yellow]Skill execution cancelled by user.[/yellow]")
                return

        console.print(f"\n[blue]Fetching JIRA context for ticket: {jira_key}...[/blue]")
        issue = self.jira_client.get_issue(jira_key)
        context = self.build_context(jira_key, issue)

        console.print(f"[dim]Resolved Context:[/dim]")
        console.print(f"[dim]  Branch Name : {context['branch_name']}[/dim]")
        console.print(f"[dim]  PR Title    : {context['pr_title']}[/dim]")
        console.print(f"[dim]  JIRA Status : {issue.status}[/dim]\n")

        steps = skill.get("steps", [])
        for idx, step in enumerate(steps, 1):
            action = step.get("action", "")
            params = step.get("params", {})
            console.print(f"[bold]Step {idx}/{len(steps)}: {action}[/bold]")

            if dry_run:
                console.print(f"[dim]  Params: {params}[/dim]")
                continue

            self._run_step(action, params, context, force=force)

        console.print(f"\n[bold green]✨ Skill '{skill_key}' completed successfully![/bold green]")

    def _run_step(self, action: str, params: Dict[str, Any], context: Dict[str, str], force: bool = False) -> None:
        """
        Dispatch step action to JiraClient or GitExecutor.
        """
        if action == "jira.fetch":
            issue_key = self.interpolate(params.get("issue_key", "{jira_key}"), context)
            self.jira_client.get_issue(issue_key)

        elif action == "jira.transition":
            issue_key = self.interpolate(params.get("issue_key", "{jira_key}"), context)
            status = self.interpolate(params.get("status", "In Progress"), context)
            self.jira_client.transition_issue(issue_key, status)

        elif action == "git.checkout_branch":
            branch_name = self.interpolate(params.get("branch_name", "{branch_name}"), context)
            create_missing = params.get("create_if_missing", True)
            self.git_executor.checkout_branch(branch_name, create_if_missing)

        elif action == "git.push":
            set_upstream = params.get("set_upstream", True)
            is_force = params.get("force", False)
            self.git_executor.push(set_upstream=set_upstream, is_force=is_force, force=force)

        elif action == "git.create_pr":
            title = self.interpolate(params.get("title", "{pr_title}"), context)
            body = self.interpolate(params.get("body", "Closing {jira_key}"), context)
            draft = params.get("draft", False)
            self.git_executor.create_pull_request(title=title, body=body, draft=draft)

        elif action == "git.delete_branch":
            branch_name = self.interpolate(params.get("branch_name", "{branch_name}"), context)
            remote = params.get("remote", False)
            self.git_executor.delete_branch(branch_name=branch_name, remote=remote, force=force)

        else:
            console.print(f"[yellow]Unknown step action '{action}'. Skipping step.[/yellow]")
