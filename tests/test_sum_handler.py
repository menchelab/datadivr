import pytest

from datadivr.handlers.builtin.sum_handler import handle_sum_result, msg_handler, sum_handler
from datadivr.transport.models import WebSocketMessage


@pytest.mark.asyncio
async def test_sum_handler_empty_payload():
    message = WebSocketMessage(event_name="sum_event", payload=None)
    result = await sum_handler(message)
    assert result.event_name == "error"


@pytest.mark.asyncio
async def test_handle_sum_result(capsys):
    message = WebSocketMessage(event_name="sum_handler_result", payload=42, from_id="test")
    await handle_sum_result(message)
    captured = capsys.readouterr()
    assert "42" in captured.out


@pytest.mark.asyncio
async def test_msg_handler(capsys):
    message = WebSocketMessage(event_name="msg", message="test message", from_id="test")
    await msg_handler(message)
    captured = capsys.readouterr()
    assert "test message" in captured.out
