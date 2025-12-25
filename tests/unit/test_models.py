"""
Unit tests for models.py - LLM model wrappers and configuration.

Tests cover:
- ModelConfig dataclass
- ChatGenerationResult parsing
- Rate limiting
- API key handling
- LiteLLM wrappers
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json


@pytest.mark.unit
@pytest.mark.models
class TestModelConfig:
    """Tests for ModelConfig dataclass."""

    def test_model_config_creation(self):
        """Test creating a ModelConfig with all parameters."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4",
            api_base="https://api.openai.com/v1",
            ctx_length=8192,
            limit_requests=100,
            limit_input=100000,
            limit_output=4096,
            vision=True,
            kwargs={"temperature": 0.7},
        )

        assert config.type == ModelType.CHAT
        assert config.provider == "openai"
        assert config.name == "gpt-4"
        assert config.ctx_length == 8192
        assert config.vision is True

    def test_model_config_defaults(self):
        """Test ModelConfig default values."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4",
        )

        assert config.api_base == ""
        assert config.ctx_length == 0
        assert config.limit_requests == 0
        assert config.limit_input == 0
        assert config.limit_output == 0
        assert config.vision is False
        assert config.kwargs == {}

    def test_build_kwargs_with_api_base(self):
        """Test build_kwargs includes api_base when set."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4",
            api_base="https://custom.api.com/v1",
            kwargs={"temperature": 0.5},
        )

        kwargs = config.build_kwargs()
        assert kwargs["api_base"] == "https://custom.api.com/v1"
        assert kwargs["temperature"] == 0.5

    def test_build_kwargs_without_api_base(self):
        """Test build_kwargs excludes api_base when empty."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4",
            kwargs={"temperature": 0.5},
        )

        kwargs = config.build_kwargs()
        assert "api_base" not in kwargs
        assert kwargs["temperature"] == 0.5

    def test_build_kwargs_does_not_override_existing(self):
        """Test build_kwargs does not override existing api_base in kwargs."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4",
            api_base="https://default.api.com/v1",
            kwargs={"api_base": "https://custom.api.com/v1"},
        )

        kwargs = config.build_kwargs()
        assert kwargs["api_base"] == "https://custom.api.com/v1"


@pytest.mark.unit
@pytest.mark.models
class TestModelType:
    """Tests for ModelType enum."""

    def test_model_type_values(self):
        """Test ModelType enum values."""
        from models import ModelType

        assert ModelType.CHAT.value == "Chat"
        assert ModelType.EMBEDDING.value == "Embedding"

    def test_model_type_comparison(self):
        """Test ModelType comparison."""
        from models import ModelType

        assert ModelType.CHAT != ModelType.EMBEDDING
        assert ModelType.CHAT == ModelType.CHAT


