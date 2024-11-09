import json
from typing import Any, Optional, Union

from fastapi import WebSocket
from websockets import WebSocketClientProtocol

from datadivr.transport.models import WebSocketMessage
from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


async def send_message(websocket: Union[WebSocket, WebSocketClientProtocol], message: WebSocketMessage) -> None:
    """Send a message through the websocket."""
    message_data = message.model_dump()
    logger.debug("send_message", message=message_data)
    if isinstance(websocket, WebSocket):
        await websocket.send_json(message_data)
    elif isinstance(websocket, WebSocketClientProtocol):
        await websocket.send(json.dumps(message_data))


def create_error_message(error_msg: str, to: str) -> WebSocketMessage:
    """Create a standardized error message."""
    return WebSocketMessage(event_name="error", message=error_msg, to=to)


def create_message(event_name: str, payload: Any, to: str, message: Optional[str] = None) -> WebSocketMessage:
    """Create a standardized message."""
    return WebSocketMessage(event_name=event_name, payload=payload, to=to, message=message)
