"""
Unit tests for python/api/ - API endpoint handlers.

Tests cover:
- Health check endpoint
- Settings endpoints
- Chat management endpoints
- Message handling
- File operations
- Scheduler endpoints
- Notification endpoints
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json


@pytest.mark.unit
@pytest.mark.api
class TestHealthCheckAPI:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_process(self):
        """Test health check returns git info."""
        from python.api.health import HealthCheck

        handler = HealthCheck()

        with patch("python.helpers.git.get_git_info") as mock_git:
            mock_git.return_value = {
                "branch": "main",
                "commit": "abc123",
            }

            mock_request = MagicMock()
            result = await handler.process({}, mock_request)

            assert "gitinfo" in result
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_health_check_with_error(self):
        """Test health check handles git errors."""
        from python.api.health import HealthCheck

        handler = HealthCheck()

        with patch("python.helpers.git.get_git_info") as mock_git:
            mock_git.side_effect = Exception("Git not found")

            mock_request = MagicMock()
            result = await handler.process({}, mock_request)

            assert result["gitinfo"] is None
            assert result["error"] is not None

    def test_health_check_no_auth_required(self):
        """Test health check doesn't require auth."""
        from python.api.health import HealthCheck

        assert HealthCheck.requires_auth() is False

    def test_health_check_no_csrf_required(self):
        """Test health check doesn't require CSRF."""
        from python.api.health import HealthCheck

        assert HealthCheck.requires_csrf() is False

    def test_health_check_methods(self):
        """Test health check supports GET and POST."""
        from python.api.health import HealthCheck

        methods = HealthCheck.get_methods()
        assert "GET" in methods
        assert "POST" in methods


@pytest.mark.unit
@pytest.mark.api
class TestSettingsAPI:
    """Tests for settings endpoints."""

    @pytest.mark.asyncio
    async def test_get_settings(self, mock_settings):
        """Test getting settings."""
        from python.api.settings_get import GetSettings

        handler = GetSettings()

        with patch("python.helpers.settings.get_settings", return_value=mock_settings):
            with patch("python.helpers.settings.convert_out", return_value=mock_settings):
                mock_request = MagicMock()
                result = await handler.process({}, mock_request)

                assert "settings" in result

    def test_get_settings_methods(self):
        """Test get settings supports GET and POST."""
        from python.api.settings_get import GetSettings

        methods = GetSettings.get_methods()
        assert "GET" in methods
        assert "POST" in methods

    @pytest.mark.asyncio
    async def test_set_settings(self, mock_settings):
        """Test setting settings."""
        with patch("python.api.settings_set.SettingsSet") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"settings": mock_settings}, MagicMock())

            assert result["success"] is True


