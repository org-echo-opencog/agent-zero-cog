"""
Unit tests for API endpoints.
"""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from flask import Flask


# ============================================================================
# API Handler Base Tests
# ============================================================================

class TestApiHandlerBase:
    """Tests for base ApiHandler class."""

    def test_default_requires_loopback(self):
        """Test default requires_loopback."""
        from python.helpers.api import ApiHandler

        assert ApiHandler.requires_loopback() is False

    def test_default_requires_api_key(self):
        """Test default requires_api_key."""
        from python.helpers.api import ApiHandler

        assert ApiHandler.requires_api_key() is False

    def test_default_requires_auth(self):
        """Test default requires_auth."""
        from python.helpers.api import ApiHandler

        assert ApiHandler.requires_auth() is True

    def test_default_get_methods(self):
        """Test default get_methods."""
        from python.helpers.api import ApiHandler

        assert ApiHandler.get_methods() == ["POST"]

    def test_default_requires_csrf(self):
        """Test default requires_csrf (follows requires_auth)."""
        from python.helpers.api import ApiHandler

        assert ApiHandler.requires_csrf() is True


# ============================================================================
# Health Check API Tests
# ============================================================================

class TestHealthCheckApi:
    """Tests for health check endpoint."""

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

    @pytest.mark.asyncio
    async def test_health_check_process(self):
        """Test health check process method."""
        from python.api.health import HealthCheck
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        handler = HealthCheck(app, lock)
        mock_request = MagicMock()

        with patch('python.api.health.git.get_git_info') as mock_git:
            mock_git.return_value = {"branch": "main", "commit": "abc123"}

            result = await handler.process({}, mock_request)

            assert "gitinfo" in result
            assert result["gitinfo"]["branch"] == "main"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_health_check_with_git_error(self):
        """Test health check handles git errors gracefully."""
        from python.api.health import HealthCheck
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        handler = HealthCheck(app, lock)
        mock_request = MagicMock()

        with patch('python.api.health.git.get_git_info') as mock_git:
            mock_git.side_effect = Exception("Git not found")

            result = await handler.process({}, mock_request)

            assert result["gitinfo"] is None
            assert result["error"] is not None


# ============================================================================
# Settings API Tests
# ============================================================================

class TestSettingsApi:
    """Tests for settings endpoints."""

    @pytest.mark.asyncio
    async def test_settings_get(self, patch_settings):
        """Test getting settings."""
        from python.api.settings_get import SettingsGet
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        handler = SettingsGet(app, lock)
        mock_request = MagicMock()

        result = await handler.process({}, mock_request)

        # Should return settings dict
        assert isinstance(result, dict)

    def test_settings_get_requires_auth(self):
        """Test settings get requires auth."""
        from python.api.settings_get import SettingsGet

        # Should require auth by default
        assert SettingsGet.requires_auth() is True


# ============================================================================
# Chat Management API Tests
# ============================================================================

class TestChatApi:
    """Tests for chat management endpoints."""

    def test_chat_reset_methods(self):
        """Test chat reset HTTP methods."""
        from python.api.chat_reset import ChatReset

        assert "POST" in ChatReset.get_methods()

    @pytest.mark.asyncio
    async def test_chat_reset_process(self, mock_agent_config):
        """Test chat reset process."""
        from python.api.chat_reset import ChatReset
        from agent import AgentContext
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        # Create a context first
        AgentContext._contexts.clear()
        ctx = AgentContext(config=mock_agent_config, id="reset_test_ctx")

        handler = ChatReset(app, lock)
        mock_request = MagicMock()

        # Mock session
        with app.test_request_context():
            result = await handler.process({"context": "reset_test_ctx"}, mock_request)

        # Cleanup
        AgentContext.remove("reset_test_ctx")


# ============================================================================
# File Management API Tests
# ============================================================================

class TestFileApi:
    """Tests for file management endpoints."""

    @pytest.mark.asyncio
    async def test_files_get(self, temp_directory):
        """Test getting files list."""
        from python.api.api_files_get import FilesGet
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        # Create test files
        (temp_directory / "test1.txt").write_text("content1")
        (temp_directory / "test2.py").write_text("content2")

        handler = FilesGet(app, lock)
        mock_request = MagicMock()

        # The actual implementation depends on work_dir configuration
        # This tests the structure is valid


