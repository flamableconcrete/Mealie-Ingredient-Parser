"""Session persistence manager for saving and loading session state."""

import json
from pathlib import Path

from loguru import logger

from mealie_parser.models.session_state import SessionState


SESSION_DIR = Path(".ai")
SESSION_FILE = SESSION_DIR / "session-state.json"


class SessionManager:
    """Manager for session state persistence."""

    @staticmethod
    def ensure_session_dir() -> None:
        """Ensure session directory exists."""
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured session directory exists: {SESSION_DIR}")

    @staticmethod
    def save_session(state: SessionState) -> None:
        """
        Save session state to JSON file with atomic write.

        Parameters
        ----------
        state : SessionState
            Session state to save

        Examples
        --------
        >>> manager = SessionManager()
        >>> manager.save_session(session_state)
        """
        SessionManager.ensure_session_dir()

        try:
            # Atomic write: write to temp file, then rename
            temp_file = SESSION_FILE.with_suffix(".tmp")

            with temp_file.open("w", encoding="utf-8") as f:
                json.dump(state.to_dict(), f, indent=2)

            # Atomic rename (works on all platforms)
            temp_file.replace(SESSION_FILE)

            logger.info(f"Saved session state: {state.summary}")
            logger.debug(f"Session file: {SESSION_FILE}")

        except Exception as e:
            logger.error(f"Failed to save session state: {e}", exc_info=True)
            raise

    @staticmethod
    def load_session() -> SessionState | None:
        """
        Load session state from JSON file.

        Returns
        -------
        Optional[SessionState]
            Loaded session state, or None if file doesn't exist or is invalid

        Examples
        --------
        >>> manager = SessionManager()
        >>> state = manager.load_session()
        >>> if state:
        ...     print(f"Resumed session: {state.summary}")
        """
        if not SESSION_FILE.exists():
            logger.debug("No session file found")
            return None

        try:
            with SESSION_FILE.open(encoding="utf-8") as f:
                data = json.load(f)

            state = SessionState.from_dict(data)
            logger.info(f"Loaded session state: {state.summary}")
            return state

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse session file (corrupted JSON): {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load session state: {e}", exc_info=True)
            return None

    @staticmethod
    def clear_session() -> None:
        """
        Delete session file.

        Examples
        --------
        >>> manager = SessionManager()
        >>> manager.clear_session()
        """
        if SESSION_FILE.exists():
            try:
                SESSION_FILE.unlink()
                logger.info("Cleared session state file")
            except Exception as e:
                logger.error(f"Failed to clear session file: {e}", exc_info=True)
                raise
        else:
            logger.debug("No session file to clear")

    @staticmethod
    def session_exists() -> bool:
        """
        Check if session file exists.

        Returns
        -------
        bool
            True if session file exists, False otherwise

        Examples
        --------
        >>> manager = SessionManager()
        >>> if manager.session_exists():
        ...     print("Session found!")
        """
        exists = SESSION_FILE.exists()
        logger.debug(f"Session file exists: {exists}")
        return exists
