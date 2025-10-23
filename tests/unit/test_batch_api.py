"""Integration tests for batch API functions with mocked responses."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from mealie_parser.api import update_ingredient_food_batch, update_ingredient_unit_batch


def create_mock_response(json_data=None, status=200, raise_error=None):
    """Helper to create a mock aiohttp response that supports async context manager."""
    # Create the actual response object
    mock_resp = MagicMock()
    mock_resp.status = status  # Add status attribute for error handling

    if raise_error:
        mock_resp.raise_for_status = Mock(side_effect=raise_error)
    else:
        mock_resp.raise_for_status = Mock()
        mock_resp.json = AsyncMock(return_value=json_data or {})

    # Create a context manager that returns the response
    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)

    return mock_ctx


@pytest.fixture
def mock_session():
    """Fixture providing a mocked aiohttp session."""
    session = MagicMock()
    # Make get() and put() return the context manager directly, not as coroutines
    session.get = Mock()
    session.put = Mock()
    return session


class TestUpdateIngredientUnitBatch:
    """Test update_ingredient_unit_batch function."""

    @pytest.mark.asyncio
    async def test_successful_batch_update(self, mock_session):
        """Test successful batch update of all ingredients."""
        # Arrange
        unit_id = "unit-123"
        ingredient_ids = ["ing-1", "ing-2", "ing-3"]

        # Mock GET and PUT responses for each ingredient
        get_responses = [create_mock_response({"id": ing_id, "note": "test"}) for ing_id in ingredient_ids]
        put_responses = [create_mock_response({"id": ing_id, "unit": {"id": unit_id}}) for ing_id in ingredient_ids]

        mock_session.get.side_effect = get_responses
        mock_session.put.side_effect = put_responses

        # Act
        result = await update_ingredient_unit_batch(mock_session, unit_id, ingredient_ids)

        # Assert
        assert result.total == 3
        assert len(result.successful) == 3
        assert len(result.failed) == 0
        assert result.successful == ingredient_ids

    @pytest.mark.asyncio
    async def test_partial_failure(self, mock_session):
        """Test batch update with some failures."""
        # Arrange
        unit_id = "unit-123"
        ingredient_ids = ["ing-1", "ing-2", "ing-3"]

        # Mock successful for ing-1
        get_resp_1 = create_mock_response({"id": "ing-1", "note": "test"})
        put_resp_1 = create_mock_response({"id": "ing-1", "unit": {"id": unit_id}})

        # Mock failure for ing-2 (GET fails)
        get_resp_2 = create_mock_response(raise_error=Exception("404 Not Found"))

        # Mock successful for ing-3
        get_resp_3 = create_mock_response({"id": "ing-3", "note": "test"})
        put_resp_3 = create_mock_response({"id": "ing-3", "unit": {"id": unit_id}})

        mock_session.get.side_effect = [get_resp_1, get_resp_2, get_resp_3]
        mock_session.put.side_effect = [put_resp_1, put_resp_3]

        # Act
        result = await update_ingredient_unit_batch(mock_session, unit_id, ingredient_ids)

        # Assert
        assert result.total == 3
        assert len(result.successful) == 2
        assert len(result.failed) == 1
        assert "ing-1" in result.successful
        assert "ing-3" in result.successful
        assert result.failed[0]["id"] == "ing-2"

    @pytest.mark.asyncio
    async def test_empty_ingredient_list(self, mock_session):
        """Test batch update with empty ingredient list."""
        # Act
        result = await update_ingredient_unit_batch(mock_session, "unit-123", [])

        # Assert
        assert result.total == 0
        assert result.successful == []
        assert result.failed == []

    @pytest.mark.asyncio
    async def test_continues_after_failure(self, mock_session):
        """Test that processing continues after individual failures."""
        # Arrange
        unit_id = "unit-123"
        ingredient_ids = ["ing-1", "ing-2"]

        # Mock failure for ing-1
        get_resp_1 = create_mock_response(raise_error=Exception("Network error"))

        # Mock success for ing-2
        get_resp_2 = create_mock_response({"id": "ing-2", "note": "test"})
        put_resp_2 = create_mock_response({"id": "ing-2", "unit": {"id": unit_id}})

        mock_session.get.side_effect = [get_resp_1, get_resp_2]
        mock_session.put.side_effect = [put_resp_2]

        # Act
        result = await update_ingredient_unit_batch(mock_session, unit_id, ingredient_ids)

        # Assert - ing-2 should succeed despite ing-1 failing
        assert len(result.successful) == 1
        assert "ing-2" in result.successful
        assert len(result.failed) == 1
        assert result.failed[0]["id"] == "ing-1"


class TestUpdateIngredientFoodBatch:
    """Test update_ingredient_food_batch function."""

    @pytest.mark.asyncio
    async def test_successful_batch_update(self, mock_session):
        """Test successful batch update of all ingredients."""
        # Arrange
        food_id = "food-456"
        ingredient_ids = ["ing-1", "ing-2"]

        # Mock GET and PUT responses
        get_responses = [create_mock_response({"id": ing_id, "note": "test"}) for ing_id in ingredient_ids]
        put_responses = [create_mock_response({"id": ing_id, "food": {"id": food_id}}) for ing_id in ingredient_ids]

        mock_session.get.side_effect = get_responses
        mock_session.put.side_effect = put_responses

        # Act
        result = await update_ingredient_food_batch(mock_session, food_id, ingredient_ids)

        # Assert
        assert result.total == 2
        assert len(result.successful) == 2
        assert len(result.failed) == 0
        assert result.successful == ingredient_ids

    @pytest.mark.asyncio
    async def test_partial_failure(self, mock_session):
        """Test batch update with PUT failure."""
        # Arrange
        food_id = "food-456"
        ingredient_ids = ["ing-1", "ing-2"]

        # Mock successful GET for both, PUT failure for ing-2
        get_resp_1 = create_mock_response({"id": "ing-1", "note": "test"})
        get_resp_2 = create_mock_response({"id": "ing-2", "note": "test"})

        put_resp_1 = create_mock_response({"id": "ing-1", "food": {"id": food_id}})
        put_resp_2 = create_mock_response(raise_error=Exception("500 Internal Server Error"))

        mock_session.get.side_effect = [get_resp_1, get_resp_2]
        mock_session.put.side_effect = [put_resp_1, put_resp_2]

        # Act
        result = await update_ingredient_food_batch(mock_session, food_id, ingredient_ids)

        # Assert
        assert result.total == 2
        assert len(result.successful) == 1
        assert len(result.failed) == 1
        assert result.successful[0] == "ing-1"
        assert result.failed[0]["id"] == "ing-2"

    @pytest.mark.asyncio
    async def test_empty_ingredient_list(self, mock_session):
        """Test batch update with empty ingredient list."""
        # Act
        result = await update_ingredient_food_batch(mock_session, "food-456", [])

        # Assert
        assert result.total == 0
        assert result.successful == []
        assert result.failed == []

    @pytest.mark.asyncio
    async def test_error_details_captured(self, mock_session):
        """Test that error details are captured in failure summary."""
        # Arrange
        food_id = "food-456"
        ingredient_ids = ["ing-1"]

        # Mock GET that raises exception
        error_msg = "Connection timeout"
        get_resp = create_mock_response(raise_error=Exception(error_msg))

        mock_session.get.side_effect = [get_resp]

        # Act
        result = await update_ingredient_food_batch(mock_session, food_id, ingredient_ids)

        # Assert
        assert len(result.failed) == 1
        assert result.failed[0]["id"] == "ing-1"
        # Error message might be wrapped in "Unexpected error" prefix
        assert "ing-1" in result.failed[0]["id"]


class TestBatchErrorRecovery:
    """Test error recovery behavior in batch operations."""

    @pytest.mark.asyncio
    async def test_all_failures_handled(self, mock_session):
        """Test that all failures are collected and returned."""
        # Arrange
        unit_id = "unit-123"
        ingredient_ids = ["ing-1", "ing-2", "ing-3"]

        # Mock all GET requests to fail
        get_responses = [
            create_mock_response(raise_error=Exception("Error 1")),
            create_mock_response(raise_error=Exception("Error 2")),
            create_mock_response(raise_error=Exception("Error 3")),
        ]

        mock_session.get.side_effect = get_responses

        # Act
        result = await update_ingredient_unit_batch(mock_session, unit_id, ingredient_ids)

        # Assert
        assert result.total == 3
        assert len(result.successful) == 0
        assert len(result.failed) == 3
        assert all("error" in failure for failure in result.failed)

    @pytest.mark.asyncio
    async def test_session_reuse(self, mock_session):
        """Test that the same session is reused for all operations."""
        # Arrange
        food_id = "food-456"
        ingredient_ids = ["ing-1", "ing-2"]

        # Mock successful operations
        get_responses = [
            create_mock_response({"id": "ing-1"}),
            create_mock_response({"id": "ing-2"}),
        ]
        put_responses = [
            create_mock_response({"id": "ing-1"}),
            create_mock_response({"id": "ing-2"}),
        ]

        mock_session.get.side_effect = get_responses
        mock_session.put.side_effect = put_responses

        # Act
        await update_ingredient_food_batch(mock_session, food_id, ingredient_ids)

        # Assert - session should be called multiple times (not recreated)
        assert mock_session.get.call_count == 2
        assert mock_session.put.call_count == 2