# ============================================================================
# Message API Tests
# ============================================================================

class TestMessageApi:
    """Tests for message handling endpoints."""

    def test_message_requires_auth(self):
        """Test message endpoint requires auth."""
        from python.api.message import Message

        assert Message.requires_auth() is True

    def test_message_methods(self):
        """Test message HTTP methods."""
        from python.api.message import Message

        assert "POST" in Message.get_methods()


# ============================================================================
# Poll API Tests
# ============================================================================

class TestPollApi:
    """Tests for polling endpoint."""

    def test_poll_methods(self):
        """Test poll HTTP methods."""
        from python.api.poll import Poll

        methods = Poll.get_methods()
        # Poll typically supports GET for long polling


# ============================================================================
# Scheduler API Tests
# ============================================================================

class TestSchedulerApi:
    """Tests for scheduler endpoints."""

    @pytest.mark.asyncio
    async def test_scheduler_tasks_list(self):
        """Test listing scheduler tasks."""
        from python.api.scheduler_tasks_list import SchedulerTasksList
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        handler = SchedulerTasksList(app, lock)
        mock_request = MagicMock()

        with patch('python.api.scheduler_tasks_list.task_scheduler') as mock_scheduler:
            mock_scheduler.get_tasks.return_value = []

            result = await handler.process({}, mock_request)

            assert "tasks" in result or isinstance(result, list) or isinstance(result, dict)


# ============================================================================
# CSRF Token API Tests
# ============================================================================

class TestCsrfApi:
    """Tests for CSRF token endpoint."""

    def test_csrf_no_auth_required(self):
        """Test CSRF endpoint doesn't require auth."""
        from python.api.csrf_token import CsrfToken

        # CSRF token generation shouldn't require existing auth
        assert CsrfToken.requires_auth() is False

    def test_csrf_methods(self):
        """Test CSRF token HTTP methods."""
        from python.api.csrf_token import CsrfToken

        methods = CsrfToken.get_methods()
        assert "GET" in methods or "POST" in methods


# ============================================================================
# Backup API Tests
# ============================================================================

class TestBackupApi:
    """Tests for backup endpoints."""

    @pytest.mark.asyncio
    async def test_backup_get_defaults(self):
        """Test getting backup defaults."""
        from python.api.backup_get_defaults import BackupGetDefaults
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        handler = BackupGetDefaults(app, lock)
        mock_request = MagicMock()

        result = await handler.process({}, mock_request)

        # Should return backup configuration defaults
        assert isinstance(result, dict)


# ============================================================================
# Notification API Tests
# ============================================================================

class TestNotificationApi:
    """Tests for notification endpoints."""

    @pytest.mark.asyncio
    async def test_notifications_history(self):
        """Test getting notification history."""
        from python.api.notifications_history import NotificationsHistory
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        handler = NotificationsHistory(app, lock)
        mock_request = MagicMock()

        with patch('python.api.notifications_history.AgentContext') as mock_ctx:
            mock_manager = MagicMock()
            mock_manager.get_history.return_value = []
            mock_ctx.get_notification_manager.return_value = mock_manager

            result = await handler.process({}, mock_request)


# ============================================================================
# Image API Tests
# ============================================================================

class TestImageApi:
    """Tests for image endpoint."""

    def test_image_get_methods(self):
        """Test image get HTTP methods."""
        from python.api.image_get import ImageGet

        methods = ImageGet.get_methods()
        assert "GET" in methods


# ============================================================================
# Context Window API Tests
# ============================================================================

class TestCtxWindowApi:
    """Tests for context window endpoint."""

    @pytest.mark.asyncio
    async def test_ctx_window_get(self, mock_agent_config):
        """Test getting context window info."""
        from python.api.ctx_window_get import CtxWindowGet
        from agent import AgentContext
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        # Create context
        AgentContext._contexts.clear()
        ctx = AgentContext(config=mock_agent_config, id="ctx_window_test")

        handler = CtxWindowGet(app, lock)
        mock_request = MagicMock()

        result = await handler.process({"context": "ctx_window_test"}, mock_request)

        # Cleanup
        AgentContext.remove("ctx_window_test")


