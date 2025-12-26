"""
Pytest configuration and shared fixtures for Agent Zero tests.

This module provides comprehensive fixtures for testing the Agent Zero framework,
including mocks for LLM models, agent configurations, API endpoints, and more.
"""

import asyncio
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Environment Setup Fixtures
# =============================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables and paths."""
    os.environ["TESTING"] = "true"
    os.environ["LITELLM_LOG"] = "ERROR"
    os.environ["LOG_LEVEL"] = "ERROR"
    os.environ["ANONYMIZED_TELEMETRY"] = "false"
    os.environ["DISABLE_TELEMETRY"] = "true"

    # Set default API keys for testing (mock values)
    if "API_KEY_OPENAI" not in os.environ:
        os.environ["API_KEY_OPENAI"] = "sk-test-key-for-testing"
    if "API_KEY_ANTHROPIC" not in os.environ:
        os.environ["API_KEY_ANTHROPIC"] = "test-anthropic-key"

    yield

    # Cleanup
    os.environ.pop("TESTING", None)


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# =============================================================================
# Model Configuration Fixtures
# =============================================================================


@pytest.fixture
def mock_model_config():
    """Create a mock ModelConfig for testing."""
    from models import ModelConfig, ModelType

    return ModelConfig(
        type=ModelType.CHAT,
        provider="openai",
        name="gpt-4",
        api_base="",
        ctx_length=8192,
        limit_requests=100,
        limit_input=100000,
        limit_output=4096,
        vision=True,
        kwargs={"temperature": 0.7},
    )


@pytest.fixture
def mock_embedding_config():
    """Create a mock embedding ModelConfig for testing."""
    from models import ModelConfig, ModelType

    return ModelConfig(
        type=ModelType.EMBEDDING,
        provider="openai",
        name="text-embedding-ada-002",
        api_base="",
        ctx_length=8191,
        limit_requests=100,
        limit_input=100000,
        limit_output=0,
        vision=False,
        kwargs={},
    )


@pytest.fixture
def mock_agent_config(mock_model_config, mock_embedding_config):
    """Create a mock AgentConfig for testing."""
    from agent import AgentConfig

    return AgentConfig(
        chat_model=mock_model_config,
        utility_model=mock_model_config,
        embeddings_model=mock_embedding_config,
        browser_model=mock_model_config,
        mcp_servers="",
        profile="",
        memory_subdir="test_memory",
        knowledge_subdirs=["default", "test"],
    )


# =============================================================================
# Mock LLM Fixtures
# =============================================================================


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    return {
        "tool_name": "response",
        "tool_args": {
            "text": "This is a test response from the agent."
        },
        "choices": [
            {
                "delta": {
                    "content": "This is a test response.",
                    "reasoning_content": ""
                },
                "message": {
                    "content": "This is a test response."
                }
            }
        ]
    }


@pytest.fixture
def mock_llm_stream():
    """Create a mock streaming LLM response."""
    chunks = [
        '{"tool',
        '_name": "response",',
        ' "tool_args": {"text": "Test"}}',
    ]
    return chunks


@pytest.fixture
def mock_streaming_response():
    """Create a mock streaming LLM response with choices."""
    chunks = [
        {"choices": [{"delta": {"content": "Hello"}}]},
        {"choices": [{"delta": {"content": " "}}]},
        {"choices": [{"delta": {"content": "World"}}]},
        {"choices": [{"delta": {"content": "!"}}]},
    ]
    return chunks


@pytest.fixture
def mock_chat_model(mock_llm_response):
    """Create a mock chat model that returns predictable responses."""
    mock = MagicMock()
    mock.model_name = "test/gpt-4"
    mock.provider = "test"

    async def mock_unified_call(*args, **kwargs):
        response_callback = kwargs.get("response_callback")
        if response_callback:
            response = json.dumps(mock_llm_response)
            await response_callback(response, response)
        return json.dumps(mock_llm_response), ""

    mock.unified_call = AsyncMock(side_effect=mock_unified_call)
    return mock


