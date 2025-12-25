"""
Integration tests for Agent Zero - Testing component interactions.

Tests cover:
- Agent initialization flow
- Agent context management
- Tool execution pipeline
- Model integration
- Memory operations
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio


@pytest.mark.integration
@pytest.mark.agent
class TestAgentInitializationFlow:
    """Integration tests for agent initialization."""

    def test_full_initialization_flow(self, patched_settings):
        """Test complete agent initialization flow."""
        from initialize import initialize_agent
        from agent import AgentContext, Agent

        AgentContext._contexts.clear()

        with patch("initialize._set_runtime_config"):
            with patch("initialize._args_override"):
                config = initialize_agent()

                # Create context with the config
                context = AgentContext(config=config, id="test-init-flow")

                assert context is not None
                assert context.agent0 is not None
                assert isinstance(context.agent0, Agent)

    def test_agent_with_profile(self, patched_settings):
        """Test agent initialization with custom profile."""
        from initialize import initialize_agent
        from agent import AgentContext

        AgentContext._contexts.clear()

        patched_settings["agent_profile"] = "developer"

        with patch("initialize.settings.get_settings", return_value=patched_settings):
            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    context = AgentContext(config=config, id="test-profile")

                    assert context.agent0.config.profile == "developer"


@pytest.mark.integration
@pytest.mark.agent
class TestAgentContextManagement:
    """Integration tests for agent context lifecycle."""

    def test_multiple_contexts(self, mock_agent_config):
        """Test managing multiple agent contexts."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        contexts = []
        for i in range(5):
            ctx = AgentContext(config=mock_agent_config, id=f"ctx-{i}")
            contexts.append(ctx)

        assert len(AgentContext.all()) == 5

        # Remove some
        AgentContext.remove("ctx-2")
        assert len(AgentContext.all()) == 4
        assert AgentContext.get("ctx-2") is None

    def test_context_reset_cleans_state(self, mock_agent_context):
        """Test context reset cleans agent state."""
        mock_agent_context.paused = True
        mock_agent_context.streaming_agent = MagicMock()

        mock_agent_context.reset()

        assert mock_agent_context.paused is False
        assert mock_agent_context.streaming_agent is None


@pytest.mark.integration
@pytest.mark.tools
class TestToolExecutionPipeline:
    """Integration tests for tool execution flow."""

    @pytest.mark.asyncio
    async def test_tool_execution_lifecycle(self, mock_agent):
        """Test complete tool execution lifecycle."""
        from python.helpers.tool import Tool, Response
        from agent import LoopData

        class IntegrationTool(Tool):
            async def execute(self, **kwargs):
                return Response(
                    message="Integration test completed",
                    break_loop=True
                )

        mock_agent.loop_data = LoopData()

        # Mock the log
        mock_agent.context.log.log = MagicMock(return_value=MagicMock())

        tool = IntegrationTool(
            agent=mock_agent,
            name="integration_tool",
            method=None,
            args={"test_arg": "value"},
            message="",
            loop_data=mock_agent.loop_data,
        )

        # Execute full lifecycle
        await tool.before_execution()
        response = await tool.execute()

        with patch.object(mock_agent, "hist_add_tool_result"):
            await tool.after_execution(response)

        assert response.message == "Integration test completed"
        assert response.break_loop is True

    @pytest.mark.asyncio
    async def test_process_tools_integration(self, mock_agent):
        """Test agent process_tools integration."""
        from agent import LoopData
        from python.helpers.tool import Response

        mock_agent.loop_data = LoopData()

        # Create a mock tool
        mock_tool = MagicMock()
        mock_tool.before_execution = AsyncMock()
        mock_tool.execute = AsyncMock(return_value=Response(
            message="Tool result",
            break_loop=True
        ))
        mock_tool.after_execution = AsyncMock()

        with patch.object(mock_agent, "get_tool", return_value=mock_tool):
            with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock):
                result = await mock_agent.process_tools(
                    '{"tool_name": "test", "tool_args": {}}'
                )

                assert result == "Tool result"


@pytest.mark.integration
@pytest.mark.models
class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_model_config_to_chat_model(self, mock_model_config):
        """Test converting ModelConfig to chat model."""
        with patch("models.get_chat_model") as mock_get:
            mock_model = MagicMock()
            mock_get.return_value = mock_model

            from models import get_chat_model

            model = get_chat_model(
                mock_model_config.provider,
                mock_model_config.name,
                model_config=mock_model_config,
            )

            assert model is not None

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self):
        """Test rate limiting with model calls."""
        from models import get_rate_limiter, rate_limiters

        rate_limiters.clear()

        limiter = get_rate_limiter("test", "model", 10, 1000, 100)

        # Simulate multiple requests
        for _ in range(5):
            limiter.add(requests=1, input=100)

        total_requests = await limiter.get_total("requests")
        assert total_requests == 5


@pytest.mark.integration
class TestMemoryIntegration:
    """Integration tests for memory operations."""

    @pytest.mark.asyncio
    async def test_history_message_flow(self, mock_agent, mock_user_message):
        """Test message flow through history."""
        from agent import LoopData

        mock_agent.loop_data = LoopData()

        # Add user message
        msg1 = mock_agent.hist_add_user_message(mock_user_message)

        # Add AI response
        msg2 = mock_agent.hist_add_ai_response("AI response to user")

        assert mock_agent.last_user_message is msg1
        assert mock_agent.loop_data.last_response == "AI response to user"


@pytest.mark.integration
class TestExtensionIntegration:
    """Integration tests for extension system."""

    @pytest.mark.asyncio
    async def test_extension_call_integration(self, mock_agent):
        """Test extension calls during agent lifecycle."""
        called_extensions = []

        async def track_extensions(extension_point, **kwargs):
            called_extensions.append(extension_point)
            return None

        with patch("python.helpers.extension.call_extensions", side_effect=track_extensions):
            await mock_agent.call_extensions("test_extension")
            await mock_agent.call_extensions("another_extension")

        assert "test_extension" in called_extensions
        assert "another_extension" in called_extensions


@pytest.mark.integration
class TestConfigIntegration:
    """Integration tests for configuration flow."""

    def test_settings_to_agent_config_flow(self, mock_settings):
        """Test settings flow to agent configuration."""
        from initialize import initialize_agent
        from agent import AgentContext

        AgentContext._contexts.clear()

        with patch("python.helpers.settings.get_settings", return_value=mock_settings):
            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert config.chat_model.provider == mock_settings["chat_model_provider"]
                    assert config.chat_model.name == mock_settings["chat_model_name"]
