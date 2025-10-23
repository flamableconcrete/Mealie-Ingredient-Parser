"""Unit tests for PatternGroup and BatchOperation data models."""

from __future__ import annotations

import pytest

from mealie_parser.models.pattern import BatchOperation, PatternGroup, PatternStatus


class TestPatternGroupCreation:
    """Test PatternGroup creation and initialization."""

    def test_create_pattern_group_with_valid_data(self):
        """Test creating PatternGroup with all valid fields."""
        # Arrange & Act
        pattern = PatternGroup(
            pattern_text="tsp",
            ingredient_ids=["ing-1", "ing-2"],
            recipe_ids=["recipe-1"],
            suggested_similar_patterns=["teaspoon", "t"],
            unit_status=PatternStatus.PENDING,
            food_status=PatternStatus.PENDING,
        )

        # Assert
        assert pattern.pattern_text == "tsp"
        assert pattern.ingredient_ids == ["ing-1", "ing-2"]
        assert pattern.recipe_ids == ["recipe-1"]
        assert pattern.suggested_similar_patterns == ["teaspoon", "t"]
        assert pattern.unit_status == PatternStatus.PENDING
        assert pattern.food_status == PatternStatus.PENDING

    def test_create_pattern_group_with_defaults(self):
        """Test creating PatternGroup with only required field."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="flour")

        # Assert
        assert pattern.pattern_text == "flour"
        assert pattern.ingredient_ids == []
        assert pattern.recipe_ids == []
        assert pattern.suggested_similar_patterns == []
        assert pattern.unit_status == PatternStatus.PENDING
        assert pattern.food_status == PatternStatus.PENDING

    def test_pattern_text_is_trimmed(self):
        """Test that pattern_text is automatically trimmed."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="  tsp  ")

        # Assert
        assert pattern.pattern_text == "tsp"

    def test_empty_pattern_text_raises_error(self):
        """Test that empty pattern_text raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="pattern_text must not be empty"):
            PatternGroup(pattern_text="")

    def test_whitespace_only_pattern_text_raises_error(self):
        """Test that whitespace-only pattern_text raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="pattern_text must not be empty"):
            PatternGroup(pattern_text="   ")


