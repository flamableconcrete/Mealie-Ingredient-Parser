"""Session state management for progress persistence."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from loguru import logger


@dataclass
class SessionState:
    """
    Session state for persisting batch operation progress.

    Attributes
    ----------
    session_id : str
        Unique session identifier (UUID)
    created_at : str
        ISO timestamp of session creation
    last_updated : str
        ISO timestamp of last session update
    mode : str
        Operation mode ("batch" or "sequential")
    processed_patterns : list[str]
        List of pattern texts marked as completed
    skipped_patterns : list[str]
        List of pattern texts marked as skipped
    created_units : dict[str, str]
        Mapping of pattern_text -> unit_id
    created_foods : dict[str, str]
        Mapping of pattern_text -> food_id
    current_operation : Optional[dict]
        Details of in-progress operation
    parsing_started : bool
        Flag indicating if parsing workflow has started
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    mode: str = "batch"
    processed_patterns: list[str] = field(default_factory=list)
    skipped_patterns: list[str] = field(default_factory=list)
    created_units: dict[str, str] = field(default_factory=dict)
    created_foods: dict[str, str] = field(default_factory=dict)
    current_operation: dict | None = None
    parsing_started: bool = False

    def to_dict(self) -> dict:
        """
        Serialize session state to dictionary for JSON encoding.

        Returns
        -------
        dict
            Dictionary representation of session state
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "mode": self.mode,
            "processed_patterns": self.processed_patterns,
            "skipped_patterns": self.skipped_patterns,
            "created_units": self.created_units,
            "created_foods": self.created_foods,
            "current_operation": self.current_operation,
            "parsing_started": self.parsing_started,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        """
        Deserialize session state from dictionary.

        Parameters
        ----------
        data : dict
            Dictionary representation of session state

        Returns
        -------
        SessionState
            Reconstructed session state object
        """
        return cls(**data)

    def update_timestamp(self) -> None:
        """Update last_updated timestamp to current time."""
        self.last_updated = datetime.now(UTC).isoformat()
        logger.debug(f"Updated session timestamp: {self.last_updated}")

    def add_processed_pattern(self, pattern_text: str) -> None:
        """
        Mark pattern as processed.

        Parameters
        ----------
        pattern_text : str
            Pattern text to mark as processed
        """
        if pattern_text not in self.processed_patterns:
            self.processed_patterns.append(pattern_text)
            self.update_timestamp()
            logger.info(f"Marked pattern as processed: '{pattern_text}'")

    def add_skipped_pattern(self, pattern_text: str) -> None:
        """
        Mark pattern as skipped.

        Parameters
        ----------
        pattern_text : str
            Pattern text to mark as skipped
        """
        if pattern_text not in self.skipped_patterns:
            self.skipped_patterns.append(pattern_text)
            self.update_timestamp()
            logger.info(f"Marked pattern as skipped: '{pattern_text}'")

    def add_created_unit(self, pattern_text: str, unit_id: str) -> None:
        """
        Record created unit mapping.

        Parameters
        ----------
        pattern_text : str
            Pattern text that triggered unit creation
        unit_id : str
            ID of created unit
        """
        self.created_units[pattern_text] = unit_id
        self.update_timestamp()
        logger.info(f"Recorded created unit: '{pattern_text}' -> {unit_id}")

    def add_created_food(self, pattern_text: str, food_id: str) -> None:
        """
        Record created food mapping.

        Parameters
        ----------
        pattern_text : str
            Pattern text that triggered food creation
        food_id : str
            ID of created food
        """
        self.created_foods[pattern_text] = food_id
        self.update_timestamp()
        logger.info(f"Recorded created food: '{pattern_text}' -> {food_id}")

    @property
    def total_processed(self) -> int:
        """Get total number of processed patterns (completed + skipped)."""
        return len(self.processed_patterns) + len(self.skipped_patterns)

    @property
    def summary(self) -> str:
        """Get human-readable summary of session state."""
        return (
            f"Session {self.session_id[:8]}: "
            f"{len(self.processed_patterns)} processed, "
            f"{len(self.skipped_patterns)} skipped, "
            f"{len(self.created_units)} units created, "
            f"{len(self.created_foods)} foods created"
        )