@pytest.fixture
def mock_embedding_model():
    """Create a mock embedding model."""
    mock = MagicMock()
    mock.model_name = "test/embedding"

    def mock_embed_documents(texts):
        return [[0.1] * 384 for _ in texts]

    def mock_embed_query(text):
        return [0.1] * 384

    mock.embed_documents = MagicMock(side_effect=mock_embed_documents)
    mock.embed_query = MagicMock(side_effect=mock_embed_query)
    return mock


@pytest.fixture
def mock_tool_response_json():
    """Create a mock tool response from LLM as JSON."""
    tool_call = {
        "tool_name": "response",
        "tool_args": {
            "message": "Task completed successfully."
        }
    }
    return json.dumps(tool_call)


# =============================================================================
# Agent Context Fixtures
# =============================================================================


@pytest.fixture
def mock_agent_context(mock_agent_config):
    """Create a mock AgentContext for testing."""
    from agent import AgentContext, AgentContextType

    # Clean up any existing contexts first
    AgentContext._contexts.clear()

    context = AgentContext(
        config=mock_agent_config,
        id="test-context-001",
        name="Test Context",
        type=AgentContextType.USER,
    )

    yield context

    # Cleanup
    AgentContext._contexts.clear()


@pytest.fixture
def mock_agent(mock_agent_context, mock_chat_model):
    """Create a mock Agent for testing."""
    from agent import Agent

    agent = mock_agent_context.agent0

    # Mock the model getters
    with patch.object(agent, "get_chat_model", return_value=mock_chat_model):
        with patch.object(agent, "get_utility_model", return_value=mock_chat_model):
            yield agent


@pytest.fixture
def mock_user_message():
    """Create a mock UserMessage for testing."""
    from agent import UserMessage

    return UserMessage(
        message="Hello, this is a test message.",
        attachments=[],
        system_message=[],
    )


# =============================================================================
# API/Flask Fixtures
# =============================================================================


@pytest.fixture
def flask_app():
    """Create a Flask test application."""
    from flask import Flask

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["WTF_CSRF_ENABLED"] = False

    return app


@pytest.fixture
def flask_client(flask_app):
    """Create a Flask test client."""
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def mock_request_context(flask_app):
    """Create a mock request context."""
    with flask_app.test_request_context():
        yield


# =============================================================================
# File System Fixtures
# =============================================================================


@pytest.fixture
def mock_prompt_files(temp_directory):
    """Create mock prompt files for testing."""
    prompts_dir = temp_directory / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    # Create some test prompt files
    files = {
        "agent.system.main.md": "You are a helpful AI assistant.",
        "fw.user_message.md": "User message: {{message}}",
        "fw.ai_response.md": "{{message}}",
        "fw.warning.md": "Warning: {{message}}",
        "fw.msg_repeat.md": "Please don't repeat the same response.",
        "fw.msg_misformat.md": "Please format your response correctly.",
    }

    for filename, content in files.items():
        (prompts_dir / filename).write_text(content)

    return prompts_dir


@pytest.fixture
def mock_agent_profiles(temp_directory):
    """Create mock agent profile directories."""
    agents_dir = temp_directory / "agents"

    profiles = ["default", "developer", "researcher"]
    for profile in profiles:
        profile_dir = agents_dir / profile
        profile_dir.mkdir(parents=True, exist_ok=True)

        # Create context file
        (profile_dir / "_context.md").write_text(f"Context for {profile} agent.")

        # Create prompts directory
        prompts_dir = profile_dir / "prompts"
        prompts_dir.mkdir(exist_ok=True)
        (prompts_dir / "agent.system.main.md").write_text(
            f"You are a {profile} assistant."
        )

    return agents_dir


@pytest.fixture
def sample_prompt_file(temp_directory):
    """Create a sample prompt file for testing."""
    prompt_file = temp_directory / "test_prompt.md"
    prompt_file.write_text("# Test Prompt\n\nThis is a {{variable}} test prompt.")
    return prompt_file


@pytest.fixture
def sample_knowledge_file(temp_directory):
    """Create a sample knowledge file for testing."""
    knowledge_file = temp_directory / "test_knowledge.md"
    knowledge_file.write_text("# Test Knowledge\n\nThis is test knowledge content for embedding.")
    return knowledge_file


