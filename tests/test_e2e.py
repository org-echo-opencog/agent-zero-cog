"""
End-to-end tests for Agent Zero workflows.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio


# ============================================================================
# Agent Initialization E2E Tests
# ============================================================================

class TestAgentInitializationE2E:
    """E2E tests for agent initialization."""

    def test_full_agent_initialization(self, mock_settings, patch_settings):
        """Test full agent initialization from settings."""
        from initialize import initialize_agent

        with patch('initialize.runtime.args', {}):
            config = initialize_agent()

            assert config is not None
            assert config.chat_model is not None
            assert config.utility_model is not None
            assert config.embeddings_model is not None
            assert config.browser_model is not None

    def test_agent_context_creation_flow(self, mock_agent_config):
        """Test complete agent context creation flow."""
        from agent import AgentContext, Agent

        AgentContext._contexts.clear()

        # Create context
        context = AgentContext(
            config=mock_agent_config,
            id="e2e_test_context"
        )

        # Verify context is registered
        assert AgentContext.get("e2e_test_context") is context

        # Verify agent is created
        assert context.agent0 is not None
        assert isinstance(context.agent0, Agent)

        # Verify bidirectional relationship
        assert context.agent0.context is context

        # Cleanup
        AgentContext.remove("e2e_test_context")

    def test_multiple_contexts_isolation(self, mock_agent_config):
        """Test that multiple contexts are properly isolated."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        ctx1 = AgentContext(config=mock_agent_config, id="ctx_1")
        ctx2 = AgentContext(config=mock_agent_config, id="ctx_2")

        # Verify isolation
        assert ctx1.agent0 is not ctx2.agent0
        assert ctx1.log is not ctx2.log

        # Verify both are tracked
        assert len(AgentContext.all()) == 2

        # Cleanup
        AgentContext.remove("ctx_1")
        AgentContext.remove("ctx_2")


# ============================================================================
# Message Processing E2E Tests
# ============================================================================

class TestMessageProcessingE2E:
    """E2E tests for message processing flow."""

    def test_user_message_creation(self):
        """Test user message creation."""
        from agent import UserMessage

        msg = UserMessage(
            message="Hello, Agent Zero!",
            attachments=["/path/to/file.txt"],
            system_message=["Be helpful"]
        )

        assert msg.message == "Hello, Agent Zero!"
        assert len(msg.attachments) == 1
        assert len(msg.system_message) == 1

    def test_history_message_flow(self, mock_agent):
        """Test message history flow."""
        from agent import UserMessage

        # Add user message to history
        msg = UserMessage(message="Test message")
        mock_agent.hist_add_user_message(msg)

        # Verify message is in history
        assert mock_agent.last_user_message is not None

    def test_loop_data_lifecycle(self):
        """Test LoopData lifecycle."""
        from agent import LoopData

        loop_data = LoopData()

        # Initial state
        assert loop_data.iteration == -1

        # Simulate iteration
        loop_data.iteration += 1
        assert loop_data.iteration == 0

        # Add temporary params
        loop_data.params_temporary["key"] = "value"
        assert loop_data.params_temporary["key"] == "value"

        # Clear temporary params (as done in real loop)
        loop_data.params_temporary = {}
        assert "key" not in loop_data.params_temporary


# ============================================================================
# Tool Execution E2E Tests
# ============================================================================

class TestToolExecutionE2E:
    """E2E tests for tool execution flow."""

    @pytest.mark.asyncio
    async def test_tool_lookup_flow(self, mock_agent):
        """Test tool lookup and instantiation flow."""
        from agent import LoopData

        loop_data = LoopData()

        # Get a known tool
        tool = mock_agent.get_tool(
            name="response",
            method=None,
            args={"message": "test"},
            message="",
            loop_data=loop_data
        )

        assert tool is not None

    @pytest.mark.asyncio
    async def test_unknown_tool_handling(self, mock_agent):
        """Test handling of unknown tools."""
        from agent import LoopData
        from python.tools.unknown import Unknown

        loop_data = LoopData()

        tool = mock_agent.get_tool(
            name="definitely_not_a_real_tool",
            method=None,
            args={},
            message="",
            loop_data=loop_data
        )

        assert isinstance(tool, Unknown)

    @pytest.mark.asyncio
    async def test_tool_with_method(self, mock_agent):
        """Test tool with method specification."""
        from agent import LoopData

        loop_data = LoopData()

        # Tool name with method
        tool = mock_agent.get_tool(
            name="memory_save",
            method="important",
            args={},
            message="",
            loop_data=loop_data
        )

        assert tool is not None


