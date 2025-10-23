"""Validation utilities for user inputs and data integrity checks."""

import re
from dataclasses import dataclass, field

from loguru import logger


# Validation constants
MAX_NAME_LENGTH = 100
MAX_ABBREVIATION_LENGTH = 20
DISALLOWED_CHARS = ["<", ">", "&", ";", "|"]
VALID_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\s\-\_\.\(\)\']+$")


class ValidationError(Exception):
    """Raised when validation fails critically."""

    pass


@dataclass
class ValidationResult:
    """
    Result of a validation operation.

    Attributes
    ----------
    is_valid : bool
        Whether the validation passed
    errors : list[str]
        List of error messages
    warnings : list[str]
        List of warning messages
    """

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """
        Add error message and set is_valid to False.

        Parameters
        ----------
        message : str
            Error message to add
        """
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """
        Add warning message without affecting validity.

        Parameters
        ----------
        message : str
            Warning message to add
        """
        self.warnings.append(message)


def check_disallowed_chars(text: str) -> list[str]:
    """
    Check for disallowed characters in text.

    Parameters
    ----------
    text : str
        Text to check

    Returns
    -------
    list[str]
        List of disallowed characters found
    """
    found = []
    for char in DISALLOWED_CHARS:
        if char in text:
            found.append(char)
    return found


def check_duplicate_name(name: str, existing_items: list[dict]) -> bool:
    """
    Check if name already exists (case-insensitive).

    Parameters
    ----------
    name : str
        Name to check
    existing_items : list[dict]
        List of existing items with 'name' field

    Returns
    -------
    bool
        True if duplicate found, False otherwise
    """
    name_lower = name.lower().strip()
    return any(item.get("name", "").lower().strip() == name_lower for item in existing_items)


def validate_unit_name(name: str, existing_units: list[dict]) -> ValidationResult:
    """
    Validate unit name for creation.

    Parameters
    ----------
    name : str
        The unit name to validate
    existing_units : list[dict]
        List of existing units to check for duplicates

    Returns
    -------
    ValidationResult
        Validation result with errors and warnings

    Examples
    --------
    >>> result = validate_unit_name("tsp", existing_units)
    >>> if result.is_valid:
    ...     # Proceed with creation
    ... else:
    ...     # Display errors
    """
    result = ValidationResult(is_valid=True)

    # Check empty
    if not name or not name.strip():
        result.add_error("Unit name cannot be empty")
        return result

    # Check max length
    if len(name) > MAX_NAME_LENGTH:
        result.add_error(f"Unit name cannot exceed {MAX_NAME_LENGTH} characters")

    # Check disallowed characters
    disallowed = check_disallowed_chars(name)
    if disallowed:
        result.add_error(f"Unit name cannot contain: {', '.join(disallowed)}")

    # Check valid pattern
    if not VALID_NAME_PATTERN.match(name):
        result.add_error(
            "Unit name can only contain letters, numbers, spaces, hyphens, underscores, periods, and parentheses"
        )

    # Check duplicates
    if check_duplicate_name(name, existing_units):
        result.add_error(f"Unit '{name}' already exists")

    if result.is_valid:
        logger.debug(f"Unit name '{name}' passed validation")
    else:
        logger.warning(f"Unit name '{name}' validation failed: {result.errors}")

    return result


def validate_food_name(name: str, existing_foods: list[dict]) -> ValidationResult:
    """
    Validate food name for creation.

    Parameters
    ----------
    name : str
        The food name to validate
    existing_foods : list[dict]
        List of existing foods to check for duplicates

    Returns
    -------
    ValidationResult
        Validation result with errors and warnings

    Examples
    --------
    >>> result = validate_food_name("chicken breast", existing_foods)
    >>> if result.is_valid:
    ...     # Proceed with creation
    ... else:
    ...     # Display errors
    """
    result = ValidationResult(is_valid=True)

    # Check empty
    if not name or not name.strip():
        result.add_error("Food name cannot be empty")
        return result

    # Check max length
    if len(name) > MAX_NAME_LENGTH:
        result.add_error(f"Food name cannot exceed {MAX_NAME_LENGTH} characters")

    # Check disallowed characters
    disallowed = check_disallowed_chars(name)
    if disallowed:
        result.add_error(f"Food name cannot contain: {', '.join(disallowed)}")

    # Check valid pattern
    if not VALID_NAME_PATTERN.match(name):
        result.add_error(
            "Food name can only contain letters, numbers, spaces, hyphens, underscores, periods, parentheses, and apostrophes"
        )

    # Check duplicates
    if check_duplicate_name(name, existing_foods):
        result.add_error(f"Food '{name}' already exists")

    if result.is_valid:
        logger.debug(f"Food name '{name}' passed validation")
    else:
        logger.warning(f"Food name '{name}' validation failed: {result.errors}")

    return result


