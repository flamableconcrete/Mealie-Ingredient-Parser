"""Logging configuration for Mealie Ingredient Parser."""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level=logging.INFO):
    """
    Configure logging with both file and console handlers.

    Creates a logs directory and writes to timestamped log files.
    Also outputs to console for immediate feedback.
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"mealie_parser_{timestamp}.log"

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler - captures all logs
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler - only warnings and errors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")

    return log_file


def get_logger(name):
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)
