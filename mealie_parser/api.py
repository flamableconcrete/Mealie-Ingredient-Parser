"""API functions for interacting with Mealie."""

import aiohttp
from loguru import logger

from .config import API_URL
from .error_handling import (
    BatchOperationResult,
    PermanentAPIError,
    TransientAPIError,
    classify_http_error,
    retry_with_backoff,
)


def _handle_http_error(response: aiohttp.ClientResponse, operation: str):
    """
    Convert HTTP errors to custom exception classes.

    Parameters
    ----------
    response : aiohttp.ClientResponse
        HTTP response object
    operation : str
        Description of the operation for logging

    Raises
    ------
    TransientAPIError or PermanentAPIError
        Appropriate error type based on status code
    """
    error_class = classify_http_error(response.status)
    error_msg = f"{operation} failed with status {response.status}"
    logger.error(error_msg)
    raise error_class(error_msg)


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
async def get_all_recipes(session):
    """Fetch all recipes from Mealie with pagination."""
    recipes = []
    page = 1
    try:
        while True:
            async with session.get(f"{API_URL}/recipes", params={"page": page}) as r:
                if r.status >= 400:
                    _handle_http_error(r, f"Fetch recipes page {page}")
                data = await r.json()
                recipes.extend(data["items"])
                logger.debug(f"Fetched page {page} of recipes ({len(data['items'])} items)")
                if not data.get("next"):
                    break
                page += 1
        logger.info(f"Successfully fetched {len(recipes)} recipes")
        return recipes
    except (TransientAPIError, PermanentAPIError):
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching recipes at page {page}: {e}")
        raise TransientAPIError(f"Network error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error fetching recipes at page {page}: {e}", exc_info=True)
        raise PermanentAPIError(f"Unexpected error: {e}") from e


async def get_recipe_details(session, slug):
    """Fetch detailed information for a specific recipe."""
    try:
        async with session.get(f"{API_URL}/recipes/{slug}") as r:
            r.raise_for_status()
            return await r.json()
            # logger.debug(f"Fetched details for recipe: {slug}")
    except Exception as e:
        logger.error(f"Error fetching recipe details for '{slug}': {e}", exc_info=True)
        raise