def validate_abbreviation(abbr: str) -> ValidationResult:
    """
    Validate abbreviation (optional field).

    Parameters
    ----------
    abbr : str
        The abbreviation to validate (can be empty)

    Returns
    -------
    ValidationResult
        Validation result with errors and warnings

    Examples
    --------
    >>> result = validate_abbreviation("tsp")
    >>> if result.is_valid:
    ...     # Proceed
    ... else:
    ...     # Display errors
    """
    result = ValidationResult(is_valid=True)

    # Empty is allowed
    if not abbr:
        return result

    # Check max length
    if len(abbr) > MAX_ABBREVIATION_LENGTH:
        result.add_error(f"Abbreviation cannot exceed {MAX_ABBREVIATION_LENGTH} characters")

    # No spaces allowed in abbreviations
    if " " in abbr:
        result.add_error("Abbreviation cannot contain spaces")

    # Check disallowed characters
    disallowed = check_disallowed_chars(abbr)
    if disallowed:
        result.add_error(f"Abbreviation cannot contain: {', '.join(disallowed)}")

    if result.is_valid:
        logger.debug(f"Abbreviation '{abbr}' passed validation")
    else:
        logger.warning(f"Abbreviation '{abbr}' validation failed: {result.errors}")

    return result


def validate_pattern_text(text: str) -> ValidationResult:
    """
    Validate pattern text for grouping.

    Parameters
    ----------
    text : str
        The pattern text to validate

    Returns
    -------
    ValidationResult
        Validation result with errors and warnings

    Examples
    --------
    >>> result = validate_pattern_text("tsp")
    >>> if result.is_valid:
    ...     # Add to pattern group
    ... else:
    ...     # Skip pattern
    """
    result = ValidationResult(is_valid=True)

    # Check empty
    if not text or not text.strip():
        result.add_error("Pattern text cannot be empty")
        return result

    # Check normalized (trimmed, lowercase)
    if text != text.strip().lower():
        result.add_warning("Pattern text should be normalized (trimmed and lowercase)")

    if result.is_valid:
        logger.debug(f"Pattern text '{text}' passed validation")
    else:
        logger.warning(f"Pattern text '{text}' validation failed: {result.errors}")

    return result


def validate_ingredient_ids(ingredient_ids: list[str], all_recipes: list[dict]) -> ValidationResult:
    """
    Validate that ingredient IDs exist in recipes.

    Parameters
    ----------
    ingredient_ids : list[str]
        List of ingredient IDs to validate
    all_recipes : list[dict]
        List of all recipes with ingredients

    Returns
    -------
    ValidationResult
        Validation result with list of invalid IDs in errors

    Examples
    --------
    >>> result = validate_ingredient_ids(["id1", "id2"], recipes)
    >>> if result.is_valid:
    ...     # Proceed with batch operation
    ... else:
    ...     # Show error with invalid IDs
    """
    result = ValidationResult(is_valid=True)

    # Build set of all valid ingredient IDs
    valid_ids = set()
    for recipe in all_recipes:
        for ing in recipe.get("recipeIngredient", []):
            if isinstance(ing, dict) and ing.get("id"):
                valid_ids.add(ing["id"])

    # Check each provided ID
    invalid_ids = []
    for ing_id in ingredient_ids:
        if ing_id not in valid_ids:
            invalid_ids.append(ing_id)

    if invalid_ids:
        result.add_error(f"Invalid ingredient IDs: {', '.join(invalid_ids[:10])}")
        if len(invalid_ids) > 10:
            result.add_error(f"... and {len(invalid_ids) - 10} more")
        logger.warning(f"Found {len(invalid_ids)} invalid ingredient IDs")

    return result


def validate_api_response(response: dict, expected_fields: list[str]) -> ValidationResult:
    """
    Validate API response structure.

    Parameters
    ----------
    response : dict
        API response to validate
    expected_fields : list[str]
        List of expected field names

    Returns
    -------
    ValidationResult
        Validation result with missing fields in errors

    Examples
    --------
    >>> result = validate_api_response(response, ["id", "name"])
    >>> if result.is_valid:
    ...     # Process response
    ... else:
    ...     # Log validation error
    """
    result = ValidationResult(is_valid=True)

    missing_fields = []
    for field_name in expected_fields:
        if field_name not in response:
            missing_fields.append(field_name)

    if missing_fields:
        result.add_error(f"Missing required fields: {', '.join(missing_fields)}")
        logger.error(f"API response missing fields: {missing_fields}")

    return result
