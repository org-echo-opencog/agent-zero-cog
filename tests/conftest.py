"""
Pytest configuration and shared fixtures for Agent Zero tests.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import MagicMock, AsyncMock, patch
from dataclasses import dataclass

import pytest

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# Environment Setup
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ.setdefault("TESTING", "1")
    os.environ.setdefault("LITELLM_LOG", "ERROR")
    os.environ.setdefault("LOG_LEVEL", "ERROR")
    yield
    # Cleanup if needed


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Mock Fixtures for Models
# ============================================================================

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
        limit_input=10000,
        limit_output=4096,
        vision=False,
        kwargs={}
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
        limit_input=10000,
        limit_output=0,
        vision=False,
        kwargs={}
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
        knowledge_subdirs=["default", "custom"],
    )


# ============================================================================
# Mock Fixtures for LLM Responses
# ============================================================================

@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    return {
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
def mock_streaming_response():
    """Create a mock streaming LLM response."""
    chunks = [
        {"choices": [{"delta": {"content": "Hello"}}]},
        {"choices": [{"delta": {"content": " "}}]},
        {"choices": [{"delta": {"content": "World"}}]},
        {"choices": [{"delta": {"content": "!"}}]},
    ]
    return chunks


@pytest.fixture
def mock_tool_response():
    """Create a mock tool response from LLM."""
    import json
    tool_call = {
        "tool_name": "response",
        "tool_args": {
            "message": "Task completed successfully."
        }
    }
    return json.dumps(tool_call)


# ============================================================================
# Mock Fixtures for Agent Context
# ============================================================================

@pytest.fixture
def mock_agent_context(mock_agent_config):
    """Create a mock AgentContext for testing."""
    from agent import AgentContext

    # Clean up any existing contexts first
    AgentContext._contexts.clear()

    context = AgentContext(
        config=mock_agent_config,
        id="test_context_123"
    )
    yield context

    # Cleanup
    AgentContext.remove(context.id)


@pytest.fixture
def mock_agent(mock_agent_config, mock_agent_context):
    """Create a mock Agent for testing."""
    from agent import Agent

    agent = Agent(
        number=0,
        config=mock_agent_config,
        context=mock_agent_context
    )
    return agent


# ============================================================================
# Mock Fixtures for Settings
# ============================================================================

@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return {
        "chat_model_provider": "openai",
        "chat_model_name": "gpt-4",
        "chat_model_api_base": "",
        "chat_model_ctx_length": 8192,
        "chat_model_vision": False,
        "chat_model_rl_requests": 100,
        "chat_model_rl_input": 10000,
        "chat_model_rl_output": 4096,
        "chat_model_kwargs": {},
        "util_model_provider": "openai",
        "util_model_name": "gpt-3.5-turbo",
        "util_model_api_base": "",
        "util_model_ctx_length": 4096,
        "util_model_rl_requests": 100,
        "util_model_rl_input": 10000,
        "util_model_rl_output": 2048,
        "util_model_kwargs": {},
        "embed_model_provider": "openai",
        "embed_model_name": "text-embedding-ada-002",
        "embed_model_api_base": "",
        "embed_model_rl_requests": 100,
        "embed_model_kwargs": {},
        "browser_model_provider": "openai",
        "browser_model_name": "gpt-4-vision-preview",
        "browser_model_api_base": "",
        "browser_model_vision": True,
        "browser_model_kwargs": {},
        "agent_profile": "",
        "agent_memory_subdir": "test",
        "agent_knowledge_subdir": "custom",
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
def patch_settings(mock_settings):
    """Patch the settings module with mock settings."""
    with patch("python.helpers.settings.get_settings", return_value=mock_settings):
        yield mock_settings


# ============================================================================
# Mock Fixtures for HTTP/API
# ============================================================================

@pytest.fixture
def mock_flask_app():
    """Create a mock Flask app for testing."""
    from flask import Flask

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    return app


@pytest.fixture
def mock_flask_client(mock_flask_app):
    """Create a Flask test client."""
    return mock_flask_app.test_client()


# ============================================================================
# Mock Fixtures for Tools
# ============================================================================

@pytest.fixture
def mock_tool_base():
    """Create a mock base tool for testing."""
    from python.helpers.tool import Tool, Response

    class MockTool(Tool):
        async def execute(self, **kwargs):
            return Response(message="Mock tool executed", break_loop=False)

    return MockTool


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def temp_directory(tmp_path):
    """Create a temporary directory for test files."""
    test_dir = tmp_path / "agent_zero_tests"
    test_dir.mkdir(exist_ok=True)
    return test_dir


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


# ============================================================================
# OpenCog Fixtures
# ============================================================================

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


# ============================================================================
# Async Test Helpers
# ============================================================================

@pytest.fixture
def async_mock():
    """Create an async mock that can be awaited."""
    def _create_async_mock(return_value=None):
        mock = AsyncMock(return_value=return_value)
        return mock
    return _create_async_mock


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_user_message():
    """Create a sample user message for testing."""
    from agent import UserMessage

    return UserMessage(
        message="Hello, this is a test message.",
        attachments=[],
        system_message=[]
    )


@pytest.fixture
def sample_chat_history():
    """Create sample chat history for testing."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help you?"},
        {"role": "user", "content": "What's the weather like?"},
    ]


# ============================================================================
# Skip Conditions
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "requires_opencog: mark test as requiring OpenCog installation"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: mark test as requiring API keys"
    )
    config.addinivalue_line(
        "markers", "requires_docker: mark test as requiring Docker"
    )


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
