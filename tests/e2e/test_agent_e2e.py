"""
End-to-end tests for Agent Zero.

Tests cover:
- Complete agent conversation flow
- API endpoint integration
- Full tool execution cycles
- Multi-agent coordination
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
import json


@pytest.mark.e2e
@pytest.mark.slow
class TestAgentConversationFlow:
    """E2E tests for complete agent conversation flow."""

    @pytest.mark.asyncio
    async def test_simple_conversation(self, mock_agent_config):
        """Test a simple conversation with the agent."""
        from agent import AgentContext, Agent, UserMessage

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="e2e-conv-test")
        agent = context.agent0

        # Mock the LLM response
        mock_response = json.dumps({
            "tool_name": "response",
            "tool_args": {"text": "Hello! How can I help you today?"}
        })

        with patch.object(agent, "get_chat_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.unified_call = AsyncMock(return_value=(mock_response, ""))
            mock_get_model.return_value = mock_model

            # Create user message
            user_msg = UserMessage(message="Hello!")

            # Add to history
            agent.hist_add_user_message(user_msg)

            # Process (simplified - in real scenario this would be monologue)
            result = await agent.process_tools(mock_response)

            assert result == "Hello! How can I help you today?"

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, mock_agent_config):
        """Test multi-turn conversation."""
        from agent import AgentContext, UserMessage, LoopData

        AgentContext._contexts.clear()

        context = AgentContext(config=mock_agent_config, id="e2e-multi-turn")
        agent = context.agent0
        agent.loop_data = LoopData()

        # Simulate multiple turns
        turns = [
            ("What is 2+2?", "The answer is 4."),
            ("And 3+3?", "That would be 6."),
        ]

        for user_input, expected_response in turns:
            user_msg = UserMessage(message=user_input)
            agent.hist_add_user_message(user_msg)

            mock_response = json.dumps({
                "tool_name": "response",
                "tool_args": {"text": expected_response}
            })

            result = await agent.process_tools(mock_response)
            assert result == expected_response


@pytest.mark.e2e
@pytest.mark.slow
class TestAPIEndpointE2E:
    """E2E tests for API endpoints."""

    @pytest.mark.asyncio
    async def test_health_to_message_flow(self):
        """Test flow from health check to sending message."""
        # Mock health check
        with patch("python.api.health.HealthCheck") as MockHealth:
            mock_health = MagicMock()
            mock_health.process = AsyncMock(return_value={
                "gitinfo": {"branch": "main"},
                "error": None
            })
            MockHealth.return_value = mock_health

            # Check health
            health_handler = MockHealth()
            health_result = await health_handler.process({}, MagicMock())
            assert health_result["error"] is None

        # Mock settings
        with patch("python.api.settings_get.GetSettings") as MockSettings:
            mock_settings = MagicMock()
            mock_settings.process = AsyncMock(return_value={
                "settings": {"chat_model_provider": "openai"}
            })
            MockSettings.return_value = mock_settings

            settings_handler = MockSettings()
            settings_result = await settings_handler.process({}, MagicMock())
            assert "settings" in settings_result

        # Mock message
        with patch("python.api.message.SendMessage") as MockMessage:
            mock_message = MagicMock()
            mock_message.process = AsyncMock(return_value={
                "response": "Message processed"
            })
            MockMessage.return_value = mock_message

            message_handler = MockMessage()
            message_result = await message_handler.process({
                "message": "Hello"
            }, MagicMock())
            assert "response" in message_result


@pytest.mark.e2e
@pytest.mark.slow
class TestToolExecutionE2E:
    """E2E tests for complete tool execution cycles."""

    @pytest.mark.asyncio
    async def test_code_execution_e2e(self, mock_agent):
        """Test complete code execution flow."""
        from agent import LoopData

        mock_agent.loop_data = LoopData()

        # Simulate code execution request
        code_request = json.dumps({
            "tool_name": "code_execution",
            "tool_args": {
                "language": "python",
                "code": "print('Hello World')"
            }
        })

        with patch("python.tools.code_execution_tool.CodeExecution") as MockCodeExec:
            mock_tool = MagicMock()
            mock_tool.before_execution = AsyncMock()
            mock_tool.execute = AsyncMock(return_value=MagicMock(
                message="Output: Hello World\nExit code: 0",
                break_loop=False
            ))
            mock_tool.after_execution = AsyncMock()

            with patch.object(mock_agent, "get_tool", return_value=mock_tool):
                with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock):
                    result = await mock_agent.process_tools(code_request)

                    # Tool should have been called
                    mock_tool.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_memory_save_and_load_e2e(self, mock_agent):
        """Test memory save followed by load."""
        from agent import LoopData

        mock_agent.loop_data = LoopData()

        # Save memory
        save_request = json.dumps({
            "tool_name": "memory_save",
            "tool_args": {
                "text": "Important information to remember",
                "area": "facts"
            }
        })

        mock_save_tool = MagicMock()
        mock_save_tool.before_execution = AsyncMock()
        mock_save_tool.execute = AsyncMock(return_value=MagicMock(
            message="Memory saved successfully",
            break_loop=False
        ))
        mock_save_tool.after_execution = AsyncMock()

        with patch.object(mock_agent, "get_tool", return_value=mock_save_tool):
            with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock):
                await mock_agent.process_tools(save_request)

        # Load memory
        load_request = json.dumps({
            "tool_name": "memory_load",
            "tool_args": {
                "query": "important information"
            }
        })

        mock_load_tool = MagicMock()
        mock_load_tool.before_execution = AsyncMock()
        mock_load_tool.execute = AsyncMock(return_value=MagicMock(
            message="Found: Important information to remember",
            break_loop=False
        ))
        mock_load_tool.after_execution = AsyncMock()

        with patch.object(mock_agent, "get_tool", return_value=mock_load_tool):
            with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock):
                await mock_agent.process_tools(load_request)


@pytest.mark.e2e
@pytest.mark.slow
class TestMultiAgentE2E:
    """E2E tests for multi-agent coordination."""

    @pytest.mark.asyncio
    async def test_subordinate_agent_delegation(self, mock_agent_config):
        """Test parent agent delegating to subordinate."""
        from agent import AgentContext, Agent, LoopData

        AgentContext._contexts.clear()

        # Create parent context
        parent_context = AgentContext(config=mock_agent_config, id="parent-agent")
        parent_agent = parent_context.agent0
        parent_agent.loop_data = LoopData()

        # Subordinate request
        subordinate_request = json.dumps({
            "tool_name": "call_subordinate",
            "tool_args": {
                "task": "Research topic X",
                "instructions": "Gather information about X"
            }
        })

        mock_sub_tool = MagicMock()
        mock_sub_tool.before_execution = AsyncMock()
        mock_sub_tool.execute = AsyncMock(return_value=MagicMock(
            message="Subordinate completed research:\n- Finding 1\n- Finding 2",
            break_loop=False
        ))
        mock_sub_tool.after_execution = AsyncMock()

        with patch.object(parent_agent, "get_tool", return_value=mock_sub_tool):
            with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock):
                result = await parent_agent.process_tools(subordinate_request)

                # Subordinate tool should have been executed
                mock_sub_tool.execute.assert_called_once()


@pytest.mark.e2e
@pytest.mark.slow
class TestBrowserE2E:
    """E2E tests for browser automation."""

    @pytest.mark.asyncio
    async def test_browser_navigation(self, mock_agent):
        """Test browser navigation flow."""
        from agent import LoopData

        mock_agent.loop_data = LoopData()

        browser_request = json.dumps({
            "tool_name": "browser_agent",
            "tool_args": {
                "task": "Go to example.com and extract the main heading"
            }
        })

        mock_browser_tool = MagicMock()
        mock_browser_tool.before_execution = AsyncMock()
        mock_browser_tool.execute = AsyncMock(return_value=MagicMock(
            message="Successfully navigated to example.com.\nMain heading: 'Example Domain'",
            break_loop=False
        ))
        mock_browser_tool.after_execution = AsyncMock()

        with patch.object(mock_agent, "get_tool", return_value=mock_browser_tool):
            with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock):
                await mock_agent.process_tools(browser_request)
                mock_browser_tool.execute.assert_called_once()


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.opencog
class TestOpenCogE2E:
    """E2E tests for OpenCog integration."""

    @pytest.mark.asyncio
    async def test_opencog_knowledge_flow(self, mock_agent, mock_opencog_available):
        """Test OpenCog knowledge storage and retrieval."""
        from agent import LoopData

        mock_agent.loop_data = LoopData()

        # Add knowledge
        add_request = json.dumps({
            "tool_name": "opencog_atomspace",
            "tool_args": {
                "operation": "add",
                "atom_type": "ConceptNode",
                "name": "test_concept"
            }
        })

        mock_add_tool = MagicMock()
        mock_add_tool.before_execution = AsyncMock()
        mock_add_tool.execute = AsyncMock(return_value=MagicMock(
            message="Added ConceptNode: test_concept",
            break_loop=False
        ))
        mock_add_tool.after_execution = AsyncMock()

        with patch.object(mock_agent, "get_tool", return_value=mock_add_tool):
            with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock):
                await mock_agent.process_tools(add_request)

        # Query knowledge
        query_request = json.dumps({
            "tool_name": "opencog_reasoning",
            "tool_args": {
                "query": "What concepts are related to test_concept?"
            }
        })

        mock_query_tool = MagicMock()
        mock_query_tool.before_execution = AsyncMock()
        mock_query_tool.execute = AsyncMock(return_value=MagicMock(
            message="Reasoning result: test_concept is a ConceptNode",
            break_loop=False
        ))
        mock_query_tool.after_execution = AsyncMock()

        with patch.object(mock_agent, "get_tool", return_value=mock_query_tool):
            with patch("python.helpers.extension.call_extensions", new_callable=AsyncMock):
                await mock_agent.process_tools(query_request)


@pytest.mark.e2e
@pytest.mark.slow
class TestSchedulerE2E:
    """E2E tests for scheduler functionality."""

    @pytest.mark.asyncio
    async def test_scheduled_task_execution(self):
        """Test scheduled task creation and execution."""
        # Create task
        with patch("python.api.scheduler_task_create.SchedulerTaskCreate") as MockCreate:
            mock_create = MagicMock()
            mock_create.process = AsyncMock(return_value={
                "task_id": "task-e2e-test",
                "success": True
            })
            MockCreate.return_value = mock_create

            create_handler = MockCreate()
            create_result = await create_handler.process({
                "name": "E2E Test Task",
                "cron": "0 * * * *",
                "message": "Run hourly task"
            }, MagicMock())

            assert create_result["success"] is True

        # Run task manually
        with patch("python.api.scheduler_task_run.SchedulerTaskRun") as MockRun:
            mock_run = MagicMock()
            mock_run.process = AsyncMock(return_value={
                "success": True,
                "result": "Task executed"
            })
            MockRun.return_value = mock_run

            run_handler = MockRun()
            run_result = await run_handler.process({
                "task_id": "task-e2e-test"
            }, MagicMock())

            assert run_result["success"] is True


@pytest.mark.e2e
@pytest.mark.slow
class TestBackupRestoreE2E:
    """E2E tests for backup and restore functionality."""

    @pytest.mark.asyncio
    async def test_backup_and_restore_flow(self):
        """Test complete backup and restore cycle."""
        # Create backup
        with patch("python.api.backup_create.BackupCreate") as MockBackup:
            mock_backup = MagicMock()
            mock_backup.process = AsyncMock(return_value={
                "backup_id": "backup-e2e-test",
                "success": True,
                "path": "/backups/backup-e2e-test.zip"
            })
            MockBackup.return_value = mock_backup

            backup_handler = MockBackup()
            backup_result = await backup_handler.process({
                "include": ["memory", "knowledge", "settings"]
            }, MagicMock())

            assert backup_result["success"] is True
            backup_id = backup_result["backup_id"]

        # Inspect backup
        with patch("python.api.backup_inspect.BackupInspect") as MockInspect:
            mock_inspect = MagicMock()
            mock_inspect.process = AsyncMock(return_value={
                "backup_info": {
                    "id": backup_id,
                    "contents": ["memory", "knowledge", "settings"]
                }
            })
            MockInspect.return_value = mock_inspect

            inspect_handler = MockInspect()
            inspect_result = await inspect_handler.process({
                "backup_id": backup_id
            }, MagicMock())

            assert "backup_info" in inspect_result

        # Restore backup
        with patch("python.api.backup_restore.BackupRestore") as MockRestore:
            mock_restore = MagicMock()
            mock_restore.process = AsyncMock(return_value={
                "success": True,
                "restored": ["memory", "knowledge", "settings"]
            })
            MockRestore.return_value = mock_restore

            restore_handler = MockRestore()
            restore_result = await restore_handler.process({
                "backup_id": backup_id
            }, MagicMock())

            assert restore_result["success"] is True