class TestPatternGroupSerialization:
    """Test PatternGroup serialization methods."""

    def test_to_dict(self):
        """Test serialization to dictionary."""
        # Arrange
        pattern = PatternGroup(
            pattern_text="cup",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
            suggested_similar_patterns=["c"],
            unit_status=PatternStatus.MATCHED,
            food_status=PatternStatus.PENDING,
        )

        # Act
        result = pattern.to_dict()

        # Assert - verify new fields are included
        assert result["pattern_text"] == "cup"
        assert result["ingredient_ids"] == ["ing-1"]
        assert result["recipe_ids"] == ["recipe-1"]
        assert result["suggested_similar_patterns"] == ["c"]
        assert result["unit_status"] == "matched"
        assert result["food_status"] == "pending"
        assert result["parsed_unit"] == ""
        assert result["parsed_food"] == ""
        assert result["matched_unit_id"] is None
        assert result["matched_food_id"] is None
        assert result["unit_error_message"] is None
        assert result["food_error_message"] is None
        assert result["error_timestamp"] is None

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        # Arrange
        data = {
            "pattern_text": "tbsp",
            "ingredient_ids": ["ing-1", "ing-2"],
            "recipe_ids": ["recipe-1", "recipe-2"],
            "suggested_similar_patterns": ["tablespoon"],
            "unit_status": "parsing",
            "food_status": "pending",
        }

        # Act
        pattern = PatternGroup.from_dict(data)

        # Assert
        assert pattern.pattern_text == "tbsp"
        assert pattern.ingredient_ids == ["ing-1", "ing-2"]
        assert pattern.recipe_ids == ["recipe-1", "recipe-2"]
        assert pattern.suggested_similar_patterns == ["tablespoon"]
        assert pattern.unit_status == PatternStatus.PARSING
        assert pattern.food_status == PatternStatus.PENDING

    def test_from_dict_with_minimal_data(self):
        """Test deserialization with only required field."""
        # Arrange
        data = {"pattern_text": "salt"}

        # Act
        pattern = PatternGroup.from_dict(data)

        # Assert
        assert pattern.pattern_text == "salt"
        assert pattern.ingredient_ids == []
        assert pattern.recipe_ids == []
        assert pattern.suggested_similar_patterns == []
        assert pattern.unit_status == PatternStatus.PENDING
        assert pattern.food_status == PatternStatus.PENDING

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are reversible."""
        # Arrange
        original = PatternGroup(
            pattern_text="onion",
            ingredient_ids=["ing-1", "ing-2", "ing-3"],
            recipe_ids=["recipe-1"],
            suggested_similar_patterns=["yellow onion", "white onion"],
            unit_status=PatternStatus.IGNORE,
            food_status=PatternStatus.MATCHED,
        )

        # Act
        serialized = original.to_dict()
        deserialized = PatternGroup.from_dict(serialized)

        # Assert
        assert deserialized.pattern_text == original.pattern_text
        assert deserialized.ingredient_ids == original.ingredient_ids
        assert deserialized.recipe_ids == original.recipe_ids
        assert deserialized.suggested_similar_patterns == original.suggested_similar_patterns
        assert deserialized.unit_status == original.unit_status
        assert deserialized.food_status == original.food_status


class TestPatternGroupEdgeCases:
    """Test PatternGroup with edge case inputs."""

    def test_unicode_characters(self):
        """Test pattern_text with Unicode characters."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="jalapeño")

        # Assert
        assert pattern.pattern_text == "jalapeño"

    def test_special_characters(self):
        """Test pattern_text with special characters."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="café-style")

        # Assert
        assert pattern.pattern_text == "café-style"

    def test_very_long_pattern_text(self):
        """Test pattern_text with very long string."""
        # Arrange
        long_text = "a" * 1000

        # Act
        pattern = PatternGroup(pattern_text=long_text)

        # Assert
        assert pattern.pattern_text == long_text
        assert len(pattern.pattern_text) == 1000

    def test_pattern_with_numbers(self):
        """Test pattern_text containing numbers."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="1/2 cup")

        # Assert
        assert pattern.pattern_text == "1/2 cup"

    def test_pattern_with_mixed_whitespace(self):
        """Test pattern_text with tabs and newlines is trimmed."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="\t\ntsp\n\t")

        # Assert
        assert pattern.pattern_text == "tsp"


class TestBatchOperationCreation:
    """Test BatchOperation creation and initialization."""

    def test_create_batch_operation_with_valid_data(self):
        """Test creating BatchOperation with all valid fields."""
        # Arrange & Act
        operation = BatchOperation(
            operation_type="create_unit",
            target_pattern="tsp",
            affected_ingredients=["ing-1", "ing-2"],
            mealie_entity_id="unit-123",
        )

        # Assert
        assert operation.operation_type == "create_unit"
        assert operation.target_pattern == "tsp"
        assert operation.affected_ingredients == ["ing-1", "ing-2"]
        assert operation.mealie_entity_id == "unit-123"

    def test_create_batch_operation_with_defaults(self):
        """Test creating BatchOperation with required fields only."""
        # Arrange & Act
        operation = BatchOperation(
            operation_type="create_food",
            target_pattern="chicken",
            affected_ingredients=["ing-1"],
        )

        # Assert
        assert operation.operation_type == "create_food"
        assert operation.target_pattern == "chicken"
        assert operation.affected_ingredients == ["ing-1"]
        assert operation.mealie_entity_id is None

    def test_target_pattern_is_trimmed(self):
        """Test that target_pattern is automatically trimmed."""
        # Arrange & Act
        operation = BatchOperation(
            operation_type="add_alias",
            target_pattern="  flour  ",
            affected_ingredients=["ing-1"],
        )

        # Assert
        assert operation.target_pattern == "flour"

    def test_empty_target_pattern_raises_error(self):
        """Test that empty target_pattern raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="target_pattern must not be empty"):
            BatchOperation(
                operation_type="create_unit",
                target_pattern="",
                affected_ingredients=["ing-1"],
            )

    def test_whitespace_only_target_pattern_raises_error(self):
        """Test that whitespace-only target_pattern raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="target_pattern must not be empty"):
            BatchOperation(
                operation_type="create_unit",
                target_pattern="   ",
                affected_ingredients=["ing-1"],
            )

    def test_empty_affected_ingredients_raises_error(self):
        """Test that empty affected_ingredients raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="affected_ingredients must not be empty"):
            BatchOperation(
                operation_type="create_unit",
                target_pattern="tsp",
                affected_ingredients=[],
            )

    def test_all_operation_types(self):
        """Test that all valid operation types work."""
        # Arrange & Act
        create_unit = BatchOperation(
            operation_type="create_unit",
            target_pattern="cup",
            affected_ingredients=["ing-1"],
        )
        create_food = BatchOperation(
            operation_type="create_food",
            target_pattern="salt",
            affected_ingredients=["ing-2"],
        )
        add_alias = BatchOperation(
            operation_type="add_alias",
            target_pattern="chicken breast",
            affected_ingredients=["ing-3"],
        )

        # Assert
        assert create_unit.operation_type == "create_unit"
        assert create_food.operation_type == "create_food"
        assert add_alias.operation_type == "add_alias"


