from datadivr.handlers.registry import HandlerType, websocket_handler
from datadivr.transport.messages import create_error_message
from datadivr.transport.models import WebSocketMessage


@websocket_handler("sum_event", HandlerType.SERVER)
@websocket_handler("sum_event_client", HandlerType.CLIENT)
async def sum_handler(message: WebSocketMessage) -> WebSocketMessage:
    """Handle requests to calculate the sum of a list of numbers.

    This handler processes both server and client-side sum calculation requests.
    It expects a payload containing a list of numbers and returns their sum.

    Args:
        message: A WebSocketMessage containing a payload with a "numbers" key
                holding a list of numeric values

    Returns:
        WebSocketMessage: A message containing the sum result or an error message

    Example payload:
        {"numbers": [1, 2, 3, 4, 5]}
    """
    try:
        payload = message.payload
        if not isinstance(payload, dict):
            return create_error_message("Invalid payload format", message.from_id)

        numbers = payload.get("numbers")
        if not isinstance(numbers, list):
            return create_error_message("Payload must contain a list of numbers", message.from_id)

        result = sum(float(n) for n in numbers)
        return WebSocketMessage(
            event_name="sum_handler_result",
            payload=result,
            to=message.from_id,
        )
    except Exception as e:
        return create_error_message(f"Error: {e!s}", message.from_id)


@websocket_handler("sum_handler_result", HandlerType.CLIENT)
async def handle_sum_result(message: WebSocketMessage) -> None:
    """Handle the result of a sum calculation on the client side.

    Args:
        message: A WebSocketMessage containing the sum result in its payload
    """
    print(f"*** handle_sum_result(): {message.from_id}: '{message.payload}'")
    return None


@websocket_handler("msg", HandlerType.CLIENT)
async def msg_handler(message: WebSocketMessage) -> None:
    """Handle generic text messages on the client side.

    Args:
        message: A WebSocketMessage containing a text message
    """
    print(f">> {message.from_id}({message.event_name}): '{message.message}'")
    return None
