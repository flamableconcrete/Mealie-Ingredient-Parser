"""Utility functions for the Mealie parser."""


def is_recipe_unparsed(recipe_ingredients):
    """
    Check if a recipe has unparsed ingredients.

    An ingredient is considered unparsed if it has text (note or originalText)
    but no associated food or unit.
    """
    if not recipe_ingredients:
        return False

    for ing in recipe_ingredients:
        if isinstance(ing, dict):
            has_food = ing.get("food") and (
                isinstance(ing["food"], dict) and ing["food"].get("id")
            )
            has_unit = ing.get("unit") and (
                isinstance(ing["unit"], dict) and ing["unit"].get("id")
            )
            has_text = ing.get("note") or ing.get("originalText")

            if has_text and not (has_food or has_unit):
                return True

    return False


def extract_missing_units(parsed_ingredients, known_units):
    """
    Extract missing units from parsed ingredients.

    Returns a dict mapping unit names to occurrence info:
    {
        "unit_name": {
            "suggestion": "unit_name",
            "count": 2,
            "ingredients": ["1 cup flour", "2 cups sugar"]
        }
    }
    """
    known_unit_names = {u["name"].lower() for u in known_units}
    missing_units = {}

    for ing in parsed_ingredients:
        if not isinstance(ing, dict):
            continue

        # Check if unit exists but isn't in known units
        # Parser returns structure: {"ingredient": {"unit": {...}}, "input": "..."}
        unit = ing.get("ingredient", {}).get("unit")
        original_text = ing.get("input", "")

        if unit and isinstance(unit, dict):
            unit_name = unit.get("name", "")
            if unit_name and unit_name.lower() not in known_unit_names:
                if unit_name not in missing_units:
                    missing_units[unit_name] = {
                        "suggestion": unit_name,
                        "count": 0,
                        "ingredients": []
                    }
                missing_units[unit_name]["count"] += 1
                missing_units[unit_name]["ingredients"].append(original_text)

    return missing_units
