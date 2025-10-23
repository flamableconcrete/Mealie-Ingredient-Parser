"""Pattern grouping and batch operation data models for batch ingredient processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal


class PatternStatus(str, Enum):
    """
    Comprehensive state machine for pattern processing lifecycle.

    States:
        PENDING: Initial state - pattern identified but not yet processed
        PARSING: Automated parsing in progress (NLP/Brute/OpenAI)
        MATCHED: Pattern successfully matched to existing unit/food in database
        UNMATCHED: Pattern parsed but no database match found - needs user decision
        QUEUED: Pattern ready for batch creation (user has specified details)
        IGNORE: Pattern marked to skip - excluded from batch operations
        ERROR: Processing failed - see error_message for details

    Valid State Transitions:
        PENDING → PARSING (batch parse initiated)
        PARSING → MATCHED (parse found database match)
        PARSING → UNMATCHED (parse succeeded but no match)
        PARSING → ERROR (parse failed)
        UNMATCHED → QUEUED (user specifies creation details)
        UNMATCHED → PARSING (user initiates re-parse)
        QUEUED → MATCHED (batch POST succeeded)
        QUEUED → ERROR (batch POST failed)
        ERROR → IGNORE (user gives up on this pattern)
        ERROR → PARSING (user retries after fixing error)
    """

    PENDING = "pending"
    PARSING = "parsing"
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    QUEUED = "queued"
    IGNORE = "ignore"
    ERROR = "error"

    @classmethod
    def get_valid_transitions(cls) -> dict[str, set[str]]:
        """
        Get mapping of valid state transitions.

        Returns:
            Dictionary mapping each state to its set of valid next states
        """
        return {
            cls.PENDING: {cls.PARSING},
            cls.PARSING: {cls.MATCHED, cls.UNMATCHED, cls.ERROR},
            cls.MATCHED: set(),
            cls.UNMATCHED: {cls.QUEUED, cls.PARSING},  # Allow re-parsing
            cls.QUEUED: {cls.MATCHED, cls.ERROR, cls.UNMATCHED},  # Allow toggling back
            cls.IGNORE: set(),
            cls.ERROR: {cls.IGNORE, cls.PARSING},  # Allow retry after error
        }

    def can_transition_to(self, target_status: PatternStatus) -> bool:
        """
        Check if transition from this state to target state is valid.

        Args:
            target_status: The desired next state

        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = self.get_valid_transitions()
        return target_status.value in valid_transitions.get(self.value, set())

    def validate_transition(self, target_status: PatternStatus) -> None:
        """
        Validate state transition and raise error if invalid.

        Args:
            target_status: The desired next state

        Raises:
            ValueError: If the transition is not valid
        """
        if not self.can_transition_to(target_status):
            valid_next = self.get_valid_transitions().get(self.value, set())
            raise ValueError(
                f"Invalid state transition: {self.value} → {target_status.value}. "
                f"Valid transitions from {self.value}: {', '.join(sorted(valid_next))}"
            )


