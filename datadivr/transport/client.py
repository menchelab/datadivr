"""WebSocket client implementation for datadivr.

This module provides a WebSocket client that can connect to a datadivr server,
send messages, and handle responses using registered event handlers.

Example:
    ```python
    client = WebSocketClient("ws://localhost:8765/ws")
    await client.connect()

    # Send a message
    await client.send_message(
        payload={"numbers": [1, 2, 3]},
        event_name="sum_event"
    )

    # Start receiving messages
    await client.receive_messages()
    ```
"""

import json
from typing import Any, Optional

import websockets
from websockets import WebSocketClientProtocol

from datadivr.exceptions import NotConnectedError
from datadivr.handlers.registry import HandlerType, get_handlers
from datadivr.transport.messages import send_message
from datadivr.transport.models import WebSocketMessage


class WebSocketClient:
    """A WebSocket client for communicating with a datadivr server.

    This class handles the connection to a WebSocket server, message sending,
    and event handling for received messages.

    Attributes:
        uri: The WebSocket server URI to connect to
        handlers: Dictionary of registered event handlers
        websocket: The active WebSocket connection (if connected)

    Example:
        ```python
        client = WebSocketClient("ws://localhost:8765/ws")
        await client.connect()
        await client.send_message(payload=data, event_name="custom_event")
        ```
    """

    def __init__(self, uri: str):
        """Initialize the WebSocket client.

        Args:
            uri: The WebSocket server URI to connect to
        """
        self.uri = uri
        self.handlers = get_handlers(HandlerType.CLIENT)
        self.websocket: Optional[WebSocketClientProtocol] = None

    async def connect(self) -> None:
        """Connect to the WebSocket server and send initial handler information."""
        self.websocket = await websockets.connect(self.uri)
        await self.send_handler_names()

    async def receive_messages(self) -> None:
        """Listen for incoming messages from the server.

        This method runs in a loop, receiving and handling messages until
        the connection is closed.

        Raises:
            NotConnectedError: If called before connecting to the server
        """
        if not self.websocket:
            raise NotConnectedError()

        try:
            while True:
                message = await self.websocket.recv()
                event_data = json.loads(message)
                print(f"< received message: {event_data}")
                await self.handle_event(event_data, self.websocket)
        except websockets.exceptions.ConnectionClosed:
            print("X Connection closed")

    async def handle_event(self, event_data: dict, websocket: WebSocketClientProtocol) -> None:
        """Handle an incoming event using registered handlers.

        Args:
            event_data: The received event data
            websocket: The WebSocket connection to use for responses
        """
        event_name = event_data["event_name"]
        if event_name in self.handlers:
            print(f"<< handling event: {event_name}")
            handler = self.handlers[event_name]
            message = WebSocketMessage.model_validate(event_data)
            response = await handler(message)
            if response and isinstance(response, WebSocketMessage):
                await send_message(websocket, response)
        else:
            print(f"<< no handler for event: {event_name}")

    async def send_message(self, payload: Any, event_name: str, msg: Optional[str] = None, to: str = "others") -> None:
        """Send a message to the server.

        Args:
            payload: The message payload
            event_name: The name of the event
            msg: Optional text message
            to: The recipient of the message (default: "others")

        Raises:
            NotConnectedError: If called before connecting to the server
        """
        if self.websocket:
            message = WebSocketMessage(event_name=event_name, payload=payload, to=to, message=msg)
            await send_message(self.websocket, message)
        else:
            raise NotConnectedError()

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def send_handler_names(self) -> None:
        """Send a message with the names of all registered handlers.

        This is called automatically after connection to inform the server
        about available client-side handlers.
        """
        handler_names = list(self.handlers.keys())
        payload = {"handlers": handler_names}
        print(f">> sending handler names  : {handler_names}")
        await self.send_message(payload=payload, event_name="connected successfully", to="others")
