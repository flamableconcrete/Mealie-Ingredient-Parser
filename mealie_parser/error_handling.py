"""Error handling utilities for API operations with retry logic."""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from functools import wraps

import aiohttp
from loguru import logger


# Error Category Classification
class ErrorCategory(Enum):
    """Categories for error classification."""

    NETWORK = "network"
    SERVER = "server"
    CLIENT = "client"
    AUTH = "auth"
    UNKNOWN = "unknown"


# Custom Exception Hierarchy
class APIError(Exception):
    """Base class for API errors."""

    pass


class TransientAPIError(APIError):
    """Errors that should be retried (network, 5xx)."""

    pass


class PermanentAPIError(APIError):
    """Errors that should not be retried (4xx, auth)."""

    pass


class RateLimitError(TransientAPIError):
    """Rate limiting errors (429)."""

    pass


@dataclass
class BatchOperationResult:
    """
    Result of a batch operation with error tracking.

    Attributes
    ----------
    successful : list[str]
        List of successful ingredient IDs
    failed : list[dict]
        List of failed operations with id and error
    total : int
        Total number of operations attempted
    """

    successful: list[str] = field(default_factory=list)
    failed: list[dict] = field(default_factory=list)
    total: int = 0

    def add_success(self, ingredient_id: str) -> None:
        """Record successful ingredient update."""
        self.successful.append(ingredient_id)

    def add_failure(self, ingredient_id: str, error_message: str) -> None:
        """Record failed ingredient update."""
        self.failed.append({"id": ingredient_id, "error": error_message})

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 0.0
        return (len(self.successful) / self.total) * 100


def classify_http_error(status_code: int) -> type[APIError]:
    """
    Classify HTTP error by status code.

    Parameters
    ----------
    status_code : int
        HTTP status code

    Returns
    -------
    type[APIError]
        Appropriate error class (TransientAPIError or PermanentAPIError)

    Examples
    --------
    >>> error_class = classify_http_error(500)
    >>> raise error_class("Server error")
    """
    # Transient errors (should retry)
    if status_code >= 500:
        logger.debug(f"Classified status {status_code} as TransientAPIError (server error)")
        return TransientAPIError
    if status_code == 429:
        logger.debug(f"Classified status {status_code} as RateLimitError")
        return RateLimitError

    # Permanent errors (should not retry)
    if status_code in [401, 403]:
        logger.debug(f"Classified status {status_code} as PermanentAPIError (auth)")
        return PermanentAPIError
    if status_code >= 400:
        logger.debug(f"Classified status {status_code} as PermanentAPIError (client)")
        return PermanentAPIError

    # Unknown - default to permanent
    logger.debug(f"Classified status {status_code} as PermanentAPIError (unknown)")
    return PermanentAPIError


def categorize_error(exception: Exception) -> ErrorCategory:
    """
    Categorize exception into error category.

    Parameters
    ----------
    exception : Exception
        Exception to categorize

    Returns
    -------
    ErrorCategory
        Error category enum value
    """
    if isinstance(exception, (asyncio.TimeoutError, aiohttp.ClientConnectorError)):
        return ErrorCategory.NETWORK
    if isinstance(exception, TransientAPIError):
        return ErrorCategory.SERVER
    if isinstance(exception, PermanentAPIError):
        # Check if auth error
        if "auth" in str(exception).lower() or "401" in str(exception) or "403" in str(exception):
            return ErrorCategory.AUTH
        return ErrorCategory.CLIENT
    return ErrorCategory.UNKNOWN