# ============================================================================
# Extension System E2E Tests
# ============================================================================

class TestExtensionSystemE2E:
    """E2E tests for extension system."""

    @pytest.mark.asyncio
    async def test_extension_point_call(self, mock_agent):
        """Test calling extension points."""
        from agent import LoopData

        loop_data = LoopData()

        # Call a known extension point
        result = await mock_agent.call_extensions(
            "message_loop_start",
            loop_data=loop_data
        )

        # Should not raise, extensions may or may not exist

    @pytest.mark.asyncio
    async def test_system_prompt_extension(self, mock_agent):
        """Test system prompt extension point."""
        system_prompt = []

        await mock_agent.call_extensions(
            "system_prompt",
            system_prompt=system_prompt,
            loop_data=mock_agent.loop_data if hasattr(mock_agent, 'loop_data') else None
        )

        # System prompt might be populated by extensions


# ============================================================================
# Configuration E2E Tests
# ============================================================================

class TestConfigurationE2E:
    """E2E tests for configuration handling."""

    def test_model_config_flow(self):
        """Test model configuration flow."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4",
            ctx_length=8192,
            kwargs={"temperature": 0.7}
        )

        # Test kwargs building
        kwargs = config.build_kwargs()
        assert kwargs["temperature"] == 0.7

    def test_agent_config_with_profile(self, mock_model_config, mock_embedding_config):
        """Test agent config with profile."""
        from agent import AgentConfig

        config = AgentConfig(
            chat_model=mock_model_config,
            utility_model=mock_model_config,
            embeddings_model=mock_embedding_config,
            browser_model=mock_model_config,
            mcp_servers="",
            profile="developer"
        )

        assert config.profile == "developer"


# ============================================================================
# History Management E2E Tests
# ============================================================================

class TestHistoryManagementE2E:
    """E2E tests for history management."""

    def test_history_output_format(self, mock_agent):
        """Test history output format."""
        from agent import UserMessage

        # Add messages to history
        msg = UserMessage(message="Hello")
        mock_agent.hist_add_user_message(msg)

        # Get history output
        output = mock_agent.history.output()

        assert isinstance(output, list)

    def test_history_new_topic(self, mock_agent):
        """Test new topic in history."""
        from agent import UserMessage

        # Add first message (starts new topic)
        msg1 = UserMessage(message="First message")
        mock_agent.hist_add_user_message(msg1)

        # Add second message (starts another new topic)
        msg2 = UserMessage(message="Second message")
        mock_agent.hist_add_user_message(msg2)


# ============================================================================
# Log System E2E Tests
# ============================================================================

class TestLogSystemE2E:
    """E2E tests for logging system."""

    def test_log_full_workflow(self, mock_agent_context):
        """Test complete logging workflow."""
        from python.helpers.log import Log

        log = mock_agent_context.log

        # Log various types
        log.log(type="info", heading="Info", content="Information message")
        log.log(type="warning", heading="Warning", content="Warning message")
        log.log(type="error", heading="Error", content="Error message")

        output = log.output()

        assert len(output) == 3

    def test_log_with_kvps(self, mock_agent_context):
        """Test logging with key-value pairs."""
        log = mock_agent_context.log

        log.log(
            type="info",
            heading="Data",
            content="Message with data",
            kvps={"key1": "value1", "key2": 42}
        )

        output = log.output()
        assert len(output) == 1


# ============================================================================
# Context Lifecycle E2E Tests
# ============================================================================

class TestContextLifecycleE2E:
    """E2E tests for context lifecycle."""

    def test_context_creation_to_destruction(self, mock_agent_config):
        """Test full context lifecycle."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        # Create
        ctx = AgentContext(config=mock_agent_config, id="lifecycle_test")
        assert AgentContext.get("lifecycle_test") is not None

        # Reset
        original_agent = ctx.agent0
        ctx.reset()
        assert ctx.agent0 is not original_agent

        # Remove
        AgentContext.remove("lifecycle_test")
        assert AgentContext.get("lifecycle_test") is None

    def test_context_serialization_roundtrip(self, mock_agent_config):
        """Test context serialization."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        ctx = AgentContext(
            config=mock_agent_config,
            id="serialize_test",
            name="Test Context"
        )

        # Serialize
        serialized = ctx.serialize()

        # Verify serialized data
        assert serialized["id"] == "serialize_test"
        assert serialized["name"] == "Test Context"
        assert "created_at" in serialized
        assert "log_guid" in serialized

        # Cleanup
        AgentContext.remove("serialize_test")


# ============================================================================
# Error Handling E2E Tests
# ============================================================================

class TestErrorHandlingE2E:
    """E2E tests for error handling."""

    def test_intervention_exception_flow(self):
        """Test InterventionException handling."""
        from agent import InterventionException

        try:
            raise InterventionException("User intervention")
        except InterventionException as e:
            assert str(e) == "User intervention"

    def test_handled_exception_wrapping(self):
        """Test HandledException wrapping."""
        from agent import HandledException

        original = ValueError("Original error")
        handled = HandledException(original)

        assert handled.args[0] is original


# ============================================================================
# Multi-Agent E2E Tests
# ============================================================================

class TestMultiAgentE2E:
    """E2E tests for multi-agent scenarios."""

    def test_subordinate_agent_creation(self, mock_agent_config):
        """Test creating subordinate agents."""
        from agent import Agent, AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="multi_agent_test")

        # Create subordinate
        subordinate = Agent(
            number=1,
            config=mock_agent_config,
            context=context
        )

        assert subordinate.number == 1
        assert subordinate.agent_name == "A1"
        assert subordinate.context is context

        # Cleanup
        AgentContext.remove("multi_agent_test")

    def test_agent_data_sharing(self, mock_agent_config):
        """Test data sharing between agents."""
        from agent import Agent, AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="data_share_test")

        agent0 = context.agent0
        agent1 = Agent(number=1, config=mock_agent_config, context=context)

        # Set data on agent0
        agent0.set_data("shared_key", "shared_value")

        # Agent1 has its own data space
        agent1.set_data("agent1_key", "agent1_value")

        assert agent0.get_data("shared_key") == "shared_value"
        assert agent1.get_data("agent1_key") == "agent1_value"
        assert agent0.get_data("agent1_key") is None

        # Cleanup
        AgentContext.remove("data_share_test")


# ============================================================================
# Prompt System E2E Tests
# ============================================================================

class TestPromptSystemE2E:
    """E2E tests for prompt system."""

    def test_read_prompt(self, mock_agent):
        """Test reading prompt files."""
        # Try to read a known prompt file
        try:
            prompt = mock_agent.read_prompt("fw.msg_repeat.md")
            assert prompt is not None
            assert isinstance(prompt, str)
        except FileNotFoundError:
            pytest.skip("Prompt file not found")

    def test_parse_prompt_with_variables(self, mock_agent):
        """Test parsing prompt with variable substitution."""
        try:
            content = mock_agent.parse_prompt(
                "fw.user_message.md",
                message="Test message",
                attachments=[],
                system_message=[]
            )
            assert content is not None
        except FileNotFoundError:
            pytest.skip("Prompt file not found")


# ============================================================================
# Rate Limiting E2E Tests
# ============================================================================

class TestRateLimitingE2E:
    """E2E tests for rate limiting."""

    def test_rate_limiter_integration(self):
        """Test rate limiter integration."""
        from models import get_rate_limiter

        limiter = get_rate_limiter(
            provider="openai",
            name="gpt-4",
            requests=10,
            input=10000,
            output=4096
        )

        # Add some usage
        limiter.add(requests=1, input=100, output=50)

        assert limiter.get_usage("requests") == 1
        assert limiter.get_usage("input") == 100
        assert limiter.get_usage("output") == 50

    @pytest.mark.asyncio
    async def test_rate_limiter_wait(self):
        """Test rate limiter wait functionality."""
        from models import get_rate_limiter
        import time

        limiter = get_rate_limiter(
            provider="test_provider",
            name="test_model",
            requests=100,
            input=10000,
            output=4096
        )

        # Should not wait when under limit
        start = time.time()
        await limiter.wait()
        elapsed = time.time() - start

        assert elapsed < 1  # Should be nearly instant


# ============================================================================
# Model Wrapper E2E Tests
# ============================================================================

class TestModelWrapperE2E:
    """E2E tests for model wrappers."""

    def test_chat_model_wrapper_creation(self, mock_model_config):
        """Test chat model wrapper creation."""
        from models import LiteLLMChatWrapper

        wrapper = LiteLLMChatWrapper(
            model="gpt-4",
            provider="openai",
            model_config=mock_model_config
        )

        assert wrapper.model_name == "openai/gpt-4"
        assert wrapper._llm_type == "litellm-chat"

    def test_embedding_wrapper_creation(self, mock_embedding_config):
        """Test embedding wrapper creation."""
        from models import LiteLLMEmbeddingWrapper

        wrapper = LiteLLMEmbeddingWrapper(
            model="text-embedding-ada-002",
            provider="openai",
            model_config=mock_embedding_config
        )

        assert wrapper.model_name == "text-embedding-ada-002"
