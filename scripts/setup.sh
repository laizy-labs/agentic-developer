#!/usr/bin/env bash
set -e

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}🚀 Agentic Developer Setup & Onboarding Script (Python)${RESET}\n"

# 1. Dependency Verification Helper
check_cmd() {
    local cmd=$1
    local name=$2
    local required=$3
    if command -v "$cmd" &> /dev/null; then
        echo -e "[${GREEN}✓${RESET}] $name ($cmd) is installed: $(command -v "$cmd")"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "[${RED}✗${RESET}] $name ($cmd) is REQUIRED but NOT installed."
            return 1
        else
            echo -e "[${YELLOW}!${RESET}] $name ($cmd) is optional and not found."
            return 0
        fi
    fi
}

echo -e "${BOLD}Checking System Dependencies...${RESET}"
MISSING_REQ=0

check_cmd "python3" "Python 3 (>=3.10)" "true" || MISSING_REQ=1
check_cmd "pip3" "Pip Package Manager" "true" || MISSING_REQ=1
check_cmd "git" "Git Version Control" "true" || MISSING_REQ=1
check_cmd "gh" "GitHub CLI (gh)" "false"
check_cmd "glab" "GitLab CLI (glab)" "false"

if [ "$MISSING_REQ" -ne 0 ]; then
    echo -e "\n${RED}Error: Missing required system dependencies. Please install Python 3.10+, pip3, and git.${RESET}"
    exit 1
fi

# 2. Check & Prompt CLI Authentication Status
echo -e "\n${BOLD}Checking CLI Authentication...${RESET}"
if command -v gh &> /dev/null; then
    if gh auth status &> /dev/null; then
        echo -e "[${GREEN}✓${RESET}] GitHub CLI (gh) is authenticated."
    else
        echo -e "[${YELLOW}!${RESET}] GitHub CLI (gh) is installed but NOT authenticated."
        if [ -t 0 ]; then
            echo -en "${YELLOW}Would you like to run 'gh auth login' now? (y/N):${RESET} "
            read -r do_gh_login
            if [[ "$do_gh_login" =~ ^[Yy]$ ]]; then
                gh auth login || true
            fi
        fi
    fi
fi

if command -v glab &> /dev/null; then
    if glab auth status &> /dev/null; then
        echo -e "[${GREEN}✓${RESET}] GitLab CLI (glab) is authenticated."
    else
        echo -e "[${YELLOW}!${RESET}] GitLab CLI (glab) is installed but NOT authenticated."
        if [ -t 0 ]; then
            echo -en "${YELLOW}Would you like to run 'glab auth login' now? (y/N):${RESET} "
            read -r do_glab_login
            if [[ "$do_glab_login" =~ ^[Yy]$ ]]; then
                glab auth login || true
            fi
        fi
    fi
fi

# 3. Environment Variable Onboarding
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

echo -e "\n${BOLD}Configuring Environment Variables...${RESET}"

if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo -e "[${GREEN}✓${RESET}] Created .env from .env.example"
    else
        touch "$ENV_FILE"
        echo -e "[${GREEN}✓${RESET}] Created new .env file"
    fi
fi

prompt_env_var() {
    local var_name=$1
    local prompt_msg=$2
    local current_val
    current_val=$(grep "^${var_name}=" "$ENV_FILE" | cut -d '=' -f2-)

    if [ -z "$current_val" ] || [ "$current_val" = "your-jira-domain.atlassian.net" ] || [ "$current_val" = "your-email@example.com" ] || [ "$current_val" = "your-jira-api-token" ]; then
        echo -en "${YELLOW}$prompt_msg:${RESET} "
        read -r input_val
        if [ -n "$input_val" ]; then
            if grep -q "^${var_name}=" "$ENV_FILE"; then
                sed -i '' "s|^${var_name}=.*|${var_name}=${input_val}|" "$ENV_FILE" 2>/dev/null || sed -i "s|^${var_name}=.*|${var_name}=${input_val}|" "$ENV_FILE"
            else
                echo "${var_name}=${input_val}" >> "$ENV_FILE"
            fi
            echo -e "[${GREEN}✓${RESET}] Saved $var_name"
        fi
    else
        echo -e "[${GREEN}✓${RESET}] $var_name is configured."
    fi
}

if [ -t 0 ]; then
    prompt_env_var "JIRA_HOST" "Enter JIRA Host Domain (e.g. company.atlassian.net)"
    prompt_env_var "JIRA_EMAIL" "Enter JIRA Account Email"
    prompt_env_var "JIRA_API_TOKEN" "Enter JIRA API Token"
    prompt_env_var "GIT_PROVIDER" "Enter default Git Provider (github / gitlab)"
fi

# 4. MCP Configuration Initialization
echo -e "\n${BOLD}Initializing Model Context Protocol (MCP) Configuration...${RESET}"
MCP_DIR=".mcp"
MCP_CONFIG="$MCP_DIR/mcp-config.json"
MCP_EXAMPLE="$MCP_DIR/mcp-config.json.example"

mkdir -p "$MCP_DIR"
if [ ! -f "$MCP_CONFIG" ] && [ -f "$MCP_EXAMPLE" ]; then
    cp "$MCP_EXAMPLE" "$MCP_CONFIG"
    echo -e "[${GREEN}✓${RESET}] Created active $MCP_CONFIG for @modelcontextprotocol/server-jira"
else
    echo -e "[${GREEN}✓${RESET}] MCP Configuration file ($MCP_CONFIG) is ready."
fi

echo -e "\n${GREEN}${BOLD}✨ Python Setup completed successfully!${RESET}"
echo -e "Install package locally with: ${BOLD}pip install -e .${RESET}\n"