def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 10.0) -> float:
    """
    Calculate exponential backoff delay.

    Parameters
    ----------
    attempt : int
        Current retry attempt (0-indexed)
    base_delay : float
        Base delay in seconds (default: 1.0)
    max_delay : float
        Maximum delay in seconds (default: 10.0)

    Returns
    -------
    float
        Delay in seconds before next retry

    Examples
    --------
    >>> calculate_backoff_delay(0)  # First retry
    1.0
    >>> calculate_backoff_delay(1)  # Second retry
    2.0
    >>> calculate_backoff_delay(2)  # Third retry
    4.0
    """
    delay = base_delay * (2**attempt)
    return min(delay, max_delay)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    on_retry: Callable | None = None,
):
    """
    Decorator for automatic retry with exponential backoff.

    Parameters
    ----------
    max_retries : int
        Maximum number of retry attempts (default: 3)
    base_delay : float
        Base delay in seconds (default: 1.0)
    max_delay : float
        Maximum delay in seconds (default: 10.0)
    on_retry : Optional[Callable]
        Callback function called on each retry: on_retry(attempt, delay, error)

    Examples
    --------
    >>> @retry_with_backoff(max_retries=3)
    ... async def fetch_data(session, url):
    ...     async with session.get(url) as r:
    ...         r.raise_for_status()
    ...         return await r.json()
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except TransientAPIError as e:
                    if attempt >= max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}")
                        raise
                    delay = calculate_backoff_delay(attempt, base_delay, max_delay)
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} after {delay}s: {e}")
                    if on_retry:
                        on_retry(attempt, delay, e)
                    await asyncio.sleep(delay)
                except PermanentAPIError as e:
                    logger.error(f"Permanent error in {func.__name__}, not retrying: {e}")
                    raise
                except Exception as e:
                    # Unknown error - treat as permanent, don't retry
                    logger.error(
                        f"Unknown error in {func.__name__}, not retrying: {e}",
                        exc_info=True,
                    )
                    raise
            return None

        return wrapper

    return decorator


class ErrorMessageFormatter:
    """Formatter for user-friendly error messages."""

    @staticmethod
    def format_error_for_user(error: APIError) -> str:
        """
        Convert technical error to user-friendly message.

        Parameters
        ----------
        error : APIError
            Technical error to format

        Returns
        -------
        str
            User-friendly error message with actionable guidance

        Examples
        --------
        >>> formatter = ErrorMessageFormatter()
        >>> message = formatter.format_error_for_user(TransientAPIError("Timeout"))
        >>> print(message)
        Network error - retrying automatically...
        """
        error_str = str(error).lower()

        # Transient errors
        if isinstance(error, RateLimitError):
            return "Server busy - waiting before retry..."
        if isinstance(error, TransientAPIError):
            if "timeout" in error_str:
                return "Network timeout - retrying automatically..."
            if "connection" in error_str or "connect" in error_str:
                return "Cannot reach Mealie server - retrying..."
            return "Server error - retrying automatically..."

        # Permanent errors
        if isinstance(error, PermanentAPIError):
            if "401" in error_str or "unauthorized" in error_str:
                return "Authentication failed - check API key in .env file"
            if "403" in error_str or "forbidden" in error_str:
                return "Access denied - check API key permissions"
            if "404" in error_str or "not found" in error_str:
                return "Resource not found - may have been deleted"
            if "400" in error_str or "bad request" in error_str:
                return "Invalid request - please check your input"
            return "Request failed - please try again"

        # Unknown errors
        return "An unexpected error occurred - check logs for details"


@dataclass
class ErrorReport:
    """
    Structured error report for batch operations.

    Attributes
    ----------
    timestamp : str
        ISO timestamp of report creation
    operation_type : str
        Type of operation (e.g., "create_unit_batch")
    pattern_text : str
        Pattern being processed
    total_ingredients : int
        Total number of ingredients
    succeeded : int
        Number of successful operations
    failed : int
        Number of failed operations
    total_retries : int
        Total number of retry attempts
    errors : list[dict]
        Detailed error information
    """

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    operation_type: str = ""
    pattern_text: str = ""
    total_ingredients: int = 0
    succeeded: int = 0
    failed: int = 0
    total_retries: int = 0
    errors: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert error report to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "operation_type": self.operation_type,
            "pattern_text": self.pattern_text,
            "total_ingredients": self.total_ingredients,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "total_retries": self.total_retries,
            "errors": self.errors,
        }


class ErrorReportExporter:
    """Export error reports to JSON files."""

    @staticmethod
    def generate_error_report(
        result: BatchOperationResult,
        operation_type: str,
        pattern_text: str = "",
    ) -> ErrorReport:
        """
        Generate error report from batch operation result.

        Parameters
        ----------
        result : BatchOperationResult
            Batch operation result with errors
        operation_type : str
            Type of operation performed
        pattern_text : str, optional
            Pattern text being processed

        Returns
        -------
        ErrorReport
            Structured error report
        """
        report = ErrorReport(
            operation_type=operation_type,
            pattern_text=pattern_text,
            total_ingredients=result.total,
            succeeded=len(result.successful),
            failed=len(result.failed),
            total_retries=0,  # TODO: Track retries in result
            errors=result.failed,
        )

        logger.info(f"Generated error report: {report.succeeded} succeeded, {report.failed} failed")

        return report

    @staticmethod
    def export_error_report(report: ErrorReport, filepath: str) -> None:
        """
        Export error report to JSON file.

        Parameters
        ----------
        report : ErrorReport
            Error report to export
        filepath : str
            Path to save JSON file

        Examples
        --------
        >>> exporter = ErrorReportExporter()
        >>> exporter.export_error_report(report, "error-report.json")
        """
        import json

        try:
            from pathlib import Path

            with Path(filepath).open("w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, indent=2)
            logger.info(f"Exported error report to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export error report to {filepath}: {e}", exc_info=True)
            raise
