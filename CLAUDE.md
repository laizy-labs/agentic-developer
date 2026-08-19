# Claude CLI Instructions for Agentic Developer

This repository provides **Agentic Developer**, a CLI-based developer assistant integrating JIRA (via MCP), GitHub/GitLab CLIs, and custom developer skills (`config/skills.yaml`).

## MCP JIRA Server Configuration

To register the JIRA MCP server with Claude CLI, run:
```bash
claude mcp add jira npx -y @modelcontextprotocol/server-jira \
  -e JIRA_HOST="your-jira-domain.atlassian.net" \
  -e JIRA_EMAIL="your-email@example.com" \
  -e JIRA_API_TOKEN="your-jira-api-token"
```

## Available CLI Commands for Claude

When acting on developer tasks in this repository, use the following `agentic-dev` CLI commands:

- **List Available Skills**:
  ```bash
  agentic-dev skills list
  ```
- **Fetch JIRA Issue Context**:
  ```bash
  agentic-dev jira view <jira-key>
  ```
- **Start Feature Workflow** (Fetches ticket, transitions status to In Progress, creates branch):
  ```bash
  agentic-dev run start-feature <jira-key>
  ```
- **Create Pull Request / Merge Request**:
  ```bash
  agentic-dev pr create <jira-key>
  ```
- **Run Skill in Simulation Mode**:
  ```bash
  agentic-dev run <skill-name> <jira-key> --dry-run
  ```

## Workflows Defined in `config/skills.yaml`

- `start-feature`: Fetches ticket, transitions status, creates git branch.
- `create-pr`: Pushes active branch and creates GitHub PR / GitLab MR pre-populated with ticket context.
- `finish-issue`: Pushes branch, creates PR, and moves JIRA ticket status to `In Review`.
- `force-cleanup`: Safely deletes local/remote branches with guardrail confirmation.
