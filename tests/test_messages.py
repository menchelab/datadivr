"""Tests for the messages module."""

import json
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import WebSocket
from websockets import WebSocketClientProtocol

from datadivr.exceptions import UnsupportedWebSocketTypeError
from datadivr.transport.messages import create_error_message, create_message, send_message
from datadivr.transport.models import WebSocketMessage


@pytest.fixture
def fastapi_websocket() -> Mock:
    """Create a mock FastAPI WebSocket."""
    ws = Mock(spec=WebSocket)
    ws.send_json = AsyncMock()
    return ws


@pytest.fixture
def websockets_client() -> Mock:
    """Create a mock websockets WebSocketClientProtocol."""
    ws = Mock(spec=WebSocketClientProtocol)
    ws.send = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_send_message_fastapi(fastapi_websocket: Mock) -> None:
    """Test sending a message through FastAPI WebSocket."""
    message = WebSocketMessage(event_name="test", payload={"data": 123})
    await send_message(fastapi_websocket, message)

    fastapi_websocket.send_json.assert_called_once_with(message.model_dump())


@pytest.mark.asyncio
async def test_send_message_websockets(websockets_client: Mock) -> None:
    """Test sending a message through websockets client."""
    message = WebSocketMessage(event_name="test", payload={"data": 123})
    await send_message(websockets_client, message)

    websockets_client.send.assert_called_once_with(json.dumps(message.model_dump()))


def test_create_error_message() -> None:
    """Test creating an error message."""
    error_msg = "Test error"
    recipient = "client123"

    message = create_error_message(error_msg, recipient)

    assert message.event_name == "error"
    assert message.message == error_msg
    assert message.to == recipient
    assert message.payload is None


@pytest.mark.parametrize(
    "event_name,payload,to,message,expected",
    [
        (
            "test_event",
            {"data": 123},
            "all",
            None,
            {
                "event_name": "test_event",
                "payload": {"data": 123},
                "to": "all",
                "message": None,
                "from_id": "server",
            },
        ),
        (
            "msg",
            None,
            "others",
            "Hello",
            {
                "event_name": "msg",
                "payload": None,
                "to": "others",
                "message": "Hello",
                "from_id": "server",
            },
        ),
    ],
)
def test_create_message(event_name: str, payload: Any, to: str, message: str, expected: dict) -> None:
    """Test creating messages with different parameters."""
    result = create_message(event_name, payload, to, message)
    assert result.model_dump() == expected


@pytest.mark.asyncio
async def test_send_message_invalid_socket_type() -> None:
    """Test sending a message with an invalid socket type."""
    message = WebSocketMessage(event_name="test")
    invalid_socket = Mock()  # Not a WebSocket or WebSocketClientProtocol

    with pytest.raises(UnsupportedWebSocketTypeError, match="Unsupported WebSocket type"):
        await send_message(invalid_socket, message)


def test_create_message_defaults() -> None:
    """Test create_message with default values."""
    event_name = "test_event"
    payload = {"data": 123}
    to = "recipient"

    message = create_message(event_name, payload, to)

    assert message.event_name == event_name
    assert message.payload == payload
    assert message.to == to
    assert message.message is None
    assert message.from_id == "server"
