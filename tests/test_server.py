"""Tests for the server module."""

from unittest.mock import AsyncMock, patch

import pytest
from starlette.testclient import TestClient

from datadivr.exceptions import InvalidMessageFormat
from datadivr.transport.models import WebSocketMessage
from datadivr.transport.server import app, handle_msg


@pytest.fixture
def client() -> TestClient:
    """Create a TestClient for testing."""
    with TestClient(app) as client:
        yield client


def test_websocket_connection(client: TestClient) -> None:
    """Test WebSocket connection handling."""
    with client.websocket_connect("/ws") as websocket:
        # Send a valid message to confirm the connection
        websocket.send_json({
            "event_name": "ping",  # Add the required event_name field
            "payload": {},  # Include an empty payload or appropriate data
            "to": "all",  # Specify the recipient
        })
        response = websocket.receive_json()
        assert response is not None  # Check that a response is received


@pytest.mark.asyncio
async def test_handle_msg_valid() -> None:
    """Test handling a valid message."""
    message = WebSocketMessage(event_name="test_event", payload={"data": 123}, to="all")

    with patch("datadivr.transport.server.get_handlers") as mock_get_handlers:
        mock_handler = AsyncMock(return_value=message)
        mock_get_handlers.return_value = {"test_event": mock_handler}

        response = await handle_msg(message)

        assert response == message
        mock_handler.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_handle_msg_invalid() -> None:
    """Test handling an invalid message."""
    message = WebSocketMessage(event_name="invalid_event", payload={"data": 123}, to="all")

    with patch("datadivr.transport.server.get_handlers") as mock_get_handlers:
        mock_get_handlers.return_value = {}

        response = await handle_msg(message)

        assert response == message  # Should return the original message if no handler is found


def test_handle_connection_invalid_message_format(client: TestClient) -> None:
    """Test handling an invalid message format."""
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"invalid": "data"})  # Send invalid data

        with pytest.raises(InvalidMessageFormat):
            websocket.receive_json()  # Expect an InvalidMessageFormat exception
