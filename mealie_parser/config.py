"""Configuration and environment setup."""

import os

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

API_URL = os.getenv("MEALIE_URL")
API_KEY = os.getenv("MEALIE_API_KEY")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))

# Column width configurations for batch mode tables
COLUMN_WIDTH_PATTERN_TEXT = int(os.getenv("COLUMN_WIDTH_PATTERN_TEXT", "50"))
COLUMN_WIDTH_STATUS = int(os.getenv("COLUMN_WIDTH_STATUS", "15"))
COLUMN_WIDTH_PARSED_UNIT = int(os.getenv("COLUMN_WIDTH_PARSED_UNIT", "40"))
COLUMN_WIDTH_PARSED_FOOD = int(os.getenv("COLUMN_WIDTH_PARSED_FOOD", "40"))
COLUMN_WIDTH_CREATE = int(os.getenv("COLUMN_WIDTH_CREATE", "8"))

if not API_KEY:
    raise RuntimeError("❌ MEALIE_API_KEY not found in environment. Add it to your .env file.")

headers = {"Authorization": f"Bearer {API_KEY}"}
