"""Data models for screen state preservation across mode transitions."""

from dataclasses import dataclass, field


@dataclass
class RecipeListState:
    """
    State for RecipeListScreen (Sequential Mode).

    Tracks progress and statistics for the sequential recipe processing workflow.

    Attributes
    ----------
    processed_recipes : list[str]
        List of recipe slugs that have been processed
    units_created : int
        Count of units created in sequential mode
    foods_created : int
        Count of foods created in sequential mode
    aliases_created : int
        Count of aliases created in sequential mode
    """

    processed_recipes: list[str] = field(default_factory=list)
    units_created: int = 0
    foods_created: int = 0
    aliases_created: int = 0

    def to_dict(self) -> dict:
        """
        Serialize state to dictionary for passing between screens.

        Returns
        -------
        dict
            Dictionary representation of state
        """
        return {
            "processed_recipes": self.processed_recipes,
            "units_created": self.units_created,
            "foods_created": self.foods_created,
            "aliases_created": self.aliases_created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecipeListState":
        """
        Deserialize state from dictionary.

        Parameters
        ----------
        data : dict
            Dictionary representation of state

        Returns
        -------
        RecipeListState
            Reconstructed state object
        """
        return cls(**data)


@dataclass
class PatternGroupState:
    """
    State for PatternGroupScreen (Batch Mode).

    Tracks batch processing progress and created entities.

    Attributes
    ----------
    processed_patterns : list[str]
        List of pattern texts that have been completed
    skipped_patterns : list[str]
        List of pattern texts that have been skipped
    units_created : dict[str, str]
        Mapping of pattern text to created unit ID
    foods_created : dict[str, str]
        Mapping of pattern text to created food ID
    """

    processed_patterns: list[str] = field(default_factory=list)
    skipped_patterns: list[str] = field(default_factory=list)
    units_created: dict[str, str] = field(default_factory=dict)
    foods_created: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Serialize state to dictionary for passing between screens.

        Returns
        -------
        dict
            Dictionary representation of state
        """
        return {
            "processed_patterns": self.processed_patterns,
            "skipped_patterns": self.skipped_patterns,
            "units_created": self.units_created,
            "foods_created": self.foods_created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PatternGroupState":
        """
        Deserialize state from dictionary.

        Parameters
        ----------
        data : dict
            Dictionary representation of state

        Returns
        -------
        PatternGroupState
            Reconstructed state object
        """
        return cls(**data)

    def merge_into_recipe_state(self, recipe_state: RecipeListState) -> RecipeListState:
        """
        Merge pattern group stats into recipe list state.

        This is used when returning from batch mode to sequential mode.

        Parameters
        ----------
        recipe_state : RecipeListState
            The sequential mode state to merge into

        Returns
        -------
        RecipeListState
            Updated state with merged statistics
        """
        recipe_state.units_created += len(self.units_created)
        recipe_state.foods_created += len(self.foods_created)
        # Aliases are tracked separately in batch operations
        return recipe_state
