"""
Unit tests for agent.py - Core agent functionality.

Tests cover:
- AgentContext management
- Agent lifecycle
- Message handling
- Tool execution
- History management
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
from datetime import datetime, timezone


@pytest.mark.unit
@pytest.mark.agent
class TestAgentContextType:
    """Tests for AgentContextType enum."""

    def test_context_type_values(self):
        """Test AgentContextType enum values."""
        from agent import AgentContextType

        assert AgentContextType.USER.value == "user"
        assert AgentContextType.TASK.value == "task"
        assert AgentContextType.BACKGROUND.value == "background"


@pytest.mark.unit
@pytest.mark.agent
class TestAgentContext:
    """Tests for AgentContext class."""

    def test_context_creation(self, mock_agent_config):
        """Test creating an AgentContext."""
        from agent import AgentContext, AgentContextType

        AgentContext._contexts.clear()

        context = AgentContext(
            config=mock_agent_config,
            id="test-123",
            name="Test Context",
            type=AgentContextType.USER,
        )

        assert context.id == "test-123"
        assert context.name == "Test Context"
        assert context.type == AgentContextType.USER
        assert context.paused is False

    def test_context_auto_id_generation(self, mock_agent_config):
        """Test automatic ID generation for context."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config)

        assert context.id is not None
        assert len(context.id) == 8

    def test_context_get(self, mock_agent_config):
        """Test getting a context by ID."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="lookup-test")

        retrieved = AgentContext.get("lookup-test")
        assert retrieved is context

    def test_context_get_nonexistent(self):
        """Test getting a non-existent context returns None."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        retrieved = AgentContext.get("nonexistent")
        assert retrieved is None

    def test_context_first(self, mock_agent_config):
        """Test getting the first context."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context1 = AgentContext(config=mock_agent_config, id="first")
        context2 = AgentContext(config=mock_agent_config, id="second")

        first = AgentContext.first()
        assert first.id == "first"

    def test_context_first_empty(self):
        """Test getting first context when none exist."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        first = AgentContext.first()
        assert first is None

    def test_context_all(self, mock_agent_config):
        """Test getting all contexts."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context1 = AgentContext(config=mock_agent_config, id="ctx1")
        context2 = AgentContext(config=mock_agent_config, id="ctx2")

        all_contexts = AgentContext.all()
        assert len(all_contexts) == 2

    def test_context_remove(self, mock_agent_config):
        """Test removing a context."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="to-remove")

        removed = AgentContext.remove("to-remove")
        assert removed is context
        assert AgentContext.get("to-remove") is None

    def test_context_remove_nonexistent(self):
        """Test removing a non-existent context."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        removed = AgentContext.remove("nonexistent")
        assert removed is None

    def test_context_serialize(self, mock_agent_config):
        """Test context serialization."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(
            config=mock_agent_config,
            id="serialize-test",
            name="Serialization Test",
        )

        serialized = context.serialize()

        assert serialized["id"] == "serialize-test"
        assert serialized["name"] == "Serialization Test"
        assert "created_at" in serialized
        assert "no" in serialized
        assert serialized["paused"] is False

    def test_context_reset(self, mock_agent_config):
        """Test context reset."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="reset-test")
        context.paused = True

        context.reset()

        assert context.paused is False
        assert context.streaming_agent is None

    def test_context_replaces_existing(self, mock_agent_config):
        """Test creating context with existing ID replaces it."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        context1 = AgentContext(config=mock_agent_config, id="duplicate")
        context2 = AgentContext(config=mock_agent_config, id="duplicate")

        assert AgentContext.get("duplicate") is context2
        assert len(AgentContext.all()) == 1

    def test_generate_id_unique(self, mock_agent_config):
        """Test ID generation creates unique IDs."""
        from agent import AgentContext

        AgentContext._contexts.clear()

        ids = set()
        for _ in range(100):
            id = AgentContext.generate_id()
            assert id not in ids
            ids.add(id)


@pytest.mark.unit
@pytest.mark.agent
class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_agent_config_creation(self, mock_model_config, mock_embedding_config):
        """Test creating an AgentConfig."""
        from agent import AgentConfig

        config = AgentConfig(
            chat_model=mock_model_config,
            utility_model=mock_model_config,
            embeddings_model=mock_embedding_config,
            browser_model=mock_model_config,
            mcp_servers="",
            profile="developer",
            memory_subdir="test_memory",
        )

        assert config.profile == "developer"
        assert config.memory_subdir == "test_memory"

    def test_agent_config_defaults(self, mock_model_config, mock_embedding_config):
        """Test AgentConfig default values."""
        from agent import AgentConfig

        config = AgentConfig(
            chat_model=mock_model_config,
            utility_model=mock_model_config,
            embeddings_model=mock_embedding_config,
            browser_model=mock_model_config,
            mcp_servers="",
        )

        assert config.profile == ""
        assert config.memory_subdir == ""
        assert config.knowledge_subdirs == ["default", "custom"]
        assert config.code_exec_ssh_enabled is True


