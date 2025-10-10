"""API functions for interacting with Mealie."""

import logging
from .config import API_URL

logger = logging.getLogger(__name__)


async def get_all_recipes(session):
    """Fetch all recipes from Mealie with pagination."""
    recipes = []
    page = 1
    try:
        while True:
            async with session.get(f"{API_URL}/recipes", params={"page": page}) as r:
                r.raise_for_status()
                data = await r.json()
                recipes.extend(data["items"])
                logger.debug(f"Fetched page {page} of recipes ({len(data['items'])} items)")
                if not data.get("next"):
                    break
                page += 1
        logger.info(f"Successfully fetched {len(recipes)} recipes")
        return recipes
    except Exception as e:
        logger.error(f"Error fetching recipes at page {page}: {e}", exc_info=True)
        raise


async def get_recipe_details(session, slug):
    """Fetch detailed information for a specific recipe."""
    try:
        async with session.get(f"{API_URL}/recipes/{slug}") as r:
            r.raise_for_status()
            result = await r.json()
            logger.debug(f"Fetched details for recipe: {slug}")
            return result
    except Exception as e:
        logger.error(f"Error fetching recipe details for '{slug}': {e}", exc_info=True)
        raise


async def parse_ingredients(session, ingredients):
    """Parse ingredient strings using Mealie's NLP parser."""
    body = {"parser": "nlp", "ingredients": ingredients}
    try:
        async with session.post(f"{API_URL}/parser/ingredients", json=body) as r:
            r.raise_for_status()
            result = await r.json()
            logger.debug(f"Parsed {len(ingredients)} ingredients")
            return result
    except Exception as e:
        logger.error(f"Error parsing ingredients: {e}", exc_info=True)
        logger.debug(f"Failed ingredients: {ingredients}")
        raise


async def get_units_full(session):
    """Fetch all units from Mealie."""
    try:
        async with session.get(f"{API_URL}/units") as r:
            r.raise_for_status()
            data = await r.json()
            logger.debug(f"Fetched {len(data['items'])} units")
            return data["items"]
    except Exception as e:
        logger.error(f"Error fetching units: {e}", exc_info=True)
        raise


async def get_foods_full(session):
    """Fetch all foods from Mealie."""
    try:
        async with session.get(f"{API_URL}/foods") as r:
            r.raise_for_status()
            data = await r.json()
            logger.debug(f"Fetched {len(data['items'])} foods")
            return data["items"]
    except Exception as e:
        logger.error(f"Error fetching foods: {e}", exc_info=True)
        raise


async def create_unit(session, name, abbreviation="", description=""):
    """Create a new unit in Mealie."""
    body = {
        "name": name,
        "abbreviation": abbreviation or name[:3],
        "description": description,
        "fraction": True,
        "useAbbreviation": False,
    }
    try:
        async with session.post(f"{API_URL}/units", json=body) as r:
            r.raise_for_status()
            result = await r.json()
            logger.info(f"Created unit: {name}")
            return result
    except Exception as e:
        logger.error(f"Error creating unit '{name}': {e}", exc_info=True)
        logger.debug(f"Unit data: {body}")
        raise


async def create_food(session, name, description=""):
    """Create a new food in Mealie."""
    body = {"name": name, "description": description}
    try:
        async with session.post(f"{API_URL}/foods", json=body) as r:
            r.raise_for_status()
            result = await r.json()
            logger.info(f"Created food: {name}")
            return result
    except Exception as e:
        logger.error(f"Error creating food '{name}': {e}", exc_info=True)
        logger.debug(f"Food data: {body}")
        raise


async def add_food_alias(session, food_id, alias):
    """Add an alias to an existing food."""
    try:
        async with session.get(f"{API_URL}/foods/{food_id}") as r:
            r.raise_for_status()
            food = await r.json()

        aliases = food.get("aliases", [])
        if alias.lower() not in [a.lower() for a in aliases]:
            aliases.append(alias)
            food["aliases"] = aliases

            async with session.put(f"{API_URL}/foods/{food_id}", json=food) as r:
                r.raise_for_status()
                result = await r.json()
                logger.info(f"Added alias '{alias}' to food '{food.get('name')}' (ID: {food_id})")
                return result
        else:
            logger.debug(f"Alias '{alias}' already exists for food ID: {food_id}")

        return food
    except Exception as e:
        logger.error(f"Error adding alias '{alias}' to food ID {food_id}: {e}", exc_info=True)
        raise


async def add_unit_alias(session, unit_id, alias):
    """Add an alias to an existing unit."""
    try:
        async with session.get(f"{API_URL}/units/{unit_id}") as r:
            r.raise_for_status()
            unit = await r.json()

        aliases = unit.get("aliases", [])
        if alias.lower() not in [a.lower() for a in aliases]:
            aliases.append(alias)
            unit["aliases"] = aliases

            async with session.put(f"{API_URL}/units/{unit_id}", json=unit) as r:
                r.raise_for_status()
                result = await r.json()
                logger.info(f"Added alias '{alias}' to unit '{unit.get('name')}' (ID: {unit_id})")
                return result
        else:
            logger.debug(f"Alias '{alias}' already exists for unit ID: {unit_id}")

        return unit
    except Exception as e:
        logger.error(f"Error adding alias '{alias}' to unit ID {unit_id}: {e}", exc_info=True)
        raise


async def update_recipe(session, slug, recipe_data):
    """Update a recipe with new data."""
    try:
        async with session.put(f"{API_URL}/recipes/{slug}", json=recipe_data) as r:
            r.raise_for_status()
            result = await r.json()
            logger.info(f"Updated recipe: {slug}")
            return result
    except Exception as e:
        logger.error(f"Error updating recipe '{slug}': {e}", exc_info=True)
        raise
