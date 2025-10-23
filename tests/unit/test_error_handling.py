"""Unit tests for error handling utilities."""

import pytest

from mealie_parser.error_handling import (
    BatchOperationResult,
    ErrorCategory,
    ErrorMessageFormatter,
    ErrorReport,
    ErrorReportExporter,
    PermanentAPIError,
    RateLimitError,
    TransientAPIError,
    calculate_backoff_delay,
    categorize_error,
    classify_http_error,
    retry_with_backoff,
)


class TestErrorClassification:
    """Tests for error classification functions."""

    def test_classify_5xx_as_transient(self):
        """Test 5xx status codes classified as transient."""
        assert classify_http_error(500) == TransientAPIError
        assert classify_http_error(502) == TransientAPIError
        assert classify_http_error(503) == TransientAPIError
        assert classify_http_error(504) == TransientAPIError

    def test_classify_429_as_rate_limit(self):
        """Test 429 status code classified as rate limit."""
        assert classify_http_error(429) == RateLimitError

    def test_classify_401_403_as_permanent_auth(self):
        """Test auth errors classified as permanent."""
        assert classify_http_error(401) == PermanentAPIError
        assert classify_http_error(403) == PermanentAPIError

    def test_classify_4xx_as_permanent(self):
        """Test 4xx client errors classified as permanent."""
        assert classify_http_error(400) == PermanentAPIError
        assert classify_http_error(404) == PermanentAPIError
        assert classify_http_error(409) == PermanentAPIError

    def test_categorize_network_errors(self):
        """Test network errors categorized correctly."""
        timeout_error = TimeoutError()
        assert categorize_error(timeout_error) == ErrorCategory.NETWORK

    def test_categorize_transient_errors(self):
        """Test transient errors categorized as server."""
        error = TransientAPIError("Server error")
        assert categorize_error(error) == ErrorCategory.SERVER

    def test_categorize_auth_errors(self):
        """Test auth errors categorized correctly."""
        error = PermanentAPIError("401 Unauthorized")
        assert categorize_error(error) == ErrorCategory.AUTH

    def test_categorize_client_errors(self):
        """Test client errors categorized correctly."""
        error = PermanentAPIError("400 Bad Request")
        assert categorize_error(error) == ErrorCategory.CLIENT

    def test_categorize_unknown_errors(self):
        """Test unknown errors categorized correctly."""
        error = Exception("Unknown error")
        assert categorize_error(error) == ErrorCategory.UNKNOWN


class TestBackoffCalculation:
    """Tests for exponential backoff calculation."""

    def test_backoff_first_attempt(self):
        """Test first retry delay."""
        delay = calculate_backoff_delay(0, base_delay=1.0)
        assert delay == 1.0

    def test_backoff_second_attempt(self):
        """Test second retry delay."""
        delay = calculate_backoff_delay(1, base_delay=1.0)
        assert delay == 2.0

    def test_backoff_third_attempt(self):
        """Test third retry delay."""
        delay = calculate_backoff_delay(2, base_delay=1.0)
        assert delay == 4.0

    def test_backoff_max_delay_capped(self):
        """Test delay capped at max_delay."""
        delay = calculate_backoff_delay(10, base_delay=1.0, max_delay=10.0)
        assert delay == 10.0

    def test_backoff_custom_base(self):
        """Test custom base delay."""
        delay = calculate_backoff_delay(0, base_delay=2.0)
        assert delay == 2.0


class TestRetryDecorator:
    """Tests for retry_with_backoff decorator."""

    @pytest.mark.asyncio
    async def test_no_retry_on_success(self):
        """Test no retry when function succeeds."""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self):
        """Test retry on transient error."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        async def transient_error_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientAPIError("Server error")
            return "success"

        result = await transient_error_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_permanent_error(self):
        """Test no retry on permanent error."""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        async def permanent_error_func():
            nonlocal call_count
            call_count += 1
            raise PermanentAPIError("Auth failed")

        with pytest.raises(PermanentAPIError):
            await permanent_error_func()

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test max retries exceeded raises error."""
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise TransientAPIError("Always fails")

        with pytest.raises(TransientAPIError):
            await always_fails()

        assert call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_on_retry_callback(self):
        """Test on_retry callback is called."""
        retry_calls = []

        def on_retry(attempt, delay, error):
            retry_calls.append((attempt, delay))

        @retry_with_backoff(max_retries=2, base_delay=0.01, on_retry=on_retry)
        async def failing_func():
            if len(retry_calls) < 1:
                raise TransientAPIError("Fail once")
            return "success"

        await failing_func()
        assert len(retry_calls) == 1


