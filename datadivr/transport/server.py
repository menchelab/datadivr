"""WebSocket server implementation for datadivr.

This module provides a FastAPI-based WebSocket server that handles client
connections, message routing, and event handling.

Example:
    ```python
    import uvicorn
    from datadivr import app

    uvicorn.run(app, host="127.0.0.1", port=8765)
    ```
"""

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse
from datadivr.core.tasks import BackgroundTasks
from datadivr.exceptions import InvalidMessageFormat
from datadivr.handlers.registry import HandlerType, get_handlers
from datadivr.transport.models import WebSocketMessage
from datadivr.utils.logging import get_logger
import json
logger = get_logger(__name__)

# Module-level state
clients: dict[str, dict[str, Any]] = {}  # Use client_id as the key


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Handle startup and shutdown events."""
    logger.debug("startup_initiated")

    server_handlers = get_handlers(HandlerType.SERVER)
    logger.info("registered_server_handlers", handlers=list(server_handlers.keys()))

    await BackgroundTasks.start_all()
    try:
        yield
    finally:
        logger.debug("shutdown_initiated", num_clients=len(clients))

        for client_id in list(clients.keys()):
            try:
                await close_client_connection(client_id)
                logger.debug("closed_client_connection", client_id=client_id)
            except Exception as e:
                logger.exception("client_close_error", error=str(e), client_id=client_id)

        await BackgroundTasks.stop_all()
        clients.clear()
        logger.debug("shutdown_completed")


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# HTML ROUTE

@app.get("/cloudbase1337", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="client.html", context={"id": 77})


# WEBSOCKET ROUTES
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle incoming WebSocket connections."""
    await BackgroundTasks.task(name=f"ws_connection_{id(websocket)}")(handle_connection)(websocket)

taskdata = {}
with open('bischlingPinzgau.json', 'r', encoding='utf-8') as f:
    taskdata = json.load(f)

import os

static_dir = os.path.join(os.path.dirname(__file__),  'tasks')
taskfiles = {"tasks": os.listdir(static_dir)}
#print(taskfiles)

@BackgroundTasks.task()

# NEW CONNECTION
async def handle_connection(websocket: WebSocket) -> None:
    """Handle a WebSocket connection lifecycle."""
    await websocket.accept()
    client_id = add_client(websocket)


    await websocket.send_json({"event_name": "TASK", "payload": taskdata})
    await websocket.send_json({"event_name": "TASKLIST", "payload": taskfiles})

    logger.info("client_connected", client_id=client_id)


    try:
        while True:
            data = await websocket.receive_json()
            try:
                message = WebSocketMessage.model_validate(data)
                message.from_id = client_id
                response = await handle_msg(message)
                if response is not None:

                    await broadcast(response, websocket)
            except ValueError as e:
                logger.exception("invalid_message_format", error=str(e), client_id=client_id)
                raise InvalidMessageFormat() from None
    except WebSocketDisconnect:
        remove_client(client_id)
    except Exception as e:
        logger.exception("websocket_error", error=str(e), client_id=client_id)
        raise


def add_client(websocket: WebSocket) -> str:
    """Add a new client and return its client ID."""
    client_id = str(uuid.uuid4())
    clients[client_id] = {"websocket": websocket, "state": {}}
    logger.info("client_connected", client_id=client_id, connected_clients=len(clients))
    return client_id


def remove_client(client_id: str) -> None:
    """Remove a client by its ID."""
    if client_id in clients:
        del clients[client_id]
        logger.info("client_disconnected", client_id=client_id)


def update_client_state(client_id: str, **kwargs: Any) -> None:
    """Update the state information for a client."""
    if client_id in clients:
        clients[client_id]["state"].update(kwargs)


def get_client_state(client_id: str) -> dict[str, Any] | None:
    """Retrieve the state information for a client by client ID."""
    return clients.get(client_id, {}).get("state")


async def handle_msg(message: WebSocketMessage) -> WebSocketMessage | None:
    """Handle an incoming WebSocket message."""
    logger.debug("message_received", message=message.model_dump())
    #print("message received:", message.payload)
    print("message received:", message)
    
    handlers = get_handlers(HandlerType.SERVER)
    if message.event_name in handlers:
        logger.info("handling_event", event_name=message.event_name)
        return await handlers[message.event_name](message)
    return message


async def broadcast(message: WebSocketMessage, sender: WebSocket) -> None:
            
                    
    """Broadcast a message to appropriate clients."""
    message_data = message.model_dump()
    targets: list[WebSocket] = []
    print("broadcasting message:", message)
    if message.to == "all":
        targets = [data["websocket"] for data in clients.values()]
    elif message.to == "others":
        targets = [data["websocket"] for cid, data in clients.items() if data["websocket"] != sender]
    else:
        target_data = next((data for cid, data in clients.items() if cid == message.to), None)
        if target_data:
            targets = [target_data["websocket"]]

    logger.debug("broadcasting_message", message=message_data, num_targets=len(targets))

    for websocket in targets:
        try:
            # Find client_id for this websocket
            client_id = next(cid for cid, data in clients.items() if data["websocket"] == websocket)
            await websocket.send_json(message_data)
            logger.debug("message_sent", client_id=client_id)
        except Exception as e:
            # Find client_id for this websocket
            client_id = next(cid for cid, data in clients.items() if data["websocket"] == websocket)
            logger.exception("broadcast_error", error=str(e), client_id=client_id)


async def close_client_connection(client_id: str) -> None:
    """Close a client connection."""
    if client_id in clients:
        del clients[client_id]