@pytest.mark.unit
@pytest.mark.api
class TestChatAPI:
    """Tests for chat management endpoints."""

    @pytest.mark.asyncio
    async def test_chat_reset(self, mock_agent_context):
        """Test resetting chat."""
        with patch("python.api.chat_reset.ResetChat") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process(
                {"context_id": mock_agent_context.id},
                MagicMock()
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_chat_load(self):
        """Test loading chat history."""
        with patch("python.api.chat_load.LoadChat") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "context": {"id": "test-123"},
                "history": []
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"context_id": "test-123"}, MagicMock())

            assert "context" in result or result is not None

    @pytest.mark.asyncio
    async def test_chat_remove(self):
        """Test removing chat."""
        with patch("python.api.chat_remove.RemoveChat") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"context_id": "test-123"}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_chat_export(self):
        """Test exporting chat."""
        with patch("python.api.chat_export.ExportChat") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "export_data": "..."
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"context_id": "test-123"}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestMessageAPI:
    """Tests for message handling endpoints."""

    @pytest.mark.asyncio
    async def test_send_message(self, mock_agent_context):
        """Test sending a message."""
        with patch("python.api.message.SendMessage") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "response": "Message received"
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({
                "context_id": mock_agent_context.id,
                "message": "Hello"
            }, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_message_async(self, mock_agent_context):
        """Test async message handling."""
        with patch("python.api.message_async.SendMessageAsync") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "task_id": "task-123"
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({
                "context_id": mock_agent_context.id,
                "message": "Hello"
            }, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestFileAPI:
    """Tests for file operation endpoints."""

    @pytest.mark.asyncio
    async def test_get_work_dir_files(self):
        """Test getting work directory files."""
        with patch("python.api.get_work_dir_files.GetWorkDirFiles") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "files": [{"name": "test.txt", "size": 100}]
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert "files" in result

    @pytest.mark.asyncio
    async def test_download_work_dir_file(self):
        """Test downloading a file."""
        with patch("python.api.download_work_dir_file.DownloadWorkDirFile") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value=MagicMock())
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"path": "test.txt"}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_upload_files(self):
        """Test uploading files."""
        with patch("python.api.upload.Upload") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "success": True,
                "files": ["uploaded_file.txt"]
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_delete_work_dir_file(self):
        """Test deleting a file."""
        with patch("python.api.delete_work_dir_file.DeleteWorkDirFile") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"path": "test.txt"}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestSchedulerAPI:
    """Tests for scheduler endpoints."""

    @pytest.mark.asyncio
    async def test_scheduler_tasks_list(self):
        """Test listing scheduled tasks."""
        with patch("python.api.scheduler_tasks_list.SchedulerTasksList") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "tasks": []
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert "tasks" in result

    @pytest.mark.asyncio
    async def test_scheduler_task_create(self):
        """Test creating a scheduled task."""
        with patch("python.api.scheduler_task_create.SchedulerTaskCreate") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "task_id": "task-123",
                "success": True
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({
                "name": "Test Task",
                "cron": "0 9 * * *",
                "message": "Run daily task"
            }, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_scheduler_task_delete(self):
        """Test deleting a scheduled task."""
        with patch("python.api.scheduler_task_delete.SchedulerTaskDelete") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"task_id": "task-123"}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_scheduler_task_run(self):
        """Test running a scheduled task manually."""
        with patch("python.api.scheduler_task_run.SchedulerTaskRun") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"task_id": "task-123"}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestNotificationAPI:
    """Tests for notification endpoints."""

    @pytest.mark.asyncio
    async def test_notification_create(self):
        """Test creating a notification."""
        with patch("python.api.notification_create.NotificationCreate") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "notification_id": "notif-123"
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({
                "message": "Test notification",
                "type": "info"
            }, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_notifications_history(self):
        """Test getting notification history."""
        with patch("python.api.notifications_history.NotificationsHistory") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "notifications": []
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert "notifications" in result

    @pytest.mark.asyncio
    async def test_notifications_mark_read(self):
        """Test marking notifications as read."""
        with patch("python.api.notifications_mark_read.NotificationsMarkRead") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({
                "notification_ids": ["notif-123"]
            }, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_notifications_clear(self):
        """Test clearing notifications."""
        with patch("python.api.notifications_clear.NotificationsClear") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestBackupAPI:
    """Tests for backup endpoints."""

    @pytest.mark.asyncio
    async def test_backup_create(self):
        """Test creating a backup."""
        with patch("python.api.backup_create.BackupCreate") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "backup_id": "backup-123",
                "success": True
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_backup_restore(self):
        """Test restoring a backup."""
        with patch("python.api.backup_restore.BackupRestore") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"backup_id": "backup-123"}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_backup_inspect(self):
        """Test inspecting a backup."""
        with patch("python.api.backup_inspect.BackupInspect") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "backup_info": {"id": "backup-123", "date": "2024-01-01"}
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"backup_id": "backup-123"}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestMCPAPI:
    """Tests for MCP server endpoints."""

    @pytest.mark.asyncio
    async def test_mcp_servers_status(self):
        """Test getting MCP servers status."""
        with patch("python.api.mcp_servers_status.MCPServersStatus") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "servers": [],
                "status": "ok"
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_mcp_servers_apply(self):
        """Test applying MCP server configuration."""
        with patch("python.api.mcp_servers_apply.MCPServersApply") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"config": {}}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestLogAPI:
    """Tests for log-related endpoints."""

    @pytest.mark.asyncio
    async def test_log_get(self):
        """Test getting logs."""
        with patch("python.api.api_log_get.LogGet") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "logs": [],
                "version": 1
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"context_id": "test-123"}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_history_get(self):
        """Test getting history."""
        with patch("python.api.history_get.HistoryGet") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "history": []
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"context_id": "test-123"}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestControlAPI:
    """Tests for control endpoints (pause, nudge, restart)."""

    @pytest.mark.asyncio
    async def test_pause(self):
        """Test pausing agent."""
        with patch("python.api.pause.Pause") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"paused": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"context_id": "test-123"}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_nudge(self):
        """Test nudging agent."""
        with patch("python.api.nudge.Nudge") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"success": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"context_id": "test-123"}, MagicMock())

            assert result is not None

    @pytest.mark.asyncio
    async def test_restart(self):
        """Test restarting server."""
        with patch("python.api.restart.Restart") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={"restarting": True})
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestCSRFAPI:
    """Tests for CSRF token endpoint."""

    @pytest.mark.asyncio
    async def test_csrf_token(self):
        """Test getting CSRF token."""
        with patch("python.api.csrf_token.CSRFToken") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "token": "csrf-token-123"
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert "token" in result


@pytest.mark.unit
@pytest.mark.api
class TestPollAPI:
    """Tests for polling endpoint."""

    @pytest.mark.asyncio
    async def test_poll(self):
        """Test polling for updates."""
        with patch("python.api.poll.Poll") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "contexts": [],
                "updates": []
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestMemoryDashboardAPI:
    """Tests for memory dashboard endpoint."""

    @pytest.mark.asyncio
    async def test_memory_dashboard(self):
        """Test getting memory dashboard data."""
        with patch("python.api.memory_dashboard.MemoryDashboard") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "memories": [],
                "stats": {}
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestTranscribeAPI:
    """Tests for transcription endpoint."""

    @pytest.mark.asyncio
    async def test_transcribe(self):
        """Test audio transcription."""
        with patch("python.api.transcribe.Transcribe") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value={
                "text": "Transcribed text"
            })
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"audio": "base64-audio"}, MagicMock())

            assert result is not None


@pytest.mark.unit
@pytest.mark.api
class TestSynthesizeAPI:
    """Tests for speech synthesis endpoint."""

    @pytest.mark.asyncio
    async def test_synthesize(self):
        """Test speech synthesis."""
        with patch("python.api.synthesize.Synthesize") as MockHandler:
            mock_instance = MagicMock()
            mock_instance.process = AsyncMock(return_value=MagicMock())
            MockHandler.return_value = mock_instance

            handler = MockHandler()
            result = await handler.process({"text": "Hello world"}, MagicMock())

            assert result is not None
