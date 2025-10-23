"""Parse result processing utilities.

This module provides utilities for processing parse results from Mealie's ingredient
parser API. It extracts parsed unit/food names, confidence scores, and determines
matching status against known units/foods.
"""

from typing import Any

from loguru import logger

from mealie_parser.models import PatternStatus
from mealie_parser.models.pattern import PatternGroup


def extract_parsed_unit(ingredient: dict[str, Any]) -> str:
    """
    Extract parsed unit name from ingredient data.

    Parameters
    ----------
    ingredient : dict
        Ingredient object from parser response

    Returns
    -------
    str
        Parsed unit name, or empty string if not found
    """
    if not ingredient.get("unit"):
        return ""

    unit_data = ingredient["unit"]
    if isinstance(unit_data, dict):
        return unit_data.get("name", "")
    if isinstance(unit_data, str):
        return unit_data
    return ""


def extract_parsed_food(ingredient: dict[str, Any]) -> str:
    """
    Extract parsed food name from ingredient data.

    Parameters
    ----------
    ingredient : dict
        Ingredient object from parser response

    Returns
    -------
    str
        Parsed food name, or empty string if not found
    """
    if not ingredient.get("food"):
        return ""

    food_data = ingredient["food"]
    if isinstance(food_data, dict):
        return food_data.get("name", "")
    if isinstance(food_data, str):
        return food_data
    return ""


def extract_confidence_scores(
    parsed_result: dict[str, Any],
) -> tuple[float, float]:
    """
    Extract unit and food confidence scores from parse result.

    Parameters
    ----------
    parsed_result : dict
        Single parse result from parser API

    Returns
    -------
    tuple[float, float]
        (unit_confidence, food_confidence)
    """
    confidence = parsed_result.get("confidence", {})

    if isinstance(confidence, dict):
        # Confidence can have 'unit', 'food', 'quantity', 'average' fields
        unit_conf = confidence.get("unit", confidence.get("average", 0.0))
        food_conf = confidence.get("food", confidence.get("average", 0.0))
        return float(unit_conf), float(food_conf)
    # Fallback to single confidence value
    conf_value = float(confidence) if confidence else 0.0
    return conf_value, conf_value


def check_unit_match(parsed_unit_name: str, known_units: list[dict]) -> bool:
    """
    Check if parsed unit name matches any known unit (case-insensitive).

    Parameters
    ----------
    parsed_unit_name : str
        Parsed unit name to check
    known_units : list[dict]
        List of known units from Mealie

    Returns
    -------
    bool
        True if match found, False otherwise
    """
    if not parsed_unit_name:
        return False

    return any(u.get("name", "").lower() == parsed_unit_name.lower() for u in known_units)


def check_food_match(parsed_food_name: str, known_foods: list[dict]) -> bool:
    """
    Check if parsed food name matches any known food (case-insensitive).

    Parameters
    ----------
    parsed_food_name : str
        Parsed food name to check
    known_foods : list[dict]
        List of known foods from Mealie

    Returns
    -------
    bool
        True if match found, False otherwise
    """
    if not parsed_food_name:
        return False

    return any(f.get("name", "").lower() == parsed_food_name.lower() for f in known_foods)


def get_matched_unit_id(parsed_unit_name: str, known_units: list[dict]) -> str | None:
    """
    Get the ID of the matched unit.

    Parameters
    ----------
    parsed_unit_name : str
        Parsed unit name
    known_units : list[dict]
        List of known units from Mealie

    Returns
    -------
    str | None
        Unit ID if match found, None otherwise
    """
    if not parsed_unit_name:
        return None

    return next(
        (u.get("id") for u in known_units if u.get("name") == parsed_unit_name),
        None,
    )


def get_matched_food_id(parsed_food_name: str, known_foods: list[dict]) -> str | None:
    """
    Get the ID of the matched food.

    Parameters
    ----------
    parsed_food_name : str
        Parsed food name
    known_foods : list[dict]
        List of known foods from Mealie

    Returns
    -------
    str | None
        Food ID if match found, None otherwise
    """
    if not parsed_food_name:
        return None

    return next(
        (f.get("id") for f in known_foods if f.get("name") == parsed_food_name),
        None,
    )


