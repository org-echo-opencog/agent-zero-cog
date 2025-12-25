# Agent Zero Makefile
# Convenience commands for development, testing, and deployment

.PHONY: help install install-dev test test-unit test-integration test-e2e test-all lint format type-check security clean build docker-build docker-run pre-commit coverage
# Makefile for Agent Zero with OpenCog integration
# Provides convenient commands for development, testing, and CI

.PHONY: help install install-dev install-test clean lint format test test-unit test-integration test-e2e test-opencog test-all coverage security build docker-build docker-test docker-lint docker-security docker-all run

# Default Python version
PYTHON ?= python3
PIP ?= pip3

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)Agent Zero Development Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	$(PIP) install -r requirements.txt

install-dev: install ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -e ".[dev]"
	$(PIP) install pytest pytest-asyncio pytest-cov pytest-mock pytest-timeout pytest-xdist pytest-html
	$(PIP) install ruff black isort mypy bandit safety pre-commit
	@echo "$(GREEN)Development environment ready!$(RESET)"

install-pre-commit: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(RESET)"
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)Pre-commit hooks installed!$(RESET)"

# =============================================================================
# Testing
# =============================================================================

test: test-unit ## Run tests (alias for test-unit)

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(RESET)"
	TESTING=true pytest tests/unit/ -v --tb=short --cov=python --cov=agent --cov=models --cov-report=term-missing

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	TESTING=true pytest tests/integration/ -v --tb=short -m integration

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(RESET)"
	TESTING=true pytest tests/e2e/ -v --tb=short -m e2e --timeout=600

test-all: ## Run all tests
	@echo "$(BLUE)Running all tests...$(RESET)"
	TESTING=true pytest tests/ -v --tb=short --cov=python --cov=agent --cov=models --cov-report=term-missing --cov-report=html

test-fast: ## Run tests in parallel (fast mode)
	@echo "$(BLUE)Running tests in parallel...$(RESET)"
	TESTING=true pytest tests/unit/ -v --tb=short -n auto

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	ptw -- tests/unit/ -v --tb=short

coverage: ## Generate coverage report
	@echo "$(BLUE)Generating coverage report...$(RESET)"
	TESTING=true pytest tests/ --cov=python --cov=agent --cov=models --cov-report=html --cov-report=xml
	@echo "$(GREEN)Coverage report generated in coverage_html/$(RESET)"

coverage-open: coverage ## Generate and open coverage report
	@echo "$(BLUE)Opening coverage report...$(RESET)"
	open coverage_html/index.html 2>/dev/null || xdg-open coverage_html/index.html 2>/dev/null || echo "Open coverage_html/index.html in your browser"

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run linters (ruff)
	@echo "$(BLUE)Running linters...$(RESET)"
	ruff check python/ --fix

lint-check: ## Check linting without fixes
	@echo "$(BLUE)Checking linting...$(RESET)"
	ruff check python/

format: ## Format code (black + isort)
	@echo "$(BLUE)Formatting code...$(RESET)"
	black python/ tests/
	isort python/ tests/

format-check: ## Check formatting without changes
	@echo "$(BLUE)Checking code format...$(RESET)"
	black --check python/ tests/
	isort --check-only python/ tests/

type-check: ## Run type checking (mypy)
	@echo "$(BLUE)Running type checking...$(RESET)"
	mypy python/ --ignore-missing-imports

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	bandit -r python/ -ll
	safety check -r requirements.txt || true

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	pre-commit run --all-files

quality: lint format type-check security ## Run all quality checks

# =============================================================================
# Build & Package
# =============================================================================

build: clean ## Build Python package
	@echo "$(BLUE)Building package...$(RESET)"
	$(PYTHON) -m build
	@echo "$(GREEN)Package built in dist/$(RESET)"

