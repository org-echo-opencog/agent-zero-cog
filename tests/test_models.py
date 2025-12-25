"""
Unit tests for models.py - Model configuration and LLM wrappers.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import List


# ============================================================================
# ModelType Tests
# ============================================================================

class TestModelType:
    """Tests for ModelType enum."""

    def test_model_types(self):
        """Test all model types."""
        from models import ModelType

        assert ModelType.CHAT.value == "Chat"
        assert ModelType.EMBEDDING.value == "Embedding"


# ============================================================================
# ModelConfig Tests
# ============================================================================

class TestModelConfig:
    """Tests for ModelConfig dataclass."""

    def test_model_config_creation(self):
        """Test basic ModelConfig creation."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4"
        )

        assert config.type == ModelType.CHAT
        assert config.provider == "openai"
        assert config.name == "gpt-4"
        assert config.api_base == ""
        assert config.ctx_length == 0
        assert config.vision is False

    def test_model_config_full(self):
        """Test ModelConfig with all fields."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="anthropic",
            name="claude-3-opus",
            api_base="https://api.anthropic.com",
            ctx_length=200000,
            limit_requests=60,
            limit_input=100000,
            limit_output=4096,
            vision=True,
            kwargs={"temperature": 0.7}
        )

        assert config.ctx_length == 200000
        assert config.vision is True
        assert config.kwargs["temperature"] == 0.7

    def test_build_kwargs(self):
        """Test build_kwargs method."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4",
            api_base="https://custom.api.com",
            kwargs={"temperature": 0.5}
        )

        kwargs = config.build_kwargs()

        assert kwargs["api_base"] == "https://custom.api.com"
        assert kwargs["temperature"] == 0.5

    def test_build_kwargs_no_override(self):
        """Test build_kwargs doesn't override existing api_base."""
        from models import ModelConfig, ModelType

        config = ModelConfig(
            type=ModelType.CHAT,
            provider="openai",
            name="gpt-4",
            api_base="https://default.api.com",
            kwargs={"api_base": "https://override.api.com", "temperature": 0.5}
        )

        kwargs = config.build_kwargs()

        # Existing api_base in kwargs should not be overridden
        assert kwargs["api_base"] == "https://override.api.com"


# ============================================================================
# ChatChunk Tests
# ============================================================================

class TestChatChunk:
    """Tests for ChatChunk TypedDict."""

    def test_chat_chunk_creation(self):
        """Test ChatChunk creation."""
        from models import ChatChunk

        chunk: ChatChunk = {
            "response_delta": "Hello",
            "reasoning_delta": "Thinking..."
        }

        assert chunk["response_delta"] == "Hello"
        assert chunk["reasoning_delta"] == "Thinking..."


# ============================================================================
# ChatGenerationResult Tests
# ============================================================================

