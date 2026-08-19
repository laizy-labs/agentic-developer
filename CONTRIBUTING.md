# Contributing to Agentic Developer 🤝

Thank you for your interest in contributing to **Agentic Developer**! We welcome bug reports, feature requests, workflow skill ideas, and pull requests from the open-source community.

---

## 🚀 Getting Started with Local Development

### 1. Fork and Clone the Repository
```bash
git clone https://github.com/your-username/agentic-developer.git
cd agentic-developer
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package in editable mode with development tools
pip install -e .[dev]
```

### 3. Run Onboarding Setup Script
```bash
make setup
```

---

## 🧪 Testing and Linting

Before submitting a Pull Request, ensure all tests pass and your code complies with formatting guidelines:

### Run Code Syntax Check
```bash
make lint
# OR
python3 -m py_compile src/*.py
```

### Code Formatting (Black & Flake8)
```bash
black src/
flake8 src/
```

### Run Dry-Run Skill Tests
```bash
agentic-dev run start-feature TEST-999 --dry-run
```

---

## 🛠️ Adding New Actions & Workflow Skills

### Adding a New Skill to `config/skills.yaml`
Skills define workflow sequences. To add a new skill, append your action steps to `config/skills.yaml`:

```yaml
  my-custom-skill:
    name: "My Custom Skill Workflow"
    description: "Brief summary of what this skill accomplishes."
    steps:
      - action: "jira.fetch"
        params:
          issue_key: "{jira_key}"
      - action: "git.checkout_branch"
        params:
          branch_name: "{branch_name}"
```

### Adding a New Action Dispatcher in `src/skills.py`
If your skill requires a brand new action type (e.g. `slack.notify` or `docker.build`), implement the action handler inside `_run_step()` in [src/skills.py](src/skills.py):

```python
elif action == "my_module.my_action":
    param_val = self.interpolate(params.get("my_param", ""), context)
    # Action implementation logic...
```

---

## 📦 Submitting a Pull Request

1. **Branch Naming**: Use feature branches with clear names (e.g., `feature/add-slack-notifications` or `fix/jira-parser-adf`).
2. **Commit Messages**: Format commit messages clearly: `[DEV-101] feat: add slack notifications step`.
3. **PR Descriptions**: Include a brief summary of changes, motivation, and any testing performed.
4. **Safety Check**: Ensure safety guardrails (`confirm_destructive_action`) are preserved for destructive CLI operations.

---

## 📄 License

By contributing to Agentic Developer, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
