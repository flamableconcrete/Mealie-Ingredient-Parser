"""Unit tests for PatternAnalyzer service."""

from __future__ import annotations

import pytest

from mealie_parser.services.pattern_analyzer import PatternAnalyzer


@pytest.fixture
def sample_recipes():
    """Fixture providing sample recipe data with unparsed ingredients."""
    return [
        {
            "id": "recipe-1",
            "name": "Recipe 1",
            "recipeIngredient": [
                {
                    "id": "ing-1",
                    "note": "1 tsp salt",
                    "originalText": "1 tsp salt",
                    "unit": {"name": "tsp"},  # No id - unparsed unit
                    "food": {"id": "food-1", "name": "salt"},  # Has id - parsed food
                },
                {
                    "id": "ing-2",
                    "note": "2 TSP sugar",
                    "originalText": "2 TSP sugar",
                    "unit": {"name": "TSP"},  # No id - unparsed unit
                    "food": {"name": "sugar"},  # No id - unparsed food
                },
            ],
        },
        {
            "id": "recipe-2",
            "name": "Recipe 2",
            "recipeIngredient": [
                {
                    "id": "ing-3",
                    "note": "3 tsp pepper",
                    "originalText": "3 tsp pepper",
                    "unit": {"name": "  tsp  "},  # Whitespace variation - unparsed unit
                    "food": {"id": "food-2", "name": "pepper"},  # Has id - parsed food
                },
                {
                    "id": "ing-4",
                    "note": "chicken breast",
                    "originalText": "chicken breast",
                    "food": {"name": "chicken breast"},  # No id - unparsed food
                },
                {
                    "id": "ing-5",
                    "note": "Chicken Breast",
                    "originalText": "Chicken Breast",
                    "food": {"name": "Chicken Breast"},  # Case variation - unparsed food
                },
            ],
        },
        {
            "id": "recipe-3",
            "name": "Recipe 3",
            "recipeIngredient": [
                {
                    "id": "ing-6",
                    "note": "1 cup flour",
                    "originalText": "1 cup flour",
                    "unit": {"id": "unit-1", "name": "cup"},  # Has id - parsed unit
                    "food": {"id": "food-3", "name": "flour"},  # Has id - parsed food
                },
            ],
        },
    ]


@pytest.fixture
def analyzer():
    """Fixture providing PatternAnalyzer instance."""
    return PatternAnalyzer()


class TestExtractUnparsedIngredients:
    """Test extract_unparsed_ingredients method."""

    def test_extract_unparsed_ingredients(self, analyzer, sample_recipes):
        """Test extraction of unparsed ingredients."""
        # Act
        result = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Assert - should extract ing-1 through ing-5 (not ing-6 which is fully parsed)
        assert len(result) == 5
        ingredient_ids = [item["ingredient_id"] for item in result]
        assert "ing-1" in ingredient_ids
        assert "ing-2" in ingredient_ids
        assert "ing-3" in ingredient_ids
        assert "ing-4" in ingredient_ids
        assert "ing-5" in ingredient_ids
        assert "ing-6" not in ingredient_ids

    def test_extract_identifies_missing_unit(self, analyzer, sample_recipes):
        """Test that extraction correctly identifies missing unit.id."""
        # Act
        result = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Assert
        ing_1 = next(item for item in result if item["ingredient_id"] == "ing-1")
        assert ing_1["missing_unit"] is True
        assert ing_1["missing_food"] is False  # Has food.id

        ing_2 = next(item for item in result if item["ingredient_id"] == "ing-2")
        assert ing_2["missing_unit"] is True
        assert ing_2["missing_food"] is True

    def test_extract_identifies_missing_food(self, analyzer, sample_recipes):
        """Test that extraction correctly identifies missing food.id."""
        # Act
        result = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Assert
        ing_4 = next(item for item in result if item["ingredient_id"] == "ing-4")
        assert ing_4["missing_food"] is True
        assert ing_4["missing_unit"] is True  # No unit at all

    def test_extract_with_empty_recipe_list(self, analyzer):
        """Test extraction with empty recipe list."""
        # Act
        result = analyzer.extract_unparsed_ingredients([])

        # Assert
        assert result == []

    def test_extract_with_no_unparsed_ingredients(self, analyzer):
        """Test extraction when all ingredients are parsed."""
        # Arrange
        recipes = [
            {
                "id": "recipe-1",
                "recipeIngredient": [
                    {
                        "id": "ing-1",
                        "note": "1 cup flour",
                        "unit": {"id": "unit-1", "name": "cup"},
                        "food": {"id": "food-1", "name": "flour"},
                    }
                ],
            }
        ]

        # Act
        result = analyzer.extract_unparsed_ingredients(recipes)

        # Assert
        assert result == []

    def test_extract_without_text_is_ignored(self, analyzer):
        """Test that ingredients without note/originalText are ignored."""
        # Arrange
        recipes = [
            {
                "id": "recipe-1",
                "recipeIngredient": [
                    {
                        "id": "ing-1",
                        "unit": {"name": "cup"},  # No id but also no text
                        "food": {"name": "flour"},
                    }
                ],
            }
        ]

        # Act
        result = analyzer.extract_unparsed_ingredients(recipes)

        # Assert
        assert result == []