class TestBatchOperationResult:
    """Tests for BatchOperationResult dataclass."""

    def test_create_empty_result(self):
        """Test creating empty result."""
        result = BatchOperationResult()
        assert result.successful == []
        assert result.failed == []
        assert result.total == 0

    def test_add_success(self):
        """Test adding successful operations."""
        result = BatchOperationResult()
        result.add_success("id1")
        result.add_success("id2")
        assert len(result.successful) == 2
        assert "id1" in result.successful

    def test_add_failure(self):
        """Test adding failed operations."""
        result = BatchOperationResult()
        result.add_failure("id1", "Network error")
        assert len(result.failed) == 1
        assert result.failed[0]["id"] == "id1"
        assert result.failed[0]["error"] == "Network error"

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = BatchOperationResult(total=10)
        for i in range(8):
            result.add_success(f"id{i}")
        for i in range(2):
            result.add_failure(f"fail{i}", "Error")

        assert result.success_rate == 80.0

    def test_success_rate_zero_total(self):
        """Test success rate with zero total."""
        result = BatchOperationResult()
        assert result.success_rate == 0.0


class TestErrorMessageFormatter:
    """Tests for ErrorMessageFormatter."""

    def test_format_transient_timeout(self):
        """Test formatting timeout error."""
        formatter = ErrorMessageFormatter()
        error = TransientAPIError("Timeout after 30s")
        message = formatter.format_error_for_user(error)
        assert "timeout" in message.lower()
        assert "retry" in message.lower()

    def test_format_transient_connection(self):
        """Test formatting connection error."""
        formatter = ErrorMessageFormatter()
        error = TransientAPIError("Connection refused")
        message = formatter.format_error_for_user(error)
        assert "server" in message.lower() or "connection" in message.lower()

    def test_format_rate_limit(self):
        """Test formatting rate limit error."""
        formatter = ErrorMessageFormatter()
        error = RateLimitError("Too many requests")
        message = formatter.format_error_for_user(error)
        assert "busy" in message.lower() or "wait" in message.lower()

    def test_format_auth_401(self):
        """Test formatting 401 error."""
        formatter = ErrorMessageFormatter()
        error = PermanentAPIError("401 Unauthorized")
        message = formatter.format_error_for_user(error)
        assert "auth" in message.lower() or "api key" in message.lower()

    def test_format_auth_403(self):
        """Test formatting 403 error."""
        formatter = ErrorMessageFormatter()
        error = PermanentAPIError("403 Forbidden")
        message = formatter.format_error_for_user(error)
        assert "access" in message.lower() or "permission" in message.lower()

    def test_format_not_found(self):
        """Test formatting 404 error."""
        formatter = ErrorMessageFormatter()
        error = PermanentAPIError("404 Not Found")
        message = formatter.format_error_for_user(error)
        assert "not found" in message.lower()

    def test_format_bad_request(self):
        """Test formatting 400 error."""
        formatter = ErrorMessageFormatter()
        error = PermanentAPIError("400 Bad Request")
        message = formatter.format_error_for_user(error)
        assert "invalid" in message.lower() or "check" in message.lower()


class TestErrorReportExporter:
    """Tests for ErrorReportExporter."""

    def test_generate_error_report(self):
        """Test generating error report from result."""
        result = BatchOperationResult(total=10)
        for i in range(8):
            result.add_success(f"id{i}")
        for i in range(2):
            result.add_failure(f"fail{i}", "Network error")

        exporter = ErrorReportExporter()
        report = exporter.generate_error_report(result, "create_unit_batch", "tsp")

        assert report.operation_type == "create_unit_batch"
        assert report.pattern_text == "tsp"
        assert report.total_ingredients == 10
        assert report.succeeded == 8
        assert report.failed == 2

    def test_error_report_to_dict(self):
        """Test error report serialization."""
        report = ErrorReport(
            operation_type="test_op",
            pattern_text="test_pattern",
            total_ingredients=5,
            succeeded=3,
            failed=2,
        )

        data = report.to_dict()
        assert data["operation_type"] == "test_op"
        assert data["pattern_text"] == "test_pattern"
        assert data["total_ingredients"] == 5
        assert "timestamp" in data

    def test_export_error_report_creates_file(self, tmp_path):
        """Test exporting error report to JSON file."""
        import json

        report = ErrorReport(operation_type="test_op", total_ingredients=5, succeeded=3, failed=2)

        filepath = tmp_path / "error-report.json"
        exporter = ErrorReportExporter()
        exporter.export_error_report(report, str(filepath))

        assert filepath.exists()

        # Verify JSON content
        with filepath.open() as f:
            data = json.load(f)
        assert data["operation_type"] == "test_op"
