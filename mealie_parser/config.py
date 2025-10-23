"""Configuration and environment setup."""

import os

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

API_URL = os.getenv("MEALIE_URL")
API_KEY = os.getenv("MEALIE_API_KEY")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))

if not API_KEY:
    raise RuntimeError("❌ MEALIE_API_KEY not found in environment. Add it to your .env file.")

headers = {"Authorization": f"Bearer {API_KEY}"}