class TestGroupByUnitPattern:
    """Test group_by_unit_pattern method."""

    def test_group_by_unit_pattern_case_insensitive(self, analyzer, sample_recipes):
        """Test that unit patterns are grouped case-insensitively."""
        # Arrange
        unparsed = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Act
        result = analyzer.group_by_unit_pattern(unparsed)

        # Assert
        pattern_texts = [pg.pattern_text for pg in result]
        # "tsp", "TSP", and "  tsp  " should all be grouped as "tsp"
        assert "tsp" in pattern_texts
        # Should not have separate entries for case variations
        assert "TSP" not in pattern_texts

        tsp_pattern = next(pg for pg in result if pg.pattern_text == "tsp")
        # Should group ing-1, ing-2, and ing-3
        assert len(tsp_pattern.ingredient_ids) == 3

    def test_group_by_unit_pattern_whitespace_normalized(self, analyzer, sample_recipes):
        """Test that whitespace is normalized in unit patterns."""
        # Arrange
        unparsed = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Act
        result = analyzer.group_by_unit_pattern(unparsed)

        # Assert
        tsp_pattern = next(pg for pg in result if pg.pattern_text == "tsp")
        # "tsp", "TSP", and "  tsp  " should all be normalized to "tsp"
        assert "ing-1" in tsp_pattern.ingredient_ids
        assert "ing-2" in tsp_pattern.ingredient_ids
        assert "ing-3" in tsp_pattern.ingredient_ids

    def test_group_by_unit_pattern_recipe_ids(self, analyzer, sample_recipes):
        """Test that recipe_ids are correctly tracked."""
        # Arrange
        unparsed = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Act
        result = analyzer.group_by_unit_pattern(unparsed)

        # Assert
        tsp_pattern = next(pg for pg in result if pg.pattern_text == "tsp")
        assert "recipe-1" in tsp_pattern.recipe_ids
        assert "recipe-2" in tsp_pattern.recipe_ids
        # Should deduplicate recipe_ids
        assert len(tsp_pattern.recipe_ids) == 2

    def test_group_by_unit_pattern_only_missing_units(self, analyzer, sample_recipes):
        """Test that only ingredients missing unit.id are grouped."""
        # Arrange
        unparsed = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Act
        result = analyzer.group_by_unit_pattern(unparsed)

        # Assert
        # ing-4 and ing-5 have no units, so should not appear in unit patterns
        for pattern in result:
            assert "ing-4" not in pattern.ingredient_ids
            assert "ing-5" not in pattern.ingredient_ids

    def test_group_by_unit_pattern_empty_list(self, analyzer):
        """Test grouping with empty ingredient list."""
        # Act
        result = analyzer.group_by_unit_pattern([])

        # Assert
        assert result == []


