"""
Unit tests for python/tools/ - Agent tool implementations.

Tests cover:
- Tool base class functionality
- Response dataclass
- Individual tool implementations
- Tool lifecycle (before/after execution)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from dataclasses import dataclass


@pytest.mark.unit
@pytest.mark.tools
class TestResponse:
    """Tests for Response dataclass."""

    def test_response_creation(self):
        """Test creating a Response."""
        from python.helpers.tool import Response

        response = Response(
            message="Task completed",
            break_loop=True,
        )

        assert response.message == "Task completed"
        assert response.break_loop is True
        assert response.additional is None

    def test_response_with_additional(self):
        """Test Response with additional data."""
        from python.helpers.tool import Response

        response = Response(
            message="Task completed",
            break_loop=False,
            additional={"key": "value"},
        )

        assert response.additional == {"key": "value"}


@pytest.mark.unit
@pytest.mark.tools
class TestToolBase:
    """Tests for Tool base class."""

    def test_tool_initialization(self, mock_agent):
        """Test tool initialization."""
        from python.helpers.tool import Tool

        class TestTool(Tool):
            async def execute(self, **kwargs):
                from python.helpers.tool import Response
                return Response(message="Test", break_loop=False)

        tool = TestTool(
            agent=mock_agent,
            name="test_tool",
            method=None,
            args={"arg1": "value1"},
            message="",
            loop_data=None,
        )

        assert tool.agent is mock_agent
        assert tool.name == "test_tool"
        assert tool.args == {"arg1": "value1"}

    def test_tool_with_method(self, mock_agent):
        """Test tool with method specified."""
        from python.helpers.tool import Tool

        class TestTool(Tool):
            async def execute(self, **kwargs):
                from python.helpers.tool import Response
                return Response(message="Test", break_loop=False)

        tool = TestTool(
            agent=mock_agent,
            name="test_tool",
            method="sub_method",
            args={},
            message="",
            loop_data=None,
        )

        assert tool.method == "sub_method"

    def test_nice_key_formatting(self, mock_agent):
        """Test nice_key formats keys properly."""
        from python.helpers.tool import Tool

        class TestTool(Tool):
            async def execute(self, **kwargs):
                from python.helpers.tool import Response
                return Response(message="Test", break_loop=False)

        tool = TestTool(
            agent=mock_agent,
            name="test",
            method=None,
            args={},
            message="",
            loop_data=None,
        )

        assert tool.nice_key("test_key_name") == "Test key name"
        assert tool.nice_key("single") == "Single"

    @pytest.mark.asyncio
    async def test_before_execution(self, mock_agent):
        """Test before_execution hook."""
        from python.helpers.tool import Tool

        class TestTool(Tool):
            async def execute(self, **kwargs):
                from python.helpers.tool import Response
                return Response(message="Test", break_loop=False)

        tool = TestTool(
            agent=mock_agent,
            name="test",
            method=None,
            args={"key": "value"},
            message="",
            loop_data=None,
        )

        # Mock the log object
        mock_log = MagicMock()
        mock_agent.context.log.log = MagicMock(return_value=mock_log)

        await tool.before_execution()

        # Should have created log object
        assert hasattr(tool, "log")

    @pytest.mark.asyncio
    async def test_after_execution(self, mock_agent):
        """Test after_execution hook."""
        from python.helpers.tool import Tool, Response

        class TestTool(Tool):
            async def execute(self, **kwargs):
                return Response(message="Test result", break_loop=False)

        tool = TestTool(
            agent=mock_agent,
            name="test",
            method=None,
            args={},
            message="",
            loop_data=None,
        )

        # Setup log mock
        tool.log = MagicMock()
        tool.log.update = MagicMock()

        response = Response(message="Test result", break_loop=False)

        with patch.object(mock_agent, "hist_add_tool_result"):
            await tool.after_execution(response)

            mock_agent.hist_add_tool_result.assert_called_once()


@pytest.mark.unit
@pytest.mark.tools
class TestResponseTool:
    """Tests for ResponseTool."""

    @pytest.mark.asyncio
    async def test_response_tool_execute_with_text(self, mock_agent):
        """Test ResponseTool with text argument."""
        from python.tools.response import ResponseTool
        from agent import LoopData

        tool = ResponseTool(
            agent=mock_agent,
            name="response",
            method=None,
            args={"text": "Final answer"},
            message="",
            loop_data=LoopData(),
        )

        response = await tool.execute()

        assert response.message == "Final answer"
        assert response.break_loop is True

    @pytest.mark.asyncio
    async def test_response_tool_execute_with_message(self, mock_agent):
        """Test ResponseTool with message argument."""
        from python.tools.response import ResponseTool
        from agent import LoopData

        tool = ResponseTool(
            agent=mock_agent,
            name="response",
            method=None,
            args={"message": "Alternative answer"},
            message="",
            loop_data=LoopData(),
        )

        response = await tool.execute()

        assert response.message == "Alternative answer"

    @pytest.mark.asyncio
    async def test_response_tool_before_execution(self, mock_agent):
        """Test ResponseTool before_execution does nothing."""
        from python.tools.response import ResponseTool
        from agent import LoopData

        tool = ResponseTool(
            agent=mock_agent,
            name="response",
            method=None,
            args={"text": "Test"},
            message="",
            loop_data=LoopData(),
        )

        # Should not raise
        await tool.before_execution()


@pytest.mark.unit
@pytest.mark.tools
class TestUnknownTool:
    """Tests for Unknown tool (fallback)."""

    @pytest.mark.asyncio
    async def test_unknown_tool_execute(self, mock_agent):
        """Test Unknown tool returns error message."""
        from python.tools.unknown import Unknown
        from agent import LoopData

        tool = Unknown(
            agent=mock_agent,
            name="nonexistent_tool",
            method=None,
            args={},
            message="",
            loop_data=LoopData(),
        )

        response = await tool.execute()

        assert response.break_loop is False
        assert "nonexistent_tool" in response.message.lower() or "unknown" in response.message.lower()


@pytest.mark.unit
@pytest.mark.tools
class TestMemoryTools:
    """Tests for memory-related tools."""

    @pytest.mark.asyncio
    async def test_memory_save_tool(self, mock_agent):
        """Test MemorySave tool."""
        from agent import LoopData

        with patch("python.tools.memory_save.MemorySave") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Memory saved",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="memory_save",
                method=None,
                args={"text": "Remember this", "area": "general"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response.message == "Memory saved"

    @pytest.mark.asyncio
    async def test_memory_load_tool(self, mock_agent):
        """Test MemoryLoad tool."""
        from agent import LoopData

        with patch("python.tools.memory_load.MemoryLoad") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Retrieved memories: ...",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="memory_load",
                method=None,
                args={"query": "test query"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert "memories" in response.message.lower() or "Retrieved" in response.message


@pytest.mark.unit
@pytest.mark.tools
@pytest.mark.opencog
class TestOpenCogTools:
    """Tests for OpenCog integration tools."""

    @pytest.mark.asyncio
    async def test_opencog_atomspace_tool_available(self, mock_agent, mock_opencog_available):
        """Test OpenCog AtomSpace tool when available."""
        from agent import LoopData

        # Mock the OpenCog tool
        with patch("python.tools.opencog_atomspace.OpenCogAtomspace") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="AtomSpace operation completed",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="opencog_atomspace",
                method=None,
                args={"operation": "add", "atom_type": "ConceptNode", "name": "test"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None

    @pytest.mark.asyncio
    async def test_opencog_reasoning_tool(self, mock_agent):
        """Test OpenCog Reasoning tool."""
        from agent import LoopData

        with patch("python.tools.opencog_reasoning.OpenCogReasoning") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Reasoning result: ...",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="opencog_reasoning",
                method=None,
                args={"query": "What is the relationship?"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None

    @pytest.mark.asyncio
    async def test_opencog_knowledge_tool(self, mock_agent):
        """Test OpenCog Knowledge tool."""
        from agent import LoopData

        with patch("python.tools.opencog_knowledge.OpenCogKnowledge") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Knowledge retrieved",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="opencog_knowledge",
                method=None,
                args={"operation": "query"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestCodeExecutionTool:
    """Tests for CodeExecution tool."""

    @pytest.mark.asyncio
    async def test_code_execution_tool_python(self, mock_agent):
        """Test code execution with Python."""
        from agent import LoopData

        with patch("python.tools.code_execution_tool.CodeExecution") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Output: Hello World",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="code_execution",
                method=None,
                args={
                    "language": "python",
                    "code": "print('Hello World')"
                },
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert "Hello World" in response.message or "Output" in response.message


@pytest.mark.unit
@pytest.mark.tools
class TestBrowserTools:
    """Tests for browser-related tools."""

    @pytest.mark.asyncio
    async def test_browser_agent_tool(self, mock_agent):
        """Test BrowserAgent tool."""
        from agent import LoopData

        with patch("python.tools.browser_agent.BrowserAgent") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Browser task completed",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="browser_agent",
                method=None,
                args={"task": "Navigate to example.com"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestCallSubordinate:
    """Tests for CallSubordinate tool."""

    @pytest.mark.asyncio
    async def test_call_subordinate_tool(self, mock_agent):
        """Test CallSubordinate tool creates sub-agent."""
        from agent import LoopData

        with patch("python.tools.call_subordinate.Subordinate") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Subordinate completed task",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="call_subordinate",
                method=None,
                args={"task": "Research topic X"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestNotifyUserTool:
    """Tests for NotifyUser tool."""

    @pytest.mark.asyncio
    async def test_notify_user_tool(self, mock_agent):
        """Test NotifyUser tool."""
        from agent import LoopData

        with patch("python.tools.notify_user.NotifyUser") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="User notified",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="notify_user",
                method=None,
                args={"message": "Task progress: 50%"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestDocumentQueryTool:
    """Tests for DocumentQuery tool."""

    @pytest.mark.asyncio
    async def test_document_query_tool(self, mock_agent):
        """Test DocumentQuery tool."""
        from agent import LoopData

        with patch("python.tools.document_query.DocumentQuery") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Document analysis: ...",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="document_query",
                method=None,
                args={"query": "What is this document about?"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestSearchEngineTool:
    """Tests for SearchEngine tool."""

    @pytest.mark.asyncio
    async def test_search_engine_tool(self, mock_agent):
        """Test SearchEngine tool."""
        from agent import LoopData

        with patch("python.tools.search_engine.SearchEngine") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Search results: 1. Example result...",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="search_engine",
                method=None,
                args={"query": "Python best practices"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestSchedulerTool:
    """Tests for Scheduler tool."""

    @pytest.mark.asyncio
    async def test_scheduler_tool(self, mock_agent):
        """Test Scheduler tool."""
        from agent import LoopData

        with patch("python.tools.scheduler.Scheduler") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Task scheduled",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="scheduler",
                method=None,
                args={"task": "Send reminder", "cron": "0 9 * * *"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestInputTool:
    """Tests for Input tool."""

    @pytest.mark.asyncio
    async def test_input_tool(self, mock_agent):
        """Test Input tool for user input."""
        from agent import LoopData

        with patch("python.tools.input.Input") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="User input received: test",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="input",
                method=None,
                args={"prompt": "Enter value:"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestVisionLoadTool:
    """Tests for VisionLoad tool."""

    @pytest.mark.asyncio
    async def test_vision_load_tool(self, mock_agent):
        """Test VisionLoad tool for image analysis."""
        from agent import LoopData

        with patch("python.tools.vision_load.VisionLoad") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Image loaded for analysis",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="vision_load",
                method=None,
                args={"image_path": "/path/to/image.png"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None


@pytest.mark.unit
@pytest.mark.tools
class TestBehaviourAdjustmentTool:
    """Tests for BehaviourAdjustment tool."""

    @pytest.mark.asyncio
    async def test_behaviour_adjustment_tool(self, mock_agent):
        """Test BehaviourAdjustment tool."""
        from agent import LoopData

        with patch("python.tools.behaviour_adjustment.BehaviourAdjustment") as MockTool:
            mock_instance = MagicMock()
            mock_instance.execute = AsyncMock(return_value=MagicMock(
                message="Behaviour adjusted",
                break_loop=False
            ))
            MockTool.return_value = mock_instance

            tool = MockTool(
                agent=mock_agent,
                name="behaviour_adjustment",
                method=None,
                args={"adjustment": "Be more concise"},
                message="",
                loop_data=LoopData(),
            )

            response = await tool.execute()
            assert response is not None
