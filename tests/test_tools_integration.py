"""
Integration tests for tools.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import os


# ============================================================================
# Response Tool Tests
# ============================================================================

class TestResponseTool:
    """Tests for the response tool."""

    @pytest.mark.asyncio
    async def test_response_tool_basic(self, mock_agent):
        """Test basic response tool functionality."""
        from python.tools.response import Response as ResponseTool
        from agent import LoopData

        loop_data = LoopData()

        tool = ResponseTool(
            agent=mock_agent,
            name="response",
            method=None,
            args={"message": "Hello, user!"},
            message="",
            loop_data=loop_data
        )

        result = await tool.execute(message="Hello, user!")

        assert result.break_loop is True
        assert result.message == "Hello, user!"

    @pytest.mark.asyncio
    async def test_response_tool_empty_message(self, mock_agent):
        """Test response tool with empty message."""
        from python.tools.response import Response as ResponseTool
        from agent import LoopData

        loop_data = LoopData()

        tool = ResponseTool(
            agent=mock_agent,
            name="response",
            method=None,
            args={"message": ""},
            message="",
            loop_data=loop_data
        )

        result = await tool.execute(message="")

        assert result.break_loop is True


# ============================================================================
# Memory Tools Tests
# ============================================================================

class TestMemoryTools:
    """Tests for memory-related tools."""

    @pytest.mark.asyncio
    async def test_memory_save_structure(self, mock_agent):
        """Test memory save tool structure."""
        from python.tools.memory_save import MemorySave
        from agent import LoopData

        loop_data = LoopData()

        tool = MemorySave(
            agent=mock_agent,
            name="memory_save",
            method=None,
            args={},
            message="",
            loop_data=loop_data
        )

        assert tool is not None
        assert hasattr(tool, 'execute')

    @pytest.mark.asyncio
    async def test_memory_load_structure(self, mock_agent):
        """Test memory load tool structure."""
        from python.tools.memory_load import MemoryLoad
        from agent import LoopData

        loop_data = LoopData()

        tool = MemoryLoad(
            agent=mock_agent,
            name="memory_load",
            method=None,
            args={},
            message="",
            loop_data=loop_data
        )

        assert tool is not None
        assert hasattr(tool, 'execute')


# ============================================================================
# Code Execution Tool Tests
# ============================================================================

class TestCodeExecutionTool:
    """Tests for code execution tool."""

    def test_code_execution_tool_exists(self):
        """Test code execution tool can be imported."""
        from python.tools.code_execution_tool import CodeExecution

        assert CodeExecution is not None

    @pytest.mark.asyncio
    async def test_code_execution_structure(self, mock_agent):
        """Test code execution tool structure."""
        from python.tools.code_execution_tool import CodeExecution
        from agent import LoopData

        loop_data = LoopData()

        tool = CodeExecution(
            agent=mock_agent,
            name="code_execution",
            method=None,
            args={},
            message="",
            loop_data=loop_data
        )

        assert hasattr(tool, 'execute')


# ============================================================================
# Search Tool Tests
# ============================================================================

class TestSearchTool:
    """Tests for search engine tool."""

    def test_search_tool_exists(self):
        """Test search tool can be imported."""
        from python.tools.search_engine import SearchEngine

        assert SearchEngine is not None

    @pytest.mark.asyncio
    async def test_search_tool_structure(self, mock_agent):
        """Test search tool structure."""
        from python.tools.search_engine import SearchEngine
        from agent import LoopData

        loop_data = LoopData()

        tool = SearchEngine(
            agent=mock_agent,
            name="search_engine",
            method=None,
            args={},
            message="",
            loop_data=loop_data
        )

        assert hasattr(tool, 'execute')


# ============================================================================
# Browser Agent Tool Tests
# ============================================================================

class TestBrowserAgentTool:
    """Tests for browser agent tool."""

    def test_browser_agent_exists(self):
        """Test browser agent tool can be imported."""
        from python.tools.browser_agent import BrowserAgent

        assert BrowserAgent is not None


# ============================================================================
# Call Subordinate Tool Tests
# ============================================================================

class TestCallSubordinateTool:
    """Tests for call subordinate tool."""

    def test_call_subordinate_exists(self):
        """Test call subordinate tool can be imported."""
        from python.tools.call_subordinate import CallSubordinate

        assert CallSubordinate is not None

    @pytest.mark.asyncio
    async def test_call_subordinate_structure(self, mock_agent):
        """Test call subordinate tool structure."""
        from python.tools.call_subordinate import CallSubordinate
        from agent import LoopData

        loop_data = LoopData()

        tool = CallSubordinate(
            agent=mock_agent,
            name="call_subordinate",
            method=None,
            args={},
            message="",
            loop_data=loop_data
        )

        assert hasattr(tool, 'execute')


# ============================================================================
# Unknown Tool Tests
# ============================================================================

class TestUnknownTool:
    """Tests for unknown/fallback tool."""

    def test_unknown_tool_exists(self):
        """Test unknown tool can be imported."""
        from python.tools.unknown import Unknown

        assert Unknown is not None

    @pytest.mark.asyncio
    async def test_unknown_tool_execution(self, mock_agent):
        """Test unknown tool execution."""
        from python.tools.unknown import Unknown
        from agent import LoopData

        loop_data = LoopData()

        tool = Unknown(
            agent=mock_agent,
            name="nonexistent_tool",
            method=None,
            args={},
            message="",
            loop_data=loop_data
        )

        result = await tool.execute()

        # Unknown tool should return an error message
        assert result.break_loop is False


# ============================================================================
# Input Tool Tests
# ============================================================================

class TestInputTool:
    """Tests for input tool."""

    def test_input_tool_exists(self):
        """Test input tool can be imported."""
        from python.tools.input import Input

        assert Input is not None


# ============================================================================
# Notify User Tool Tests
# ============================================================================

class TestNotifyUserTool:
    """Tests for notify user tool."""

    def test_notify_user_exists(self):
        """Test notify user tool can be imported."""
        from python.tools.notify_user import NotifyUser

        assert NotifyUser is not None

    @pytest.mark.asyncio
    async def test_notify_user_structure(self, mock_agent):
        """Test notify user tool structure."""
        from python.tools.notify_user import NotifyUser
        from agent import LoopData

        loop_data = LoopData()

        tool = NotifyUser(
            agent=mock_agent,
            name="notify_user",
            method=None,
            args={},
            message="",
            loop_data=loop_data
        )

        assert hasattr(tool, 'execute')


# ============================================================================
# Scheduler Tool Tests
# ============================================================================

class TestSchedulerTool:
    """Tests for scheduler tool."""

    def test_scheduler_tool_exists(self):
        """Test scheduler tool can be imported."""
        from python.tools.scheduler import Scheduler

        assert Scheduler is not None


# ============================================================================
# Document Query Tool Tests
# ============================================================================

class TestDocumentQueryTool:
    """Tests for document query tool."""

    def test_document_query_exists(self):
        """Test document query tool can be imported."""
        from python.tools.document_query import DocumentQuery

        assert DocumentQuery is not None


# ============================================================================
# Vision Tool Tests
# ============================================================================

class TestVisionTool:
    """Tests for vision load tool."""

    def test_vision_load_exists(self):
        """Test vision load tool can be imported."""
        from python.tools.vision_load import VisionLoad

        assert VisionLoad is not None


# ============================================================================
# Behaviour Adjustment Tool Tests
# ============================================================================

class TestBehaviourAdjustmentTool:
    """Tests for behaviour adjustment tool."""

    def test_behaviour_adjustment_exists(self):
        """Test behaviour adjustment tool can be imported."""
        from python.tools.behaviour_adjustment import BehaviourAdjustment

        assert BehaviourAdjustment is not None


# ============================================================================
# A2A Chat Tool Tests
# ============================================================================

class TestA2AChatTool:
    """Tests for A2A chat tool."""

    def test_a2a_chat_exists(self):
        """Test A2A chat tool can be imported."""
        from python.tools.a2a_chat import A2AChat

        assert A2AChat is not None


# ============================================================================
# OpenCog Tools Tests
# ============================================================================

class TestOpenCogTools:
    """Tests for OpenCog integration tools."""

    def test_opencog_atomspace_exists(self):
        """Test OpenCog atomspace tool can be imported."""
        from python.tools.opencog_atomspace import OpenCogAtomSpace

        assert OpenCogAtomSpace is not None

    def test_opencog_reasoning_exists(self):
        """Test OpenCog reasoning tool can be imported."""
        from python.tools.opencog_reasoning import OpenCogReasoning

        assert OpenCogReasoning is not None

    def test_opencog_knowledge_exists(self):
        """Test OpenCog knowledge tool can be imported."""
        from python.tools.opencog_knowledge import OpenCogKnowledge

        assert OpenCogKnowledge is not None


# ============================================================================
# Tool Base Class Tests
# ============================================================================

class TestToolBase:
    """Tests for Tool base class functionality."""

    def test_tool_response_structure(self):
        """Test Response class structure."""
        from python.helpers.tool import Response

        response = Response(message="Test", break_loop=False)

        assert response.message == "Test"
        assert response.break_loop is False

    def test_tool_response_break_loop(self):
        """Test Response with break_loop=True."""
        from python.helpers.tool import Response

        response = Response(message="Final", break_loop=True)

        assert response.break_loop is True


# ============================================================================
# Tool Discovery Tests
# ============================================================================

class TestToolDiscovery:
    """Tests for tool discovery and loading."""

    def test_extract_tools_function(self):
        """Test extract_tools helper."""
        from python.helpers import extract_tools

        assert hasattr(extract_tools, 'load_classes_from_file')
        assert hasattr(extract_tools, 'json_parse_dirty')

    def test_json_parse_dirty_valid_tool(self):
        """Test parsing valid tool JSON."""
        from python.helpers.extract_tools import json_parse_dirty
        import json

        tool_json = json.dumps({
            "tool_name": "response",
            "tool_args": {"message": "Hello"}
        })

        result = json_parse_dirty(f"Some text before {tool_json} and after")

        assert result is not None
        assert result.get("tool_name") == "response"

    def test_json_parse_dirty_invalid(self):
        """Test parsing invalid/no tool JSON."""
        from python.helpers.extract_tools import json_parse_dirty

        result = json_parse_dirty("Just plain text with no JSON")

        # Should return None or empty when no valid tool JSON found


# ============================================================================
# Tool Execution Hooks Tests
# ============================================================================

class TestToolExecutionHooks:
    """Tests for tool execution hooks."""

    @pytest.mark.asyncio
    async def test_before_execution_hook(self, mock_agent):
        """Test before_execution hook is called."""
        from python.tools.response import Response as ResponseTool
        from agent import LoopData

        loop_data = LoopData()

        tool = ResponseTool(
            agent=mock_agent,
            name="response",
            method=None,
            args={"message": "test"},
            message="",
            loop_data=loop_data
        )

        # before_execution should not raise
        await tool.before_execution(message="test")

    @pytest.mark.asyncio
    async def test_after_execution_hook(self, mock_agent):
        """Test after_execution hook is called."""
        from python.tools.response import Response as ResponseTool
        from python.helpers.tool import Response
        from agent import LoopData

        loop_data = LoopData()

        tool = ResponseTool(
            agent=mock_agent,
            name="response",
            method=None,
            args={"message": "test"},
            message="",
            loop_data=loop_data
        )

        response = Response(message="test", break_loop=True)

        # after_execution should not raise
        await tool.after_execution(response)
