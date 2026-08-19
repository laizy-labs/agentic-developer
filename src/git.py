import os
import subprocess
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Confirm

console = Console()


class GitExecutor:
    """
    CLI executor for Git, GitHub (gh), and GitLab (glab) CLI tools
    with explicit safety guardrails for destructive operations.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or self.detect_provider()

    def detect_provider(self) -> str:
        """
        Detect whether the current workspace connects to GitHub or GitLab.
        """
        env_provider = os.getenv("GIT_PROVIDER")
        if env_provider in ["github", "gitlab"]:
            return env_provider

        try:
            remote_url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            if "gitlab" in remote_url:
                return "gitlab"
        except Exception:
            pass
        return "github"

    def run_command(self, cmd: str, verbose: bool = False) -> str:
        """
        Execute raw shell command and return stdout.
        """
        if verbose:
            console.print(f"[dim]$ {cmd}[/dim]")
        
        result = subprocess.run(
            cmd,
            shell=True,
            text=True,
            capture_output=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Command failed [{result.returncode}]: {result.stderr.strip()}")
        
        return result.stdout.strip()

    def confirm_destructive_action(self, action_description: str, force: bool = False) -> bool:
        """
        Safety Guardrail: Require explicit user confirmation before destructive actions.
        """
        if force or os.getenv("BYPASS_SAFETY_PROMPTS", "").lower() == "true":
            console.print(f"[yellow][SAFETY GUARDRAIL] Bypassing confirmation for: {action_description}[/yellow]")
            return True

        console.print(f"\n[bold red]⚠️  SAFETY GUARDRAIL CONFIRMATION REQUIRED[/bold red]")
        console.print(f"[bold yellow]Target Action:[/bold yellow] {action_description}")

        confirmed = Confirm.ask("Are you sure you want to execute this destructive CLI command?", default=False)
        if not confirmed:
            console.print("[dim]Action cancelled by user.[/dim]")
        return confirmed

    def get_current_branch(self) -> str:
        """
        Get the current active Git branch.
        """
        try:
            return self.run_command("git rev-parse --abbrev-ref HEAD")
        except Exception as e:
            raise RuntimeError("Failed to get active git branch. Is this directory a valid git repo?") from e

    def checkout_branch(self, branch_name: str, create_if_missing: bool = True) -> None:
        """
        Checkout or create a local git branch.
        """
        current = self.get_current_branch()
        if current == branch_name:
            console.print(f"[blue]Already on branch '{branch_name}'[/blue]")
            return

        try:
            self.run_command(f"git checkout {branch_name}")
            console.print(f"[green]Switched to branch '{branch_name}'[/green]")
        except Exception:
            if create_if_missing:
                self.run_command(f"git checkout -b {branch_name}")
                console.print(f"[green]Created and checked out new branch '{branch_name}'[/green]")
            else:
                raise RuntimeError(f"Branch '{branch_name}' does not exist.")

    def push(self, set_upstream: bool = True, is_force: bool = False, force: bool = False) -> None:
        """
        Push local branch to remote repository with optional force push safety check.
        """
        branch = self.get_current_branch()
        cmd = "git push"

        if set_upstream:
            cmd += f" -u origin {branch}"

        if is_force:
            confirmed = self.confirm_destructive_action(
                f"Force Push branch '{branch}' to remote origin", force=force
            )
            if not confirmed:
                console.print("[yellow]Force push aborted.[/yellow]")
                return
            cmd += " --force-with-lease"

        console.print(f"[cyan]Pushing branch '{branch}' to remote...[/cyan]")
        self.run_command(cmd, verbose=True)
        console.print(f"[bold green]Successfully pushed '{branch}'[/bold green]")

    def create_pull_request(self, title: str, body: str, target_branch: str = "main", draft: bool = False) -> str:
        """
        Create PR / MR using `gh` CLI or `glab` CLI based on provider.
        """
        escaped_title = title.replace('"', '\\"')
        escaped_body = body.replace('"', '\\"')

        if self.provider == "github":
            cmd = f'gh pr create --title "{escaped_title}" --body "{escaped_body}" --base "{target_branch}"'
            if draft:
                cmd += " --draft"
            console.print("[cyan]Creating GitHub Pull Request via 'gh' CLI...[/cyan]")
            output = self.run_command(cmd, verbose=True)
            console.print("[bold green]GitHub Pull Request created![/bold green]")
            return output
        else:
            cmd = f'glab mr create --title "{escaped_title}" --description "{escaped_body}" --target-branch "{target_branch}" --yes'
            if draft:
                cmd += " --draft"
            console.print("[cyan]Creating GitLab Merge Request via 'glab' CLI...[/cyan]")
            output = self.run_command(cmd, verbose=True)
            console.print("[bold green]GitLab Merge Request created![/bold green]")
            return output

    def close_pull_request(self, pr_number_or_id: str, force: bool = False) -> None:
        """
        Close a PR or MR with safety guardrail prompt.
        """
        confirmed = self.confirm_destructive_action(
            f"Close {self.provider.upper()} PR/MR #{pr_number_or_id}", force=force
        )
        if not confirmed:
            return

        if self.provider == "github":
            self.run_command(f"gh pr close {pr_number_or_id}", verbose=True)
            console.print(f"[green]Closed GitHub PR #{pr_number_or_id}[/green]")
        else:
            self.run_command(f"glab mr close {pr_number_or_id}", verbose=True)
            console.print(f"[green]Closed GitLab MR #{pr_number_or_id}[/green]")

    def delete_branch(self, branch_name: str, remote: bool = False, force: bool = False) -> None:
        """
        Delete branch locally and remotely with safety check.
        """
        confirmed = self.confirm_destructive_action(
            f"Delete local branch '{branch_name}'{' and remote branch' if remote else ''}", force=force
        )
        if not confirmed:
            return

        self.run_command(f"git branch -D {branch_name}", verbose=True)
        console.print(f"[green]Deleted local branch '{branch_name}'[/green]")

        if remote:
            self.run_command(f"git push origin --delete {branch_name}", verbose=True)
            console.print(f"[green]Deleted remote branch '{branch_name}'[/green]")
