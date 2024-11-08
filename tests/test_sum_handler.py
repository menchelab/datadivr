import pytest

from datadivr.handlers.sum_handler import sum_handler
from datadivr.utils.messages import Message, create_error_message


@pytest.mark.asyncio
async def test_sum_handler_valid_input():
    message = Message(event_name="sum_request", payload={"numbers": [1, 2, 3]}, to="user123")
    result = await sum_handler(message)
    assert result.event_name == "sum_handler_result"
    assert result.payload == 6  # 1 + 2 + 3 = 6


@pytest.mark.asyncio
async def test_sum_handler_invalid_input_not_list():
    message = Message(event_name="sum_request", payload={"numbers": "not_a_list"}, to="user123")
    result = await sum_handler(message)
    error_message = create_error_message("Payload must be a list of numbers", message.from_id)
    assert result.event_name == error_message.event_name
    assert result.message == error_message.message
    assert result.to == error_message.to


@pytest.mark.asyncio
async def test_sum_handler_invalid_input_contains_non_numbers():
    message = Message(event_name="sum_request", payload={"numbers": [1, "two", 3]}, to="user123")
    result = await sum_handler(message)
    assert result.event_name.startswith("error")  # Check if it returns an error event
    assert "Error:" in result.message  # Check if the error message contains "Error:"


@pytest.mark.asyncio
async def test_sum_handler_empty_list():
    message = Message(event_name="sum_request", payload={"numbers": []}, to="user123")
    result = await sum_handler(message)
    assert result.event_name == "sum_handler_result"
    assert result.payload == 0  # Sum of an empty list should be 0