# =============================================================================
# Tool Fixtures
# =============================================================================


@pytest.fixture
def mock_tool_response():
    """Create a mock tool response."""
    from python.helpers.tool import Response

    return Response(
        message="Tool executed successfully",
        break_loop=False,
    )


@pytest.fixture
def mock_tool(mock_agent, mock_tool_response):
    """Create a mock tool for testing."""
    from python.helpers.tool import Tool

    class MockTool(Tool):
        async def execute(self, **kwargs):
            return mock_tool_response

    return MockTool(
        agent=mock_agent,
        name="mock_tool",
        method=None,
        args={},
        message="",
        loop_data=None,
    )


@pytest.fixture
def mock_tool_base():
    """Create a mock base tool class for testing."""
    from python.helpers.tool import Tool, Response

    class MockTool(Tool):
        async def execute(self, **kwargs):
            return Response(message="Mock tool executed", break_loop=False)

    return MockTool


# =============================================================================
# Settings Fixtures
# =============================================================================


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return {
        "chat_model_provider": "openai",
        "chat_model_name": "gpt-4",
        "chat_model_api_base": "",
        "chat_model_ctx_length": 8192,
        "chat_model_vision": True,
        "chat_model_rl_requests": 100,
        "chat_model_rl_input": 100000,
        "chat_model_rl_output": 4096,
        "chat_model_kwargs": {},

        "util_model_provider": "openai",
        "util_model_name": "gpt-4",
        "util_model_api_base": "",
        "util_model_ctx_length": 8192,
        "util_model_rl_requests": 100,
        "util_model_rl_input": 100000,
        "util_model_rl_output": 4096,
        "util_model_kwargs": {},

        "embed_model_provider": "openai",
        "embed_model_name": "text-embedding-ada-002",
        "embed_model_api_base": "",
        "embed_model_rl_requests": 100,
        "embed_model_kwargs": {},

        "browser_model_provider": "openai",
        "browser_model_name": "gpt-4",
        "browser_model_api_base": "",
        "browser_model_vision": True,
        "browser_model_kwargs": {},

        "agent_profile": "",
        "agent_memory_subdir": "test",
        "agent_knowledge_subdir": "default",
        "mcp_servers": "",
        "browser_http_headers": {},
        "code_exec_docker_enabled": False,
        "code_exec_ssh_enabled": False,
        "code_exec_ssh_addr": "localhost",
        "code_exec_ssh_port": 22,
        "code_exec_ssh_user": "user",
        "code_exec_ssh_pass": "",
        "mcp_server_token": "test_token_12345",
        "opencog_enabled": False,
        "opencog_host": "localhost",
        "opencog_port": 17001,
    }


@pytest.fixture
def patched_settings(mock_settings):
    """Patch settings.get_settings to return mock settings."""
    with patch("python.helpers.settings.get_settings", return_value=mock_settings):
        yield mock_settings


# =============================================================================
# OpenCog Fixtures
# =============================================================================


@pytest.fixture
def mock_opencog_available():
    """Mock OpenCog as available."""
    with patch.dict(sys.modules, {
        "opencog": MagicMock(),
        "opencog.atomspace": MagicMock(),
        "opencog.type_constructors": MagicMock(),
    }):
        yield True


@pytest.fixture
def mock_opencog_unavailable():
    """Mock OpenCog as unavailable."""
    with patch.dict(sys.modules, {"opencog": None}):
        yield False


@pytest.fixture
def opencog_available():
    """Check if OpenCog is available for testing."""
    try:
        from opencog.atomspace import AtomSpace
        return True
    except ImportError:
        return False


@pytest.fixture
def mock_atomspace():
    """Create a mock AtomSpace for testing when OpenCog is not available."""
    mock = MagicMock()
    mock.__len__ = MagicMock(return_value=0)
    return mock


# =============================================================================
# MCP Fixtures
# =============================================================================


@pytest.fixture
def mock_mcp_config():
    """Create a mock MCP configuration."""
    return {
        "servers": [],
        "tools": [],
    }