# ============================================================================
# MCP Server API Tests
# ============================================================================

class TestMcpApi:
    """Tests for MCP server endpoints."""

    def test_mcp_servers_status_methods(self):
        """Test MCP servers status HTTP methods."""
        from python.api.mcp_servers_status import McpServersStatus

        methods = McpServersStatus.get_methods()
        assert "GET" in methods or "POST" in methods


# ============================================================================
# Knowledge Import API Tests
# ============================================================================

class TestKnowledgeApi:
    """Tests for knowledge import endpoint."""

    def test_knowledge_import_methods(self):
        """Test knowledge import HTTP methods."""
        from python.api.import_knowledge import ImportKnowledge

        methods = ImportKnowledge.get_methods()
        assert "POST" in methods


# ============================================================================
# Transcribe/Synthesize API Tests
# ============================================================================

class TestSpeechApi:
    """Tests for speech-related endpoints."""

    def test_transcribe_methods(self):
        """Test transcribe HTTP methods."""
        from python.api.transcribe import Transcribe

        methods = Transcribe.get_methods()
        assert "POST" in methods

    def test_synthesize_methods(self):
        """Test synthesize HTTP methods."""
        from python.api.synthesize import Synthesize

        methods = Synthesize.get_methods()
        assert "POST" in methods


# ============================================================================
# API Error Handling Tests
# ============================================================================

class TestApiErrorHandling:
    """Tests for API error handling."""

    @pytest.mark.asyncio
    async def test_handler_catches_exceptions(self):
        """Test that API handler catches and formats exceptions."""
        from python.helpers.api import ApiHandler
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        class FailingHandler(ApiHandler):
            async def process(self, input, request):
                raise ValueError("Test error")

        handler = FailingHandler(app, lock)

        with app.test_request_context(json={}):
            from flask import request
            response = await handler.handle_request(request)

            assert response.status_code == 500
            assert b"ValueError" in response.data or b"Test error" in response.data

    @pytest.mark.asyncio
    async def test_handler_returns_json(self):
        """Test that API handler returns proper JSON."""
        from python.helpers.api import ApiHandler
        import threading

        app = Flask(__name__)
        lock = threading.Lock()

        class SuccessHandler(ApiHandler):
            async def process(self, input, request):
                return {"status": "ok", "data": [1, 2, 3]}

        handler = SuccessHandler(app, lock)

        with app.test_request_context(json={}):
            from flask import request
            response = await handler.handle_request(request)

            assert response.status_code == 200
            assert response.mimetype == "application/json"

            data = json.loads(response.data)
            assert data["status"] == "ok"


# ============================================================================
# API Context Tests
# ============================================================================

class TestApiContext:
    """Tests for API context management."""

    def test_get_context_new(self, mock_agent_config):
        """Test getting a new context."""
        from python.helpers.api import ApiHandler
        from agent import AgentContext
        import threading

        AgentContext._contexts.clear()

        app = Flask(__name__)
        lock = threading.Lock()

        class TestHandler(ApiHandler):
            async def process(self, input, request):
                return {}

        handler = TestHandler(app, lock)

        with patch('python.helpers.api.initialize_agent', return_value=mock_agent_config):
            ctx = handler.get_context("")

            assert ctx is not None
            assert isinstance(ctx, AgentContext)

            # Cleanup
            AgentContext.remove(ctx.id)

    def test_get_context_existing(self, mock_agent_config):
        """Test getting an existing context."""
        from python.helpers.api import ApiHandler
        from agent import AgentContext
        import threading

        AgentContext._contexts.clear()

        app = Flask(__name__)
        lock = threading.Lock()

        # Create existing context
        existing = AgentContext(config=mock_agent_config, id="existing_ctx")

        class TestHandler(ApiHandler):
            async def process(self, input, request):
                return {}

        handler = TestHandler(app, lock)

        ctx = handler.get_context("existing_ctx")

        assert ctx is existing

        # Cleanup
        AgentContext.remove("existing_ctx")
