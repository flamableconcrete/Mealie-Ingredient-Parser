"""Tests for API alias functions."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from mealie_parser.api import add_food_alias, add_unit_alias


@pytest.mark.asyncio
async def test_add_food_alias_with_object_format():
    """Test that food aliases are correctly formatted as objects with 'name' field."""
    # Mock session
    session = MagicMock()

    # Mock GET response - food with existing alias in object format
    get_response = MagicMock()
    get_response.raise_for_status = MagicMock()
    get_response.json = AsyncMock(
        return_value={
            "id": "food-123",
            "name": "cheddar cheese",
            "aliases": [{"name": "sharp cheddar"}],  # Existing alias in object format
        }
    )
    get_response.__aenter__ = AsyncMock(return_value=get_response)
    get_response.__aexit__ = AsyncMock(return_value=None)

    # Mock PUT response
    put_response = MagicMock()
    put_response.raise_for_status = MagicMock()
    put_response.json = AsyncMock(
        return_value={
            "id": "food-123",
            "name": "cheddar cheese",
            "aliases": [{"name": "sharp cheddar"}, {"name": "cheddar"}],
        }
    )
    put_response.__aenter__ = AsyncMock(return_value=put_response)
    put_response.__aexit__ = AsyncMock(return_value=None)

    # Configure session.get and session.put to return the mocked responses
    session.get = MagicMock(return_value=get_response)
    session.put = MagicMock(return_value=put_response)

    # Call the function
    result = await add_food_alias(session, "food-123", "cheddar")

    # Verify PUT was called with properly formatted aliases
    session.put.assert_called_once()
    put_call_args = session.put.call_args
    sent_data = put_call_args[1]["json"]

    # Check that the new alias was added in object format
    assert sent_data["aliases"] == [{"name": "sharp cheddar"}, {"name": "cheddar"}]


@pytest.mark.asyncio
async def test_add_food_alias_duplicate_check():
    """Test that duplicate aliases are not added."""
    # Mock session
    session = MagicMock()

    # Mock GET response - food with existing alias
    get_response = MagicMock()
    get_response.raise_for_status = MagicMock()
    get_response.json = AsyncMock(
        return_value={
            "id": "food-123",
            "name": "cheddar cheese",
            "aliases": [{"name": "cheddar"}],  # Alias already exists
        }
    )
    get_response.__aenter__ = AsyncMock(return_value=get_response)
    get_response.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(return_value=get_response)
    session.put = MagicMock()

    # Call the function with an alias that already exists
    result = await add_food_alias(session, "food-123", "cheddar")

    # Verify PUT was NOT called (no update needed)
    session.put.assert_not_called()


@pytest.mark.asyncio
async def test_add_unit_alias_with_object_format():
    """Test that unit aliases are correctly formatted as objects with 'name' field."""
    # Mock session
    session = MagicMock()

    # Mock GET response - unit with existing alias in object format
    get_response = MagicMock()
    get_response.raise_for_status = MagicMock()
    get_response.json = AsyncMock(
        return_value={
            "id": "unit-123",
            "name": "tablespoon",
            "aliases": [{"name": "T"}],  # Existing alias in object format
        }
    )
    get_response.__aenter__ = AsyncMock(return_value=get_response)
    get_response.__aexit__ = AsyncMock(return_value=None)

    # Mock PUT response
    put_response = MagicMock()
    put_response.raise_for_status = MagicMock()
    put_response.json = AsyncMock(
        return_value={
            "id": "unit-123",
            "name": "tablespoon",
            "aliases": [{"name": "T"}, {"name": "tbsp"}],
        }
    )
    put_response.__aenter__ = AsyncMock(return_value=put_response)
    put_response.__aexit__ = AsyncMock(return_value=None)

    # Configure session.get and session.put to return the mocked responses
    session.get = MagicMock(return_value=get_response)
    session.put = MagicMock(return_value=put_response)

    # Call the function
    result = await add_unit_alias(session, "unit-123", "tbsp")

    # Verify PUT was called with properly formatted aliases
    session.put.assert_called_once()
    put_call_args = session.put.call_args
    sent_data = put_call_args[1]["json"]

    # Check that the new alias was added in object format
    assert sent_data["aliases"] == [{"name": "T"}, {"name": "tbsp"}]


@pytest.mark.asyncio
async def test_add_unit_alias_duplicate_check():
    """Test that duplicate unit aliases are not added."""
    # Mock session
    session = MagicMock()

    # Mock GET response - unit with existing alias
    get_response = MagicMock()
    get_response.raise_for_status = MagicMock()
    get_response.json = AsyncMock(
        return_value={
            "id": "unit-123",
            "name": "tablespoon",
            "aliases": [{"name": "tbsp"}],  # Alias already exists
        }
    )
    get_response.__aenter__ = AsyncMock(return_value=get_response)
    get_response.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(return_value=get_response)
    session.put = MagicMock()

    # Call the function with an alias that already exists
    result = await add_unit_alias(session, "unit-123", "tbsp")

    # Verify PUT was NOT called (no update needed)
    session.put.assert_not_called()
