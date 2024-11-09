import json
from unittest.mock import AsyncMock, patch

import pytest
import websockets

from datadivr.transport.client import WebSocketClient
from datadivr.transport.models import WebSocketMessage


@pytest.fixture
def mock_websocket():
    # Use AsyncMock to avoid issues with unawaited coroutine warnings
    return AsyncMock(spec=websockets.WebSocketClientProtocol)


@pytest.fixture
def client():
    return WebSocketClient("ws://test.com/ws")


@pytest.mark.asyncio
async def test_connect(client, mock_websocket):
    mock_connect = AsyncMock(return_value=mock_websocket)
    mock_websocket.send = AsyncMock()  # Mock the send method

    # Mock send_handler_names correctly as an AsyncMock
    with (
        patch.object(client, "send_handler_names", AsyncMock()) as mock_send_handlers,
        patch("websockets.connect", mock_connect),
    ):
        await client.connect()
        assert client.websocket == mock_websocket
        # Verify that connect was called with the correct URI
        mock_connect.assert_called_once_with(client.uri)
        # Verify that handler names were sent
        mock_send_handlers.assert_called_once()


@pytest.mark.asyncio
async def test_send_message(client, mock_websocket):
    client.websocket = mock_websocket
    mock_websocket.send = AsyncMock()

    payload = {"test": "data"}
    await client.send_message(payload=payload, event_name="test_event")

    expected_message = WebSocketMessage(event_name="test_event", payload=payload, to="others")
    mock_websocket.send.assert_called_once_with(json.dumps(expected_message.model_dump()))


@pytest.mark.asyncio
async def test_receive_messages(client, mock_websocket):
    client.websocket = mock_websocket

    # Create a message to be received
    test_message = {"event_name": "test", "payload": "data"}

    # Mock the receive method to return a JSON string and then raise ConnectionClosed
    mock_websocket.recv = AsyncMock(
        side_effect=[
            json.dumps(test_message),
            websockets.exceptions.ConnectionClosed(rcvd=None, sent=None),  # Use None for both parameters
        ]
    )

    # Use AsyncMock for the handle_event method
    with patch.object(client, "handle_event", AsyncMock()) as mock_handle:
        await client.receive_messages()
        mock_handle.assert_called_once_with(test_message, mock_websocket)


@pytest.mark.asyncio
async def test_handle_event(client, mock_websocket):
    mock_handler = AsyncMock()
    client.handlers = {"test_event": mock_handler}

    message = {"event_name": "test_event", "payload": {"data": "test"}}

    await client.handle_event(message, mock_websocket)
    mock_handler.assert_called_once()


@pytest.mark.asyncio
async def test_send_handler_names(client, mock_websocket):
    client.websocket = mock_websocket
    client.handlers = {"test_handler1": AsyncMock(), "test_handler2": AsyncMock()}
    mock_websocket.send = AsyncMock()

    await client.send_handler_names()

    expected_message = WebSocketMessage(
        event_name="connected successfully", payload={"handlers": ["test_handler1", "test_handler2"]}, to="others"
    )
    mock_websocket.send.assert_called_once_with(json.dumps(expected_message.model_dump()))
