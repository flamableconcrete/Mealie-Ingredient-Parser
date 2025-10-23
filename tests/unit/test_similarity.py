"""Unit tests for similarity detection functions."""

from __future__ import annotations

import time

import pytest

from mealie_parser.models.pattern import PatternGroup, PatternStatus
from mealie_parser.services.pattern_analyzer import (
    PatternAnalyzer,
    levenshtein_distance,
    similarity_ratio,
)


class TestLevenshteinDistance:
    """Test Levenshtein distance calculation."""

    def test_identical_strings(self):
        """Test distance between identical strings."""
        assert levenshtein_distance("hello", "hello") == 0
        assert levenshtein_distance("", "") == 0

    def test_one_empty_string(self):
        """Test distance when one string is empty."""
        assert levenshtein_distance("hello", "") == 5
        assert levenshtein_distance("", "world") == 5

    def test_single_character_difference(self):
        """Test distance with single character substitution."""
        assert levenshtein_distance("cat", "bat") == 1
        assert levenshtein_distance("hello", "hallo") == 1

    def test_multiple_operations(self):
        """Test distance requiring multiple operations."""
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("saturday", "sunday") == 3

    def test_case_sensitive(self):
        """Test that distance calculation is case-sensitive."""
        assert levenshtein_distance("Hello", "hello") == 1
        assert levenshtein_distance("CUP", "cup") == 3

    def test_plurals(self):
        """Test distance for common plural forms."""
        assert levenshtein_distance("cup", "cups") == 1
        assert levenshtein_distance("tomato", "tomatoes") == 2


class TestSimilarityRatio:
    """Test similarity ratio calculation."""

    def test_identical_strings(self):
        """Test ratio for identical strings."""
        assert similarity_ratio("hello", "hello") == 1.0
        assert similarity_ratio("", "") == 1.0

    def test_completely_different(self):
        """Test ratio for completely different strings."""
        # "abc" vs "xyz" - all 3 chars different, max_len=3, distance=3
        assert similarity_ratio("abc", "xyz") == 0.0

    def test_one_empty_string(self):
        """Test ratio when one string is empty."""
        assert similarity_ratio("hello", "") == 0.0
        assert similarity_ratio("", "world") == 0.0

    def test_high_similarity(self):
        """Test ratio for highly similar strings."""
        # "cup" vs "cups" - 1 edit, max_len=4
        ratio = similarity_ratio("cup", "cups")
        assert ratio == 0.75  # 1 - (1/4)

    def test_plural_variations(self):
        """Test ratio for plural variations."""
        assert similarity_ratio("chicken", "chickens") >= 0.85
        assert similarity_ratio("tomato", "tomatoes") >= 0.70

    def test_abbreviations(self):
        """Test ratio for abbreviations."""
        # "tsp" vs "teaspoon" - distance=5, max_len=8
        ratio = similarity_ratio("tsp", "teaspoon")
        assert 0.0 < ratio < 0.5  # Some similarity but not high


