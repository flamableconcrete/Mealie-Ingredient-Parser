"""Pattern grouping data model for batch ingredient processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PatternGroup:
    """
    Represents a group of ingredients sharing the same unparsed unit or food pattern.

    Attributes:
        pattern_text: The normalized pattern text (lowercase, trimmed)
        ingredient_ids: List of ingredient IDs matching this pattern
        recipe_ids: List of recipe IDs containing ingredients with this pattern
        suggested_similar_patterns: List of potentially related patterns
        operation_status: Status of batch operation ("pending", "processing", "completed", "skipped")
    """

    pattern_text: str
    ingredient_ids: list[str] = field(default_factory=list)
    recipe_ids: list[str] = field(default_factory=list)
    suggested_similar_patterns: list[str] = field(default_factory=list)
    operation_status: str = "pending"

    def __post_init__(self) -> None:
        """Validate pattern_text is not empty."""
        if not self.pattern_text or not self.pattern_text.strip():
            raise ValueError("pattern_text must not be empty")
        # Normalize pattern_text to ensure consistency
        self.pattern_text = self.pattern_text.strip()

    def to_dict(self) -> dict[str, Any]:
        """Serialize PatternGroup to dictionary for JSON serialization."""
        return {
            "pattern_text": self.pattern_text,
            "ingredient_ids": self.ingredient_ids,
            "recipe_ids": self.recipe_ids,
            "suggested_similar_patterns": self.suggested_similar_patterns,
            "operation_status": self.operation_status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatternGroup:
        """Deserialize PatternGroup from dictionary."""
        return cls(
            pattern_text=data["pattern_text"],
            ingredient_ids=data.get("ingredient_ids", []),
            recipe_ids=data.get("recipe_ids", []),
            suggested_similar_patterns=data.get("suggested_similar_patterns", []),
            operation_status=data.get("operation_status", "pending"),
        )
