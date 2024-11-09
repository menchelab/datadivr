import json
from typing import Any, Optional, Union

from fastapi import WebSocket
from websockets import WebSocketClientProtocol

from datadivr.exceptions import UnsupportedWebSocketTypeError
from datadivr.transport.models import WebSocketMessage
from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


async def send_message(websocket: Union[WebSocket, WebSocketClientProtocol], message: WebSocketMessage) -> None:
    """Send a message through a WebSocket connection.

    This function handles sending messages through both FastAPI WebSocket and
    websockets.WebSocketClientProtocol connections.

    Args:
        websocket: The WebSocket connection to send the message through
        message: The WebSocketMessage to send

    Raises:
        UnsupportedWebSocketTypeError: If the websocket is not a supported type

    Example:
        ```python
        await send_message(ws, WebSocketMessage(
            event_name="update",
            payload={"status": "ok"}
        ))
        ```
    """
    message_data = message.model_dump()
    logger.debug("send_message", message=message_data)

    if isinstance(websocket, WebSocket):
        await websocket.send_json(message_data)
    elif isinstance(websocket, WebSocketClientProtocol):
        await websocket.send(json.dumps(message_data))
    else:
        raise UnsupportedWebSocketTypeError()


def create_error_message(error_msg: str, to: str) -> WebSocketMessage:
    """Create a standardized error message.

    Args:
        error_msg: The error message text
        to: The recipient of the error message

    Returns:
        A WebSocketMessage with event_name="error" containing the error message
    """
    return WebSocketMessage(event_name="error", message=error_msg, to=to)


def create_message(event_name: str, payload: Any, to: str, message: Optional[str] = None) -> WebSocketMessage:
    """Create a standardized WebSocket message.

    Args:
        event_name: The name of the event
        payload: The message payload
        to: The recipient of the message
        message: Optional text message

    Returns:
        A WebSocketMessage with the specified parameters
    """
    return WebSocketMessage(event_name=event_name, payload=payload, to=to, message=message)
