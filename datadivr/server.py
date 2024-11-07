import uuid
from collections.abc import Awaitable
from typing import Callable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from datadivr.utils.messages import Message, send_message

app = FastAPI()

# Module-level state
clients: dict[WebSocket, str] = {}  # websocket -> client_id
handlers: dict[str, Callable[[Message], Awaitable[Message]]] = {}


async def handle_connection(websocket: WebSocket) -> None:
    await websocket.accept()
    client_id = str(uuid.uuid4())
    clients[websocket] = client_id
    print(f"New client connected: {client_id}")

    try:
        while True:
            data = await websocket.receive_json()
            message = Message.from_dict(data)
            message.from_id = client_id
            response = await handle_msg(message)
            await broadcast(response, websocket)
    except WebSocketDisconnect:
        del clients[websocket]
        print(f"Client disconnected: {client_id}")


async def handle_msg(message: Message) -> Message:
    print(f"Received: {message.to_dict()}")

    if message.event_name in handlers:
        return await handlers[message.event_name](message)
    return message


async def broadcast(message: Message, sender: WebSocket) -> None:
    to = message.to

    recipients = []
    if to == "all":
        recipients = list(clients.keys())
    elif to == "others":
        recipients = [ws for ws in clients if ws != sender]
    elif to in clients.values():  # specific client
        recipients = [ws for ws, cid in clients.items() if cid == to]

    for recipient in recipients:
        await send_message(recipient, message)


def register_handler(event_name: str, handler: Callable[[Message], Awaitable[Message]]) -> None:
    print(f"* Registered handler for event: {event_name}")
    handlers[event_name] = handler


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await handle_connection(websocket)
