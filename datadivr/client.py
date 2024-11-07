import json
from typing import Any, Callable, Optional

from fastapi import WebSocket

from .exceptions import NotConnectedError
from .utils.messages import Message, send_message


class WebSocketClient:
    def __init__(self, uri: str):
        self.uri = uri
        self.handlers: dict[str, Callable] = {}
        self.websocket: Optional[WebSocket] = None

    async def connect(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        await self.websocket.accept()

    async def receive_messages(self) -> None:
        """Listen for incoming messages from the server."""
        if not self.websocket:
            raise NotConnectedError()

        try:
            while True:
                message = await self.websocket.receive_text()
                event_data = json.loads(message)
                print(f"< received message: {event_data}")
                await self.handle_event(event_data)
        except Exception as e:
            print(f"X Connection closed: {e}")

    async def handle_event(self, event_data: dict) -> None:
        event_name = event_data["event_name"]
        if event_name in self.handlers:
            print(f"<< handling event: {event_name}")
            handler = self.handlers[event_name]
            message = Message.from_dict(event_data)
            await handler(message, self.websocket)
        else:
            print(f"<< no handler for event: {event_name}")

    def register_handler(self, event_name: str, handler: Callable) -> None:
        self.handlers[event_name] = handler

    async def send_message(self, payload: Any, event_name: str, to: str = "others") -> None:
        if self.websocket:
            message = Message(event_name=event_name, payload=payload, to=to)
            await send_message(self.websocket, message)
        else:
            raise NotConnectedError()

    async def disconnect(self) -> None:
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