class TestChatGenerationResult:
    """Tests for ChatGenerationResult class."""

    def test_result_creation(self):
        """Test basic ChatGenerationResult creation."""
        from models import ChatGenerationResult

        result = ChatGenerationResult()

        assert result.reasoning == ""
        assert result.response == ""
        assert result.thinking is False

    def test_result_with_chunk(self):
        """Test ChatGenerationResult creation with initial chunk."""
        from models import ChatGenerationResult, ChatChunk

        chunk: ChatChunk = {"response_delta": "Hello", "reasoning_delta": ""}
        result = ChatGenerationResult(chunk)

        assert result.response == "Hello"

    def test_add_chunk(self):
        """Test adding chunks to result."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        chunk1: ChatChunk = {"response_delta": "Hello", "reasoning_delta": ""}
        chunk2: ChatChunk = {"response_delta": " World", "reasoning_delta": ""}

        result.add_chunk(chunk1)
        result.add_chunk(chunk2)

        assert result.response == "Hello World"

    def test_native_reasoning(self):
        """Test native reasoning handling."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        chunk: ChatChunk = {"response_delta": "Answer", "reasoning_delta": "Thinking"}
        result.add_chunk(chunk)

        assert result.native_reasoning is True
        assert result.reasoning == "Thinking"
        assert result.response == "Answer"

    def test_thinking_tags_parsing(self):
        """Test parsing of thinking tags in response."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        # Simulate model outputting thinking tags
        chunk1: ChatChunk = {"response_delta": "<think>", "reasoning_delta": ""}
        chunk2: ChatChunk = {"response_delta": "Let me think about this", "reasoning_delta": ""}
        chunk3: ChatChunk = {"response_delta": "</think>", "reasoning_delta": ""}
        chunk4: ChatChunk = {"response_delta": "The answer is 42", "reasoning_delta": ""}

        result.add_chunk(chunk1)
        result.add_chunk(chunk2)
        result.add_chunk(chunk3)
        result.add_chunk(chunk4)

        assert "Let me think about this" in result.reasoning
        assert "The answer is 42" in result.response

    def test_reasoning_tags_parsing(self):
        """Test parsing of reasoning tags in response."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        # Simulate model outputting reasoning tags
        chunk1: ChatChunk = {"response_delta": "<reasoning>", "reasoning_delta": ""}
        chunk2: ChatChunk = {"response_delta": "Step by step analysis", "reasoning_delta": ""}
        chunk3: ChatChunk = {"response_delta": "</reasoning>", "reasoning_delta": ""}
        chunk4: ChatChunk = {"response_delta": "Final answer", "reasoning_delta": ""}

        result.add_chunk(chunk1)
        result.add_chunk(chunk2)
        result.add_chunk(chunk3)
        result.add_chunk(chunk4)

        assert "Step by step analysis" in result.reasoning
        assert "Final answer" in result.response

    def test_output(self):
        """Test output method."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()
        result.add_chunk({"response_delta": "Test response", "reasoning_delta": "Test reasoning"})

        output = result.output()

        assert output["response_delta"] == "Test response"
        assert output["reasoning_delta"] == "Test reasoning"

    def test_partial_tag_handling(self):
        """Test handling of partial tags across chunks."""
        from models import ChatGenerationResult, ChatChunk

        result = ChatGenerationResult()

        # Split a tag across chunks
        chunk1: ChatChunk = {"response_delta": "<thi", "reasoning_delta": ""}
        chunk2: ChatChunk = {"response_delta": "nk>reasoning</think>answer", "reasoning_delta": ""}

        result.add_chunk(chunk1)
        result.add_chunk(chunk2)

        # Should properly parse despite split
        assert "answer" in result.response or "reasoning" in result.reasoning


# ============================================================================
# Rate Limiter Tests
# ============================================================================

class TestRateLimiter:
    """Tests for rate limiting functionality."""

    def test_get_rate_limiter(self):
        """Test getting rate limiter."""
        from models import get_rate_limiter

        limiter = get_rate_limiter(
            provider="openai",
            name="gpt-4",
            requests=100,
            input=10000,
            output=4096
        )

        assert limiter is not None
        assert limiter.limits["requests"] == 100
        assert limiter.limits["input"] == 10000
        assert limiter.limits["output"] == 4096

    def test_rate_limiter_caching(self):
        """Test rate limiter caching (same key returns same limiter)."""
        from models import get_rate_limiter

        limiter1 = get_rate_limiter("openai", "gpt-4", 100, 10000, 4096)
        limiter2 = get_rate_limiter("openai", "gpt-4", 100, 10000, 4096)

        assert limiter1 is limiter2


# ============================================================================
# API Key Tests
# ============================================================================

class TestApiKey:
    """Tests for API key handling."""

    def test_get_api_key_from_env(self):
        """Test getting API key from environment."""
        from models import get_api_key
        import os

        # Set test API key
        os.environ["API_KEY_TESTPROVIDER"] = "test_key_123"

        key = get_api_key("testprovider")
        assert key == "test_key_123"

        # Cleanup
        del os.environ["API_KEY_TESTPROVIDER"]

    def test_get_api_key_round_robin(self):
        """Test round-robin API key selection."""
        from models import get_api_key, api_keys_round_robin
        import os

        # Set multiple keys
        os.environ["API_KEY_ROUNDROBIN"] = "key1,key2,key3"

        # Reset round robin counter
        api_keys_round_robin.pop("roundrobin", None)

        key1 = get_api_key("roundrobin")
        key2 = get_api_key("roundrobin")
        key3 = get_api_key("roundrobin")
        key4 = get_api_key("roundrobin")  # Should wrap around

        assert key1 == "key1"
        assert key2 == "key2"
        assert key3 == "key3"
        assert key4 == "key1"  # Wraps around

        # Cleanup
        del os.environ["API_KEY_ROUNDROBIN"]


# ============================================================================
# Transient Error Detection Tests
# ============================================================================

class TestTransientErrorDetection:
    """Tests for transient error detection."""

    def test_transient_error_by_status_code(self):
        """Test transient error detection by status code."""
        from models import _is_transient_litellm_error

        class MockError(Exception):
            def __init__(self, status_code):
                self.status_code = status_code

        assert _is_transient_litellm_error(MockError(429)) is True  # Rate limit
        assert _is_transient_litellm_error(MockError(500)) is True  # Server error
        assert _is_transient_litellm_error(MockError(502)) is True  # Bad gateway
        assert _is_transient_litellm_error(MockError(503)) is True  # Unavailable
        assert _is_transient_litellm_error(MockError(504)) is True  # Timeout
        assert _is_transient_litellm_error(MockError(400)) is False  # Bad request
        assert _is_transient_litellm_error(MockError(401)) is False  # Unauthorized


# ============================================================================
# LiteLLM Chat Wrapper Tests
# ============================================================================

class TestLiteLLMChatWrapper:
    """Tests for LiteLLMChatWrapper class."""

    def test_wrapper_creation(self, mock_model_config):
        """Test LiteLLMChatWrapper creation."""
        from models import LiteLLMChatWrapper

        wrapper = LiteLLMChatWrapper(
            model="gpt-4",
            provider="openai",
            model_config=mock_model_config
        )

        assert wrapper.model_name == "openai/gpt-4"
        assert wrapper.provider == "openai"

    def test_wrapper_llm_type(self, mock_model_config):
        """Test _llm_type property."""
        from models import LiteLLMChatWrapper

        wrapper = LiteLLMChatWrapper(
            model="gpt-4",
            provider="openai",
            model_config=mock_model_config
        )

        assert wrapper._llm_type == "litellm-chat"

    def test_convert_messages(self, mock_model_config):
        """Test message conversion."""
        from models import LiteLLMChatWrapper
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        wrapper = LiteLLMChatWrapper(
            model="gpt-4",
            provider="openai",
            model_config=mock_model_config
        )

        messages = [
            SystemMessage(content="You are helpful"),
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!")
        ]

        converted = wrapper._convert_messages(messages)

        assert len(converted) == 3
        assert converted[0]["role"] == "system"
        assert converted[0]["content"] == "You are helpful"
        assert converted[1]["role"] == "user"
        assert converted[2]["role"] == "assistant"


# ============================================================================
# Embedding Wrapper Tests
# ============================================================================

class TestLiteLLMEmbeddingWrapper:
    """Tests for LiteLLMEmbeddingWrapper class."""

    def test_wrapper_creation(self, mock_embedding_config):
        """Test LiteLLMEmbeddingWrapper creation."""
        from models import LiteLLMEmbeddingWrapper

        wrapper = LiteLLMEmbeddingWrapper(
            model="text-embedding-ada-002",
            provider="openai",
            model_config=mock_embedding_config
        )

        assert wrapper.model_name == "text-embedding-ada-002"


# ============================================================================
# LocalSentenceTransformerWrapper Tests
# ============================================================================

class TestLocalSentenceTransformerWrapper:
    """Tests for LocalSentenceTransformerWrapper class."""

    def test_model_name_cleaning(self):
        """Test model name cleaning."""
        from models import LocalSentenceTransformerWrapper

        # Test with sentence-transformers prefix
        with patch("models.SentenceTransformer") as mock_st:
            mock_st.return_value = MagicMock()

            wrapper = LocalSentenceTransformerWrapper(
                provider="huggingface",
                model="sentence-transformers/all-MiniLM-L6-v2"
            )

            # Should remove the prefix
            assert wrapper.model_name == "all-MiniLM-L6-v2"

    def test_kwargs_filtering(self):
        """Test that non-SentenceTransformer kwargs are filtered."""
        from models import LocalSentenceTransformerWrapper

        with patch("models.SentenceTransformer") as mock_st:
            mock_st.return_value = MagicMock()

            # Pass kwargs that should be filtered
            wrapper = LocalSentenceTransformerWrapper(
                provider="huggingface",
                model="all-MiniLM-L6-v2",
                stream_timeout=30,  # Should be filtered
                device="cpu"  # Should be kept
            )

            # Verify only allowed kwargs were passed
            call_kwargs = mock_st.call_args[1]
            assert "device" in call_kwargs
            assert "stream_timeout" not in call_kwargs


# ============================================================================
# Parse Chunk Tests
# ============================================================================

class TestParseChunk:
    """Tests for _parse_chunk function."""

    def test_parse_chunk_with_delta(self):
        """Test parsing chunk with delta content."""
        from models import _parse_chunk

        chunk = {
            "choices": [{
                "delta": {
                    "content": "Hello",
                    "reasoning_content": "Thinking"
                }
            }]
        }

        parsed = _parse_chunk(chunk)

        assert parsed["response_delta"] == "Hello"
        assert parsed["reasoning_delta"] == "Thinking"

    def test_parse_chunk_with_message(self):
        """Test parsing chunk with message content."""
        from models import _parse_chunk

        chunk = {
            "choices": [{
                "delta": {},
                "message": {
                    "content": "Response from message"
                }
            }]
        }

        parsed = _parse_chunk(chunk)

        assert parsed["response_delta"] == "Response from message"

    def test_parse_chunk_empty(self):
        """Test parsing empty chunk."""
        from models import _parse_chunk

        chunk = {
            "choices": [{
                "delta": {},
                "message": {}
            }]
        }

        parsed = _parse_chunk(chunk)

        assert parsed["response_delta"] == ""
        assert parsed["reasoning_delta"] == ""


# ============================================================================
# Provider Adjustment Tests
# ============================================================================

class TestProviderAdjustment:
    """Tests for provider adjustment functions."""

    def test_adjust_call_args_openrouter(self):
        """Test OpenRouter header injection."""
        from models import _adjust_call_args

        provider, model, kwargs = _adjust_call_args("openrouter", "gpt-4", {})

        assert "extra_headers" in kwargs
        assert kwargs["extra_headers"]["HTTP-Referer"] == "https://agent-zero.ai"
        assert kwargs["extra_headers"]["X-Title"] == "Agent Zero"

    def test_adjust_call_args_other_to_openai(self):
        """Test 'other' provider remapping to 'openai'."""
        from models import _adjust_call_args

        provider, model, kwargs = _adjust_call_args("other", "custom-model", {})

        assert provider == "openai"


# ============================================================================
# Model Factory Tests
# ============================================================================

class TestModelFactories:
    """Tests for model factory functions."""

    @patch("models._get_litellm_chat")
    def test_get_chat_model(self, mock_get_chat):
        """Test get_chat_model factory."""
        from models import get_chat_model

        mock_get_chat.return_value = MagicMock()

        model = get_chat_model("openai", "gpt-4")

        mock_get_chat.assert_called_once()

    @patch("models._get_litellm_chat")
    def test_get_browser_model(self, mock_get_chat):
        """Test get_browser_model factory."""
        from models import get_browser_model

        mock_get_chat.return_value = MagicMock()

        model = get_browser_model("openai", "gpt-4-vision-preview")

        mock_get_chat.assert_called_once()

    @patch("models._get_litellm_embedding")
    def test_get_embedding_model(self, mock_get_embedding):
        """Test get_embedding_model factory."""
        from models import get_embedding_model

        mock_get_embedding.return_value = MagicMock()

        model = get_embedding_model("openai", "text-embedding-ada-002")

        mock_get_embedding.assert_called_once()
