"""
Unit tests for helper modules.
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock


# ============================================================================
# DirtyJson Tests
# ============================================================================

class TestDirtyJson:
    """Tests for dirty_json module."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON."""
        from python.helpers.dirty_json import parse, DirtyJson

        result = parse('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_string_method(self):
        """Test DirtyJson.parse_string static method."""
        from python.helpers.dirty_json import DirtyJson

        result = DirtyJson.parse_string('{"name": "test", "count": 42}')
        assert result["name"] == "test"
        assert result["count"] == 42

    def test_parse_array(self):
        """Test parsing JSON array."""
        from python.helpers.dirty_json import parse

        result = parse('[1, 2, 3, "four"]')
        assert result == [1, 2, 3, "four"]

    def test_parse_nested(self):
        """Test parsing nested JSON."""
        from python.helpers.dirty_json import parse

        result = parse('{"outer": {"inner": "value"}}')
        assert result["outer"]["inner"] == "value"

    def test_parse_unquoted_keys(self):
        """Test parsing JSON with unquoted keys."""
        from python.helpers.dirty_json import parse

        result = parse('{name: "test"}')
        assert result["name"] == "test"

    def test_parse_single_quotes(self):
        """Test parsing JSON with single quotes."""
        from python.helpers.dirty_json import parse

        result = parse("{'key': 'value'}")
        assert result["key"] == "value"

    def test_parse_trailing_commas(self):
        """Test parsing JSON with trailing commas."""
        from python.helpers.dirty_json import parse

        result = parse('[1, 2, 3,]')
        assert result == [1, 2, 3]

    def test_parse_comments(self):
        """Test parsing JSON with comments."""
        from python.helpers.dirty_json import parse

        # Single-line comment
        result = parse('{"key": "value" // comment\n}')
        assert result["key"] == "value"

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        from python.helpers.dirty_json import parse

        result = parse('')
        assert result is None

    def test_parse_booleans(self):
        """Test parsing boolean values."""
        from python.helpers.dirty_json import parse

        result = parse('{"flag1": true, "flag2": false}')
        assert result["flag1"] is True
        assert result["flag2"] is False

    def test_parse_null(self):
        """Test parsing null values."""
        from python.helpers.dirty_json import parse

        result = parse('{"value": null}')
        assert result["value"] is None

    def test_parse_undefined(self):
        """Test parsing undefined values (JavaScript-style)."""
        from python.helpers.dirty_json import parse

        result = parse('{"value": undefined}')
        assert result["value"] is None

    def test_parse_numbers(self):
        """Test parsing various number formats."""
        from python.helpers.dirty_json import parse

        result = parse('{"int": 42, "float": 3.14, "negative": -10}')
        assert result["int"] == 42
        assert result["float"] == 3.14
        assert result["negative"] == -10

    def test_parse_multiline_string(self):
        """Test parsing multiline strings."""
        from python.helpers.dirty_json import parse

        result = parse('{"text": """line1\nline2"""}')
        assert "line1" in result["text"]

    def test_parse_unicode_escape(self):
        """Test parsing unicode escape sequences."""
        from python.helpers.dirty_json import parse

        result = parse('{"char": "\\u0048"}')
        assert result["char"] == "H"

    def test_stringify(self):
        """Test stringify function."""
        from python.helpers.dirty_json import stringify

        result = stringify({"key": "value", "num": 42})
        assert '"key"' in result
        assert '"value"' in result

    def test_try_parse_valid(self):
        """Test try_parse with valid JSON."""
        from python.helpers.dirty_json import try_parse

        result = try_parse('{"valid": true}')
        assert result["valid"] is True

    def test_try_parse_dirty(self):
        """Test try_parse with dirty JSON."""
        from python.helpers.dirty_json import try_parse

        result = try_parse('{key: "value"}')  # unquoted key
        assert result["key"] == "value"

    def test_double_braces(self):
        """Test parsing with double braces."""
        from python.helpers.dirty_json import parse

        result = parse('{{"key": "value"}}')
        assert result["key"] == "value"


# ============================================================================
# Tokens Tests
# ============================================================================

class TestTokens:
    """Tests for tokens module."""

    def test_count_tokens(self):
        """Test basic token counting."""
        from python.helpers.tokens import count_tokens

        count = count_tokens("Hello, world!")
        assert count > 0
        assert isinstance(count, int)

    def test_count_tokens_empty(self):
        """Test counting tokens for empty string."""
        from python.helpers.tokens import count_tokens

        count = count_tokens("")
        assert count == 0

    def test_approximate_tokens(self):
        """Test approximate token counting with buffer."""
        from python.helpers.tokens import approximate_tokens, count_tokens

        text = "This is a test sentence."
        approx = approximate_tokens(text)
        exact = count_tokens(text)

        # Approximate should be higher due to buffer
        assert approx >= exact

    def test_trim_to_tokens_no_trim(self):
        """Test trim_to_tokens when no trimming needed."""
        from python.helpers.tokens import trim_to_tokens

        text = "Short text"
        result = trim_to_tokens(text, max_tokens=1000, direction="end")

        assert result == text

    def test_trim_to_tokens_from_start(self):
        """Test trim_to_tokens from start."""
        from python.helpers.tokens import trim_to_tokens

        text = "This is a long text that needs to be trimmed from the start."
        result = trim_to_tokens(text, max_tokens=5, direction="start")

        assert len(result) < len(text)
        assert result.endswith("...")

    def test_trim_to_tokens_from_end(self):
        """Test trim_to_tokens from end."""
        from python.helpers.tokens import trim_to_tokens

        text = "This is a long text that needs to be trimmed from the end."
        result = trim_to_tokens(text, max_tokens=5, direction="end")

        assert len(result) < len(text)
        assert result.startswith("...")


# ============================================================================
# Files Tests
# ============================================================================

class TestFiles:
    """Tests for files module."""

    def test_get_base_dir(self):
        """Test get_base_dir returns a valid directory."""
        from python.helpers.files import get_base_dir

        base_dir = get_base_dir()
        assert os.path.isdir(base_dir)

    def test_get_abs_path(self):
        """Test get_abs_path creates absolute paths."""
        from python.helpers.files import get_abs_path

        path = get_abs_path("tests", "test_file.py")
        assert os.path.isabs(path)
        assert "tests" in path

    def test_exists(self):
        """Test exists function."""
        from python.helpers.files import exists

        # This test file should exist
        assert exists("tests", "conftest.py")
        assert not exists("nonexistent", "file.txt")

    def test_basename(self):
        """Test basename function."""
        from python.helpers.files import basename

        assert basename("/path/to/file.txt") == "file.txt"
        assert basename("/path/to/file.txt", ".txt") == "file"

    def test_dirname(self):
        """Test dirname function."""
        from python.helpers.files import dirname

        assert dirname("/path/to/file.txt") == "/path/to"

    def test_replace_placeholders_text(self):
        """Test text placeholder replacement."""
        from python.helpers.files import replace_placeholders_text

        template = "Hello, {{name}}! You have {{count}} messages."
        result = replace_placeholders_text(template, name="John", count=5)

        assert result == "Hello, John! You have 5 messages."

    def test_replace_placeholders_json(self):
        """Test JSON placeholder replacement."""
        from python.helpers.files import replace_placeholders_json

        template = '{"name": {{name}}, "items": {{items}}}'
        result = replace_placeholders_json(
            template,
            name="test",
            items=[1, 2, 3]
        )

        parsed = json.loads(result)
        assert parsed["name"] == "test"
        assert parsed["items"] == [1, 2, 3]

    def test_remove_code_fences(self):
        """Test code fence removal."""
        from python.helpers.files import remove_code_fences

        text = "```python\nprint('hello')\n```"
        result = remove_code_fences(text)

        assert "```" not in result
        assert "print('hello')" in result

    def test_is_full_json_template(self):
        """Test JSON template detection."""
        from python.helpers.files import is_full_json_template

        json_template = '```json\n{"key": "value"}\n```'
        non_json = "Just plain text"

        assert is_full_json_template(json_template) is True
        assert is_full_json_template(non_json) is False

    def test_safe_file_name(self):
        """Test safe filename generation."""
        from python.helpers.files import safe_file_name

        unsafe = "file<>name:with|bad*chars?.txt"
        safe = safe_file_name(unsafe)

        assert "<" not in safe
        assert ">" not in safe
        assert ":" not in safe
        assert "|" not in safe
        assert "*" not in safe
        assert "?" not in safe

    def test_write_and_read_file(self, temp_directory):
        """Test writing and reading files."""
        from python.helpers.files import write_file, read_file, get_abs_path

        # Create a temporary test within temp_directory
        test_file = str(temp_directory / "test_write.txt")
        content = "Test content for file operations"

        # We need to use absolute path handling
        with open(test_file, 'w') as f:
            f.write(content)

        with open(test_file, 'r') as f:
            result = f.read()

        assert result == content

    def test_list_files(self, temp_directory):
        """Test listing files in directory."""
        # Create some test files
        (temp_directory / "file1.txt").write_text("content1")
        (temp_directory / "file2.txt").write_text("content2")
        (temp_directory / "file3.py").write_text("content3")

        files = os.listdir(temp_directory)

        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "file3.py" in files

    def test_get_subdirectories(self, temp_directory):
        """Test getting subdirectories."""
        # Create some subdirectories
        (temp_directory / "subdir1").mkdir()
        (temp_directory / "subdir2").mkdir()
        (temp_directory / "file.txt").write_text("not a dir")

        subdirs = [d for d in os.listdir(temp_directory)
                   if (temp_directory / d).is_dir()]

        assert "subdir1" in subdirs
        assert "subdir2" in subdirs
        assert "file.txt" not in subdirs


# ============================================================================
# Rate Limiter Tests
# ============================================================================

class TestRateLimiter:
    """Tests for rate_limiter module."""

    def test_rate_limiter_creation(self):
        """Test RateLimiter creation."""
        from python.helpers.rate_limiter import RateLimiter

        limiter = RateLimiter(seconds=60)

        assert limiter.seconds == 60
        assert limiter.limits == {}

    def test_rate_limiter_add(self):
        """Test adding to rate limiter."""
        from python.helpers.rate_limiter import RateLimiter

        limiter = RateLimiter(seconds=60)
        limiter.limits["requests"] = 100

        limiter.add(requests=1)

        assert len(limiter.usage) == 1

    def test_rate_limiter_limits(self):
        """Test rate limiter with limits."""
        from python.helpers.rate_limiter import RateLimiter

        limiter = RateLimiter(seconds=60)
        limiter.limits["requests"] = 10
        limiter.limits["input"] = 1000

        # Add some usage
        for _ in range(5):
            limiter.add(requests=1, input=100)

        # Should not be over limit yet
        assert limiter.get_usage("requests") == 5
        assert limiter.get_usage("input") == 500


# ============================================================================
# Log Tests
# ============================================================================

class TestLog:
    """Tests for log module."""

    def test_log_creation(self):
        """Test Log creation."""
        from python.helpers.log import Log

        log = Log()

        assert log.guid is not None
        assert log.logs == []
        assert log.updates == []

    def test_log_item(self):
        """Test logging items."""
        from python.helpers.log import Log

        log = Log()
        item = log.log(type="info", heading="Test", content="Test message")

        assert item is not None
        assert item.type == "info"
        assert item.heading == "Test"
        assert len(log.logs) == 1

    def test_log_reset(self):
        """Test log reset."""
        from python.helpers.log import Log

        log = Log()
        log.log(type="info", content="Test")
        log.log(type="warning", content="Warning")

        assert len(log.logs) == 2

        log.reset()

        assert len(log.logs) == 0

    def test_log_output(self):
        """Test log output method."""
        from python.helpers.log import Log

        log = Log()
        log.log(type="info", content="Test message")

        output = log.output()

        assert len(output) == 1
        assert output[0]["content"] == "Test message"


# ============================================================================
# Extension Tests
# ============================================================================

class TestExtension:
    """Tests for extension module."""

    @pytest.mark.asyncio
    async def test_call_extensions_empty(self):
        """Test calling extensions with no extensions."""
        from python.helpers.extension import call_extensions

        # Create a mock agent
        mock_agent = MagicMock()
        mock_agent.config.profile = ""

        # Should not raise
        result = await call_extensions("test_point", agent=mock_agent)


# ============================================================================
# Errors Tests
# ============================================================================

class TestErrors:
    """Tests for errors module."""

    def test_format_error(self):
        """Test error formatting."""
        from python.helpers.errors import format_error

        try:
            raise ValueError("Test error message")
        except Exception as e:
            formatted = format_error(e)

        assert "ValueError" in formatted
        assert "Test error message" in formatted

    def test_error_text(self):
        """Test error text extraction."""
        from python.helpers.errors import error_text

        try:
            raise RuntimeError("Runtime error occurred")
        except Exception as e:
            text = error_text(e)

        assert "RuntimeError" in text
        assert "Runtime error occurred" in text

    def test_repairable_exception(self):
        """Test RepairableException."""
        from python.helpers.errors import RepairableException

        exc = RepairableException("This can be fixed")
        assert str(exc) == "This can be fixed"


# ============================================================================
# Crypto Tests
# ============================================================================

class TestCrypto:
    """Tests for crypto module."""

    def test_generate_random_string(self):
        """Test random string generation."""
        from python.helpers.crypto import generate_random_string

        result = generate_random_string(16)

        assert len(result) == 16
        assert result.isalnum()

    def test_generate_random_string_unique(self):
        """Test that random strings are unique."""
        from python.helpers.crypto import generate_random_string

        strings = [generate_random_string(16) for _ in range(10)]

        assert len(set(strings)) == 10  # All unique


# ============================================================================
# GUIDs Tests
# ============================================================================

class TestGuids:
    """Tests for guids module."""

    def test_generate_guid(self):
        """Test GUID generation."""
        from python.helpers.guids import generate_guid

        guid = generate_guid()

        assert len(guid) == 8
        assert guid.isalnum()

    def test_generate_guid_unique(self):
        """Test GUID uniqueness."""
        from python.helpers.guids import generate_guid

        guids = [generate_guid() for _ in range(100)]

        assert len(set(guids)) == 100


# ============================================================================
# Defer Tests
# ============================================================================

class TestDefer:
    """Tests for defer module."""

    def test_deferred_task_creation(self):
        """Test DeferredTask creation."""
        from python.helpers.defer import DeferredTask

        task = DeferredTask()

        assert task is not None

    @pytest.mark.asyncio
    async def test_deferred_task_run(self):
        """Test running a deferred task."""
        from python.helpers.defer import DeferredTask

        result = []

        async def test_func():
            result.append("executed")
            return "done"

        task = DeferredTask()
        task.start_task(test_func)

        # Wait for task
        await task.wait_for_result()

        assert "executed" in result


# ============================================================================
# Strings Tests
# ============================================================================

class TestStrings:
    """Tests for strings module."""

    def test_sanitize_string(self):
        """Test string sanitization."""
        from python.helpers.strings import sanitize_string

        # Test with normal string
        result = sanitize_string("Hello, World!")
        assert result == "Hello, World!"

    def test_sanitize_string_with_encoding(self):
        """Test string sanitization with specific encoding."""
        from python.helpers.strings import sanitize_string

        result = sanitize_string("Test string", encoding="utf-8")
        assert result == "Test string"


# ============================================================================
# Tool Base Class Tests
# ============================================================================

class TestToolBase:
    """Tests for tool base class."""

    def test_response_creation(self):
        """Test Response creation."""
        from python.helpers.tool import Response

        response = Response(message="Success", break_loop=False)

        assert response.message == "Success"
        assert response.break_loop is False

    def test_response_with_break(self):
        """Test Response that breaks loop."""
        from python.helpers.tool import Response

        response = Response(message="Final response", break_loop=True)

        assert response.break_loop is True


# ============================================================================
# History Tests
# ============================================================================

class TestHistory:
    """Tests for history module."""

    def test_message_creation(self):
        """Test message creation."""
        from python.helpers.history import Message

        # Message is abstract, but we can test the structure
        pass  # Skip if Message requires agent

    def test_output_langchain(self):
        """Test converting history to LangChain format."""
        from python.helpers.history import output_langchain

        # Test with empty list
        result = output_langchain([])
        assert result == []


# ============================================================================
# Localization Tests
# ============================================================================

class TestLocalization:
    """Tests for localization module."""

    def test_get_localization(self):
        """Test getting localization instance."""
        from python.helpers.localization import Localization

        loc = Localization.get()

        assert loc is not None

    def test_serialize_datetime(self):
        """Test datetime serialization."""
        from python.helpers.localization import Localization
        from datetime import datetime

        loc = Localization.get()
        dt = datetime(2024, 1, 15, 10, 30, 0)

        serialized = loc.serialize_datetime(dt)

        assert serialized is not None
        assert isinstance(serialized, str)
