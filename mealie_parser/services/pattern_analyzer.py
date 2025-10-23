"""Pattern analysis service for extracting and grouping unparsed ingredients."""

from __future__ import annotations

from typing import Any

from mealie_parser.models.pattern import PatternGroup


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.

    Parameters
    ----------
    s1 : str
        First string
    s2 : str
        Second string

    Returns
    -------
    int
        Minimum number of single-character edits (insertions, deletions, substitutions)
        required to change s1 into s2
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """
    Calculate similarity ratio between two strings based on Levenshtein distance.

    Parameters
    ----------
    s1 : str
        First string
    s2 : str
        Second string

    Returns
    -------
    float
        Similarity ratio between 0.0 (completely different) and 1.0 (identical)
    """
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    max_len = max(len(s1), len(s2))
    distance = levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)


class PatternAnalyzer:
    """Service for analyzing unparsed ingredient patterns across recipes."""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize PatternAnalyzer.

        Parameters
        ----------
        similarity_threshold : float, optional
            Threshold for pattern similarity matching (0.0 to 1.0), by default 0.85
        """
        self.similarity_threshold = similarity_threshold

    def extract_unparsed_ingredients(self, recipes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Extract all unparsed ingredients from recipes.

        An ingredient is unparsed if it has text (note or originalText)
        but no associated food.id or unit.id.

        Args:
            recipes: List of recipe dictionaries with recipeIngredient arrays

        Returns:
            List of unparsed ingredient dictionaries with metadata
        """
        unparsed = []

        for recipe in recipes:
            recipe_id = recipe.get("id")
            ingredients = recipe.get("recipeIngredient", [])

            for ing in ingredients:
                if not isinstance(ing, dict):
                    continue

                # Check if ingredient has text
                has_text = ing.get("note") or ing.get("originalText")
                if not has_text:
                    continue

                # Check if food has id
                food = ing.get("food")
                has_food_id = food and isinstance(food, dict) and food.get("id")

                # Check if unit has id
                unit = ing.get("unit")
                has_unit_id = unit and isinstance(unit, dict) and unit.get("id")

                # Ingredient is unparsed if it has text but missing food or unit id
                if not has_food_id or not has_unit_id:
                    unparsed.append(
                        {
                            "ingredient": ing,
                            "recipe_id": recipe_id,
                            "ingredient_id": ing.get("id"),
                            "missing_unit": not has_unit_id,
                            "missing_food": not has_food_id,
                        }
                    )

        return unparsed

    def group_by_unit_pattern(self, unparsed_ingredients: list[dict[str, Any]]) -> list[PatternGroup]:
        """
        Group unparsed ingredients by unit pattern.

        Pattern text is normalized: lowercase and whitespace trimmed.

        For completely unparsed ingredients (unit=None), extracts unit from note field.

        Args:
            unparsed_ingredients: List from extract_unparsed_ingredients()

        Returns:
            List of PatternGroup objects grouped by unit pattern
        """
        pattern_map: dict[str, dict[str, Any]] = {}

        for item in unparsed_ingredients:
            # Only process ingredients missing unit
            if not item.get("missing_unit"):
                continue

            ing = item["ingredient"]
            recipe_id = item["recipe_id"]
            ingredient_id = item["ingredient_id"]

            # Extract unit text from unit.name or unit.abbreviation
            unit = ing.get("unit")
            unit_text = None

            if unit and isinstance(unit, dict):
                unit_text = unit.get("name") or unit.get("abbreviation")

            # If no unit object or empty unit text, try to extract from note
            # For completely unparsed ingredients, use the full note as pattern
            if not unit_text:
                note = ing.get("note") or ing.get("originalText")
                if note:
                    # Use the full note text as the pattern for completely unparsed ingredients
                    unit_text = note.strip()
                else:
                    # No extractable unit information - skip
                    continue

            # Normalize pattern text
            pattern_text = unit_text.strip().lower()
            if not pattern_text:
                continue

            # Group by normalized pattern
            if pattern_text not in pattern_map:
                pattern_map[pattern_text] = {
                    "ingredient_ids": [],
                    "recipe_ids": set(),
                }

            pattern_map[pattern_text]["ingredient_ids"].append(ingredient_id)
            pattern_map[pattern_text]["recipe_ids"].add(recipe_id)

        # Convert to PatternGroup objects
        pattern_groups = []
        for pattern_text, data in pattern_map.items():
            pattern_groups.append(
                PatternGroup(
                    pattern_text=pattern_text,
                    ingredient_ids=data["ingredient_ids"],
                    recipe_ids=list(data["recipe_ids"]),
                )
            )

        return pattern_groups

    def group_by_food_pattern(self, unparsed_ingredients: list[dict[str, Any]]) -> list[PatternGroup]:
        """
        Group unparsed ingredients by food pattern.

        Pattern text is normalized: lowercase and whitespace trimmed.

        For completely unparsed ingredients (food=None), extracts food from note field.

        Args:
            unparsed_ingredients: List from extract_unparsed_ingredients()

        Returns:
            List of PatternGroup objects grouped by food pattern
        """
        pattern_map: dict[str, dict[str, Any]] = {}

        for item in unparsed_ingredients:
            # Only process ingredients missing food
            if not item.get("missing_food"):
                continue

            ing = item["ingredient"]
            recipe_id = item["recipe_id"]
            ingredient_id = item["ingredient_id"]

            # Extract food text from food.name
            food = ing.get("food")
            food_text = None

            if food and isinstance(food, dict):
                food_text = food.get("name")

            # If no food object or empty food text, try to extract from note
            # For completely unparsed ingredients, use the full note as pattern
            if not food_text:
                note = ing.get("note") or ing.get("originalText")
                if note:
                    # Use the full note text as the pattern for completely unparsed ingredients
                    food_text = note.strip()
                else:
                    # No extractable food information - skip
                    continue

            # Normalize pattern text
            pattern_text = food_text.strip().lower()
            if not pattern_text:
                continue

            # Group by normalized pattern
            if pattern_text not in pattern_map:
                pattern_map[pattern_text] = {
                    "ingredient_ids": [],
                    "recipe_ids": set(),
                }

            pattern_map[pattern_text]["ingredient_ids"].append(ingredient_id)
            pattern_map[pattern_text]["recipe_ids"].add(recipe_id)

        # Convert to PatternGroup objects
        pattern_groups = []
        for pattern_text, data in pattern_map.items():
            pattern_groups.append(
                PatternGroup(
                    pattern_text=pattern_text,
                    ingredient_ids=data["ingredient_ids"],
                    recipe_ids=list(data["recipe_ids"]),
                )
            )

        return pattern_groups

    def group_all_patterns(self, unparsed_ingredients: list[dict[str, Any]]) -> list[PatternGroup]:
        """
        Group all unparsed ingredients into a single unified pattern list.

        Each pattern contains the full ingredient text and will store both
        parsed unit and parsed food data when parsing is performed.

        This creates one pattern per unique ingredient text, allowing both
        Unit Patterns and Food Patterns tabs to show the same data with
        different columns.

        Args:
            unparsed_ingredients: List from extract_unparsed_ingredients()

        Returns:
            List of PatternGroup objects grouped by full ingredient text
        """
        pattern_map: dict[str, dict[str, Any]] = {}

        for item in unparsed_ingredients:
            ing = item["ingredient"]
            recipe_id = item["recipe_id"]
            ingredient_id = item["ingredient_id"]

            # Use full ingredient text as pattern
            pattern_text = (ing.get("note") or ing.get("originalText") or "").strip()
            if not pattern_text:
                continue

            # Normalize pattern text (lowercase for grouping)
            pattern_key = pattern_text.lower()

            # Group by normalized pattern
            if pattern_key not in pattern_map:
                pattern_map[pattern_key] = {
                    "pattern_text": pattern_text,  # Keep original case for display
                    "ingredient_ids": [],
                    "recipe_ids": set(),
                }

            pattern_map[pattern_key]["ingredient_ids"].append(ingredient_id)
            pattern_map[pattern_key]["recipe_ids"].add(recipe_id)

        # Convert to PatternGroup objects
        pattern_groups = []
        for data in pattern_map.values():
            pattern_groups.append(
                PatternGroup(
                    pattern_text=data["pattern_text"],
                    ingredient_ids=data["ingredient_ids"],
                    recipe_ids=list(data["recipe_ids"]),
                )
            )

        return pattern_groups

    def find_similar_patterns(self, pattern_groups: list[PatternGroup]) -> list[PatternGroup]:
        """
        Detect and link similar patterns using fuzzy matching.

        Patterns are compared using Levenshtein distance-based similarity.
        Similar patterns are linked but NOT automatically merged - user
        confirmation is required for merging.

        Parameters
        ----------
        pattern_groups : list[PatternGroup]
            List of pattern groups to analyze for similarity

        Returns
        -------
        list[PatternGroup]
            Same pattern groups with suggested_similar_patterns populated
        """
        # Create a copy to avoid modifying input
        updated_groups = []

        for i, group in enumerate(pattern_groups):
            similar_patterns = []
            group_lower = group.pattern_text.lower()

            # Compare with all other patterns
            for j, other_group in enumerate(pattern_groups):
                if i == j:
                    # Skip comparing with itself
                    continue

                other_lower = other_group.pattern_text.lower()

                # Quick length-based filter: if length difference is too large,
                # similarity can't exceed threshold. For threshold 0.85:
                # max_len * (1 - 0.85) = max_len * 0.15 >= distance
                # So if |len1 - len2| > max_len * 0.15, skip comparison
                len_diff = abs(len(group_lower) - len(other_lower))
                max_len = max(len(group_lower), len(other_lower))
                if max_len > 0 and len_diff > max_len * (1 - self.similarity_threshold):
                    continue

                # Calculate similarity ratio
                ratio = similarity_ratio(group_lower, other_lower)

                # If similarity exceeds threshold, link patterns
                if ratio >= self.similarity_threshold:
                    similar_patterns.append(other_group.pattern_text)

            # Create updated PatternGroup with similar patterns
            updated_group = PatternGroup(
                pattern_text=group.pattern_text,
                ingredient_ids=group.ingredient_ids,
                recipe_ids=group.recipe_ids,
                suggested_similar_patterns=similar_patterns,
                unit_status=group.unit_status,
                food_status=group.food_status,
                parsed_unit=group.parsed_unit,
                parsed_food=group.parsed_food,
                unit_confidence=group.unit_confidence,
                food_confidence=group.food_confidence,
                matched_unit_id=group.matched_unit_id,
                matched_food_id=group.matched_food_id,
                unit_error_message=group.unit_error_message,
                food_error_message=group.food_error_message,
                error_timestamp=group.error_timestamp,
            )
            updated_groups.append(updated_group)

        return updated_groups