@pytest.mark.unit
@pytest.mark.models
class TestChatGenerationResult:
    """Tests for ChatGenerationResult parsing logic."""

    def test_empty_result(self):
        """Test empty ChatGenerationResult."""
        from models import ChatGenerationResult

        result = ChatGenerationResult()
        assert result.response == ""
        assert result.reasoning == ""
        assert result.thinking is False

    def test_add_response_chunk(self):
        """Test adding response chunks."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()
        chunk = ChatChunk(response_delta="Hello ", reasoning_delta="")
        result.add_chunk(chunk)

        assert result.response == "Hello "
        assert result.reasoning == ""

    def test_add_reasoning_chunk(self):
        """Test adding reasoning chunks with native reasoning."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()
        chunk = ChatChunk(response_delta="", reasoning_delta="Let me think...")
        result.add_chunk(chunk)

        assert result.reasoning == "Let me think..."
        assert result.native_reasoning is True

    def test_thinking_tag_parsing(self):
        """Test parsing thinking tags in response."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        # Add chunk with thinking tag
        chunk1 = ChatChunk(response_delta="<think>Internal reasoning", reasoning_delta="")
        result.add_chunk(chunk1)

        assert result.thinking is True
        assert result.thinking_tag == "</think>"

    def test_complete_thinking_tag(self):
        """Test complete thinking tag parsing."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        # Complete thinking block
        chunk = ChatChunk(
            response_delta="<think>Reasoning here</think>Final answer",
            reasoning_delta=""
        )
        result.add_chunk(chunk)

        output = result.output()
        assert output["reasoning_delta"] == "Reasoning here"
        assert output["response_delta"] == "Final answer"

    def test_reasoning_tag_parsing(self):
        """Test parsing <reasoning> tags."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        chunk = ChatChunk(
            response_delta="<reasoning>My analysis</reasoning>Response",
            reasoning_delta=""
        )
        result.add_chunk(chunk)

        output = result.output()
        assert output["reasoning_delta"] == "My analysis"
        assert output["response_delta"] == "Response"

    def test_output_with_unprocessed(self):
        """Test output includes unprocessed content."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()
        result.unprocessed = "partial"
        result.response = "Complete response "

        output = result.output()
        assert output["response_delta"] == "Complete response partial"

    def test_native_reasoning_bypasses_tag_parsing(self):
        """Test native reasoning skips thinking tag parsing."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        # First chunk with native reasoning
        chunk1 = ChatChunk(response_delta="Hello", reasoning_delta="Thinking")
        result.add_chunk(chunk1)

        # Second chunk - should not parse thinking tags
        chunk2 = ChatChunk(response_delta="<think>not parsed</think>", reasoning_delta="More")
        result.add_chunk(chunk2)

        assert "<think>" in result.response
        assert result.native_reasoning is True

    def test_partial_opening_tag(self):
        """Test partial opening tag handling."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        # Partial tag
        chunk = ChatChunk(response_delta="<thi", reasoning_delta="")
        processed = result.add_chunk(chunk)

        assert result.unprocessed == "<thi"
        assert processed["response_delta"] == ""

    def test_partial_closing_tag(self):
        """Test partial closing tag handling."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        # Open thinking
        chunk1 = ChatChunk(response_delta="<think>reasoning", reasoning_delta="")
        result.add_chunk(chunk1)

        # Partial closing tag
        chunk2 = ChatChunk(response_delta="</thi", reasoning_delta="")
        result.add_chunk(chunk2)

        assert "</thi" in result.unprocessed


@pytest.mark.unit
@pytest.mark.models
class TestApiKeyHandling:
    """Tests for API key retrieval."""

    def test_get_api_key_from_env(self):
        """Test getting API key from environment."""
        from models import get_api_key

        with patch.dict("os.environ", {"API_KEY_OPENAI": "test-key-123"}):
            key = get_api_key("openai")
            assert key == "test-key-123"

    def test_get_api_key_alternative_format(self):
        """Test alternative API key environment variable format."""
        from models import get_api_key

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "anthropic-key"}, clear=False):
            # Clear other possible formats
            import os
            os.environ.pop("API_KEY_ANTHROPIC", None)
            key = get_api_key("anthropic")
            assert key == "anthropic-key"

    def test_get_api_key_round_robin(self):
        """Test round-robin API key selection."""
        from models import get_api_key, api_keys_round_robin

        api_keys_round_robin.clear()

        with patch.dict("os.environ", {"API_KEY_TEST": "key1, key2, key3"}):
            key1 = get_api_key("test")
            key2 = get_api_key("test")
            key3 = get_api_key("test")
            key4 = get_api_key("test")

            assert key1 == "key1"
            assert key2 == "key2"
            assert key3 == "key3"
            assert key4 == "key1"  # Wraps around

    def test_get_api_key_none_when_missing(self):
        """Test API key returns 'None' when not set."""
        from models import get_api_key

        with patch.dict("os.environ", {}, clear=True):
            key = get_api_key("nonexistent_service")
            assert key == "None"


@pytest.mark.unit
@pytest.mark.models
class TestRateLimiter:
    """Tests for rate limiter integration."""

    def test_get_rate_limiter(self):
        """Test getting a rate limiter."""
        from models import get_rate_limiter, rate_limiters

        rate_limiters.clear()

        limiter = get_rate_limiter("openai", "gpt-4", 100, 100000, 4096)

        assert limiter is not None
        assert limiter.limits["requests"] == 100
        assert limiter.limits["input"] == 100000
        assert limiter.limits["output"] == 4096

    def test_get_rate_limiter_reuses_existing(self):
        """Test that rate limiter is reused for same model."""
        from models import get_rate_limiter, rate_limiters

        rate_limiters.clear()

        limiter1 = get_rate_limiter("openai", "gpt-4", 100, 100000, 4096)
        limiter2 = get_rate_limiter("openai", "gpt-4", 200, 200000, 8192)

        assert limiter1 is limiter2
        # Values should be updated
        assert limiter2.limits["requests"] == 200


@pytest.mark.unit
@pytest.mark.models
class TestParseChunk:
    """Tests for chunk parsing function."""

    def test_parse_chunk_with_content(self):
        """Test parsing chunk with content."""
        from models import _parse_chunk

        chunk = {
            "choices": [
                {
                    "delta": {"content": "Hello"},
                    "message": {},
                }
            ]
        }

        parsed = _parse_chunk(chunk)
        assert parsed["response_delta"] == "Hello"
        assert parsed["reasoning_delta"] == ""

    def test_parse_chunk_with_reasoning(self):
        """Test parsing chunk with reasoning content."""
        from models import _parse_chunk

        chunk = {
            "choices": [
                {
                    "delta": {
                        "content": "Answer",
                        "reasoning_content": "Thinking",
                    },
                    "message": {},
                }
            ]
        }

        parsed = _parse_chunk(chunk)
        assert parsed["response_delta"] == "Answer"
        assert parsed["reasoning_delta"] == "Thinking"

    def test_parse_chunk_from_message(self):
        """Test parsing chunk from message field."""
        from models import _parse_chunk

        chunk = {
            "choices": [
                {
                    "delta": {},
                    "message": {"content": "From message"},
                }
            ]
        }

        parsed = _parse_chunk(chunk)
        assert parsed["response_delta"] == "From message"


@pytest.mark.unit
@pytest.mark.models
class TestTransientErrorDetection:
    """Tests for transient error detection."""

    def test_transient_error_by_status_code(self):
        """Test transient error detection by status code."""
        from models import _is_transient_litellm_error

        class MockError(Exception):
            status_code = 429

        assert _is_transient_litellm_error(MockError()) is True

    def test_non_transient_error_by_status_code(self):
        """Test non-transient error detection."""
        from models import _is_transient_litellm_error

        class MockError(Exception):
            status_code = 400

        assert _is_transient_litellm_error(MockError()) is False

    def test_transient_error_5xx(self):
        """Test 5xx errors are transient."""
        from models import _is_transient_litellm_error

        for code in [500, 502, 503, 504, 520]:
            class MockError(Exception):
                status_code = code

            assert _is_transient_litellm_error(MockError()) is True


@pytest.mark.unit
@pytest.mark.models
class TestAdjustCallArgs:
    """Tests for _adjust_call_args function."""

    def test_openrouter_adds_headers(self):
        """Test OpenRouter adds extra headers."""
        from models import _adjust_call_args

        provider, model, kwargs = _adjust_call_args("openrouter", "gpt-4", {})

        assert "extra_headers" in kwargs
        assert kwargs["extra_headers"]["HTTP-Referer"] == "https://agent-zero.ai"
        assert kwargs["extra_headers"]["X-Title"] == "Agent Zero"

    def test_other_remapped_to_openai(self):
        """Test 'other' provider is remapped to 'openai'."""
        from models import _adjust_call_args

        provider, model, kwargs = _adjust_call_args("other", "custom-model", {})

        assert provider == "openai"


@pytest.mark.unit
@pytest.mark.models
class TestChatChunk:
    """Tests for ChatChunk TypedDict."""

    def test_chat_chunk_creation(self):
        """Test creating a ChatChunk."""
        from models import ChatChunk

        chunk = ChatChunk(response_delta="Hello", reasoning_delta="Thinking")

        assert chunk["response_delta"] == "Hello"
        assert chunk["reasoning_delta"] == "Thinking"

    def test_chat_chunk_empty(self):
        """Test empty ChatChunk."""
        from models import ChatChunk

        chunk = ChatChunk(response_delta="", reasoning_delta="")

        assert chunk["response_delta"] == ""
        assert chunk["reasoning_delta"] == ""
