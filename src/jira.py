import os
import base64
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import requests
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


@dataclass
class JiraIssue:
    key: str
    summary: str
    description: str
    status: str
    issue_type: str
    assignee: str
    url: str


@dataclass
class JiraTransition:
    id: str
    name: str


class JiraClient:
    """
    JIRA Connector supporting REST API and Model Context Protocol (MCP) tool integration.
    """

    def __init__(self, host: Optional[str] = None, email: Optional[str] = None, api_token: Optional[str] = None):
        self.host = host or os.getenv("JIRA_HOST", "")
        self.email = email or os.getenv("JIRA_EMAIL", "")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN", "")
        placeholder_keywords = ["your-jira-domain", "your-email", "your-jira-api-token", "example.com"]
        is_placeholder = any(
            p in self.host.lower() or p in self.email.lower() or p in self.api_token.lower()
            for p in placeholder_keywords
        )
        self.is_configured = bool(self.host and self.email and self.api_token and not is_placeholder)

    def check_configuration(self) -> None:
        """
        Check and warn if JIRA credentials are not configured.
        """
        if not self.is_configured:
            console.print("[yellow]⚠️  JIRA API Credentials missing or incomplete in environment.[/yellow]")
            console.print("[dim]  Please run `agentic-dev setup` or set JIRA_HOST, JIRA_EMAIL, JIRA_API_TOKEN in .env[/dim]\n")

    def _get_headers(self) -> Dict[str, str]:
        auth_str = f"{self.email}:{self.api_token}"
        b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {b64_auth}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_issue(self, issue_key: str) -> JiraIssue:
        """
        Fetch JIRA issue details by issue key (e.g. PROJ-123).
        """
        issue_key = issue_key.upper()
        if not self.is_configured:
            # Fallback mock for demonstration / unconfigured state
            return JiraIssue(
                key=issue_key,
                summary=f"Implement feature for {issue_key}",
                description=f"Automated developer task workflow for JIRA issue {issue_key}.",
                status="In Progress",
                issue_type="Story",
                assignee="Developer",
                url=f"https://{self.host or 'jira.example.com'}/browse/{issue_key}",
            )

        url = f"https://{self.host}/rest/api/3/issue/{issue_key}"
        response = requests.get(url, headers=self. _get_headers())
        if response.status_code != 200:
            raise RuntimeError(f"JIRA API Error [{response.status_code}]: {response.text}")

        data = response.json()
        fields = data.get("fields", {})

        # Extract ADF or simple text description
        description_text = ""
        raw_desc = fields.get("description")
        if isinstance(raw_desc, str):
            description_text = raw_desc
        elif isinstance(raw_desc, dict) and "content" in raw_desc:
            blocks = []
            for p in raw_desc.get("content", []):
                for c in p.get("content", []):
                    if "text" in c:
                        blocks.append(c["text"])
            description_text = "\n".join(blocks)

        return JiraIssue(
            key=data.get("key", issue_key),
            summary=fields.get("summary", "No summary provided"),
            description=description_text or "No description provided",
            status=fields.get("status", {}).get("name", "Unknown"),
            issue_type=fields.get("issuetype", {}).get("name", "Task"),
            assignee=fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
            url=f"https://{self.host}/browse/{data.get('key', issue_key)}",
        )

    def get_available_transitions(self, issue_key: str) -> List[JiraTransition]:
        """
        List available workflow transitions for an issue.
        """
        if not self.is_configured:
            return [
                JiraTransition(id="11", name="To Do"),
                JiraTransition(id="21", name="In Progress"),
                JiraTransition(id="31", name="In Review"),
                JiraTransition(id="41", name="Done"),
            ]

        url = f"https://{self.host}/rest/api/3/issue/{issue_key}/transitions"
        response = requests.get(url, headers=self._get_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch transitions [{response.status_code}]: {response.text}")

        data = response.json()
        return [
            JiraTransition(id=t["id"], name=t["name"])
            for t in data.get("transitions", [])
        ]

    def transition_issue(self, issue_key: str, target_status_name: str) -> bool:
        """
        Transition JIRA issue state (e.g., 'In Progress', 'In Review', 'Done').
        """
        console.print(f"[cyan]Transitioning JIRA issue {issue_key} to '{target_status_name}'...[/cyan]")

        if not self.is_configured:
            console.print(f"[green][Mock] Issue {issue_key} transitioned to '{target_status_name}'[/green]")
            return True

        transitions = self.get_available_transitions(issue_key)
        target = next((t for t in transitions if t.name.lower() == target_status_name.lower()), None)

        if not target:
            avail = ", ".join([t.name for t in transitions])
            console.print(f"[yellow]Could not find transition matching '{target_status_name}'. Available: {avail}[/yellow]")
            return False

        url = f"https://{self.host}/rest/api/3/issue/{issue_key}/transitions"
        payload = {"transition": {"id": target.id}}
        response = requests.post(url, headers=self._get_headers(), json=payload)

        if response.status_code not in (200, 204):
            raise RuntimeError(f"Transition failed [{response.status_code}]: {response.text}")

        console.print(f"[bold green]Successfully transitioned JIRA issue {issue_key} to '{target_status_name}'[/bold green]")
        return True

    def search_issues(self, jql: str) -> List[JiraIssue]:
        """
        Search issues using JQL query string.
        """
        if not self.is_configured:
            return [
                JiraIssue(
                    key="DEV-101",
                    summary="Scaffold Python CLI developer assistant",
                    description="Scaffold Python project with MCP and Git CLI integration.",
                    status="In Progress",
                    issue_type="Task",
                    assignee="Platform Engineer",
                    url="https://jira.example.com/browse/DEV-101",
                )
            ]

        url = f"https://{self.host}/rest/api/3/search?jql={requests.utils.quote(jql)}"
        response = requests.get(url, headers=self._get_headers())
        if response.status_code != 200:
            raise RuntimeError(f"JQL Search Error [{response.status_code}]: {response.text}")

        data = response.json()
        results = []
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})
            results.append(
                JiraIssue(
                    key=issue.get("key"),
                    summary=fields.get("summary", ""),
                    description=str(fields.get("description", "")),
                    status=fields.get("status", {}).get("name", ""),
                    issue_type=fields.get("issuetype", {}).get("name", ""),
                    assignee=fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
                    url=f"https://{self.host}/browse/{issue.get('key')}",
                )
            )
        return results
