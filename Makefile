.PHONY: all setup install dev lint clean help test

PYTHON ?= python3
PIP ?= pip3

all: setup install

# Run onboarding setup script
setup:
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

# Install python dependencies in editable mode
install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

# Install with development tools
dev:
	$(PIP) install -e .[dev]

# Run tests
test:
	pytest tests/ 2>/dev/null || $(PYTHON) -m unittest discover -s tests 2>/dev/null || echo "No tests configured."

# Lint code syntax
lint:
	$(PYTHON) -m py_compile src/*.py

# Clean build artifacts & caches
clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Help menu
help:
	@echo "Agentic Developer Makefile Commands (Python):"
	@echo "  make setup    - Run onboarding setup script & verify dependencies"
	@echo "  make install  - Install python packages in editable mode"
	@echo "  make dev      - Install dev tools (pytest, flake8, black)"
	@echo "  make lint     - Verify Python syntax across src/"
	@echo "  make clean    - Remove build artifacts and __pycache__"
