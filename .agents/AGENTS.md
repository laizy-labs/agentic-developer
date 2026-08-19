# Agentic Developer - Workspace Rules for AI Agents & IDEs

This workspace contains **Agentic Developer**, a Python-based CLI assistant integrating JIRA (via MCP), Git CLIs (`gh`/`glab`), and custom developer workflow skills (`config/skills.yaml`).

## Standard Commands for Agents & IDE Assistants

- **Verify Setup & Dependencies**: `agentic-dev setup` or `make setup`
- **List Workflows**: `agentic-dev skills list`
- **View JIRA Issue**: `agentic-dev jira view <jira-key>`
- **Start Feature Workflow**: `agentic-dev run start-feature <jira-key>`
- **Create Pull Request**: `agentic-dev pr create <jira-key>`
- **Dry-Run Workflow**: `agentic-dev run <skill-name> <jira-key> --dry-run`

## Execution Guidelines
1. When assigned a JIRA ticket key (e.g. `DEV-101`), run `agentic-dev run start-feature <jira-key>` to check out the branch and update ticket status.
2. After implementing code changes and running tests (`pytest`), run `agentic-dev pr create <jira-key>` to push and open a PR/MR.