async def parse_ingredients(session, ingredients, parser="nlp"):
    """
    Parse ingredient strings using Mealie's parser.

    Parameters
    ----------
    session : aiohttp.ClientSession
        HTTP session for API calls
    ingredients : list[str]
        List of ingredient strings to parse
    parser : str, optional
        Parser method: "nlp", "brute", or "openai" (default: "nlp")

    Returns
    -------
    list[dict]
        Parsed ingredient objects
    """
    body = {"parser": parser, "ingredients": ingredients}
    try:
        async with session.post(f"{API_URL}/parser/ingredients", json=body) as r:
            r.raise_for_status()
            result = await r.json()
            logger.debug(f"Parsed {len(ingredients)} ingredients using {parser} parser")
            return result
    except Exception as e:
        logger.error(f"Error parsing ingredients with {parser} parser: {e}", exc_info=True)
        logger.debug(f"Failed ingredients: {ingredients}")
        raise


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
async def get_units_full(session, progress_callback=None):
    """
    Fetch all units from Mealie with pagination.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The persistent HTTP session for API calls
    progress_callback : callable, optional
        Callback function called after each page: callback(current, total)
        where total is estimated from first page response

    Returns
    -------
    list[dict]
        All units from Mealie instance
    """
    units = []
    page = 1
    try:
        while True:
            async with session.get(f"{API_URL}/units", params={"page": page, "perPage": 100}) as r:
                if r.status >= 400:
                    _handle_http_error(r, f"Fetch units page {page}")
                data = await r.json()
                units.extend(data["items"])
                logger.debug(f"Fetched page {page} of units ({len(data['items'])} items)")

                # Call progress callback if provided
                if progress_callback and data.get("total"):
                    progress_callback(len(units), data["total"])

                if not data.get("next"):
                    break
                page += 1
        logger.info(f"Successfully fetched {len(units)} units")
        return units
    except (TransientAPIError, PermanentAPIError):
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching units at page {page}: {e}")
        raise TransientAPIError(f"Network error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error fetching units at page {page}: {e}", exc_info=True)
        raise PermanentAPIError(f"Unexpected error: {e}") from e


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
async def get_foods_full(session, progress_callback=None):
    """
    Fetch all foods from Mealie with pagination.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The persistent HTTP session for API calls
    progress_callback : callable, optional
        Callback function called after each page: callback(current, total)
        where total is estimated from first page response

    Returns
    -------
    list[dict]
        All foods from Mealie instance
    """
    foods = []
    page = 1
    try:
        while True:
            async with session.get(f"{API_URL}/foods", params={"page": page, "perPage": 100}) as r:
                if r.status >= 400:
                    _handle_http_error(r, f"Fetch foods page {page}")
                data = await r.json()
                foods.extend(data["items"])
                logger.debug(f"Fetched page {page} of foods ({len(data['items'])} items)")

                # Call progress callback if provided
                if progress_callback and data.get("total"):
                    progress_callback(len(foods), data["total"])

                if not data.get("next"):
                    break
                page += 1
        logger.info(f"Successfully fetched {len(foods)} foods")
        return foods
    except (TransientAPIError, PermanentAPIError):
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching foods at page {page}: {e}")
        raise TransientAPIError(f"Network error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error fetching foods at page {page}: {e}", exc_info=True)
        raise PermanentAPIError(f"Unexpected error: {e}") from e


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
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
            if r.status >= 400:
                _handle_http_error(r, f"Create unit '{name}'")
            result = await r.json()
            logger.info(f"Created unit: {name}")
            return result
    except (TransientAPIError, PermanentAPIError):
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Network error creating unit '{name}': {e}")
        raise TransientAPIError(f"Network error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error creating unit '{name}': {e}", exc_info=True)
        logger.debug(f"Unit data: {body}")
        raise PermanentAPIError(f"Unexpected error: {e}") from e


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
async def create_food(session, name, description=""):
    """Create a new food in Mealie."""
    body = {"name": name, "description": description}
    try:
        async with session.post(f"{API_URL}/foods", json=body) as r:
            if r.status >= 400:
                _handle_http_error(r, f"Create food '{name}'")
            result = await r.json()
            logger.info(f"Created food: {name}")
            return result
    except (TransientAPIError, PermanentAPIError):
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Network error creating food '{name}': {e}")
        raise TransientAPIError(f"Network error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error creating food '{name}': {e}", exc_info=True)
        logger.debug(f"Food data: {body}")
        raise PermanentAPIError(f"Unexpected error: {e}") from e


async def add_food_alias(session, food_id, alias):
    """Add an alias to an existing food."""
    try:
        async with session.get(f"{API_URL}/foods/{food_id}") as r:
            r.raise_for_status()
            food = await r.json()

        aliases = food.get("aliases", [])
        # Extract alias names from objects for comparison
        alias_names = [a.get("name", a).lower() if isinstance(a, dict) else a.lower() for a in aliases]

        if alias.lower() not in alias_names:
            # Append as object with 'name' field
            aliases.append({"name": alias})
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
        # Extract alias names from objects for comparison
        alias_names = [a.get("name", a).lower() if isinstance(a, dict) else a.lower() for a in aliases]

        if alias.lower() not in alias_names:
            # Append as object with 'name' field
            aliases.append({"name": alias})
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


