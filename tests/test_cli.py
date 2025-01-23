from unittest.mock import AsyncMock, Mock, patch

import pytest
from prompt_toolkit import PromptSession
from typer.testing import CliRunner

from datadivr.commandlineinterface.client import get_user_input, input_loop, run_client, start_client_app
from datadivr.commandlineinterface.server import start_server_app
from datadivr.exceptions import InputLoopInterrupted
from datadivr.transport.client import WebSocketClient


@pytest.fixture
def cli_runner():
    return CliRunner()


def test_start_server_cli():
    """Test the server CLI command."""
    with (
        patch("uvicorn.Config") as mock_config,
        patch("uvicorn.Server") as mock_server,
        patch("asyncio.run"),
        patch("fastapi.FastAPI"),
    ):
        start_server_app(host="localhost", port=8765, static_dir=None, log_level="INFO", pretty=False)
        mock_config.assert_called_once()
        mock_server.assert_called_once()


def test_start_client_cli():
    """Test the client CLI command."""
    with patch("asyncio.run") as mock_run:
        start_client_app(host="localhost", port=8765, log_level="INFO")
        mock_run.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_input_valid_json():
    session = Mock(spec=PromptSession)
    session.prompt_async = AsyncMock(return_value='{"test": "data"}')

    result = await get_user_input(session)
    assert result == {"test": "data"}
    session.prompt_async.assert_awaited_once_with("Enter JSON > ")


@pytest.mark.asyncio
async def test_get_user_input_quit():
    session = Mock(spec=PromptSession)
    session.prompt_async = AsyncMock(return_value="quit")

    result = await get_user_input(session)
    assert result is None
    session.prompt_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user_input_invalid_json():
    session = Mock(spec=PromptSession)
    session.prompt_async = AsyncMock(side_effect=["invalid json", '{"valid": "json"}'])

    result = await get_user_input(session)
    assert result == {"valid": "json"}
    assert session.prompt_async.await_count == 2


@pytest.mark.asyncio
async def test_get_user_input_eof():
    """Test handling of EOF (Ctrl+D) in get_user_input."""
    session = Mock(spec=PromptSession)
    session.prompt_async = AsyncMock(side_effect=EOFError())

    result = await get_user_input(session)
    assert result is None
    session.prompt_async.assert_awaited_once_with("Enter JSON > ")


@pytest.mark.asyncio
async def test_input_loop():
    client = Mock(spec=WebSocketClient)
    client.send_message = AsyncMock()

    session = Mock(spec=PromptSession)

    async def mock_get_input(session):
        if not hasattr(mock_get_input, "called"):
            mock_get_input.called = True
            return {"event_name": "test", "payload": {"data": 123}}
        raise KeyboardInterrupt()

    with (
        patch("datadivr.commandlineinterface.client.get_user_input", side_effect=mock_get_input),
        patch("prompt_toolkit.PromptSession", return_value=session),
        pytest.raises(InputLoopInterrupted),
    ):
        await input_loop(client)

    client.send_message.assert_awaited_once_with(payload={"data": 123}, event_name="test", to="others", msg=None)


@pytest.mark.asyncio
async def test_run_client():
    """Test the run_client function directly."""
    mock_client = AsyncMock(spec=WebSocketClient)
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.receive_messages = AsyncMock()

    with patch("datadivr.commandlineinterface.client.WebSocketClient", return_value=mock_client):
        await run_client("localhost", 8765)
        mock_client.connect.assert_awaited_once()
        mock_client.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_client_connection_error():
    """Test handling of connection errors in run_client."""
    mock_client = AsyncMock(spec=WebSocketClient)
    mock_client.connect = AsyncMock(side_effect=OSError("Connection refused"))
    mock_client.disconnect = AsyncMock()

    with patch("datadivr.commandlineinterface.client.WebSocketClient", return_value=mock_client):
        await run_client("localhost", 8765)
        mock_client.connect.assert_awaited_once()
        mock_client.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_client_general_error():
    """Test handling of general errors in run_client."""
    mock_client = AsyncMock(spec=WebSocketClient)
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.receive_messages = AsyncMock()

    with patch("datadivr.commandlineinterface.client.WebSocketClient", return_value=mock_client):
        await run_client("localhost", 8765)
        mock_client.connect.assert_awaited_once()
        mock_client.disconnect.assert_awaited_once()
