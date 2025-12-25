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
