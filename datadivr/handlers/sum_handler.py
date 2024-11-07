from typing import Any

from fastapi import WebSocket

from ..utils.messages import create_error_message, create_message, send_message


async def sum_handler(event_data: dict[str, Any], websocket: WebSocket) -> None:
    """Handle sum calculation requests."""
    try:
        numbers: list[int] = event_data.get("payload", {}).get("numbers", [])
        if len(numbers) == 2:
            result: int = sum(numbers)
            response = create_message(
                event_name="sum_handler_result",
                payload={"result": result},
                to=event_data["from"],
                message=f"The sum of {numbers} is: {result}",
            )
        else:
            response = create_error_message(error_msg="Please provide exactly two numbers", to=event_data["from"])

        await send_message(websocket, response)
    except Exception as e:
        error_response = create_error_message(error_msg=f"Error processing request: {e!s}", to=event_data["from"])
        await send_message(websocket, error_response)