@dataclass
class PatternGroup:
    """
    Represents a group of ingredients sharing the same unparsed unit or food pattern.

    Note: A single pattern can have both unit and food components that need separate parsing.
    For example, "2 cups flour" has unit="cups" and food="flour", each with independent status.

    Attributes:
        pattern_text: The normalized pattern text (lowercase, trimmed)
        ingredient_ids: List of ingredient IDs matching this pattern
        recipe_ids: List of recipe IDs containing ingredients with this pattern
        suggested_similar_patterns: List of potentially related patterns
        unit_status: Status of unit parsing/matching (PENDING, PARSING, MATCHED, etc.)
        food_status: Status of food parsing/matching (PENDING, PARSING, MATCHED, etc.)
        parsed_unit: Parsed unit name from NLP parser (if available)
        parsed_food: Parsed food name from NLP parser (if available)
        unit_confidence: Confidence score for unit parsing (0.0-1.0)
        food_confidence: Confidence score for food parsing (0.0-1.0)
        matched_unit_id: ID of matched unit in database (for MATCHED state)
        matched_food_id: ID of matched food in database (for MATCHED state)
        unit_error_message: Error details for unit parsing (for ERROR state)
        food_error_message: Error details for food parsing (for ERROR state)
        error_timestamp: When error occurred (for ERROR state)
    """

    pattern_text: str
    ingredient_ids: list[str] = field(default_factory=list)
    recipe_ids: list[str] = field(default_factory=list)
    suggested_similar_patterns: list[str] = field(default_factory=list)
    unit_status: PatternStatus = PatternStatus.PENDING
    food_status: PatternStatus = PatternStatus.PENDING
    parsed_unit: str = ""
    parsed_food: str = ""
    unit_confidence: float = 0.0
    food_confidence: float = 0.0
    matched_unit_id: str | None = None
    matched_food_id: str | None = None
    unit_error_message: str | None = None
    food_error_message: str | None = None
    error_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        """Validate pattern_text is not empty."""
        if not self.pattern_text or not self.pattern_text.strip():
            raise ValueError("pattern_text must not be empty")
        # Normalize pattern_text to ensure consistency
        self.pattern_text = self.pattern_text.strip()

    def transition_unit_to(self, new_status: PatternStatus, error_msg: str | None = None) -> None:
        """
        Transition unit status to a new status with validation.

        Args:
            new_status: The target status for unit
            error_msg: Optional error message (required if transitioning to ERROR)

        Raises:
            ValueError: If the transition is invalid or required data is missing
        """
        # Validate transition
        self.unit_status.validate_transition(new_status)

        # Handle ERROR state
        if new_status == PatternStatus.ERROR:
            if not error_msg:
                raise ValueError("error_msg is required when transitioning to ERROR state")
            self.unit_error_message = error_msg
            self.error_timestamp = datetime.utcnow()
        elif self.unit_status == PatternStatus.ERROR and new_status != PatternStatus.ERROR:
            # Clearing error state - reset error fields
            self.unit_error_message = None
            if not self.food_error_message:
                self.error_timestamp = None

        # Update unit status
        self.unit_status = new_status

    def transition_food_to(self, new_status: PatternStatus, error_msg: str | None = None) -> None:
        """
        Transition food status to a new status with validation.

        Args:
            new_status: The target status for food
            error_msg: Optional error message (required if transitioning to ERROR)

        Raises:
            ValueError: If the transition is invalid or required data is missing
        """
        # Validate transition
        self.food_status.validate_transition(new_status)

        # Handle ERROR state
        if new_status == PatternStatus.ERROR:
            if not error_msg:
                raise ValueError("error_msg is required when transitioning to ERROR state")
            self.food_error_message = error_msg
            self.error_timestamp = datetime.utcnow()
        elif self.food_status == PatternStatus.ERROR and new_status != PatternStatus.ERROR:
            # Clearing error state - reset error fields
            self.food_error_message = None
            if not self.unit_error_message:
                self.error_timestamp = None

        # Update food status
        self.food_status = new_status

    def set_matched(self, unit_id: str | None = None, food_id: str | None = None) -> None:
        """
        Mark pattern as matched with database entity.

        Args:
            unit_id: ID of matched unit (for unit patterns)
            food_id: ID of matched food (for food patterns)

        Raises:
            ValueError: If neither unit_id nor food_id is provided
        """
        if not unit_id and not food_id:
            raise ValueError("Either unit_id or food_id must be provided")

        if unit_id:
            self.matched_unit_id = unit_id
            self.transition_unit_to(PatternStatus.MATCHED)

        if food_id:
            self.matched_food_id = food_id
            self.transition_food_to(PatternStatus.MATCHED)

    def can_be_processed(self) -> bool:
        """
        Check if pattern can be interacted with (not locked by automation).

        Returns:
            True if pattern can be clicked/modified, False if locked
        """
        # PARSING state means automated process is running
        return self.unit_status != PatternStatus.PARSING and self.food_status != PatternStatus.PARSING

    def to_dict(self) -> dict[str, Any]:
        """Serialize PatternGroup to dictionary for JSON serialization."""
        return {
            "pattern_text": self.pattern_text,
            "ingredient_ids": self.ingredient_ids,
            "recipe_ids": self.recipe_ids,
            "suggested_similar_patterns": self.suggested_similar_patterns,
            "unit_status": self.unit_status.value,
            "food_status": self.food_status.value,
            "parsed_unit": self.parsed_unit,
            "parsed_food": self.parsed_food,
            "unit_confidence": self.unit_confidence,
            "food_confidence": self.food_confidence,
            "matched_unit_id": self.matched_unit_id,
            "matched_food_id": self.matched_food_id,
            "unit_error_message": self.unit_error_message,
            "food_error_message": self.food_error_message,
            "error_timestamp": self.error_timestamp.isoformat() if self.error_timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatternGroup:
        """Deserialize PatternGroup from dictionary."""
        # Parse unit_status
        unit_status_value = data.get("unit_status", "pending")
        unit_status = PatternStatus(unit_status_value) if isinstance(unit_status_value, str) else unit_status_value

        # Parse food_status
        food_status_value = data.get("food_status", "pending")
        food_status = PatternStatus(food_status_value) if isinstance(food_status_value, str) else food_status_value

        # Parse timestamp if present
        error_timestamp = None
        if data.get("error_timestamp"):
            error_timestamp = datetime.fromisoformat(data["error_timestamp"])

        return cls(
            pattern_text=data["pattern_text"],
            ingredient_ids=data.get("ingredient_ids", []),
            recipe_ids=data.get("recipe_ids", []),
            suggested_similar_patterns=data.get("suggested_similar_patterns", []),
            unit_status=unit_status,
            food_status=food_status,
            parsed_unit=data.get("parsed_unit", ""),
            parsed_food=data.get("parsed_food", ""),
            unit_confidence=data.get("unit_confidence", 0.0),
            food_confidence=data.get("food_confidence", 0.0),
            matched_unit_id=data.get("matched_unit_id"),
            matched_food_id=data.get("matched_food_id"),
            unit_error_message=data.get("unit_error_message"),
            food_error_message=data.get("food_error_message"),
            error_timestamp=error_timestamp,
        )


OperationType = Literal["create_unit", "create_food", "add_alias"]


@dataclass
class BatchOperation:
    """
    Represents a batch operation for creating units/foods or adding aliases.

    Attributes
    ----------
    operation_type : OperationType
        Type of operation: "create_unit", "create_food", or "add_alias"
    target_pattern : str
        The pattern text being processed
    affected_ingredients : list[str]
        List of ingredient IDs affected by this operation
    mealie_entity_id : str | None
        The unit/food ID returned by Mealie after creation (None before operation)

    Raises
    ------
    ValueError
        If target_pattern is empty or affected_ingredients is empty
    """

    operation_type: OperationType
    target_pattern: str
    affected_ingredients: list[str] = field(default_factory=list)
    mealie_entity_id: str | None = None

    def __post_init__(self) -> None:
        """Validate operation data."""
        if not self.target_pattern or not self.target_pattern.strip():
            raise ValueError("target_pattern must not be empty")
        if not self.affected_ingredients:
            raise ValueError("affected_ingredients must not be empty")
        # Normalize pattern text
        self.target_pattern = self.target_pattern.strip()

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize BatchOperation to dictionary for JSON serialization.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the batch operation
        """
        return {
            "operation_type": self.operation_type,
            "target_pattern": self.target_pattern,
            "affected_ingredients": self.affected_ingredients,
            "mealie_entity_id": self.mealie_entity_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BatchOperation:
        """
        Deserialize BatchOperation from dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary containing batch operation data

        Returns
        -------
        BatchOperation
            Deserialized batch operation instance
        """
        return cls(
            operation_type=data["operation_type"],
            target_pattern=data["target_pattern"],
            affected_ingredients=data.get("affected_ingredients", []),
            mealie_entity_id=data.get("mealie_entity_id"),
        )
