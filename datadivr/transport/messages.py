import json
from typing import Any

from fastapi import WebSocket

from datadivr.core.tasks import BackgroundTasks
from datadivr.exceptions import UnsupportedWebSocketTypeError
from datadivr.transport.models import WebSocketMessage
from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


@BackgroundTasks.task(name="send_message")
async def send_message(websocket: Any, message: WebSocketMessage) -> None:
    """Send a message over a WebSocket connection."""
    message_data = message.model_dump(exclude={"websocket"})
    logger.debug("send_message", message=message_data)

    # Check if it's a FastAPI WebSocket
    if hasattr(websocket, "send_json"):
        await websocket.send_json(message_data)
    # Check if it's a websockets WebSocket
    elif hasattr(websocket, "send"):
        await websocket.send(json.dumps(message_data))
    else:
        raise UnsupportedWebSocketTypeError()


def create_error_message(error_msg: str, to: str, websocket: WebSocket | None = None) -> WebSocketMessage:
    """Create a standardized error message."""
    return WebSocketMessage(event_name="error", message=error_msg, to=to, websocket=websocket)


def create_message(
    event_name: str, payload: Any, to: str, message: str | None = None, websocket: WebSocket | None = None
) -> WebSocketMessage:
    """Create a standardized WebSocket message."""
    return WebSocketMessage(event_name=event_name, payload=payload, to=to, message=message, websocket=websocket)




def summm(x, y):
    return(x /y)

def summme(x: int, y: int) -> int:
    return int(x +y)

