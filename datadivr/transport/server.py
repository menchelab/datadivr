import uuid
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from datadivr.exceptions import InvalidMessageFormat
from datadivr.handlers.registry import HandlerType, get_handlers
from datadivr.transport.models import WebSocketMessage
from datadivr.utils.logging import get_logger

app = FastAPI()
logger = get_logger(__name__)

# Module-level state
clients: dict[WebSocket, str] = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await handle_connection(websocket)


async def handle_connection(websocket: WebSocket) -> None:
    """Handle WebSocket connection."""
    await websocket.accept()
    client_id = str(uuid.uuid4())
    clients[websocket] = client_id
    logger.info("client_connected", client_id=client_id, connected_clients=len(clients))

    try:
        while True:
            data = await websocket.receive_json()
            try:
                message = WebSocketMessage.model_validate(data)
                message.from_id = client_id
                response = await handle_msg(message)
                if response is not None:  # Only broadcast if there's a response
                    await broadcast(response, websocket)
            except ValueError as e:
                logger.exception("invalid_message_format", error=str(e), client_id=client_id)
                raise InvalidMessageFormat() from None
    except WebSocketDisconnect:
        del clients[websocket]
        logger.info("client_disconnected", client_id=client_id)
    except Exception as e:
        logger.exception("websocket_error", error=str(e), client_id=client_id)
        raise


async def handle_msg(message: WebSocketMessage) -> Optional[WebSocketMessage]:
    """Handle incoming WebSocket message."""
    logger.debug("message_received", message=message.model_dump())

    handlers = get_handlers(HandlerType.SERVER)
    if message.event_name in handlers:
        logger.info("handling_event", event_name=message.event_name)
        return await handlers[message.event_name](message)
    return message


async def broadcast(message: WebSocketMessage, sender: WebSocket) -> None:
    """Broadcast message to appropriate clients."""
    message_data = message.model_dump()
    targets: list[WebSocket] = []

    if message.to == "all":
        targets = list(clients.keys())
    elif message.to == "others":
        targets = [ws for ws in clients if ws != sender]
    else:
        targets = [ws for ws, cid in clients.items() if cid == message.to]

    logger.debug("broadcasting_message", message=message_data, num_targets=len(targets))

    for websocket in targets:
        try:
            await websocket.send_json(message_data)
        except Exception as e:
            logger.exception("broadcast_error", error=str(e), client_id=clients[websocket])
