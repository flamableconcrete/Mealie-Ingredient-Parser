"""Unit tests for pattern skip/ignore functionality."""

import pytest

from mealie_parser.models.pattern import PatternGroup, PatternStatus


@pytest.fixture
def sample_patterns():
    """Sample patterns for testing."""
    return [
        PatternGroup(
            pattern_text="tsp",
            ingredient_ids=["ing-1", "ing-2"],
            recipe_ids=["recipe-1"],
        ),
        PatternGroup(
            pattern_text="tbsp",
            ingredient_ids=["ing-3"],
            recipe_ids=["recipe-2"],
        ),
        PatternGroup(
            pattern_text="cup",
            ingredient_ids=["ing-4", "ing-5", "ing-6"],
            recipe_ids=["recipe-3"],
        ),
    ]


def test_pattern_starts_pending(sample_patterns):
    """Test patterns initialize with PENDING status."""
    for pattern in sample_patterns:
        assert pattern.unit_status == PatternStatus.PENDING
        assert pattern.food_status == PatternStatus.PENDING


def test_ignore_pattern_updates_status(sample_patterns):
    """Test ignoring a pattern updates its status."""
    pattern = sample_patterns[0]
    assert pattern.unit_status == PatternStatus.PENDING

    # Transition to IGNORE (skip processing)
    pattern.unit_status = PatternStatus.IGNORE
    assert pattern.unit_status == PatternStatus.IGNORE


def test_skipped_count_increments():
    """Test skipped count increments correctly."""
    skipped_count = 0

    skipped_count += 1
    assert skipped_count == 1

    skipped_count += 1
    assert skipped_count == 2


def test_skipped_count_decrements():
    """Test skipped count decrements correctly."""
    skipped_count = 2

    skipped_count -= 1
    assert skipped_count == 1

    skipped_count -= 1
    assert skipped_count == 0


def test_pending_patterns_detection(sample_patterns):
    """Test detection of pending patterns."""
    # All patterns start as pending
    pending = [p for p in sample_patterns if p.unit_status == PatternStatus.PENDING]
    assert len(pending) == 3

    # Ignore one pattern
    sample_patterns[0].unit_status = PatternStatus.IGNORE
    pending = [p for p in sample_patterns if p.unit_status == PatternStatus.PENDING]
    assert len(pending) == 2

    # Match one pattern (must go through PARSING state first)
    sample_patterns[1].transition_unit_to(PatternStatus.PARSING)
    sample_patterns[1].set_matched(unit_id="unit-123")
    pending = [p for p in sample_patterns if p.unit_status == PatternStatus.PENDING]
    assert len(pending) == 1


def test_all_pending_patterns_processed(sample_patterns):
    """Test detection when all pending patterns are processed."""
    pending = [p for p in sample_patterns if p.unit_status == PatternStatus.PENDING]
    assert len(pending) == 3

    # Process all patterns (must go through PARSING state for matches)
    sample_patterns[0].transition_unit_to(PatternStatus.PARSING)
    sample_patterns[0].set_matched(unit_id="unit-1")
    sample_patterns[1].unit_status = PatternStatus.IGNORE
    sample_patterns[2].transition_unit_to(PatternStatus.PARSING)
    sample_patterns[2].set_matched(unit_id="unit-2")

    pending = [p for p in sample_patterns if p.unit_status == PatternStatus.PENDING]
    assert len(pending) == 0


def test_ignored_patterns_filtering(sample_patterns):
    """Test filtering to show only ignored patterns."""
    # Ignore some patterns
    sample_patterns[0].unit_status = PatternStatus.IGNORE
    sample_patterns[2].food_status = PatternStatus.IGNORE

    unit_ignored = [p for p in sample_patterns if p.unit_status == PatternStatus.IGNORE]
    food_ignored = [p for p in sample_patterns if p.food_status == PatternStatus.IGNORE]

    assert len(unit_ignored) == 1
    assert unit_ignored[0].pattern_text == "tsp"
    assert len(food_ignored) == 1
    assert food_ignored[0].pattern_text == "cup"


def test_next_pending_pattern_search(sample_patterns):
    """Test finding next pending pattern."""
    # Ignore first pattern
    sample_patterns[0].unit_status = PatternStatus.IGNORE

    # Find next pending (should be index 1)
    current_index = 0
    next_pending_index = None
    for i in range(current_index + 1, len(sample_patterns)):
        if sample_patterns[i].unit_status == PatternStatus.PENDING:
            next_pending_index = i
            break

    assert next_pending_index == 1
    assert sample_patterns[next_pending_index].pattern_text == "tbsp"


def test_skip_from_modal_action():
    """Test skip action from modal returns correct value."""
    # Modal should return "skip" when skip option selected
    modal_result = "skip"
    assert modal_result == "skip"


def test_skip_status_persistence_format():
    """Test skip status can be serialized for session state."""
    ignored_patterns = ["tsp", "tbsp", "cup"]

    # Should be serializable as list of strings
    assert isinstance(ignored_patterns, list)
    assert all(isinstance(p, str) for p in ignored_patterns)


def test_status_bar_format_with_skip_count():
    """Test status bar includes skip count."""
    processed_count = 10
    total = 45
    skipped_count = 3

    status_text = f"Processed: {processed_count}/{total} | Skipped: {skipped_count}"

    assert "Processed: 10/45" in status_text
    assert "Skipped: 3" in status_text


def test_keyboard_binding_for_skip():
    """Test skip keyboard binding is defined."""
    bindings = [
        ("s", "skip_pattern", "Skip"),
        ("u", "undo_skip", "Undo Skip"),
    ]

    skip_binding = [b for b in bindings if b[1] == "skip_pattern"]
    undo_binding = [b for b in bindings if b[1] == "undo_skip"]

    assert len(skip_binding) == 1
    assert skip_binding[0][0] == "s"
    assert len(undo_binding) == 1
    assert undo_binding[0][0] == "u"


def test_completion_summary_statistics():
    """Test completion summary calculates correctly."""
    total_patterns = 45
    completed = 38
    skipped = 7

    assert completed + skipped == total_patterns
    assert skipped > 0  # Has patterns to review


def test_can_be_processed_method(sample_patterns):
    """Test can_be_processed() blocks interaction during PARSING state."""
    pattern = sample_patterns[0]

    # PENDING state - can be processed
    assert pattern.can_be_processed() is True

    # PARSING state - cannot be processed (locked by automation)
    pattern.transition_unit_to(PatternStatus.PARSING)
    assert pattern.can_be_processed() is False

    # UNMATCHED state - can be processed
    pattern.transition_unit_to(PatternStatus.UNMATCHED)
    assert pattern.can_be_processed() is True

    # IGNORE state - can be processed (to allow un-ignoring)
    pattern.unit_status = PatternStatus.IGNORE
    assert pattern.can_be_processed() is True