@pytest.mark.unit
@pytest.mark.agent
class TestUserMessage:
    """Tests for UserMessage dataclass."""

    def test_user_message_creation(self):
        """Test creating a UserMessage."""
        from agent import UserMessage

        msg = UserMessage(
            message="Hello, agent!",
            attachments=["file1.txt"],
            system_message=["Be helpful"],
        )

        assert msg.message == "Hello, agent!"
        assert msg.attachments == ["file1.txt"]
        assert msg.system_message == ["Be helpful"]

    def test_user_message_defaults(self):
        """Test UserMessage default values."""
        from agent import UserMessage

        msg = UserMessage(message="Simple message")

        assert msg.message == "Simple message"
        assert msg.attachments == []
        assert msg.system_message == []


@pytest.mark.unit
@pytest.mark.agent
class TestLoopData:
    """Tests for LoopData class."""

    def test_loop_data_creation(self):
        """Test creating LoopData."""
        from agent import LoopData

        loop_data = LoopData()

        assert loop_data.iteration == -1
        assert loop_data.system == []
        assert loop_data.user_message is None
        assert loop_data.last_response == ""

    def test_loop_data_with_kwargs(self):
        """Test LoopData with custom values."""
        from agent import LoopData

        loop_data = LoopData(
            iteration=5,
            last_response="Previous response",
        )

        assert loop_data.iteration == 5
        assert loop_data.last_response == "Previous response"


@pytest.mark.unit
@pytest.mark.agent
class TestAgent:
    """Tests for Agent class."""

    def test_agent_creation(self, mock_agent_config):
        """Test creating an Agent."""
        from agent import Agent, AgentContext

        AgentContext._contexts.clear()

        agent = Agent(number=0, config=mock_agent_config)

        assert agent.number == 0
        assert agent.agent_name == "A0"
        assert agent.intervention is None

    def test_agent_with_context(self, mock_agent_context):
        """Test creating an Agent with existing context."""
        from agent import Agent

        agent = Agent(
            number=1,
            config=mock_agent_context.config,
            context=mock_agent_context,
        )

        assert agent.context is mock_agent_context

    def test_agent_data_access(self, mock_agent):
        """Test agent data get/set."""
        mock_agent.set_data("test_key", "test_value")

        assert mock_agent.get_data("test_key") == "test_value"
        assert mock_agent.get_data("nonexistent") is None

    def test_agent_get_chat_model(self, mock_agent_context, mock_chat_model):
        """Test getting chat model."""
        from agent import Agent

        agent = mock_agent_context.agent0

        with patch("models.get_chat_model", return_value=mock_chat_model):
            model = agent.get_chat_model()
            assert model is not None

    def test_agent_hist_add_message(self, mock_agent):
        """Test adding a message to history."""
        msg = mock_agent.hist_add_message(ai=False, content="Test content")

        assert msg is not None

    def test_agent_hist_add_user_message(self, mock_agent, mock_user_message):
        """Test adding a user message to history."""
        msg = mock_agent.hist_add_user_message(mock_user_message)

        assert msg is not None
        assert mock_agent.last_user_message is msg

    def test_agent_hist_add_ai_response(self, mock_agent):
        """Test adding an AI response to history."""
        # Initialize loop_data
        from agent import LoopData
        mock_agent.loop_data = LoopData()

        msg = mock_agent.hist_add_ai_response("AI response")

        assert msg is not None
        assert mock_agent.loop_data.last_response == "AI response"


@pytest.mark.unit
@pytest.mark.agent
class TestInterventionException:
    """Tests for InterventionException."""

    def test_intervention_exception(self):
        """Test InterventionException can be raised."""
        from agent import InterventionException

        with pytest.raises(InterventionException):
            raise InterventionException("Intervention message")


@pytest.mark.unit
@pytest.mark.agent
class TestHandledException:
    """Tests for HandledException."""

    def test_handled_exception(self):
        """Test HandledException can be raised."""
        from agent import HandledException

        with pytest.raises(HandledException):
            raise HandledException("Handled error")


