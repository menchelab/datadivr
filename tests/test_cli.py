from unittest.mock import AsyncMock, Mock, patch

import pytest
from prompt_toolkit import PromptSession
from typer.testing import CliRunner

from datadivr.cli import app_cli, get_user_input, input_loop, run_client
from datadivr.exceptions import InputLoopInterrupted
from datadivr.transport.client import WebSocketClient


@pytest.fixture
def cli_runner():
    return CliRunner()


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
        patch("datadivr.cli.get_user_input", side_effect=mock_get_input),
        patch("prompt_toolkit.PromptSession", return_value=session),
        pytest.raises(InputLoopInterrupted),
    ):
        await input_loop(client)

    client.send_message.assert_awaited_once_with(payload={"data": 123}, event_name="test", to="others", msg=None)


def test_start_server(cli_runner):
    with patch("uvicorn.Server.serve") as mock_serve:
        result = cli_runner.invoke(app_cli, ["start-server"])
        assert result.exit_code == 0
        mock_serve.assert_called_once()


def test_start_client(cli_runner):
    """Test the start_client CLI command."""
    mock_run = Mock()

    with patch("asyncio.run", mock_run):
        result = cli_runner.invoke(app_cli, ["start-client"])
        assert result.exit_code == 0
        mock_run.assert_called_once()


@pytest.mark.asyncio
async def test_run_client():
    """Test the run_client function directly."""
    mock_client = AsyncMock(spec=WebSocketClient)
    mock_tasks = []

    def mock_create_task(coro):
        task = AsyncMock()
        task.cancel = Mock()  # Regular Mock since cancel is synchronous
        mock_tasks.append(task)
        return task

    with (
        patch("datadivr.cli.WebSocketClient", return_value=mock_client),
        patch("asyncio.create_task", side_effect=mock_create_task),
        patch("asyncio.gather", AsyncMock()),
        patch("datadivr.cli.input_loop", AsyncMock()),
    ):
        await run_client("localhost", 8765)

        mock_client.connect.assert_awaited_once()
        mock_client.disconnect.assert_awaited_once()

        assert len(mock_tasks) == 2
        for task in mock_tasks:
            task.cancel.assert_called_once()


@pytest.mark.asyncio
async def test_run_client_connection_error():
    """Test handling of connection errors in run_client."""
    mock_client = AsyncMock(spec=WebSocketClient)
    mock_client.connect.side_effect = OSError("Connection refused")

    with patch("datadivr.cli.WebSocketClient", return_value=mock_client):
        await run_client("localhost", 8765)
        mock_client.connect.assert_awaited_once()
        mock_client.disconnect.assert_not_called()


@pytest.mark.asyncio
async def test_run_client_general_error():
    """Test handling of general errors in run_client."""
    mock_client = AsyncMock(spec=WebSocketClient)
    mock_tasks = []

    def mock_create_task(coro):
        task = AsyncMock()
        task.cancel = Mock()
        mock_tasks.append(task)
        return task

    with (
        patch("datadivr.cli.WebSocketClient", return_value=mock_client),
        patch("asyncio.create_task", side_effect=mock_create_task),
        patch("asyncio.gather", AsyncMock(side_effect=Exception("Test error"))),
        patch("datadivr.cli.input_loop", AsyncMock()),
    ):
        await run_client("localhost", 8765)

        mock_client.connect.assert_awaited_once()
        mock_client.disconnect.assert_awaited_once()

        assert len(mock_tasks) == 2
        for task in mock_tasks:
            task.cancel.assert_called_once()