build-check: build ## Build and verify package
	@echo "$(BLUE)Verifying package...$(RESET)"
	twine check dist/*

# =============================================================================
# Docker
# =============================================================================

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -f DockerfileLocal -t agent-zero:local .
	@echo "$(GREEN)Docker image built: agent-zero:local$(RESET)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(RESET)"
	docker run -it --rm -p 9000:9000 -p 55022:22 agent-zero:local

docker-shell: ## Open shell in Docker container
	@echo "$(BLUE)Opening shell in Docker container...$(RESET)"
	docker run -it --rm agent-zero:local /bin/bash

docker-clean: ## Remove Docker images and containers
	@echo "$(BLUE)Cleaning Docker...$(RESET)"
	docker rm -f $$(docker ps -aq --filter "ancestor=agent-zero:local") 2>/dev/null || true
	docker rmi agent-zero:local 2>/dev/null || true

# =============================================================================
# Development
# =============================================================================

run: ## Run the application
	@echo "$(BLUE)Starting Agent Zero...$(RESET)"
	$(PYTHON) run_ui.py

run-dev: ## Run in development mode
	@echo "$(BLUE)Starting Agent Zero in development mode...$(RESET)"
	FLASK_ENV=development $(PYTHON) run_ui.py

# =============================================================================
# Cleanup
# =============================================================================

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf coverage_html/
	rm -rf htmlcov/
	rm -f coverage.xml
	rm -f .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "$(GREEN)Cleaned!$(RESET)"

clean-all: clean docker-clean ## Clean everything including Docker

# =============================================================================
# Documentation
# =============================================================================

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(RESET)"
	@echo "$(YELLOW)Documentation building not configured yet$(RESET)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(RESET)"
	@echo "$(YELLOW)Documentation serving not configured yet$(RESET)"

# =============================================================================
# Utilities
# =============================================================================

check-deps: ## Check for outdated dependencies
	@echo "$(BLUE)Checking for outdated dependencies...$(RESET)"
	$(PIP) list --outdated

update-deps: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	$(PIP) install --upgrade -r requirements.txt

show-version: ## Show current version
	@grep -E '^version = ' pyproject.toml | head -1 | cut -d'"' -f2

.DEFAULT_GOAL := help
NC := \033[0m # No Color

# ============================================================================
# Help
# ============================================================================
help:
	@echo "$(BLUE)Agent Zero - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Installation:$(NC)"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make install-test     Install testing dependencies"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests"
	@echo "  make test-e2e         Run E2E tests"
	@echo "  make test-opencog     Run OpenCog tests"
	@echo "  make coverage         Run tests with coverage report"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  make lint             Run all linters"
	@echo "  make format           Format code with black and isort"
	@echo "  make security         Run security scans"
	@echo ""
	@echo "$(GREEN)Building:$(NC)"
	@echo "  make build            Build Python package"
	@echo "  make docker-build     Build Docker images"
	@echo ""
	@echo "$(GREEN)Docker CI:$(NC)"
	@echo "  make docker-test      Run tests in Docker"
	@echo "  make docker-lint      Run linting in Docker"
	@echo "  make docker-security  Run security scan in Docker"
	@echo "  make docker-all       Run all CI checks in Docker"
	@echo ""
	@echo "$(GREEN)Running:$(NC)"
	@echo "  make run              Run the application"
	@echo "  make clean            Clean build artifacts"

# ============================================================================
# Installation
# ============================================================================
install:
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: install
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install ruff black isort mypy pre-commit
	$(PIP) install -r requirements-test.txt

install-test:
	@echo "$(BLUE)Installing test dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-test.txt

# ============================================================================
# Cleaning
# ============================================================================
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# ============================================================================
# Linting and Formatting
# ============================================================================
lint:
	@echo "$(BLUE)Running Ruff linter...$(NC)"
	ruff check . --output-format=text || true
	@echo ""
	@echo "$(BLUE)Checking Black formatting...$(NC)"
	black --check --diff . || true
	@echo ""
	@echo "$(BLUE)Checking isort import sorting...$(NC)"
	isort --check-only --diff . || true

format:
	@echo "$(BLUE)Formatting code with Black...$(NC)"
	black .
	@echo ""
	@echo "$(BLUE)Sorting imports with isort...$(NC)"
	isort .
	@echo ""
	@echo "$(BLUE)Auto-fixing with Ruff...$(NC)"
	ruff check . --fix || true

# ============================================================================
# Testing
# ============================================================================
test: test-unit

test-unit:
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTHON) -m pytest tests/ \
		-v \
		--tb=short \
		-m "unit or not integration and not e2e and not slow" \
		--ignore=tests/test_e2e.py \
		--timeout=60 \
		|| true

test-integration:
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTHON) -m pytest tests/test_tools_integration.py \
		-v \
		--tb=short \
		--timeout=120 \
		|| true

test-e2e:
	@echo "$(BLUE)Running E2E tests...$(NC)"
	$(PYTHON) -m pytest tests/test_e2e.py \
		-v \
		--tb=short \
		--timeout=300 \
		|| true

test-opencog:
	@echo "$(BLUE)Running OpenCog tests...$(NC)"
	$(PYTHON) -m pytest tests/test_opencog_integration.py tests/test_opencog_settings.py \
		-v \
		--tb=short \
		|| true

test-all:
	@echo "$(BLUE)Running all tests...$(NC)"
	$(PYTHON) -m pytest tests/ \
		-v \
		--tb=short \
		--timeout=300 \
		|| true

coverage:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTHON) -m pytest tests/ \
		-v \
		--tb=short \
		--timeout=300 \
		--cov=python \
		--cov=agent \
		--cov=models \
		--cov-report=html \
		--cov-report=xml \
		--cov-report=term-missing \
		|| true
	@echo ""
	@echo "$(GREEN)Coverage report generated in htmlcov/$(NC)"

# ============================================================================
# Security
# ============================================================================
security:
	@echo "$(BLUE)Running Bandit security scan...$(NC)"
	bandit -r python/ agent.py models.py initialize.py -f txt || true
	@echo ""
	@echo "$(BLUE)Checking dependencies with Safety...$(NC)"
	safety check --full-report || true

# ============================================================================
# Building
# ============================================================================
build: clean
	@echo "$(BLUE)Building Python package...$(NC)"
	$(PYTHON) -m build
	@echo ""
	@echo "$(BLUE)Checking package with Twine...$(NC)"
	twine check dist/* || true

# ============================================================================
# Docker Commands
# ============================================================================
docker-build:
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker build -f DockerfileLocal -t agent-zero-cog:local .
	docker build -f Dockerfile.ci --target test -t agent-zero-cog:test .
	docker build -f Dockerfile.ci --target production -t agent-zero-cog:production .

docker-test:
	@echo "$(BLUE)Running tests in Docker...$(NC)"
	docker-compose -f docker-compose.ci.yml run --rm test-all

docker-test-unit:
	@echo "$(BLUE)Running unit tests in Docker...$(NC)"
	docker-compose -f docker-compose.ci.yml run --rm test-unit

docker-test-integration:
	@echo "$(BLUE)Running integration tests in Docker...$(NC)"
	docker-compose -f docker-compose.ci.yml run --rm test-integration

docker-test-e2e:
	@echo "$(BLUE)Running E2E tests in Docker...$(NC)"
	docker-compose -f docker-compose.ci.yml run --rm test-e2e

docker-lint:
	@echo "$(BLUE)Running linting in Docker...$(NC)"
	docker-compose -f docker-compose.ci.yml run --rm lint

docker-security:
	@echo "$(BLUE)Running security scan in Docker...$(NC)"
	docker-compose -f docker-compose.ci.yml run --rm security

docker-build-package:
	@echo "$(BLUE)Building package in Docker...$(NC)"
	docker-compose -f docker-compose.ci.yml run --rm build

docker-all: docker-lint docker-security docker-test
	@echo "$(GREEN)All Docker CI checks completed$(NC)"

docker-clean:
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	docker-compose -f docker-compose.ci.yml down --volumes --remove-orphans
	docker rmi agent-zero-cog:local agent-zero-cog:test agent-zero-cog:production 2>/dev/null || true

# ============================================================================
# Running
# ============================================================================
run:
	@echo "$(BLUE)Starting Agent Zero...$(NC)"
	$(PYTHON) run_ui.py

# ============================================================================
# CI Targets
# ============================================================================
ci-lint: lint

ci-test: test-all

ci-security: security

ci-build: build

ci-all: ci-lint ci-test ci-security ci-build
	@echo "$(GREEN)All CI checks completed$(NC)"
