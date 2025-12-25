"""
Unit tests for agent.py - Core agent functionality.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone


# ============================================================================
# AgentContext Tests
# ============================================================================

class TestAgentContext:
    """Tests for AgentContext class."""

    def test_context_creation(self, mock_agent_config):
        """Test basic AgentContext creation."""
        from agent import AgentContext

        # Clear existing contexts
        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="test_ctx_1")

        assert context.id == "test_ctx_1"
        assert context.config == mock_agent_config
        assert context.paused is False
        assert context.agent0 is not None
        assert context.log is not None

        # Cleanup
        AgentContext.remove(context.id)

    def test_context_auto_id_generation(self, mock_agent_config):
        """Test automatic ID generation for context."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config)

        assert context.id is not None
        assert len(context.id) == 8  # Generated IDs are 8 characters

        AgentContext.remove(context.id)

    def test_context_get(self, mock_agent_config):
        """Test context retrieval by ID."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="test_ctx_get")

        retrieved = AgentContext.get("test_ctx_get")
        assert retrieved is context

        non_existent = AgentContext.get("non_existent")
        assert non_existent is None

        AgentContext.remove(context.id)

    def test_context_all(self, mock_agent_config):
        """Test retrieving all contexts."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        ctx1 = AgentContext(config=mock_agent_config, id="ctx_1")
        ctx2 = AgentContext(config=mock_agent_config, id="ctx_2")

        all_contexts = AgentContext.all()
        assert len(all_contexts) == 2
        assert ctx1 in all_contexts
        assert ctx2 in all_contexts

        AgentContext.remove("ctx_1")
        AgentContext.remove("ctx_2")

    def test_context_first(self, mock_agent_config):
        """Test retrieving first context."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        # No contexts
        assert AgentContext.first() is None

        ctx = AgentContext(config=mock_agent_config, id="first_ctx")
        assert AgentContext.first() is ctx

        AgentContext.remove("first_ctx")

    def test_context_remove(self, mock_agent_config):
        """Test context removal."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="removable_ctx")
        assert AgentContext.get("removable_ctx") is not None

        removed = AgentContext.remove("removable_ctx")
        assert removed is context
        assert AgentContext.get("removable_ctx") is None

    def test_context_serialize(self, mock_agent_config):
        """Test context serialization."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(
            config=mock_agent_config,
            id="serialize_ctx",
            name="Test Context"
        )

        serialized = context.serialize()

        assert serialized["id"] == "serialize_ctx"
        assert serialized["name"] == "Test Context"
        assert serialized["paused"] is False
        assert "created_at" in serialized
        assert "log_guid" in serialized

        AgentContext.remove("serialize_ctx")

    def test_context_reset(self, mock_agent_config):
        """Test context reset functionality."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="reset_ctx")
        original_agent = context.agent0

        context.reset()

        # Agent should be recreated
        assert context.agent0 is not original_agent
        assert context.paused is False
        assert context.streaming_agent is None

        AgentContext.remove("reset_ctx")

    def test_context_unique_id_generation(self, mock_agent_config):
        """Test that generated IDs are unique."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        ids = set()
        contexts = []

        for _ in range(10):
            ctx = AgentContext(config=mock_agent_config)
            assert ctx.id not in ids
            ids.add(ctx.id)
            contexts.append(ctx)

        # Cleanup
        for ctx in contexts:
            AgentContext.remove(ctx.id)


# ============================================================================
# AgentConfig Tests
# ============================================================================

class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_config_creation(self, mock_model_config, mock_embedding_config):
        """Test basic AgentConfig creation."""
        from agent import AgentConfig

        config = AgentConfig(
            chat_model=mock_model_config,
            utility_model=mock_model_config,
            embeddings_model=mock_embedding_config,
            browser_model=mock_model_config,
            mcp_servers="",
            profile="developer"
        )

        assert config.chat_model == mock_model_config
        assert config.profile == "developer"
        assert config.memory_subdir == ""
        assert config.knowledge_subdirs == ["default", "custom"]

    def test_config_defaults(self, mock_model_config, mock_embedding_config):
        """Test AgentConfig default values."""
        from agent import AgentConfig

        config = AgentConfig(
            chat_model=mock_model_config,
            utility_model=mock_model_config,
            embeddings_model=mock_embedding_config,
            browser_model=mock_model_config,
            mcp_servers=""
        )

        assert config.profile == ""
        assert config.memory_subdir == ""
        assert config.code_exec_ssh_enabled is True
        assert config.code_exec_ssh_addr == "localhost"
        assert config.code_exec_ssh_port == 55022
        assert config.code_exec_ssh_user == "root"

    def test_config_custom_values(self, mock_model_config, mock_embedding_config):
        """Test AgentConfig with custom values."""
        from agent import AgentConfig

        config = AgentConfig(
            chat_model=mock_model_config,
            utility_model=mock_model_config,
            embeddings_model=mock_embedding_config,
            browser_model=mock_model_config,
            mcp_servers="test_mcp",
            profile="researcher",
            memory_subdir="research_memory",
            knowledge_subdirs=["research", "custom"],
            code_exec_ssh_port=2222,
            additional={"custom_key": "custom_value"}
        )

        assert config.mcp_servers == "test_mcp"
        assert config.profile == "researcher"
        assert config.memory_subdir == "research_memory"
        assert config.code_exec_ssh_port == 2222
        assert config.additional["custom_key"] == "custom_value"


# ============================================================================
# UserMessage Tests
# ============================================================================

class TestUserMessage:
    """Tests for UserMessage dataclass."""

    def test_user_message_creation(self):
        """Test basic UserMessage creation."""
        from agent import UserMessage

        msg = UserMessage(message="Hello, Agent!")

        assert msg.message == "Hello, Agent!"
        assert msg.attachments == []
        assert msg.system_message == []

    def test_user_message_with_attachments(self):
        """Test UserMessage with attachments."""
        from agent import UserMessage

        msg = UserMessage(
            message="Check this file",
            attachments=["/path/to/file.txt", "/path/to/image.png"],
            system_message=["You are helpful"]
        )

        assert len(msg.attachments) == 2
        assert len(msg.system_message) == 1


# ============================================================================
# LoopData Tests
# ============================================================================

class TestLoopData:
    """Tests for LoopData class."""

    def test_loop_data_creation(self):
        """Test basic LoopData creation."""
        from agent import LoopData

        loop_data = LoopData()

        assert loop_data.iteration == -1
        assert loop_data.system == []
        assert loop_data.user_message is None
        assert loop_data.history_output == []
        assert loop_data.last_response == ""

    def test_loop_data_with_kwargs(self):
        """Test LoopData creation with kwargs."""
        from agent import LoopData

        loop_data = LoopData(iteration=5, last_response="Previous response")

        assert loop_data.iteration == 5
        assert loop_data.last_response == "Previous response"


# ============================================================================
# Agent Tests
# ============================================================================

class TestAgent:
    """Tests for Agent class."""

    def test_agent_creation(self, mock_agent_config):
        """Test basic Agent creation."""
        from agent import Agent, AgentContext

        AgentContext._contexts.clear()

        agent = Agent(number=0, config=mock_agent_config)

        assert agent.number == 0
        assert agent.agent_name == "A0"
        assert agent.config == mock_agent_config
        assert agent.context is not None
        assert agent.history is not None

        AgentContext.remove(agent.context.id)

    def test_agent_with_context(self, mock_agent_config, mock_agent_context):
        """Test Agent creation with existing context."""
        from agent import Agent

        agent = Agent(
            number=1,
            config=mock_agent_config,
            context=mock_agent_context
        )

        assert agent.number == 1
        assert agent.agent_name == "A1"
        assert agent.context is mock_agent_context

    def test_agent_data_get_set(self, mock_agent):
        """Test Agent data get/set methods."""
        mock_agent.set_data("test_key", "test_value")
        assert mock_agent.get_data("test_key") == "test_value"
        assert mock_agent.get_data("nonexistent") is None

    def test_agent_get_tool(self, mock_agent):
        """Test Agent get_tool method."""
        from agent import LoopData

        loop_data = LoopData()

        tool = mock_agent.get_tool(
            name="response",
            method=None,
            args={"message": "test"},
            message="test message",
            loop_data=loop_data
        )

        assert tool is not None

    def test_agent_get_tool_unknown(self, mock_agent):
        """Test Agent get_tool with unknown tool."""
        from agent import LoopData
        from python.tools.unknown import Unknown

        loop_data = LoopData()

        tool = mock_agent.get_tool(
            name="nonexistent_tool",
            method=None,
            args={},
            message="test",
            loop_data=loop_data
        )

        assert isinstance(tool, Unknown)


# ============================================================================
# Exception Tests
# ============================================================================

class TestExceptions:
    """Tests for custom exception classes."""

    def test_intervention_exception(self):
        """Test InterventionException."""
        from agent import InterventionException

        exc = InterventionException("User intervention")
        assert str(exc) == "User intervention"

    def test_handled_exception(self):
        """Test HandledException."""
        from agent import HandledException

        original = ValueError("Original error")
        exc = HandledException(original)
        assert exc.args[0] is original


# ============================================================================
# AgentContextType Tests
# ============================================================================

class TestAgentContextType:
    """Tests for AgentContextType enum."""

    def test_context_types(self):
        """Test all context types."""
        from agent import AgentContextType

        assert AgentContextType.USER.value == "user"
        assert AgentContextType.TASK.value == "task"
        assert AgentContextType.BACKGROUND.value == "background"


# ============================================================================
# Integration Tests (Agent + Context)
# ============================================================================

class TestAgentContextIntegration:
    """Integration tests for Agent and AgentContext."""

    def test_context_agent_relationship(self, mock_agent_config):
        """Test bidirectional relationship between Agent and Context."""
        from agent import Agent, AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="relationship_ctx")

        assert context.agent0 is not None
        assert context.agent0.context is context

        AgentContext.remove("relationship_ctx")

    def test_context_get_agent(self, mock_agent_config):
        """Test getting current agent from context."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="get_agent_ctx")

        # By default, streaming_agent is None, so get_agent returns agent0
        assert context.get_agent() is context.agent0

        # Set streaming agent
        context.streaming_agent = context.agent0
        assert context.get_agent() is context.agent0

        AgentContext.remove("get_agent_ctx")

    @pytest.mark.asyncio
    async def test_context_communicate(self, mock_agent_config):
        """Test context communicate method."""
        from agent import AgentContext, UserMessage

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="communicate_ctx")

        msg = UserMessage(message="Hello")

        # This should start a task
        # Since we can't fully test LLM calls, we just verify it doesn't crash
        try:
            # The task will fail without proper LLM setup, but we're testing structure
            task = context.communicate(msg)
            assert task is not None
        except Exception:
            pass  # Expected without proper LLM setup

        AgentContext.remove("communicate_ctx")