def update_pattern_from_parse_result(  # noqa: C901
    pattern: PatternGroup,
    parse_result: dict[str, Any],
    known_units: list[dict],
    known_foods: list[dict],
) -> None:
    """
    Update pattern with parsed data and determine matching status.

    This is the all-in-one method that:
    1. Extracts parsed unit/food names
    2. Extracts confidence scores
    3. Updates pattern object
    4. Checks for matches
    5. Transitions pattern statuses appropriately

    Parameters
    ----------
    pattern : PatternGroup
        Pattern to update
    parse_result : dict
        Single parse result from parser API (one element from results array)
    known_units : list[dict]
        List of known units from Mealie
    known_foods : list[dict]
        List of known foods from Mealie
    """
    # Extract ingredient data
    ingredient = parse_result.get("ingredient", {})

    # Extract parsed names
    pattern.parsed_unit = extract_parsed_unit(ingredient)
    pattern.parsed_food = extract_parsed_food(ingredient)

    # Extract confidence scores
    unit_conf, food_conf = extract_confidence_scores(parse_result)
    pattern.unit_confidence = unit_conf
    pattern.food_confidence = food_conf

    logger.info(
        f"Parsed '{pattern.pattern_text}': unit='{pattern.parsed_unit}' "
        f"(conf: {pattern.unit_confidence:.2f}), food='{pattern.parsed_food}' "
        f"(conf: {pattern.food_confidence:.2f})"
    )

    # Check unit match and update status
    # Ensure we transition through PARSING state if needed
    if pattern.unit_status == PatternStatus.PENDING:
        pattern.transition_unit_to(PatternStatus.PARSING)

    if pattern.parsed_unit:
        unit_matched = check_unit_match(pattern.parsed_unit, known_units)
        logger.info(
            f"Unit match check for '{pattern.parsed_unit}': {unit_matched} (checked against {len(known_units)} units)"
        )

        if unit_matched:
            if pattern.unit_status != PatternStatus.MATCHED:
                pattern.transition_unit_to(PatternStatus.MATCHED)
            pattern.matched_unit_id = get_matched_unit_id(pattern.parsed_unit, known_units)
        else:
            if pattern.unit_status != PatternStatus.UNMATCHED:
                pattern.transition_unit_to(PatternStatus.UNMATCHED)
    else:
        # No unit was parsed, mark as UNMATCHED
        logger.info(f"No unit parsed for pattern '{pattern.pattern_text}', marking as UNMATCHED")
        if pattern.unit_status != PatternStatus.UNMATCHED:
            pattern.transition_unit_to(PatternStatus.UNMATCHED)

    # Check food match and update status
    # Ensure we transition through PARSING state if needed
    if pattern.food_status == PatternStatus.PENDING:
        pattern.transition_food_to(PatternStatus.PARSING)

    if pattern.parsed_food:
        food_matched = check_food_match(pattern.parsed_food, known_foods)
        logger.info(
            f"Food match check for '{pattern.parsed_food}': {food_matched} (checked against {len(known_foods)} foods)"
        )

        if food_matched:
            if pattern.food_status != PatternStatus.MATCHED:
                pattern.transition_food_to(PatternStatus.MATCHED)
            pattern.matched_food_id = get_matched_food_id(pattern.parsed_food, known_foods)
        else:
            if pattern.food_status != PatternStatus.UNMATCHED:
                pattern.transition_food_to(PatternStatus.UNMATCHED)
    else:
        # No food was parsed, mark as UNMATCHED
        logger.info(f"No food parsed for pattern '{pattern.pattern_text}', marking as UNMATCHED")
        if pattern.food_status != PatternStatus.UNMATCHED:
            pattern.transition_food_to(PatternStatus.UNMATCHED)

    logger.info(
        f"Pattern '{pattern.pattern_text}' status after update: "
        f"unit={pattern.unit_status.value}, food={pattern.food_status.value}"
    )