class TestGroupByFoodPattern:
    """Test group_by_food_pattern method."""

    def test_group_by_food_pattern_case_insensitive(self, analyzer, sample_recipes):
        """Test that food patterns are grouped case-insensitively."""
        # Arrange
        unparsed = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Act
        result = analyzer.group_by_food_pattern(unparsed)

        # Assert
        pattern_texts = [pg.pattern_text for pg in result]
        # "chicken breast" and "Chicken Breast" should be grouped as "chicken breast"
        assert "chicken breast" in pattern_texts
        assert "Chicken Breast" not in pattern_texts

        chicken_pattern = next(pg for pg in result if pg.pattern_text == "chicken breast")
        # Should group ing-4 and ing-5
        assert len(chicken_pattern.ingredient_ids) == 2

    def test_group_by_food_pattern_whitespace_normalized(self, analyzer):
        """Test that whitespace is normalized in food patterns."""
        # Arrange
        recipes = [
            {
                "id": "recipe-1",
                "recipeIngredient": [
                    {
                        "id": "ing-1",
                        "note": "tomato",
                        "food": {"name": "  tomato  "},
                    },
                    {
                        "id": "ing-2",
                        "note": "tomato",
                        "food": {"name": "tomato"},
                    },
                ],
            }
        ]
        unparsed = analyzer.extract_unparsed_ingredients(recipes)

        # Act
        result = analyzer.group_by_food_pattern(unparsed)

        # Assert
        assert len(result) == 1
        tomato_pattern = result[0]
        assert tomato_pattern.pattern_text == "tomato"
        assert len(tomato_pattern.ingredient_ids) == 2

    def test_group_by_food_pattern_recipe_ids(self, analyzer, sample_recipes):
        """Test that recipe_ids are correctly tracked."""
        # Arrange
        unparsed = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Act
        result = analyzer.group_by_food_pattern(unparsed)

        # Assert
        chicken_pattern = next(pg for pg in result if pg.pattern_text == "chicken breast")
        assert "recipe-2" in chicken_pattern.recipe_ids
        # Only one recipe has chicken breast ingredients
        assert len(chicken_pattern.recipe_ids) == 1

    def test_group_by_food_pattern_only_missing_foods(self, analyzer, sample_recipes):
        """Test that only ingredients missing food.id are grouped."""
        # Arrange
        unparsed = analyzer.extract_unparsed_ingredients(sample_recipes)

        # Act
        result = analyzer.group_by_food_pattern(unparsed)

        # Assert
        # ing-1 and ing-3 have food.id, so should not appear in food patterns
        for pattern in result:
            assert "ing-1" not in pattern.ingredient_ids
            assert "ing-3" not in pattern.ingredient_ids

    def test_group_by_food_pattern_empty_list(self, analyzer):
        """Test grouping with empty ingredient list."""
        # Act
        result = analyzer.group_by_food_pattern([])

        # Assert
        assert result == []


class TestPatternAnalyzerEdgeCases:
    """Test PatternAnalyzer with edge case inputs."""

    def test_unicode_in_patterns(self, analyzer):
        """Test pattern grouping with Unicode characters."""
        # Arrange
        recipes = [
            {
                "id": "recipe-1",
                "recipeIngredient": [
                    {
                        "id": "ing-1",
                        "note": "jalapeño",
                        "food": {"name": "jalapeño"},
                    },
                    {
                        "id": "ing-2",
                        "note": "jalapeño",
                        "food": {"name": "jalapeño"},
                    },
                ],
            }
        ]
        unparsed = analyzer.extract_unparsed_ingredients(recipes)

        # Act
        result = analyzer.group_by_food_pattern(unparsed)

        # Assert
        assert len(result) == 1
        assert result[0].pattern_text == "jalapeño"
        assert len(result[0].ingredient_ids) == 2

    def test_special_characters_in_patterns(self, analyzer):
        """Test pattern grouping with special characters."""
        # Arrange
        recipes = [
            {
                "id": "recipe-1",
                "recipeIngredient": [
                    {
                        "id": "ing-1",
                        "note": "café-style",
                        "food": {"name": "café-style"},
                    }
                ],
            }
        ]
        unparsed = analyzer.extract_unparsed_ingredients(recipes)

        # Act
        result = analyzer.group_by_food_pattern(unparsed)

        # Assert
        assert len(result) == 1
        assert result[0].pattern_text == "café-style"

    def test_empty_pattern_text_is_skipped(self, analyzer):
        """Test that empty pattern text is skipped during grouping."""
        # Arrange
        recipes = [
            {
                "id": "recipe-1",
                "recipeIngredient": [
                    {
                        "id": "ing-1",
                        "note": "salt",
                        "food": {"name": ""},  # Empty name
                    },
                    {
                        "id": "ing-2",
                        "note": "pepper",
                        "food": {"name": "   "},  # Whitespace only
                    },
                ],
            }
        ]
        unparsed = analyzer.extract_unparsed_ingredients(recipes)

        # Act
        result = analyzer.group_by_food_pattern(unparsed)

        # Assert
        # Both should be skipped due to empty/whitespace pattern text
        assert result == []
