import uuid
from collections.abc import Awaitable
from typing import Callable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from rich.console import Console
from rich.pretty import Pretty
import json

from datadivr.utils.messages import Message, send_message

app = FastAPI()

# Module-level state
clients: dict[WebSocket, str] = {}  # websocket -> client_id
handlers: dict[str, Callable[[Message], Awaitable[Message]]] = {}

console = Console()


async def handle_connection(websocket: WebSocket) -> None:
    await websocket.accept()
    client_id = str(uuid.uuid4())
    clients[websocket] = client_id
    console.print(f"New client connected: [bold green]{client_id}[/bold green]")

    try:
        while True:
            data = await websocket.receive_json()
            message = Message.from_dict(data)
            message.from_id = client_id
            response = await handle_msg(message)
            await broadcast(response, websocket)
    except WebSocketDisconnect:
        del clients[websocket]
        console.print(f"Client disconnected: [bold red]{client_id}[/bold red]")


async def handle_msg(message: Message) -> Message:
    # Print the received message in colorful JSON format
    console.print(f"[bold green]RECEIVED MESSAGE:[/bold green]")
    console.print(Pretty(message.to_dict()), style="green")

    if message.event_name in handlers:
        console.print(f"[bold yellow]running EVENT HANDLER: {message.event_name}[/bold yellow]")
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

    if len(recipients) > 0:
        console.print(f"[bold blue]BROADCASTING MESSAGE to {len(recipients)} clients:[/bold blue]")
        console.print(Pretty(message.to_dict()), style="blue")

    for recipient in recipients:
        await send_message(recipient, message)


def register_handler(event_name: str, handler: Callable[[Message], Awaitable[Message]]) -> None:
    console.print(f"* Registered handler for event: [bold blue]{event_name}[/bold blue]")
    handlers[event_name] = handler


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await handle_connection(websocket)