class TestBatchOperationSerialization:
    """Test BatchOperation serialization methods."""

    def test_to_dict(self):
        """Test serialization to dictionary."""
        # Arrange
        operation = BatchOperation(
            operation_type="create_unit",
            target_pattern="tbsp",
            affected_ingredients=["ing-1", "ing-2"],
            mealie_entity_id="unit-456",
        )

        # Act
        result = operation.to_dict()

        # Assert
        assert result == {
            "operation_type": "create_unit",
            "target_pattern": "tbsp",
            "affected_ingredients": ["ing-1", "ing-2"],
            "mealie_entity_id": "unit-456",
        }

    def test_to_dict_without_mealie_entity_id(self):
        """Test serialization when mealie_entity_id is None."""
        # Arrange
        operation = BatchOperation(
            operation_type="create_food",
            target_pattern="pepper",
            affected_ingredients=["ing-3"],
        )

        # Act
        result = operation.to_dict()

        # Assert
        assert result["mealie_entity_id"] is None

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        # Arrange
        data = {
            "operation_type": "add_alias",
            "target_pattern": "onion",
            "affected_ingredients": ["ing-1", "ing-2", "ing-3"],
            "mealie_entity_id": "food-789",
        }

        # Act
        operation = BatchOperation.from_dict(data)

        # Assert
        assert operation.operation_type == "add_alias"
        assert operation.target_pattern == "onion"
        assert operation.affected_ingredients == ["ing-1", "ing-2", "ing-3"]
        assert operation.mealie_entity_id == "food-789"

    def test_from_dict_with_minimal_data(self):
        """Test deserialization with only required fields."""
        # Arrange
        data = {
            "operation_type": "create_unit",
            "target_pattern": "lb",
            "affected_ingredients": ["ing-1"],
        }

        # Act
        operation = BatchOperation.from_dict(data)

        # Assert
        assert operation.operation_type == "create_unit"
        assert operation.target_pattern == "lb"
        assert operation.affected_ingredients == ["ing-1"]
        assert operation.mealie_entity_id is None

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are reversible."""
        # Arrange
        original = BatchOperation(
            operation_type="create_food",
            target_pattern="garlic",
            affected_ingredients=["ing-1", "ing-2"],
            mealie_entity_id="food-999",
        )

        # Act
        serialized = original.to_dict()
        deserialized = BatchOperation.from_dict(serialized)

        # Assert
        assert deserialized.operation_type == original.operation_type
        assert deserialized.target_pattern == original.target_pattern
        assert deserialized.affected_ingredients == original.affected_ingredients
        assert deserialized.mealie_entity_id == original.mealie_entity_id


class TestBatchOperationEdgeCases:
    """Test BatchOperation with edge case inputs."""

    def test_unicode_in_target_pattern(self):
        """Test target_pattern with Unicode characters."""
        # Arrange & Act
        operation = BatchOperation(
            operation_type="create_food",
            target_pattern="jalapeño",
            affected_ingredients=["ing-1"],
        )

        # Assert
        assert operation.target_pattern == "jalapeño"

    def test_special_characters_in_target_pattern(self):
        """Test target_pattern with special characters."""
        # Arrange & Act
        operation = BatchOperation(
            operation_type="create_unit",
            target_pattern="1/2 cup",
            affected_ingredients=["ing-1"],
        )

        # Assert
        assert operation.target_pattern == "1/2 cup"

    def test_very_long_affected_ingredients_list(self):
        """Test BatchOperation with many affected ingredients."""
        # Arrange
        many_ingredients = [f"ing-{i}" for i in range(1000)]

        # Act
        operation = BatchOperation(
            operation_type="create_unit",
            target_pattern="cup",
            affected_ingredients=many_ingredients,
        )

        # Assert
        assert len(operation.affected_ingredients) == 1000

    def test_target_pattern_with_mixed_whitespace(self):
        """Test target_pattern with tabs and newlines is trimmed."""
        # Arrange & Act
        operation = BatchOperation(
            operation_type="create_food",
            target_pattern="\t\nchicken\n\t",
            affected_ingredients=["ing-1"],
        )

        # Assert
        assert operation.target_pattern == "chicken"
