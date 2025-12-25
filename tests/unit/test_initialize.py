"""
Unit tests for initialize.py - Agent initialization and configuration.

Tests cover:
- initialize_agent function
- Model configuration normalization
- Runtime configuration
- MCP initialization
- Settings loading
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.mark.unit
class TestNormalizeModelKwargs:
    """Tests for _normalize_model_kwargs function."""

    def test_normalize_integer_string(self, patched_settings):
        """Test normalizing string integers."""
        from initialize import initialize_agent

        with patch("initialize.settings.get_settings") as mock_settings:
            mock_settings.return_value = {
                **patched_settings,
                "chat_model_kwargs": {"max_tokens": "100"},
            }

            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    # Verify kwargs were normalized
                    assert config.chat_model.kwargs["max_tokens"] == 100

    def test_normalize_float_string(self, patched_settings):
        """Test normalizing string floats."""
        from initialize import initialize_agent

        with patch("initialize.settings.get_settings") as mock_settings:
            mock_settings.return_value = {
                **patched_settings,
                "chat_model_kwargs": {"temperature": "0.7"},
            }

            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert config.chat_model.kwargs["temperature"] == 0.7

    def test_normalize_non_numeric_string(self, patched_settings):
        """Test non-numeric strings remain unchanged."""
        from initialize import initialize_agent

        with patch("initialize.settings.get_settings") as mock_settings:
            mock_settings.return_value = {
                **patched_settings,
                "chat_model_kwargs": {"model_version": "latest"},
            }

            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert config.chat_model.kwargs["model_version"] == "latest"


@pytest.mark.unit
class TestInitializeAgent:
    """Tests for initialize_agent function."""

    def test_initialize_agent_creates_config(self, patched_settings):
        """Test initialize_agent creates valid AgentConfig."""
        from initialize import initialize_agent
        from agent import AgentConfig

        with patch("initialize._set_runtime_config"):
            with patch("initialize._args_override"):
                config = initialize_agent()

                assert isinstance(config, AgentConfig)
                assert config.chat_model is not None
                assert config.utility_model is not None
                assert config.embeddings_model is not None
                assert config.browser_model is not None

    def test_initialize_agent_chat_model(self, patched_settings):
        """Test chat model configuration."""
        from initialize import initialize_agent
        from models import ModelType

        with patch("initialize._set_runtime_config"):
            with patch("initialize._args_override"):
                config = initialize_agent()

                assert config.chat_model.type == ModelType.CHAT
                assert config.chat_model.provider == "openai"
                assert config.chat_model.name == "gpt-4"

    def test_initialize_agent_embedding_model(self, patched_settings):
        """Test embedding model configuration."""
        from initialize import initialize_agent
        from models import ModelType

        with patch("initialize._set_runtime_config"):
            with patch("initialize._args_override"):
                config = initialize_agent()

                assert config.embeddings_model.type == ModelType.EMBEDDING
                assert config.embeddings_model.provider == "openai"

    def test_initialize_agent_with_profile(self, patched_settings):
        """Test agent profile configuration."""
        from initialize import initialize_agent

        patched_settings["agent_profile"] = "developer"

        with patch("initialize.settings.get_settings", return_value=patched_settings):
            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert config.profile == "developer"

    def test_initialize_agent_mcp_servers(self, patched_settings):
        """Test MCP servers configuration."""
        from initialize import initialize_agent

        patched_settings["mcp_servers"] = "server1,server2"

        with patch("initialize.settings.get_settings", return_value=patched_settings):
            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert config.mcp_servers == "server1,server2"


@pytest.mark.unit
class TestArgsOverride:
    """Tests for _args_override function."""

    def test_args_override_string(self, mock_agent_config):
        """Test overriding string config values."""
        from initialize import _args_override

        with patch("python.helpers.runtime.args", {"profile": "custom"}):
            _args_override(mock_agent_config)

            assert mock_agent_config.profile == "custom"

    def test_args_override_bool(self, mock_agent_config):
        """Test overriding boolean config values."""
        from initialize import _args_override

        with patch("python.helpers.runtime.args", {"code_exec_ssh_enabled": "false"}):
            _args_override(mock_agent_config)

            assert mock_agent_config.code_exec_ssh_enabled is False

    def test_args_override_int(self, mock_agent_config):
        """Test overriding integer config values."""
        from initialize import _args_override

        with patch("python.helpers.runtime.args", {"code_exec_ssh_port": "2222"}):
            _args_override(mock_agent_config)

            assert mock_agent_config.code_exec_ssh_port == 2222

    def test_args_override_ignores_unknown(self, mock_agent_config):
        """Test unknown args are ignored."""
        from initialize import _args_override

        original_profile = mock_agent_config.profile

        with patch("python.helpers.runtime.args", {"unknown_key": "value"}):
            _args_override(mock_agent_config)

            # Original value should remain
            assert mock_agent_config.profile == original_profile


@pytest.mark.unit
class TestSetRuntimeConfig:
    """Tests for _set_runtime_config function."""

    def test_set_runtime_config(self, mock_agent_config, mock_settings):
        """Test setting runtime configuration."""
        from initialize import _set_runtime_config

        with patch("python.helpers.settings.get_runtime_config") as mock_get_runtime:
            mock_get_runtime.return_value = {
                "code_exec_ssh_addr": "192.168.1.100",
                "code_exec_ssh_port": 2222,
            }

            _set_runtime_config(mock_agent_config, mock_settings)

            assert mock_agent_config.code_exec_ssh_addr == "192.168.1.100"
            assert mock_agent_config.code_exec_ssh_port == 2222


@pytest.mark.unit
class TestInitializeChats:
    """Tests for initialize_chats function."""

    def test_initialize_chats_returns_task(self):
        """Test initialize_chats returns a deferred task."""
        from initialize import initialize_chats

        with patch("python.helpers.persist_chat.load_tmp_chats"):
            with patch("python.helpers.defer.DeferredTask") as mock_task:
                mock_instance = MagicMock()
                mock_task.return_value = mock_instance
                mock_instance.start_task.return_value = mock_instance

                result = initialize_chats()

                assert result is mock_instance


@pytest.mark.unit
class TestInitializeMcp:
    """Tests for initialize_mcp function."""

    def test_initialize_mcp_returns_task(self, mock_settings):
        """Test initialize_mcp returns a deferred task."""
        from initialize import initialize_mcp

        with patch("python.helpers.settings.get_settings", return_value=mock_settings):
            with patch("python.helpers.defer.DeferredTask") as mock_task:
                mock_instance = MagicMock()
                mock_task.return_value = mock_instance
                mock_instance.start_task.return_value = mock_instance

                result = initialize_mcp()

                assert result is mock_instance


@pytest.mark.unit
class TestInitializeJobLoop:
    """Tests for initialize_job_loop function."""

    def test_initialize_job_loop_returns_task(self):
        """Test initialize_job_loop returns a deferred task."""
        from initialize import initialize_job_loop

        with patch("python.helpers.defer.DeferredTask") as mock_task:
            mock_instance = MagicMock()
            mock_task.return_value = mock_instance
            mock_instance.start_task.return_value = mock_instance

            result = initialize_job_loop()

            assert result is mock_instance


@pytest.mark.unit
class TestInitializePreload:
    """Tests for initialize_preload function."""

    def test_initialize_preload_returns_task(self):
        """Test initialize_preload returns a deferred task."""
        from initialize import initialize_preload

        with patch("python.helpers.defer.DeferredTask") as mock_task:
            mock_instance = MagicMock()
            mock_task.return_value = mock_instance
            mock_instance.start_task.return_value = mock_instance

            with patch.dict("sys.modules", {"preload": MagicMock()}):
                result = initialize_preload()

                assert result is mock_instance


@pytest.mark.unit
class TestModelConfigCreation:
    """Tests for model configuration creation in initialize_agent."""

    def test_chat_model_rate_limits(self, patched_settings):
        """Test chat model rate limit configuration."""
        from initialize import initialize_agent

        patched_settings["chat_model_rl_requests"] = 50
        patched_settings["chat_model_rl_input"] = 50000
        patched_settings["chat_model_rl_output"] = 2000

        with patch("initialize.settings.get_settings", return_value=patched_settings):
            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert config.chat_model.limit_requests == 50
                    assert config.chat_model.limit_input == 50000
                    assert config.chat_model.limit_output == 2000

    def test_utility_model_configuration(self, patched_settings):
        """Test utility model configuration."""
        from initialize import initialize_agent

        patched_settings["util_model_provider"] = "anthropic"
        patched_settings["util_model_name"] = "claude-3"

        with patch("initialize.settings.get_settings", return_value=patched_settings):
            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert config.utility_model.provider == "anthropic"
                    assert config.utility_model.name == "claude-3"

    def test_browser_model_vision(self, patched_settings):
        """Test browser model vision configuration."""
        from initialize import initialize_agent

        patched_settings["browser_model_vision"] = True

        with patch("initialize.settings.get_settings", return_value=patched_settings):
            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert config.browser_model.vision is True

    def test_knowledge_subdirs(self, patched_settings):
        """Test knowledge subdirectories configuration."""
        from initialize import initialize_agent

        patched_settings["agent_knowledge_subdir"] = "custom"

        with patch("initialize.settings.get_settings", return_value=patched_settings):
            with patch("initialize._set_runtime_config"):
                with patch("initialize._args_override"):
                    config = initialize_agent()

                    assert "custom" in config.knowledge_subdirs
                    assert "default" in config.knowledge_subdirs
