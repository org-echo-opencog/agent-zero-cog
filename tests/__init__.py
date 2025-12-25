"""
Agent Zero Test Suite

This package contains comprehensive tests for the Agent Zero framework:

- tests/unit/ - Unit tests for individual components
- tests/integration/ - Integration tests for component interactions
- tests/e2e/ - End-to-end tests for complete workflows

Test markers:
- @pytest.mark.unit - Unit tests
- @pytest.mark.integration - Integration tests
- @pytest.mark.e2e - End-to-end tests
- @pytest.mark.slow - Slow-running tests
- @pytest.mark.api - API endpoint tests
- @pytest.mark.tools - Tool tests
- @pytest.mark.helpers - Helper utility tests
- @pytest.mark.models - Model wrapper tests
- @pytest.mark.agent - Agent core tests
- @pytest.mark.opencog - OpenCog integration tests
- @pytest.mark.mcp - MCP protocol tests
- @pytest.mark.browser - Browser automation tests
- @pytest.mark.docker - Docker-related tests
- @pytest.mark.network - Network-dependent tests

Usage:
    # Run all tests
    pytest tests/

    # Run only unit tests
    pytest tests/unit/

    # Run tests by marker
    pytest -m "unit and not slow"

    # Run with coverage
    pytest --cov=python --cov-report=html
"""