@pytest.fixture
def mock_mcp_handler(mock_mcp_config):
    """Create a mock MCP handler."""
    mock = MagicMock()
    mock.is_initialized.return_value = True
    mock.get_tool.return_value = None
    return mock


# =============================================================================
# Async Utilities
# =============================================================================


@pytest.fixture
def async_mock():
    """Fixture for creating async mocks easily."""
    def create_async_mock(return_value=None):
        mock = AsyncMock()
        mock.return_value = return_value
        return mock
    return create_async_mock


# =============================================================================
# Rate Limiter Fixtures
# =============================================================================


@pytest.fixture
def mock_rate_limiter():
    """Create a mock rate limiter."""
    from python.helpers.rate_limiter import RateLimiter

    limiter = RateLimiter(seconds=60)
    limiter.limits = {"requests": 100, "input": 100000, "output": 10000}
    return limiter


# =============================================================================
# History Fixtures
# =============================================================================


@pytest.fixture
def mock_history(mock_agent):
    """Create a mock history for testing."""
    return mock_agent.history


@pytest.fixture
def sample_chat_history():
    """Create sample chat history for testing."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help you?"},
        {"role": "user", "content": "What's the weather like?"},
    ]


# =============================================================================
# Docker Fixtures
# =============================================================================


@pytest.fixture
def mock_docker_client():
    """Create a mock Docker client."""
    mock = MagicMock()
    mock.containers.list.return_value = []
    mock.containers.run.return_value = MagicMock(
        logs=MagicMock(return_value=b"Container output"),
        wait=MagicMock(return_value={"StatusCode": 0}),
    )
    return mock


# =============================================================================
# Browser Fixtures
# =============================================================================


@pytest.fixture
def mock_playwright():
    """Create a mock Playwright instance."""
    mock = MagicMock()
    mock.chromium.launch.return_value = MagicMock(
        new_page=MagicMock(return_value=MagicMock(
            goto=AsyncMock(),
            content=AsyncMock(return_value="<html><body>Test</body></html>"),
            screenshot=AsyncMock(return_value=b"screenshot_data"),
        ))
    )
    return mock


# =============================================================================
# Test Markers and Configuration
# =============================================================================


def pytest_configure(config):
    """Configure custom pytest markers."""
    markers = [
        "unit: Unit tests",
        "integration: Integration tests",
        "e2e: End-to-end tests",
        "slow: Slow tests",
        "api: API tests",
        "tools: Tool tests",
        "helpers: Helper tests",
        "models: Model tests",
        "agent: Agent tests",
        "opencog: OpenCog tests",
        "mcp: MCP tests",
        "browser: Browser tests",
        "docker: Docker tests",
        "network: Network tests",
        "requires_opencog: mark test as requiring OpenCog installation",
        "requires_api_key: mark test as requiring API keys",
        "requires_docker: mark test as requiring Docker",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment."""
    # Skip OpenCog tests if not installed
    try:
        from opencog.atomspace import AtomSpace
        opencog_installed = True
    except ImportError:
        opencog_installed = False

    skip_opencog = pytest.mark.skip(reason="OpenCog not installed")
    skip_api_key = pytest.mark.skip(reason="API key not configured")
    skip_docker = pytest.mark.skip(reason="Docker not available")

    for item in items:
        if "requires_opencog" in item.keywords and not opencog_installed:
            item.add_marker(skip_opencog)
        if "requires_api_key" in item.keywords:
            if not os.environ.get("API_KEY_OPENAI") and not os.environ.get("OPENAI_API_KEY"):
                item.add_marker(skip_api_key)
        if "requires_docker" in item.keywords:
            import shutil
            if not shutil.which("docker"):
                item.add_marker(skip_docker)


# =============================================================================
# Cleanup Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def cleanup_agent_contexts():
    """Cleanup agent contexts after each test."""
    yield

    # Clear agent contexts
    try:
        from agent import AgentContext
        AgentContext._contexts.clear()
        AgentContext._counter = 0
    except (ImportError, AttributeError):
        pass


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Reset rate limiters after each test."""
    yield

    try:
        import models
        models.rate_limiters.clear()
        models.api_keys_round_robin.clear()
    except (ImportError, AttributeError):
        pass
