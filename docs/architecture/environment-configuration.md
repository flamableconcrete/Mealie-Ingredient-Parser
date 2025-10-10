# Environment Configuration

## Environment Variables

```bash
# .env file template

# === MEALIE API CONFIGURATION ===
MEALIE_URL=https://your-mealie-instance.com/api
MEALIE_API_KEY=your_api_key_here

# === APPLICATION CONFIGURATION (Optional) ===
LOG_LEVEL=INFO
LOG_FILE=mealie_parser.log
STATE_FILE=.mealie_parser_state.json
SIMILARITY_THRESHOLD=0.85
MAX_RETRIES=3
API_TIMEOUT=10
```

## Configuration Loading

```python
"""Configuration management module."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class AppConfig:
    """Application configuration loaded from environment variables."""

    mealie_url: str
    mealie_api_key: str
    log_level: str = "INFO"
    log_file: Path = Path("mealie_parser.log")
    state_file: Path = Path(".mealie_parser_state.json")
    similarity_threshold: float = 0.85
    max_retries: int = 3
    api_timeout: int = 10

    @classmethod
    def from_env(cls) -> AppConfig:
        """Load configuration from environment variables."""
        load_dotenv()

        mealie_url = os.getenv("MEALIE_URL")
        mealie_api_key = os.getenv("MEALIE_API_KEY")

        if not mealie_url or not mealie_api_key:
            raise ValueError("MEALIE_URL and MEALIE_API_KEY required")

        return cls(
            mealie_url=mealie_url.rstrip("/"),
            mealie_api_key=mealie_api_key,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            log_file=Path(os.getenv("LOG_FILE", "mealie_parser.log")),
            state_file=Path(os.getenv("STATE_FILE", ".mealie_parser_state.json")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.85")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            api_timeout=int(os.getenv("API_TIMEOUT", "10")),
        )
```

## Security Considerations

1. **Credential storage:** API keys in `.env` file only, never committed
2. **File permissions:** `.env` should have restricted permissions (`chmod 600`)
3. **Gitignore:** `.env` must be in `.gitignore`
4. **No logging of secrets:** API keys redacted from logs
5. **Example file:** Provide `.env.example` with placeholders

---
