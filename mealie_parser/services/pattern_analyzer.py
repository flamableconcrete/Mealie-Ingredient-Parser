"""Pattern analysis service for extracting and grouping unparsed ingredients."""

from __future__ import annotations

from typing import Any

from mealie_parser.models.pattern import PatternGroup


class PatternAnalyzer:
    """Service for analyzing unparsed ingredient patterns across recipes."""

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
                    unparsed.append({
                        "ingredient": ing,
                        "recipe_id": recipe_id,
                        "ingredient_id": ing.get("id"),
                        "missing_unit": not has_unit_id,
                        "missing_food": not has_food_id,
                    })

        return unparsed

    def group_by_unit_pattern(
        self, unparsed_ingredients: list[dict[str, Any]]
    ) -> list[PatternGroup]:
        """
        Group unparsed ingredients by unit pattern.

        Pattern text is normalized: lowercase and whitespace trimmed.

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

            # Extract unit text from unit.name or unit.abbreviation only
            unit = ing.get("unit")
            if not unit or not isinstance(unit, dict):
                # No unit object at all - skip
                continue

            unit_text = unit.get("name") or unit.get("abbreviation")
            if not unit_text:
                # Unit object exists but has no name/abbreviation - skip
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

    def group_by_food_pattern(
        self, unparsed_ingredients: list[dict[str, Any]]
    ) -> list[PatternGroup]:
        """
        Group unparsed ingredients by food pattern.

        Pattern text is normalized: lowercase and whitespace trimmed.

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

            # Extract food text from food.name only
            food = ing.get("food")
            if not food or not isinstance(food, dict):
                # No food object at all - skip
                continue

            food_text = food.get("name")
            if not food_text:
                # Food object exists but has no name - skip
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