async def update_ingredient_unit_batch(session, unit_id, ingredient_ids, progress_callback=None):
    """
    Update multiple ingredients with the same unit ID in batch.

    Processes each ingredient individually and collects success/failure results.
    Continues processing remaining ingredients even if some fail.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The persistent HTTP session for API calls
    unit_id : str
        The unit ID to assign to all ingredients
    ingredient_ids : list[str]
        List of ingredient IDs to update
    progress_callback : callable, optional
        Callback function called after each ingredient: callback(current, total)

    Returns
    -------
    BatchOperationResult
        Result object with successful, failed, and total counts

    Examples
    --------
    >>> result = await update_ingredient_unit_batch(session, "unit-123", ["ing-1", "ing-2"])
    >>> print(f"Success: {len(result.successful)}, Failed: {len(result.failed)}")
    >>> print(f"Success rate: {result.success_rate:.1f}%")
    """
    result = BatchOperationResult(total=len(ingredient_ids))

    logger.info(f"Starting batch update: {len(ingredient_ids)} ingredients with unit ID {unit_id}")

    for idx, ing_id in enumerate(ingredient_ids, 1):
        try:
            # Get current ingredient data
            async with session.get(f"{API_URL}/recipes/ingredients/{ing_id}") as r:
                if r.status >= 400:
                    _handle_http_error(r, f"Fetch ingredient {ing_id}")
                ingredient = await r.json()

            # Update unit reference
            ingredient["unit"] = {"id": unit_id}

            # Save updated ingredient
            async with session.put(f"{API_URL}/recipes/ingredients/{ing_id}", json=ingredient) as r:
                if r.status >= 400:
                    _handle_http_error(r, f"Update ingredient {ing_id}")
                await r.json()

            result.add_success(ing_id)
            logger.debug(f"Updated ingredient {ing_id} with unit {unit_id}")

        except (TransientAPIError, PermanentAPIError) as e:
            error_msg = str(e)
            result.add_failure(ing_id, error_msg)
            logger.warning(f"Failed to update ingredient {ing_id}: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            result.add_failure(ing_id, error_msg)
            logger.warning(f"Unexpected failure for ingredient {ing_id}: {error_msg}")

        # Call progress callback if provided
        if progress_callback:
            progress_callback(idx, len(ingredient_ids))

    logger.info(
        f"Batch update complete: {len(result.successful)} successful, "
        f"{len(result.failed)} failed ({result.success_rate:.1f}% success rate)"
    )

    return result


async def update_ingredient_food_batch(session, food_id, ingredient_ids, progress_callback=None):
    """
    Update multiple ingredients with the same food ID in batch.

    Processes each ingredient individually and collects success/failure results.
    Continues processing remaining ingredients even if some fail.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The persistent HTTP session for API calls
    food_id : str
        The food ID to assign to all ingredients
    ingredient_ids : list[str]
        List of ingredient IDs to update
    progress_callback : callable, optional
        Callback function called after each ingredient: callback(current, total)

    Returns
    -------
    BatchOperationResult
        Result object with successful, failed, and total counts

    Examples
    --------
    >>> result = await update_ingredient_food_batch(session, "food-456", ["ing-1", "ing-2"])
    >>> print(f"Success: {len(result.successful)}, Failed: {len(result.failed)}")
    >>> print(f"Success rate: {result.success_rate:.1f}%")
    """
    result = BatchOperationResult(total=len(ingredient_ids))

    logger.info(f"Starting batch update: {len(ingredient_ids)} ingredients with food ID {food_id}")

    for idx, ing_id in enumerate(ingredient_ids, 1):
        try:
            # Get current ingredient data
            async with session.get(f"{API_URL}/recipes/ingredients/{ing_id}") as r:
                if r.status >= 400:
                    _handle_http_error(r, f"Fetch ingredient {ing_id}")
                ingredient = await r.json()

            # Update food reference
            ingredient["food"] = {"id": food_id}

            # Save updated ingredient
            async with session.put(f"{API_URL}/recipes/ingredients/{ing_id}", json=ingredient) as r:
                if r.status >= 400:
                    _handle_http_error(r, f"Update ingredient {ing_id}")
                await r.json()

            result.add_success(ing_id)
            logger.debug(f"Updated ingredient {ing_id} with food {food_id}")

        except (TransientAPIError, PermanentAPIError) as e:
            error_msg = str(e)
            result.add_failure(ing_id, error_msg)
            logger.warning(f"Failed to update ingredient {ing_id}: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            result.add_failure(ing_id, error_msg)
            logger.warning(f"Unexpected failure for ingredient {ing_id}: {error_msg}")

        # Call progress callback if provided
        if progress_callback:
            progress_callback(idx, len(ingredient_ids))

    logger.info(
        f"Batch update complete: {len(result.successful)} successful, "
        f"{len(result.failed)} failed ({result.success_rate:.1f}% success rate)"
    )

    return result
