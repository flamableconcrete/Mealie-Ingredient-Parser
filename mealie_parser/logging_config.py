"""Logging configuration for Mealie Ingredient Parser."""

import sys
from datetime import datetime
from pathlib import Path

from loguru import logger


def setup_logging(log_level="INFO"):
    """
    Configure logging with both file and console handlers using loguru.

    Creates a logs directory and writes to timestamped log files.
    Also outputs to console for immediate feedback.
    """
    # Remove default handler
    logger.remove()

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"mealie_parser_{timestamp}.log"

    # File handler - captures all logs with DEBUG level
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} - {name}:{function}:{line} - {level} - {message}",
        level="DEBUG",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )

    # Console handler - only errors and critical
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} - {name}:{function}:{line} - {level} - {message}",
        level="ERROR",
        colorize=True,
    )

    # Log startup
    logger.info(f"Logging initialized. Log file: {log_file}")
    logger.info(f"Log level: {log_level}")

    return log_file
