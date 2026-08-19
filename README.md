# Agentic Developer 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-blue.svg)](https://www.python.org/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-JIRA-orange.svg)](https://modelcontextprotocol.io)

> An open-source, CLI-based developer assistant built in **Python** that seamlessly connects to JIRA via the **Model Context Protocol (MCP)**, integrates with GitHub (`gh`) and GitLab (`glab`) CLIs, and executes customized developer workflows ("skills") tailored to personal work patterns.

---

## 🌟 Core Architecture & Features

1. **Setup & Onboarding Script (`scripts/setup.sh`)**: Verifies system dependencies (`python3`, `pip3`, `git`, `gh`, `glab`), prompts for `.env` credentials, and configures MCP settings.
2. **Skill Engine (`config/skills.yaml`)**: YAML configuration where users define custom developer patterns and workflows (e.g., branch naming conventions, commit formats, ticket state transitions).
3. **MCP Integration (`.mcp/mcp-config.json.example`)**: Pre-configured configuration template for `@modelcontextprotocol/server-jira`.
4. **CLI Orchestration (`src/`)**: Python CLI built with `click` and `rich` executing `gh` or `glab` commands based on JIRA ticket context.
5. **Safety Guardrails**: Explicit interactive prompts required before executing destructive CLI actions (e.g., force pushing, branch deletion, PR closing).
6. **Offline Mock Mode**: Instant offline testing capabilities without requiring a live JIRA account.

---

## 📁 Repository Structure

```text
agentic-developer/
├── .agents/
│   └── AGENTS.md                 # Antigravity IDE workspace agent rules
├── .mcp/
│   └── mcp-config.json.example   # MCP configuration template pre-configured for JIRA
├── config/
│   └── skills.yaml               # YAML engine defining custom skills & developer patterns
├── scripts/
│   └── setup.sh                  # Shell script to verify dependencies & prompt .env
├── src/
│   ├── __init__.py               # Package initializer
│   ├── main.py                   # CLI Entrypoint (Click CLI framework)
│   ├── jira.py                   # JIRA MCP connector & REST client (with Offline Mock mode)
│   ├── git.py                    # GitHub (gh) & GitLab (glab) CLI executor with safety guardrails
│   └── skills.py                 # Pattern parser & skill execution engine
├── CLAUDE.md                     # Claude CLI native instructions & mcp integration rules
├── .cursorrules                  # Cursor IDE configuration & MCP server setup rules
├── pyproject.toml                # Python package metadata & dependencies
├── requirements.txt              # Pip dependency specification
├── .env.example                  # Environment configuration template
├── .gitignore                    # Python git ignore rules
├── Makefile                      # Build & setup orchestration
└── README.md                     # Production-ready Python documentation
```

---

## 🛠️ Prerequisites

Make sure the following tools are installed on your system:

- **Python**: `>= 3.10`
- **Pip**: `>= 21.0`
- **Git**: `>= 2.30`
- **GitHub CLI (`gh`)** *(Optional for GitHub workflows)*: [gh installation guide](https://cli.github.com/)
- **GitLab CLI (`glab`)** *(Optional for GitLab workflows)*: [glab installation guide](https://gitlab.com/gitlab-org/cli)

---

## 🚀 Installation & Onboarding

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/agentic-developer.git
cd agentic-developer
```

### 2. Run Setup Script
Run the setup script or Makefile target to check dependencies and configure `.env`:

```bash
make setup
# OR
./scripts/setup.sh
```

### 3. Install Package Locally
Install Python dependencies and link the `agentic-dev` executable:

```bash
pip install -r requirements.txt
pip install -e .
```

---

## ⚙️ Environment Configuration (`.env`)

Copy `.env.example` to `.env` and set your credentials:

```env
JIRA_HOST=your-jira-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
GIT_PROVIDER=github
LOG_LEVEL=info
BYPASS_SAFETY_PROMPTS=false
```

---

## 🧩 Defining Skills (`config/skills.yaml`)

Define your developer workflow patterns in `config/skills.yaml`:

```yaml
version: "1.0"

conventions:
  branch_pattern: "{type}/{jira_key}-{slugified_summary}"
  commit_pattern: "[{jira_key}] {type}: {summary}"
  pr_title_pattern: "[{jira_key}] {summary}"

skills:
  start-feature:
    name: "Start Feature Workflow"
    description: "Fetch JIRA ticket details, transition status to 'In Progress', and create git branch."
    jira_transition: "In Progress"
    steps:
      - action: "jira.fetch"
        params:
          issue_key: "{jira_key}"
      - action: "jira.transition"
        params:
          issue_key: "{jira_key}"
          status: "In Progress"
      - action: "git.checkout_branch"
        params:
          branch_name: "{branch_name}"
          create_if_missing: true

  create-pr:
    name: "Create Pull Request / Merge Request"
    description: "Push current branch and create PR on GitHub (gh) or GitLab (glab) linked to JIRA issue."
    steps:
      - action: "git.push"
        params:
          set_upstream: true
      - action: "git.create_pr"
        params:
          title: "{pr_title}"
          body: "Closes [{jira_key}]({jira_url})\n\n### Summary\n{jira_description}"
```

---

## 💻 CLI Commands & Examples

### List Available Skills
```bash
agentic-dev skills list
```

### Execute a Skill Workflow
```bash
# Execute start-feature skill for JIRA ticket DEV-101
agentic-dev run start-feature DEV-101

# Test skill execution in Dry-Run simulation mode
agentic-dev run start-feature DEV-101 --dry-run
```

### View JIRA Issue Details
```bash
agentic-dev jira view DEV-101
```

### Create Smart Pull Request
```bash
agentic-dev pr create DEV-101 --draft
```

---

## 💡 Testing Without a JIRA Account (Offline Mock Mode)

Don't have an active JIRA instance? **Agentic Developer** features an automatic **Offline Mock Mode**:

1. **View Mock Issue**:
   ```bash
   agentic-dev jira view TEST-999
   ```
2. **Simulate Skill Execution**:
   ```bash
   agentic-dev run start-feature TEST-999 --dry-run
   ```

---

## 🤖 AI Assistant & IDE Integration

This repository includes out-of-the-box configuration rules for popular AI coding assistants:

- **Antigravity IDE**: Automatically reads [.agents/AGENTS.md](.agents/AGENTS.md) workspace rules.
- **Claude CLI**: Uses native instructions in [CLAUDE.md](CLAUDE.md) and supports `claude mcp add jira ...`.
- **Cursor IDE**: Pre-configured with [.cursorrules](.cursorrules) and standard MCP server setup.

---

## 🛡️ Safety Guardrails

Destructive CLI actions automatically trigger interactive safety confirmation prompts powered by `rich.prompt`:

- Force pushing remote branches (`git push --force`)
- Deleting local / remote git branches (`git branch -D`)
- Closing Pull Requests / Merge Requests (`gh pr close` / `glab mr close`)

Pass `-f` / `--force` to bypass safety prompts in automated CI/CD scripts.

---

## 🤝 Contributing

Contributions are welcome! Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for local environment setup, testing guidelines, and submission steps.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.