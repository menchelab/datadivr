from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket, WebSocketDisconnect

from datadivr.exceptions import InvalidMessageFormat
from datadivr.transport.models import WebSocketMessage
from datadivr.transport.server import (
    app,
    broadcast,
    clients,
    handle_connection,
    handle_msg,
)


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def websocket_mock():
    mock = AsyncMock(spec=WebSocket)
    mock.receive_json = AsyncMock()
    mock.send_json = AsyncMock()
    return mock


@pytest.fixture
def clear_clients():
    # Clear the global clients dict before and after each test
    clients.clear()
    yield
    clients.clear()


@pytest.mark.asyncio
async def test_websocket_connection(websocket_mock, clear_clients):
    """Test basic WebSocket connection and disconnection"""
    # Mock a valid message response
    websocket_mock.receive_json.side_effect = [
        # First call returns valid message
        {"event_name": "test_event", "payload": {"data": "test"}, "to": "all"},
        # Second call raises WebSocketDisconnect
        WebSocketDisconnect(),
    ]

    # Test connection and immediate disconnection
    await handle_connection(websocket_mock)

    # Verify the connection was made before disconnect
    websocket_mock.accept.assert_called_once()
    assert len(clients) == 0  # Should be 0 after disconnect


@pytest.mark.asyncio
async def test_handle_msg_valid():
    """Test handling a valid message"""
    message = WebSocketMessage(event_name="test_event", payload={"data": "test"}, to="all")

    # Mock a handler
    with patch("datadivr.transport.server.get_handlers") as mock_handlers:
        mock_handler = AsyncMock(return_value=message)
        mock_handlers.return_value = {"test_event": mock_handler}

        response = await handle_msg(message)
        assert response == message
        mock_handler.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_handle_msg_unknown_event():
    """Test handling a message with unknown event"""
    message = WebSocketMessage(event_name="unknown_event", payload={"data": "test"}, to="all")

    with patch("datadivr.transport.server.get_handlers") as mock_handlers:
        mock_handlers.return_value = {}
        response = await handle_msg(message)
        assert response == message


@pytest.mark.asyncio
async def test_broadcast_to_all(websocket_mock, clear_clients):
    """Test broadcasting message to all clients"""
    clients[websocket_mock] = "test_client"

    message = WebSocketMessage(event_name="test_event", payload={"data": "test"}, to="all")

    await broadcast(message, websocket_mock)
    websocket_mock.send_json.assert_called_once_with(message.model_dump())


@pytest.mark.asyncio
async def test_broadcast_to_others(websocket_mock, clear_clients):
    """Test broadcasting message to others"""
    sender = AsyncMock(spec=WebSocket)
    receiver = websocket_mock

    clients[sender] = "sender"
    clients[receiver] = "receiver"

    message = WebSocketMessage(event_name="test_event", payload={"data": "test"}, to="others")

    await broadcast(message, sender)
    receiver.send_json.assert_called_once_with(message.model_dump())
    sender.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_broadcast_to_specific_client(websocket_mock, clear_clients):
    """Test broadcasting message to specific client"""
    target_client = websocket_mock
    other_client = AsyncMock(spec=WebSocket)

    clients[target_client] = "target"
    clients[other_client] = "other"

    message = WebSocketMessage(event_name="test_event", payload={"data": "test"}, to="target")

    await broadcast(message, other_client)
    target_client.send_json.assert_called_once_with(message.model_dump())
    other_client.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_message_format(websocket_mock, clear_clients):
    """Test handling invalid message format"""
    # Set up the mock to first accept connection, then return invalid message
    websocket_mock.receive_json.side_effect = [
        {
            "invalid_field": "value",  # Missing required fields
        }
    ]

    with pytest.raises(InvalidMessageFormat):
        await handle_connection(websocket_mock)

    websocket_mock.accept.assert_called_once()


@pytest.mark.asyncio
async def test_broadcast_error_handling(websocket_mock, clear_clients):
    """Test error handling during broadcast"""
    clients[websocket_mock] = "test_client"
    websocket_mock.send_json.side_effect = Exception("Test error")

    message = WebSocketMessage(event_name="test_event", payload={"data": "test"}, to="all")

    # Should not raise exception
    await broadcast(message, AsyncMock(spec=WebSocket))


@pytest.mark.asyncio
async def test_multiple_clients_broadcasting(clear_clients):
    """Test broadcasting with multiple clients for 'all' and 'others' scenarios."""
    # Create 4 mock clients
    clients_mocks = [AsyncMock(spec=WebSocket) for _ in range(4)]

    # Set up each mock with basic async methods
    for i, mock in enumerate(clients_mocks):
        mock.send_json = AsyncMock()
        mock.receive_json = AsyncMock()
        clients[mock] = f"client_{i}"  # Register each client with a unique ID

    # Test broadcasting to 'all'
    message_to_all = WebSocketMessage(event_name="test_event", payload={"data": "test_all"}, to="all")

    # Broadcast from client_0 to all
    await broadcast(message_to_all, clients_mocks[0])

    # Verify all clients received the message
    message_data = message_to_all.model_dump()
    for client in clients_mocks:
        client.send_json.assert_called_once_with(message_data)
        client.send_json.reset_mock()  # Reset for next test

    # Test broadcasting to 'others'
    message_to_others = WebSocketMessage(event_name="test_event", payload={"data": "test_others"}, to="others")

    # Broadcast from client_1 to others
    sender = clients_mocks[1]
    await broadcast(message_to_others, sender)

    # Verify all clients except sender received the message
    message_data = message_to_others.model_dump()
    for client in clients_mocks:
        if client == sender:
            client.send_json.assert_not_called()
        else:
            client.send_json.assert_called_once_with(message_data)
        client.send_json.reset_mock()

    # Verify client count
    assert len(clients) == 4