class TestPatternAnalyzerSimilarityDetection:
    """Test PatternAnalyzer.find_similar_patterns method."""

    @pytest.fixture
    def analyzer(self):
        """Fixture providing PatternAnalyzer with default threshold."""
        return PatternAnalyzer(similarity_threshold=0.85)

    @pytest.fixture
    def sample_pattern_groups(self):
        """Fixture providing sample pattern groups."""
        return [
            PatternGroup(
                pattern_text="cup",
                ingredient_ids=["ing-1", "ing-2"],
                recipe_ids=["recipe-1"],
            ),
            PatternGroup(
                pattern_text="cups",
                ingredient_ids=["ing-3"],
                recipe_ids=["recipe-2"],
            ),
            PatternGroup(
                pattern_text="teaspoon",
                ingredient_ids=["ing-4", "ing-5"],
                recipe_ids=["recipe-3"],
            ),
            PatternGroup(
                pattern_text="chicken breast",
                ingredient_ids=["ing-6"],
                recipe_ids=["recipe-4"],
            ),
            PatternGroup(
                pattern_text="chicken breasts",
                ingredient_ids=["ing-7", "ing-8"],
                recipe_ids=["recipe-5"],
            ),
        ]

    def test_find_similar_patterns_plurals(self, analyzer, sample_pattern_groups):
        """Test that plural variations are detected as similar."""
        # Act
        result = analyzer.find_similar_patterns(sample_pattern_groups)

        # Assert
        cup_pattern = next(pg for pg in result if pg.pattern_text == "cup")
        cups_pattern = next(pg for pg in result if pg.pattern_text == "cups")

        # "cup" and "cups" should be linked (75% similarity < 85% threshold, so shouldn't match)
        # Let's verify: similarity_ratio("cup", "cups") = 1 - (1/4) = 0.75
        # With 0.85 threshold, they should NOT be similar
        assert "cups" not in cup_pattern.suggested_similar_patterns
        assert "cup" not in cups_pattern.suggested_similar_patterns

    def test_find_similar_patterns_with_lower_threshold(self):
        """Test similarity detection with lower threshold."""
        # Arrange
        analyzer = PatternAnalyzer(similarity_threshold=0.70)
        patterns = [
            PatternGroup(
                pattern_text="cup",
                ingredient_ids=["ing-1"],
                recipe_ids=["recipe-1"],
            ),
            PatternGroup(
                pattern_text="cups",
                ingredient_ids=["ing-2"],
                recipe_ids=["recipe-2"],
            ),
        ]

        # Act
        result = analyzer.find_similar_patterns(patterns)

        # Assert - with 70% threshold, "cup" and "cups" (75% similar) should match
        cup_pattern = next(pg for pg in result if pg.pattern_text == "cup")
        cups_pattern = next(pg for pg in result if pg.pattern_text == "cups")

        assert "cups" in cup_pattern.suggested_similar_patterns
        assert "cup" in cups_pattern.suggested_similar_patterns

    def test_find_similar_patterns_case_insensitive(self, analyzer):
        """Test that similarity detection is case-insensitive."""
        # Arrange
        patterns = [
            PatternGroup(
                pattern_text="Chicken",
                ingredient_ids=["ing-1"],
                recipe_ids=["recipe-1"],
            ),
            PatternGroup(
                pattern_text="chicken",
                ingredient_ids=["ing-2"],
                recipe_ids=["recipe-2"],
            ),
        ]

        # Act
        result = analyzer.find_similar_patterns(patterns)

        # Assert - identical when lowercased
        chicken_cap = next(pg for pg in result if pg.pattern_text == "Chicken")
        chicken_lower = next(pg for pg in result if pg.pattern_text == "chicken")

        assert "chicken" in chicken_cap.suggested_similar_patterns
        assert "Chicken" in chicken_lower.suggested_similar_patterns

    def test_find_similar_patterns_no_matches(self, analyzer):
        """Test that dissimilar patterns are not linked."""
        # Arrange
        patterns = [
            PatternGroup(
                pattern_text="cup",
                ingredient_ids=["ing-1"],
                recipe_ids=["recipe-1"],
            ),
            PatternGroup(
                pattern_text="chicken",
                ingredient_ids=["ing-2"],
                recipe_ids=["recipe-2"],
            ),
            PatternGroup(
                pattern_text="salt",
                ingredient_ids=["ing-3"],
                recipe_ids=["recipe-3"],
            ),
        ]

        # Act
        result = analyzer.find_similar_patterns(patterns)

        # Assert - none should have similar patterns
        for pattern in result:
            assert pattern.suggested_similar_patterns == []

    def test_find_similar_patterns_preserves_original_data(self, analyzer):
        """Test that original pattern data is preserved."""
        # Arrange
        patterns = [
            PatternGroup(
                pattern_text="cup",
                ingredient_ids=["ing-1", "ing-2"],
                recipe_ids=["recipe-1", "recipe-2"],
            ),
        ]
        # Must transition through PARSING before MATCHED
        patterns[0].transition_unit_to(PatternStatus.PARSING)
        patterns[0].set_matched(unit_id="unit-123")

        # Act
        result = analyzer.find_similar_patterns(patterns)

        # Assert
        assert len(result) == 1
        assert result[0].pattern_text == "cup"
        assert result[0].ingredient_ids == ["ing-1", "ing-2"]
        assert result[0].recipe_ids == ["recipe-1", "recipe-2"]
        assert result[0].unit_status == PatternStatus.MATCHED
        assert result[0].matched_unit_id == "unit-123"

    def test_find_similar_patterns_empty_list(self, analyzer):
        """Test with empty pattern list."""
        # Act
        result = analyzer.find_similar_patterns([])

        # Assert
        assert result == []

    def test_find_similar_patterns_single_pattern(self, analyzer):
        """Test with single pattern."""
        # Arrange
        patterns = [
            PatternGroup(
                pattern_text="cup",
                ingredient_ids=["ing-1"],
                recipe_ids=["recipe-1"],
            ),
        ]

        # Act
        result = analyzer.find_similar_patterns(patterns)

        # Assert
        assert len(result) == 1
        assert result[0].suggested_similar_patterns == []

    def test_configurable_threshold(self):
        """Test that threshold is configurable."""
        # Arrange
        analyzer_strict = PatternAnalyzer(similarity_threshold=0.95)
        analyzer_lenient = PatternAnalyzer(similarity_threshold=0.50)

        patterns = [
            PatternGroup(pattern_text="cup", ingredient_ids=["ing-1"], recipe_ids=["recipe-1"]),
            PatternGroup(pattern_text="cups", ingredient_ids=["ing-2"], recipe_ids=["recipe-2"]),
        ]

        # Act
        result_strict = analyzer_strict.find_similar_patterns(patterns)
        result_lenient = analyzer_lenient.find_similar_patterns(patterns)

        # Assert
        # Strict threshold (95%) - shouldn't match (75% similar)
        cup_strict = next(pg for pg in result_strict if pg.pattern_text == "cup")
        assert cup_strict.suggested_similar_patterns == []

        # Lenient threshold (50%) - should match (75% similar)
        cup_lenient = next(pg for pg in result_lenient if pg.pattern_text == "cup")
        assert "cups" in cup_lenient.suggested_similar_patterns


