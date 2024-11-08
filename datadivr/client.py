import json
from typing import Any, Callable, Optional

import websockets
from websockets import WebSocketClientProtocol

from .utils.messages import Message, send_message


class NotConnectedError(RuntimeError):
    """Exception raised when the client is not connected to the server."""

    def __init__(self) -> None:
        super().__init__("Not connected to server")


class WebSocketClient:
    def __init__(self, uri: str):
        self.uri = uri
        self.handlers: dict[str, Callable] = {}
        self.websocket: Optional[WebSocketClientProtocol] = None

    async def connect(self) -> None:
        self.websocket = await websockets.connect(self.uri)
        await self.send_handler_names()

    async def receive_messages(self) -> None:
        """Listen for incoming messages from the server."""
        if not self.websocket:
            raise NotConnectedError()

        try:
            async for message in self.websocket:
                event_data = json.loads(message)
                print(f"< received message: {event_data}")
                await self.handle_event(event_data, self.websocket)
        except websockets.exceptions.ConnectionClosed:
            print("X Connection closed")

    async def handle_event(self, event_data: dict, websocket: WebSocketClientProtocol) -> None:
        event_name = event_data["event_name"]
        if event_name in self.handlers:
            print(f"<< handling event: {event_name}")
            handler = self.handlers[event_name]
            message = Message.from_dict(event_data)
            response = await handler(message)
            if response and isinstance(response, Message):
                await send_message(websocket, response)
        else:
            print(f"<< no handler for event: {event_name}")

    def register_handler(self, event_name: str, handler: Callable) -> None:
        self.handlers[event_name] = handler

    async def send_message(self, payload: Any, event_name: str, message: str = None, to: str = "others") -> None:
        if self.websocket:
            message = Message(event_name=event_name, payload=payload, to=to, message=message)
            await send_message(self.websocket, message)
        else:
            raise NotConnectedError()

    async def disconnect(self) -> None:
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def send_handler_names(self) -> None:
        """Send a message with the names of all registered handlers."""
        handler_names = list(self.handlers.keys())
        payload = {"handlers": handler_names}
        print(f">> sending handler names: {handler_names}")
        await self.send_message(payload=payload, event_name="connected successfully", to="others")
