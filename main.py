#!/usr/bin/env python3
"""Entry point for the Mealie Ingredient Parser application."""

from loguru import logger

from mealie_parser.app import MealieParserApp
from mealie_parser.logging_config import setup_logging


def main():
    """Run the Mealie Parser application."""
    # Initialize logging
    log_file = setup_logging(log_level="INFO")

    try:
        logger.info("=" * 60)
        logger.info("Mealie Ingredient Parser Starting")
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 60)

        app = MealieParserApp()
        app.run()

        logger.info("Application exited normally")
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        raise


if __name__ == "__main__":
    main()