@pytest.mark.unit
@pytest.mark.agent
class TestAgentAsyncMethods:
    """Tests for Agent async methods."""

    @pytest.mark.asyncio
    async def test_agent_wait_if_paused(self, mock_agent):
        """Test wait_if_paused when not paused."""
        mock_agent.context.paused = False

        # Should return immediately
        await asyncio.wait_for(mock_agent.wait_if_paused(), timeout=1.0)

    @pytest.mark.asyncio
    async def test_agent_handle_intervention_no_intervention(self, mock_agent):
        """Test handle_intervention when no intervention."""
        mock_agent.intervention = None
        mock_agent.context.paused = False

        # Should not raise
        await mock_agent.handle_intervention()

    @pytest.mark.asyncio
    async def test_agent_handle_intervention_with_intervention(self, mock_agent, mock_user_message):
        """Test handle_intervention with intervention set."""
        from agent import InterventionException, LoopData

        mock_agent.intervention = mock_user_message
        mock_agent.context.paused = False
        mock_agent.loop_data = LoopData()

        with pytest.raises(InterventionException):
            await mock_agent.handle_intervention()

    @pytest.mark.asyncio
    async def test_agent_call_extensions(self, mock_agent):
        """Test calling extensions."""
        with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock) as mock_ext:
            mock_ext.return_value = None
            await mock_agent.call_extensions("test_extension")
            mock_ext.assert_called_once()


@pytest.mark.unit
@pytest.mark.agent
class TestAgentToolExecution:
    """Tests for Agent tool execution."""

    @pytest.mark.asyncio
    async def test_process_tools_with_valid_tool(self, mock_agent):
        """Test processing tools with valid tool request."""
        from agent import LoopData
        mock_agent.loop_data = LoopData()

        tool_msg = '{"tool_name": "response", "tool_args": {"text": "Hello"}}'

        with patch.object(mock_agent, "get_tool") as mock_get_tool:
            mock_tool = MagicMock()
            mock_tool.before_execution = AsyncMock()
            mock_tool.execute = AsyncMock(return_value=MagicMock(
                message="Done",
                break_loop=True
            ))
            mock_tool.after_execution = AsyncMock()
            mock_get_tool.return_value = mock_tool

            result = await mock_agent.process_tools(tool_msg)

            assert result == "Done"

    @pytest.mark.asyncio
    async def test_process_tools_invalid_format(self, mock_agent):
        """Test processing tools with invalid format."""
        from agent import LoopData
        mock_agent.loop_data = LoopData()

        invalid_msg = "This is not a valid tool request"

        result = await mock_agent.process_tools(invalid_msg)
        assert result is None

    def test_get_tool_from_default(self, mock_agent):
        """Test getting tool from default tools directory."""
        with patch("python.helpers.extract_tools.load_classes_from_file") as mock_load:
            mock_tool_class = MagicMock()
            mock_load.return_value = [mock_tool_class]

            tool = mock_agent.get_tool(
                name="response",
                method=None,
                args={},
                message="",
                loop_data=None,
            )

            assert tool is not None

    def test_get_tool_unknown_returns_unknown(self, mock_agent):
        """Test getting unknown tool returns Unknown class."""
        with patch("python.helpers.extract_tools.load_classes_from_file") as mock_load:
            mock_load.side_effect = Exception("Not found")

            tool = mock_agent.get_tool(
                name="nonexistent_tool",
                method=None,
                args={},
                message="",
                loop_data=None,
            )

            # Should return Unknown tool instance
            assert tool is not None


@pytest.mark.unit
@pytest.mark.agent
class TestAgentPrompts:
    """Tests for Agent prompt handling."""

    def test_read_prompt(self, mock_agent, mock_prompt_files):
        """Test reading prompt files."""
        with patch("python.helpers.files.get_abs_path") as mock_path:
            mock_path.return_value = str(mock_prompt_files)

            with patch("python.helpers.files.read_prompt_file") as mock_read:
                mock_read.return_value = "Test prompt content"

                prompt = mock_agent.read_prompt("test.md")
                assert prompt is not None

    def test_parse_prompt(self, mock_agent, mock_prompt_files):
        """Test parsing prompt files."""
        with patch("python.helpers.files.get_abs_path") as mock_path:
            mock_path.return_value = str(mock_prompt_files)

            with patch("python.helpers.files.parse_file") as mock_parse:
                mock_parse.return_value = "Parsed prompt"

                prompt = mock_agent.parse_prompt("test.md", var="value")
                assert prompt == "Parsed prompt"


@pytest.mark.unit
@pytest.mark.agent
class TestAgentModels:
    """Tests for Agent model getters."""

    def test_get_utility_model(self, mock_agent, mock_chat_model):
        """Test getting utility model."""
        with patch("models.get_chat_model", return_value=mock_chat_model):
            model = mock_agent.get_utility_model()
            assert model is not None

    def test_get_embedding_model(self, mock_agent, mock_embedding_model):
        """Test getting embedding model."""
        with patch("models.get_embedding_model", return_value=mock_embedding_model):
            model = mock_agent.get_embedding_model()
            assert model is not None

    def test_get_browser_model(self, mock_agent, mock_chat_model):
        """Test getting browser model."""
        with patch("models.get_browser_model", return_value=mock_chat_model):
            model = mock_agent.get_browser_model()
            assert model is not None