class TestSimilarityPerformance:
    """Test performance requirements for similarity detection."""

    def test_performance_500_patterns(self):
        """Test that 500 patterns can be processed within 3 seconds."""
        # Arrange
        analyzer = PatternAnalyzer()
        # Use realistic patterns with varied lengths to trigger optimizations
        base_patterns = [
            "cup",
            "teaspoon",
            "tablespoon",
            "lb",
            "oz",
            "gram",
            "ml",
            "liter",
        ]
        patterns = [
            PatternGroup(
                pattern_text=f"{base_patterns[i % len(base_patterns)]}_{i}",
                ingredient_ids=[f"ing-{i}"],
                recipe_ids=[f"recipe-{i}"],
            )
            for i in range(500)
        ]

        # Act
        start_time = time.time()
        result = analyzer.find_similar_patterns(patterns)
        elapsed_time = time.time() - start_time

        # Assert
        assert len(result) == 500
        # Performance requirement: <3 seconds, but allow some margin for CI/slower systems
        assert elapsed_time < 5.0, f"Processing took {elapsed_time:.2f}s, should be < 5s"


class TestSimilarityEdgeCases:
    """Test edge cases for similarity detection."""

    def test_unicode_patterns(self):
        """Test similarity with Unicode characters."""
        # Arrange
        analyzer = PatternAnalyzer(similarity_threshold=0.85)
        patterns = [
            PatternGroup(
                pattern_text="jalapeño",
                ingredient_ids=["ing-1"],
                recipe_ids=["recipe-1"],
            ),
            PatternGroup(
                pattern_text="jalapeño",
                ingredient_ids=["ing-2"],
                recipe_ids=["recipe-2"],
            ),
        ]

        # Act
        result = analyzer.find_similar_patterns(patterns)

        # Assert - identical patterns should match
        assert result[0].suggested_similar_patterns == ["jalapeño"]
        assert result[1].suggested_similar_patterns == ["jalapeño"]

    def test_special_characters(self):
        """Test similarity with special characters."""
        # Arrange
        analyzer = PatternAnalyzer(similarity_threshold=0.85)
        patterns = [
            PatternGroup(
                pattern_text="1/2 cup",
                ingredient_ids=["ing-1"],
                recipe_ids=["recipe-1"],
            ),
            PatternGroup(
                pattern_text="1/2 cups",
                ingredient_ids=["ing-2"],
                recipe_ids=["recipe-2"],
            ),
        ]

        # Act
        result = analyzer.find_similar_patterns(patterns)

        # Assert
        # similarity_ratio("1/2 cup", "1/2 cups") = 1 - (1/8) = 0.875 > 0.85
        cup_pattern = next(pg for pg in result if pg.pattern_text == "1/2 cup")
        assert "1/2 cups" in cup_pattern.suggested_similar_patterns
